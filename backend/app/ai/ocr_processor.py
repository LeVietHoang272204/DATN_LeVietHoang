"""OCR processor with fallback strategy.

Improvement: EasyOCR primary → Tesseract fallback if available.
Also includes image preprocessing for better Vietnamese OCR accuracy.
"""

import io
import logging
from typing import Optional
from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)

_easyocr_reader = None


def _get_easyocr_reader():
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr
        _easyocr_reader = easyocr.Reader(["vi", "en"], gpu=False)
    return _easyocr_reader


def preprocess_image(image: Image.Image) -> Image.Image:
    """Improve image quality before OCR."""
    # Convert to grayscale
    img = image.convert("L")
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)
    # Binarize (threshold)
    img = img.point(lambda x: 0 if x < 140 else 255, "1")
    return img.convert("RGB")


def ocr_image(image: Image.Image, preprocess: bool = True) -> str:
    """Run OCR on a single image. Returns extracted text."""
    if preprocess:
        image = preprocess_image(image)

    # Primary: EasyOCR
    try:
        reader = _get_easyocr_reader()
        # Convert PIL to bytes
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)
        results = reader.readtext(buf.getvalue(), detail=0, paragraph=True)
        text = "\n".join(results)
        if text.strip():
            return text.strip()
    except Exception as e:
        logger.warning(f"EasyOCR failed: {e}")

    # Fallback: Tesseract (if installed)
    try:
        import pytesseract
        text = pytesseract.image_to_string(image, lang="vie")
        if text.strip():
            logger.info("Used Tesseract fallback for OCR")
            return text.strip()
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"Tesseract fallback also failed: {e}")

    return ""


def ocr_pdf_page(page_image: Image.Image) -> str:
    """OCR a single PDF page image."""
    return ocr_image(page_image, preprocess=True)
