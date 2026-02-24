import cv2
import numpy as np

def preprocess_invoice_image(image_bytes: bytes) -> bytes:
    """
    Améliore la qualité d'une photo de facture mobile avant envoi à Gemini.
    - Correction contraste
    - Débruitage
    - Conversion WebP optimisé
    """
    # Lecture des bytes vers une matrice numpy via cv2
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        # En cas d'échec de lecture, on retourne l'image d'origine pour que Gemini essaie quand même
        return image_bytes

    # Débruitage pour supprimer les grains de la photo mobile (particulièrement en basse lumière)
    img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

    # Amélioration dynamique du contraste (CLAHE - Contrast Limited Adaptive Histogram Equalization)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    img = cv2.merge((l, a, b))
    img = cv2.cvtColor(img, cv2.COLOR_LAB2BGR)

    # Encode de l'image nettoyée en format WebP avec une qualité de 85%
    success, buffer = cv2.imencode('.webp', img, [cv2.IMWRITE_WEBP_QUALITY, 85])

    if not success:
        return image_bytes

    return buffer.tobytes()
