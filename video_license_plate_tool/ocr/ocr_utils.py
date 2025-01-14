import cv2
import numpy as np
import re
from paddleocr import PaddleOCR

# Initialize PaddleOCR with English language
ocr = PaddleOCR(use_angle_cls=True, use_gpu=True, lang='en')

def extract_text_from_image(frame):
    """
    Run OCR on the given image (assumes it's already cropped to a license plate).
    :param image: np.ndarray (BGR or grayscale)
    :return: cleaned text from the plate
    """
    # Convert to grayscale if needed
    # if len(image.shape) == 3:
    #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # else:
    #     gray = image

    # Use PaddleOCR
    results = ocr.ocr(frame, det=False, rec=True, cls=False)

    plate_text = ""
    for r in results:
        scores = r[0][1]
        if np.isnan(scores):
            scores = 0
        else:
            scores = int(scores * 100)

        if scores > 60:
            plate_text = r[0][0]

    pattern = re.compile('[\W_]')  
    plate_text = pattern.sub('', plate_text)
    plate_text = plate_text.replace("???", "")
    plate_text = plate_text.replace("O", "0")

    return str(plate_text)
