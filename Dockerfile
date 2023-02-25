FROM python:3.9-slim

RUN useradd impatient
WORKDIR /home/impatient

RUN apt update && apt install -y gcc git tesseract-ocr tesseract-ocr-osd tesseract-ocr-fra poppler-utils
COPY --chown=impatient:impatient pyproject.toml pyproject.toml
COPY --chown=impatient:impatient poetry.lock poetry.lock

RUN python -m pip install poetry
RUN python -m poetry config virtualenvs.create false
RUN python -m poetry install --no-root --no-interaction && rm -rf ~/.cache/pypoetry/{cache,artifacts}

COPY --chown=impatient:impatient impatient.py config.py docker/boot.sh ./
COPY --chown=impatient:impatient app app
COPY --chown=impatient:impatient config config

RUN chown impatient:impatient /home/impatient
RUN chmod a+x boot.sh

ENV FLASK_APP impatient.py

RUN usermod -u 1000 impatient
RUN usermod -G staff impatient
USER impatient

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
