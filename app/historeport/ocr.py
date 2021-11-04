from shlex import join
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_bytes
import spacy
from thefuzz import fuzz
import collections
import json
from flask import current_app
import os


class Rapport:
    """PDF File class used to detect text and analyse it"""

    def __init__(self, file_obj, lang):
        self.file_obj = file_obj
        self.lang = lang
        self.ontology_path = os.path.join(
            current_app.config["ONTOLOGY_FOLDER"], "ontology.json"
        )
        self.image_stack = []
        self.raw_text = ""
        self.text_as_list = []
        self.header_text = []
        if self.lang == "fra":
            self.nlp = spacy.load("fr_core_news_lg")
            self.negexlist = current_app.config["NEGEX_LIST_FR"]
        if self.lang == "eng":
            self.nlp = spacy.load("en_core_web_lg")
            self.negexlist = current_app.config["NEGEX_LIST_EN"]
        # self.section = collections.OrderedDict()
        # self.section_text = collections.OrderedDict()
        # self.section_names = [
        #     "Hématéine-éosine et trichrome de Gomori",
        #     "Activité myosine ATPasique",
        #     "Différenciation des fibres :",
        #     "Répartition numérique des fibres :",
        #     "Répartition topographique des différents types de fibres",
        #     "Activité myosine ATPasique",
        #     "Activités oxydatives (SDH, NADH-TR",
        #     "Cox :",
        #     "PAS :",
        #     "Phosphorylases :",
        #     "Soudans :",
        #     "Soudan :",
        #     "Lipides :",
        #     "Lipides soudan:",
        #     "Technique de Koëlle",
        #     "CONCLUSIONS :",
        # ]
        self.results_match_dict = {}

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

    # def detect_sections(self):
    #     """ "Detect the line number where each section starts"""
    #     index = 0
    #     non_sorted_dict = {}
    #     for i in self.text_as_list:
    #         for j in self.section_names:
    #             if fuzz.partial_ratio(j, i) > 90:
    #                 non_sorted_dict[j] = index
    #         index += 1
    #     sorted_tuple = sorted(
    #         non_sorted_dict.items(), key=lambda x: x[1], reverse=False
    #     )
    #     for i in sorted_tuple:
    #         self.section[i[0]] = i[1]

    # def extract_section_text(self):
    #     """ "Use the list of line number section start to separate text between hearder, section and conclusion"""
    #     self.header_text = self.text_as_list[: list(self.section.items())[0][1]]

    #     for i in range(len(self.section) - 1):
    #         self.section_text[list(self.section.items())[i][0]] = " ".join(
    #             self.text_as_list[
    #                 list(self.section.items())[i][1] : list(self.section.items())[
    #                     i + 1
    #                 ][1]
    #             ]
    #         )
    #     self.section_text[list(self.section.items())[-1][0]] = " ".join(
    #         self.text_as_list[list(self.section.items())[-1][1] :]
    #     )

    def _spacy_ngrams(self, text_section: str) -> dict:
        """ "Extract 1,2,3 ngrams for a block of text using spacy."""
        doc = self.nlp(text_section)
        final_one_ngrams = []
        final_two_ngrams = []
        final_three_ngrams = []
        for sent in doc.sents:
            flag_neg = False
            for negex_term in self.negexlist:
                if negex_term in sent.text.lower():
                    flag_neg = True
            temp_token_list = []
            for token in sent:
                # if not token.is_stop and not token.is_punct and token.is_alpha:
                if not token.is_punct and token.is_alpha:
                    final_one_ngrams.append([token.text.lower(), 0 if flag_neg else 1])
                    temp_token_list.append(token.text.lower())
            if len(temp_token_list) > 1:
                for i in range(len(temp_token_list) - 1):
                    final_two_ngrams.append(
                        [" ".join([temp_token_list[i], temp_token_list[i + 1]]), 0 if flag_neg else 1]
                    )
            if len(temp_token_list) > 2:
                for i in range(len(temp_token_list) - 2):
                    final_three_ngrams.append([
                        " ".join(
                            [
                                temp_token_list[i],
                                temp_token_list[i + 1],
                                temp_token_list[i + 2],
                            ]
                        ), 0 if flag_neg else 1]
                    )
        full_ngrams = final_one_ngrams + final_two_ngrams + final_three_ngrams
        return full_ngrams

    def _match_ngram_ontology(self, full_ngrams) -> list:
        ontology_terms = []
        match_list = []
        json_onto = json.load(open(self.ontology_path, "rb"))
        for i in json_onto:
            ontology_terms.append(i["text"])
        for i in full_ngrams:
            for j in ontology_terms:
                score = fuzz.ratio(i[0].lower(), j.lower())
                if score >= 80:
                    match_list.append([i[1], i[0], j])
        return match_list

    # def analyze_all_sections(self) -> dict:
    #     for section in self.section_text.keys():
    #         text_block = self.section_text[section]
    #         full_ngrams = self._spacy_ngrams(text_block)
    #         match_list = self._match_ngram_ontology(full_ngrams)
    #         self.results_match_dict[section] = match_list

    def analyze_text(self) -> json:
        full_ngrams = self._spacy_ngrams(self.raw_text)
        match_list = self._match_ngram_ontology(full_ngrams)
        return match_list
