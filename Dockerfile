FROM python:3.9-slim

RUN useradd myoxia

WORKDIR /home/myoxia

RUN apt update && apt install -y gcc tesseract-ocr tesseract-ocr-osd tesseract-ocr-fra
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
RUN python -m pip install poetry
RUN python -m poetry config virtualenvs.in-project true
RUN python -m poetry install
RUN .venv/bin/python -m spacy download fr_core_news_lg

COPY app app
COPY migrations migrations
COPY config config
COPY myoxia.py config.py boot.sh ./

RUN chmod a+x boot.sh

ENV FLASK_APP myoxia.py

RUN chown -R myoxia:myoxia ./

USER myoxia

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
