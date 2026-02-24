"""
Watchdog service to monitor a local folder and process new invoices automatically.
"""
import os
import time
import shutil
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from backend.core.orchestrator import ExtractionOrchestrator

logger = logging.getLogger(__name__)

class InvoiceHandler(FileSystemEventHandler):
    def __init__(self, orchestrator: ExtractionOrchestrator, watch_path: str, watcher):
        self.orchestrator = orchestrator
        self.watch_path = Path(watch_path)
        self.watcher = watcher
        self.processed_path = self.watch_path / "Traitees"
        self.error_path = self.watch_path / "Erreurs"

        # Ensure subfolders exist
        self.processed_path.mkdir(exist_ok=True)
        self.error_path.mkdir(exist_ok=True)

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix.lower() not in ['.pdf', '.jpg', '.jpeg', '.png', '.webp']:
            return

        # Record entry
        size = f"{round(os.path.getsize(file_path) / 1024, 1)} KB"
        self.watcher.add_activity(file_path.name, "🔄 En cours", size=size)

        # Small delay to ensure file is fully written
        time.sleep(1)
        self.process_file(file_path)

    def scan_existing(self):
        """Processes files already present in the folder (and subfolders) at startup."""
        # Use rglob to find all files in subfolders
        for item in self.watch_path.rglob("*"):
            if item.is_file() and item.suffix.lower() in ['.pdf', '.jpg', '.jpeg', '.png', '.webp']:
                # Skip files already in Traitees or Erreurs
                if "Traitees" in item.parts or "Erreurs" in item.parts:
                    continue

                logger.info(f"🚚 Deep Scan : Traitement de {item.name} ({item.relative_to(self.watch_path)})")
                size = f"{round(os.path.getsize(item) / 1024, 1)} KB"
                self.watcher.add_activity(item.name, "🔄 En cours (Scan Deep)", size=size)
                self.process_file(item)

    def process_file(self, file_path: Path):
        logger.info(f"🔍 Chien de garde : Traitement détecté pour {file_path.name}")
        try:
            with open(file_path, "rb") as f:
                content = f.read()

            # Process via orchestrator
            self.orchestrator.process_file(content, file_path.name)

            # Move to processed
            dest = self.processed_path / file_path.name
            shutil.move(str(file_path), str(dest))
            logger.info(f"✅ {file_path.name} traité et déplacé vers 'Traitees'")
            self.watcher.add_activity(file_path.name, "✅ Terminé")

        except Exception as e:
            logger.error(f"❌ Erreur lors du traitement auto de {file_path.name}: {e}")
            self.watcher.add_activity(file_path.name, f"❌ Erreur: {str(e)}")
            # Move to error
            dest = self.error_path / file_path.name
            shutil.move(str(file_path), str(dest))

class DoclingWatcher:
    def __init__(self, orchestrator: ExtractionOrchestrator, watch_path: str = "Docling_Factures"):
        self.orchestrator = orchestrator
        self.watch_path = watch_path
        self.observer = Observer()
        self.activity_log = [] # List of {filename, status, timestamp}

    def add_activity(self, filename: str, status: str, size: str = None):
        self.activity_log.append({
            "filename": filename,
            "status": status,
            "size": size,
            "ext": filename.split('.')[-1].upper() if '.' in filename else "FILE",
            "time": time.strftime("%H:%M:%S")
        })
        # Keep only last 10
        if len(self.activity_log) > 10:
            self.activity_log.pop(0)

    def get_activity(self):
        return self.activity_log[::-1] # Newest first

    def start(self):
        # Create watch directory if it doesn't exist
        os.makedirs(self.watch_path, exist_ok=True)

        handler = InvoiceHandler(self.orchestrator, self.watch_path, self)
        # Enable recursive monitoring
        self.observer.schedule(handler, self.watch_path, recursive=True)
        self.observer.start()
        logger.info(f"🛡️ Chien de garde activé sur le dossier : {os.path.abspath(self.watch_path)}")

        # Initial scan
        handler.scan_existing()

    def stop(self):
        self.observer.stop()
        self.observer.join()
        logger.info("🛡️ Chien de garde arrêté")
