FROM python:3.9-slim

RUN useradd ehroes
WORKDIR /home/ehroes

RUN apt update && apt install -y gcc git tesseract-ocr tesseract-ocr-osd tesseract-ocr-fra poppler-utils
COPY --chown=ehroes:ehroes pyproject.toml pyproject.toml
COPY --chown=ehroes:ehroes poetry.lock poetry.lock

RUN python -m pip install poetry
RUN python -m poetry config virtualenvs.create false
RUN python -m poetry install --no-root --no-interaction && rm -rf ~/.cache/pypoetry/{cache,artifacts}

COPY --chown=ehroes:ehroes ehroes.py config.py docker/boot.sh ./
COPY --chown=ehroes:ehroes app app
COPY --chown=ehroes:ehroes migrations migrations
COPY --chown=ehroes:ehroes config config

RUN chown ehroes:ehroes /home/ehroes
RUN chmod a+x boot.sh

ENV FLASK_APP ehroes.py

RUN usermod -u 1000 ehroes
RUN usermod -G staff ehroes
USER ehroes

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
