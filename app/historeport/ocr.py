import collections
import json
import os
from shlex import join

import cv2
import numpy as np
import pytesseract
import spacy
from flask import current_app
from pdf2image import convert_from_bytes
from thefuzz import fuzz
from textacy.extract.basics import ngrams


class TextReport:
    """Class for textual reports handling"""

    def __init__(self, file_obj, lang):
        """Init Method for the class

        Args:
            file_obj (file object): File object of the PDF
            lang (str): Language of the PDF (fra for french, eng for english)
        """
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
            self.nlp = spacy.load("fr_core_news_sm")
            self.negexlist = current_app.config["NEGEX_LIST_FR"]
            self.negex_sent = current_app.config["NEGEX_SENT_FR"]
        if self.lang == "eng":
            self.nlp = spacy.load("en_core_web_sm")
            self.negexlist = current_app.config["NEGEX_LIST_EN"]
            self.negex_sent = current_app.config["NEGEX_SENT_EN"]
        self.all_stopwords = self.nlp.Defaults.stop_words
        self.results_match_dict = {}

    def get_grayscale(self, image):
        """Convert an image as numpy array to grayscale

        Args:
            image (numpy array): Image as numpy array

        Returns:
            image: image object
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def thresholding(self, image):
        """Treshold pixel of greyscale image

        Args:
            image (numpy array): Image as numpy array

        Returns:
            image: image object
        """
        return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    def pdf_to_text(self):
        """Convert PDF file object from image to text using Tesseract with langage settings.
        OEM 1 PSM 1

        Returns:
            str: raw text as a string
        """
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
            # print(pytesseract.image_to_data(open_cv_image, config=custom_config))
            # hocr_results = pytesseract.image_to_pdf_or_hocr(
            #     open_cv_image, config=custom_config, extension="hocr"
            # )
            # with open("hocr.html", "wb") as f:
            #     f.write(hocr_results)
            # Save text results
            page_list.append(text_page)
        self.raw_text = "\n".join(page_list)
        self.text_as_list = self.raw_text.split("\n")
        return self.raw_text

    def _detect_negation(self, sentence: str) -> list:
        """Detection negation in a sentence using negex terms

        Args:
            sentence (str): string of the sentence

        Returns:
            two value: sentence as string and a boolean value for negation:
                        true if negation is detected, false otherwise.
        """
        """Detect negation in a sentence"""
        sent = self.nlp(sentence)
        for negex_term in self.negexlist:
            if len(negex_term.split(" ")) == 1:
                token_list = [word.text.lower() for word in sent if word.is_alpha]
                for i in token_list:
                    if i == negex_term:
                        return sent, True
            else:
                if negex_term in sent.text.lower():
                    return sent, True
        return sent, False

    def _split_sentence(self, sent_original: object) -> list:
        """Split sntence into sub-sentences based on list of break terms (from negex).

        Args:
            sent_original (object): Spacy Sentence object

        Returns:
            list: list of sub-sentences from the original sentence
        """
        for sent_sep in self.negex_sent:
            if sent_sep.lower() in sent_original.text.lower():
                sent_list = sent_original.text.lower().split(sent_sep)
                break
            else:
                sent_list = [sent_original.text]
        return sent_list

    def _spacy_ngrams(self, text_section: str) -> dict:
        """Extract ngrams (1,2,3) from a block of text using spacy

        Args:
            text_section (str): block of text to analyse

        Returns:
            dict: all n-grams detected with negation boolean
        """
        doc = self.nlp(text_section)
        full_ngrams = []
        for sent_original in doc.sents:
            sent_list = self._split_sentence(sent_original)
            # Detect negation in sentence part and extract n-grams up to 6 words
            for sent_str in sent_list:
                n_gram_size = []
                sent, flag_neg = self._detect_negation(sent_str)
                ngrams_generator = ngrams(sent, (1, 2, 3, 4, 5, 6), filter_punct=True)
                for i in ngrams_generator:
                    full_ngrams.append((i.text.lower(), 0 if flag_neg else 1))

        return full_ngrams

    def _match_ngram_ontology(self, full_ngrams) -> list:
        """Match the dictionary of ngrams with the standard vocabulary

        Args:
            full_ngrams (dict): all n-grams detected with negation boolean

        Returns:
            list: list of list of match between ngrams and standard vocabulary
            First value is the neg flag, second value is the ngram, third value
            is the matching terms, last value is the node ID.
        """
        ontology_terms = []
        match_list = []
        json_onto = json.load(open(self.ontology_path, "rb"))
        for i in json_onto:
            ontology_terms.append([i["id"], i["text"]])
            for synonym in i["data"]["synonymes"].split(","):
                ontology_terms.append([i["id"], synonym])

        n_grams_words = [i[0] for i in full_ngrams]
        onto_words = [i[1] for i in ontology_terms]
        full_ngrams_processed = self._lemmatize_list(n_grams_words)
        full_onto_processed = self._lemmatize_list(onto_words)
        for n_gram_index, i in enumerate(full_ngrams_processed):
            for onto_index, j in enumerate(full_onto_processed):
                score = fuzz.ratio(i.lower(), j.lower())
                if score >= 85:
                    # [neg_flag, ngram, match_term, node_id, score]
                    match_list.append(
                        [
                            full_ngrams[n_gram_index][1],
                            i,
                            j,
                            ontology_terms[onto_index][0],
                            score,
                        ]
                    )
        return match_list

    def _lemmatize_list(self, list_ngrams: list) -> list:
        result_list = []
        for elm in list_ngrams:
            result = self.nlp(elm, disable=["tok2vec", "parser", "ner"])
            sent_no_stop = " ".join(
                [word.lemma_ for word in result if not word.is_stop]
            )
            result_list.append(sent_no_stop)
        return result_list

    def analyze_text(self) -> list:
        """Analyse the whole text of the PDF and match it to the standard vocabulary

        Returns:
            list: list of list of match between ngrams and standard vocabulary
            First value is the neg flag, second value is the ngram, third value
            is the matching terms, last value is the node ID.
        """
        full_ngrams = self._spacy_ngrams(self.raw_text)
        match_list = self._match_ngram_ontology(full_ngrams)
        return match_list


if __name__ == "__main__":
    import sys

    pdf_path = sys.argv[1]
    pdf_lang = sys.argv[2]
    pdf_object = TextReport(file_obj=open(pdf_path, "rb"), lang=pdf_lang)
    pdf_object.pdf_to_text()
    # print(pdf_object.raw_text)
