FROM python:3.9-slim as env

SHELL ["/bin/bash", "-c"]
RUN useradd myoxia
WORKDIR /home/myoxia

RUN apt update && apt install -y gcc git
COPY --chown=myoxia:myoxia pyproject.toml pyproject.toml
COPY --chown=myoxia:myoxia poetry.lock poetry.lock

RUN python -m pip install poetry
RUN python -m poetry config virtualenvs.in-project true
RUN python -m poetry install
RUN .venv/bin/python -m spacy download fr_core_news_lg

FROM python:3.9-slim as release

SHELL ["/bin/bash", "-c"]
RUN useradd myoxia
WORKDIR /home/myoxia

RUN apt update && apt install -y gcc tesseract-ocr tesseract-ocr-osd tesseract-ocr-fra

COPY --chown=myoxia:myoxia --from=env /home/myoxia/.venv .venv
COPY --chown=myoxia:myoxia myoxia.py config.py docker/boot.sh ./
COPY --chown=myoxia:myoxia app app
COPY --chown=myoxia:myoxia migrations migrations
COPY --chown=myoxia:myoxia config config

RUN chown myoxia:myoxia /home/myoxia
RUN chmod a+x boot.sh

ENV FLASK_APP myoxia.py
USER myoxia

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
