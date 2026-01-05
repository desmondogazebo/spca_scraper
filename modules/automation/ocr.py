import pytesseract
from PIL import ImageGrab, ImageOps

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# ----------------------------
# Low-level helpers
# ----------------------------

def grab_region(x1, y1, x2, y2):
    """
    Screen capture only.
    Separated so watcher can reuse without re-OCR.
    """ 
    return ImageGrab.grab(bbox=(x1, y1, x2, y2))


def calculate_confidence(data):
    valid = [int(c) for c in data["conf"] if c != "-1"]
    return sum(valid) / len(valid) if valid else 0


# ----------------------------
# Core OCR
# ----------------------------

def perform_ocr(image):
    data_original = pytesseract.image_to_data(
        image,
        output_type=pytesseract.Output.DICT,
    )
    text_original = " ".join(data_original["text"]).strip()
    conf_original = calculate_confidence(data_original)

    inverted = ImageOps.invert(image.convert("RGB"))
    data_inverted = pytesseract.image_to_data(
        inverted,
        output_type=pytesseract.Output.DICT,
    )
    text_inverted = " ".join(data_inverted["text"]).strip()
    conf_inverted = calculate_confidence(data_inverted)

    if conf_inverted > conf_original:
        return text_inverted, conf_inverted

    return text_original, conf_original


# ----------------------------
# Public APIs
# ----------------------------

def run_ocr_with_fallback(image):
    """
    Used by OCRWatcher.
    Returns (text, confidence)
    """
    return perform_ocr(image)


def run_ocr_with_coords(x1, y1, x2, y2):
    """
    Backward-compatible API.
    Also returns (text, confidence).
    """
    image = grab_region(x1, y1, x2, y2)
    return perform_ocr(image)
