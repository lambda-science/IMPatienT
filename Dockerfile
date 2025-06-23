FROM python:3.12-slim-bullseye
COPY --from=ghcr.io/astral-sh/uv:0.5.30 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_CACHE=1

RUN useradd impatient
WORKDIR /home/impatient

RUN apt update && apt install -y gcc git tesseract-ocr tesseract-ocr-osd tesseract-ocr-fra poppler-utils cmake build-essential git-lfs
RUN git lfs install
ARG GIT_LFS_SKIP_SMUDGE=0
RUN git clone https://huggingface.co/spaces/corentinm7/IMPatienT --depth 1 /home/impatient # To Get Git LFS files
RUN git lfs pull

COPY --chown=impatient:impatient pyproject.toml pyproject.toml
COPY --chown=impatient:impatient src /home/impatient/src

RUN uv sync --no-install-project --no-sources --no-dev

COPY --chown=impatient:impatient docker/boot.sh ./
RUN chown -R impatient:impatient /home/impatient
RUN chmod a+x boot.sh

ENV FLASK_APP=src/impatient/impatient_app.py

RUN usermod -u 1000 impatient
RUN usermod -G staff impatient
USER impatient

EXPOSE 7860
ENTRYPOINT ["./boot.sh"]
