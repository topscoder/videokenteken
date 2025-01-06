# ocr/ocr_utils.py

import pytesseract
import cv2
import numpy as np
import re

def extract_text_from_image(image):
    """
    Run OCR on the given image (assumes it's already cropped to a license plate).
    :param image: np.ndarray (BGR or grayscale)
    :return: cleaned text from the plate
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Optional: apply threshold
    # _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
    # For simplicity, let's just feed gray
    plate_text = pytesseract.image_to_string(gray, config="--psm 7")

    # Clean up result: remove non-alphanumeric characters and extra spaces
    plate_text = re.sub(r"[^a-zA-Z0-9]", "", plate_text)
    return plate_text.strip()
