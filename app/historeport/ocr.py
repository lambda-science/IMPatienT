import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_bytes
import spacy
from fuzzywuzzy import fuzz
import collections


class Rapport:
    """PDF File class used to detect text and analyse it"""

    def __init__(self, file_obj):
        self.file_obj = file_obj
        self.lang = "fra"
        self.image_stack = []
        self.raw_text = ""
        self.text_as_list = []
        self.header_text = []
        self.nlp = spacy.load("fr_core_news_lg")
        self.section = collections.OrderedDict()
        self.section_text = collections.OrderedDict()
        self.section_names = [
            "Hématéine-éosine et trichrome de Gomori",
            "Activité myosine ATPasique",
            "Différenciation des fibres :",
            "Répartition numérique des fibres :",
            "Répartition topographique des différents types de fibres",
            "Activité myosine ATPasique",
            "Activités oxydatives (SDH, NADH-TR",
            "Cox :",
            "PAS :",
            "Phosphorylases :",
            "Soudans :",
            "Soudan :",
            "Lipides :",
            "Lipides soudan:",
            "Technique de Koëlle",
            "CONCLUSIONS :",
        ]

    def get_grayscale(self, image):
        """Convert image to grayscale"""
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def thresholding(self, image):
        """Treshold pixel of greyscaled image"""
        return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    def pdf_to_text(self):
        """Convert PDF file object to image to text using Tesseract with langage setting. OEM 1 PSM 1"""
        self.image_stack = convert_from_bytes(self.file_obj.read())
        page_list = []
        # Loop on each image (page) of the PDF file
        for image in self.image_stack:
            open_cv_image = np.array(image)
            # Convert RGB to BGR
            open_cv_image = open_cv_image[:, :, ::-1].copy()
            # Preprocess image
            open_cv_image = self.thresholding(self.get_grayscale(open_cv_image))
            # Tesseract OCR
            custom_config = r"-l " + self.lang + r" --oem 1 --psm 1 "
            text_page = pytesseract.image_to_string(open_cv_image, config=custom_config)
            # Save text results
            page_list.append(text_page)
        self.raw_text = "\n".join(page_list)
        self.text_as_list = self.raw_text.split("\n")
        return self.raw_text

    def detect_sections(self):
        index = 0
        non_sorted_dict = {}
        for i in self.text_as_list:
            for j in self.section_names:
                if fuzz.partial_ratio(j, i) > 90:
                    non_sorted_dict[j] = index
            index += 1
        sorted_tuple = sorted(
            non_sorted_dict.items(), key=lambda x: x[1], reverse=False
        )
        for i in sorted_tuple:
            self.section[i[0]] = i[1]

    def extract_section_text(self):
        self.header_text = self.text_as_list[: list(self.section.items())[0][1]]

        for i in range(len(self.section) - 1):
            self.section_text[list(self.section.items())[i][0]] = " ".join(
                self.text_as_list[
                    list(self.section.items())[i][1] : list(self.section.items())[
                        i + 1
                    ][1]
                ]
            )
        self.section_text[list(self.section.items())[-1][0]] = " ".join(
            self.text_as_list[list(self.section.items())[-1][1] :]
        )
