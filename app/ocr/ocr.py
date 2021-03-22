import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path


class Rapport:
    """PDF File class used to detect text and analyse it"""
    def __init__(self, path, lang):
        self.path = path
        self.lang = lang
        self.image_stack = []
        self.raw_text = ""
        self.text_as_list = []

    def get_grayscale(self, image):
        """Convert image to grayscale"""
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def thresholding(self, image):
        """Treshold pixel of greyscaled image"""
        return cv2.threshold(image, 0, 255,
                             cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    def pdf_to_text(self):
        """Convert PDF path to image to text using Tesseract with langage setting. OEM 1 PSM 1"""
        self.image_stack = convert_from_path(self.path)
        page_list = []
        # Loop on each image (page) of the PDF file
        for image in self.image_stack:
            open_cv_image = np.array(image)
            # Convert RGB to BGR
            open_cv_image = open_cv_image[:, :, ::-1].copy()
            # Preprocess image
            open_cv_image = self.thresholding(
                self.get_grayscale(open_cv_image))
            # Tesseract OCR
            custom_config = r'-l ' + self.lang + r' --oem 1 --psm 1 '
            text_page = pytesseract.image_to_string(open_cv_image,
                                                    config=custom_config)
            # Save text results
            page_list.append(text_page)
        self.raw_text = '\n'.join(page_list)
        self.text_as_list = self.raw_text.split("\n")
        return self.raw_text
