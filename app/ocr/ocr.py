import pytesseract
import cv2
import numpy as np
import glob
from pdf2image import convert_from_bytes, convert_from_path


def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def pdf_to_text(path, lang):
    #images = convert_from_bytes(bytes_pdf)
    images = convert_from_path(path)
    text = []
    for image in images:
        open_cv_image = np.array(image)
        # Convert RGB to BGR
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        open_cv_image = thresholding(get_grayscale(open_cv_image))
        custom_config = r'-l ' + lang + r' --oem 1 --psm 1 '
        text_page = pytesseract.image_to_string(open_cv_image,
                                                config=custom_config)
        text.append(text_page)
    return text


def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)