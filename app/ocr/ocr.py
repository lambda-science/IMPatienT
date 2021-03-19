import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path


def get_grayscale(image):
    """Convert image to grayscale"""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def thresholding(image):
    """Treshold pixel of greyscaled image"""
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def pdf_to_text(path, lang):
    """Convert PDF path to image to text using Tesseract with langage setting. OEM 1 PSM 1"""
    images = convert_from_path(path)
    text = []
    # Loop on each image (page) of the PDF file
    for image in images:
        open_cv_image = np.array(image)
        # Convert RGB to BGR
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        # Preprocess image
        open_cv_image = thresholding(get_grayscale(open_cv_image))
        # Tesseract OCR
        custom_config = r'-l ' + lang + r' --oem 1 --psm 1 '
        text_page = pytesseract.image_to_string(open_cv_image,
                                                config=custom_config)
        # Save text results
        text.append(text_page)
    return text
