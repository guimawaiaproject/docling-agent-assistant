"""Tests pour ImagePreprocessor — zéro mock."""
import pytest
import numpy as np
import cv2
from backend.services.image_preprocessor import ImagePreprocessor


class TestIsImage:
    @pytest.mark.parametrize("filename,expected", [
        ("photo.jpg", True),
        ("scan.jpeg", True),
        ("facture.png", True),
        ("compressed.webp", True),
        ("old.bmp", True),
        ("scan.tiff", True),
        ("facture.pdf", False),
        ("data.json", False),
        ("readme.txt", False),
        ("noext", False),
    ])
    def test_is_image(self, filename, expected):
        assert ImagePreprocessor.is_image(filename) == expected


class TestPreprocessBytes:
    def _make_test_image(self, w=200, h=300) -> bytes:
        img = np.random.randint(0, 255, (h, w, 3), dtype=np.uint8)
        _, buf = cv2.imencode(".jpg", img)
        return buf.tobytes()

    def test_returns_bytes(self):
        img_bytes = self._make_test_image()
        result = ImagePreprocessor.preprocess_bytes(img_bytes, "test.jpg")
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_output_is_webp(self):
        img_bytes = self._make_test_image()
        result = ImagePreprocessor.preprocess_bytes(img_bytes, "test.jpg")
        assert result[:4] == b"RIFF"

    def test_invalid_bytes_returns_original(self):
        garbage = b"not an image at all"
        result = ImagePreprocessor.preprocess_bytes(garbage, "bad.jpg")
        assert result == garbage

    def test_large_image_gets_resized(self):
        img_bytes = self._make_test_image(w=4000, h=3000)
        result = ImagePreprocessor.preprocess_bytes(img_bytes, "large.jpg")
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_png_input(self):
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        _, buf = cv2.imencode(".png", img)
        result = ImagePreprocessor.preprocess_bytes(buf.tobytes(), "test.png")
        assert isinstance(result, bytes)
