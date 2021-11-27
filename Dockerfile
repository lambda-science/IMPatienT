FROM python:3.9-slim as env

SHELL ["/bin/bash", "-c"]
RUN useradd ehroes
WORKDIR /home/ehroes

RUN apt update && apt install -y gcc git
COPY --chown=ehroes:ehroes pyproject.toml pyproject.toml
COPY --chown=ehroes:ehroes poetry.lock poetry.lock

RUN python -m pip install poetry
RUN python -m poetry config virtualenvs.in-project true
RUN python -m poetry install
RUN .venv/bin/python -m spacy download fr_core_news_lg
RUN .venv/bin/python -m spacy download en_core_web_lg

FROM python:3.9-slim as release

SHELL ["/bin/bash", "-c"]
RUN useradd ehroes
WORKDIR /home/ehroes

RUN apt update && apt install -y gcc tesseract-ocr tesseract-ocr-osd tesseract-ocr-fra poppler-utils

COPY --chown=ehroes:ehroes --from=env /home/ehroes/.venv .venv
COPY --chown=ehroes:ehroes ehroes.py config.py docker/boot.sh ./
COPY --chown=ehroes:ehroes app app
COPY --chown=ehroes:ehroes migrations migrations
COPY --chown=ehroes:ehroes config config

RUN chown ehroes:ehroes /home/ehroes
RUN chmod a+x boot.sh

ENV FLASK_APP ehroes.py
USER ehroes

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
