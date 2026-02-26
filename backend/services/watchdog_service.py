"""
WatchdogService — Docling Agent v3
Surveille le dossier magique local et traite automatiquement
les nouveaux PDF/images déposés.
Compatible PC Windows/Linux via watchdog library.
"""

import asyncio
import logging
import shutil
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from backend.core.config import Config
from backend.core.orchestrator import Orchestrator

logger = logging.getLogger(__name__)

# Extensions acceptées
EXTENSIONS_OK = {".pdf", ".jpg", ".jpeg", ".png", ".webp", ".heic"}

# Délai avant traitement (évite les fichiers en cours de copie)
DEBOUNCE_SECONDS = 2.0


class InvoiceFileHandler(FileSystemEventHandler):
    """Handler watchdog — appelé à chaque nouveau fichier."""

    def __init__(self, model_id: str, loop: asyncio.AbstractEventLoop):
        super().__init__()
        self.model_id    = model_id
        self.loop        = loop
        self._processing = set()   # Évite double traitement

    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() not in EXTENSIONS_OK:
            return
        if path.parent.name in ("Traitees", "Erreurs"):
            return   # Ignorer les sous-dossiers de sortie
        if str(path) in self._processing:
            return

        logger.info(f"📂 Nouveau fichier détecté: {path.name}")
        self._processing.add(str(path))
        asyncio.run_coroutine_threadsafe(
            self._process_with_delay(path),
            self.loop
        )

    async def _process_with_delay(self, path: Path):
        """Attente + traitement + déplacement."""
        await asyncio.sleep(DEBOUNCE_SECONDS)

        try:
            # Vérifier que le fichier existe encore (pas supprimé entre temps)
            if not path.exists():
                return

            file_bytes = path.read_bytes()
            result = await Orchestrator.process_file(
                file_bytes=file_bytes,
                filename=path.name,
                model_id=self.model_id,
                source="watchdog",
            )

            if result["success"]:
                # Déplacer vers /Traitees
                dest = path.parent / "Traitees" / path.name
                dest.parent.mkdir(exist_ok=True)
                shutil.move(str(path), str(dest))
                logger.info(
                    f"✅ {path.name}: {result['products_added']} produits "
                    f"→ déplacé vers Traitees/"
                )
                _watchdog_status["last_file"]      = path.name
                _watchdog_status["last_status"]    = "ok"
                _watchdog_status["total_processed"] += 1
                _watchdog_status["total_products"]  += result["products_added"]
            else:
                # Déplacer vers /Erreurs
                dest = path.parent / "Erreurs" / path.name
                dest.parent.mkdir(exist_ok=True)
                shutil.move(str(path), str(dest))
                logger.error(f"❌ {path.name}: {result.get('error')} → Erreurs/")
                _watchdog_status["last_file"]   = path.name
                _watchdog_status["last_status"] = "error"

        except Exception as e:
            logger.error(f"Erreur watchdog {path.name}: {e}")
            _watchdog_status["last_status"] = "error"
        finally:
            self._processing.discard(str(path))


# ─── Statut partagé (accessible via API /api/v1/sync/status) ─────────────────
_watchdog_status = {
    "active":          False,
    "folder":          Config.WATCHDOG_FOLDER,
    "last_file":       None,
    "last_status":     None,
    "total_processed": 0,
    "total_products":  0,
}

_observer: Observer | None = None


def start_watchdog(model_id: str, loop: asyncio.AbstractEventLoop) -> None:
    global _observer

    if not Config.WATCHDOG_ENABLED:
        logger.info("Watchdog désactivé (WATCHDOG_ENABLED=false)")
        return

    folder = Path(Config.WATCHDOG_FOLDER)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "Traitees").mkdir(exist_ok=True)
    (folder / "Erreurs").mkdir(exist_ok=True)

    handler   = InvoiceFileHandler(model_id=model_id, loop=loop)
    _observer = Observer()
    _observer.schedule(handler, str(folder), recursive=False)
    _observer.start()

    _watchdog_status["active"] = True
    logger.info(f"👁️  Watchdog actif → {folder.resolve()}")


def stop_watchdog() -> None:
    global _observer
    if _observer:
        _observer.stop()
        _observer.join()
        _observer = None
    _watchdog_status["active"] = False
    logger.info("Watchdog arrêté")


def get_watchdog_status() -> dict:
    return {
        **_watchdog_status,
        "folder_absolute": str(Path(Config.WATCHDOG_FOLDER).resolve()),
        "files_en_attente": len([
            f for f in Path(Config.WATCHDOG_FOLDER).glob("*")
            if f.is_file() and f.suffix.lower() in EXTENSIONS_OK
        ]) if Path(Config.WATCHDOG_FOLDER).exists() else 0,
    }
