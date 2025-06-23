---
title: IMPatienT
emoji: 🗂️
colorFrom: yellow
colorTo: red
sdk: docker
pinned: true
license: agpl-3.0
header: mini
short_description: Annotate multimodal patient data web-app
tags:
   - ontology
   - myology
   - biology
   - histology
   - muscle
   - annotation
   - myopathy
---

![Twitter Follow](https://img.shields.io/twitter/follow/corentinm_py?style=social) ![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/lambda-science/impatient) ![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/lambda-science/IMPatienT) [![Build](https://github.com/lambda-science/IMPatienT/actions/workflows/docker-build-push.yml/badge.svg)](https://github.com/lambda-science/IMPatienT/actions/workflows/docker-build-push.yml) ![GitHub last commit](https://img.shields.io/github/last-commit/lambda-science/impatient) ![GitHub](https://img.shields.io/github/license/lambda-science/IMPatienT)

# IMPatienT 🗂️: an integrated web application to digitize, process and explore multimodal patient data.

<p align="center">
  <img src="https://i.imgur.com/iH7UeUs.png" alt="IMPatienT Banner" style="border-radius: 25px;" />
</p>

**IMPatienT 🗂️** (**I**ntegrated digital **M**ultimodal **PATIEN**t da**T**a) **is a web application developped in the MYO-xIA project for patient data digitization and exploration.**
It features a standard vocabulary creator, optical character recognition (OCR), natural language processing (NLP), image annotation and segmentation using machine learning, interactive visualizations and automatic diagnosis suggestion.

A demo version is currently deployed at: https://huggingface.co/spaces/corentinm7/IMPatienT
This project is free and open-source under the AGPL license, feel free to fork and contribute to the development. Several guides are available at the bottom of this page for the production deployment and developer mode.

## Contact:

The main maintainer is:
[**Corentin Meyer** - PhD in Biomedical AI](https://cmeyer.fr) <contact@cmeyer.fr>

## Citing IMPatienT🗂️

[placeholder]

## Partners

<p align="center">
  <img src="https://i.imgur.com/csEXDnW.png" alt="Partner Banner" style="border-radius: 25px;" />
</p>

IMPatienT is developped and used in collaboration with the [Morphological Unit of the Institute of Myology of Paris](https://www.institut-myologie.org/en/recherche-2/neuromuscular-investigation-center/morphological-unit/). A production instance is deployed to help discovering new relevant features for congenital myopathies classification and diagnosis.

## IMPatienT🗂️ Abstract

**Background**  
Medical acts, such as imaging, generally lead to the production of several medical text reports that describe the relevant findings. Such processes induce multimodality in patient data by linking image data to free-text data and consequently, multimodal data have become central to drive research and improve diagnosis of patients. However, the exploitation of patient data is challenging as the ecosystem of available analysis tools is fragmented depending on the type of data (images, text, genetic sequences), the task to be performed (digitization, processing, exploration) and the domain of interest (clinical phenotype, histology…). To address the challenges, the analysis tools need to be integrated in a simple, comprehensive, and flexible platform.  
**Results**  
Here, we present IMPatienT (**I**ntegrated digital **M**ultimodal **PATIEN**t da**T**a), a free and open-source web application to digitize, process and explore multimodal patient data. IMPatienT has a modular architecture, including four components to: (i) create a standard vocabulary for a domain, (ii) digitize and process free-text data by mapping it to a set of standard terms, (iii) annotate images and perform image segmentation, and (iv) generate an automatic visualization dashboard to provide insight on the data and perform automatic diagnosis suggestions. Finally, we demonstrate the usefulness of IMPatienT on a corpus of 40 simulated muscle biopsy reports of congenital myopathy patients.  
**Conclusions**  
IMPatienT is a platform to digitize, process and explore patient data that can handle image and free-text data. As it
relies on a user-designed vocabulary, it can be adapted to fit any domain of research and can be used as a patient
registry for exploratory data analysis (EDA). A demo instance of the application is available
at https://huggingface.co/spaces/corentinm7/IMPatienT.

## Setup guides

### Local Developer mode using Docker (to contribute)

1. Clone the repository `git clone git@github.com:lambda-science/IMPatienT.git`
2. Build the docker image and run it using by running: `chmod +x docker/dev_build_run.sh` and
   `./docker/dev_build_run.sh`
   Congrats, the app is now running on `http://localhost:7860`!
   Any modification you do to the code will be saved and applied directly to the app.

### Deploy to Production using Docker

1. Clone the repository `git clone git@github.com:lambda-science/IMPatienT.git`
2. Build the docker image: `chmod +x docker/build.sh`
3. Edit the configuration sample with your secrets:

```bash
cp docker/run_sample.sh docker/run.sh
nano docker/run.sh
```

4. Run the docker image: `./docker/run.sh`
   Congrats, the app is now running on `http://localhost:7860` with demo database and ontology ! Use any reverse-proxy (
   like Nginx) to expose it to the internet. If you want to customize, see the note below about persistent data.

**Note about persistent data:**

Currently, all your data are ephemeral inside the docker container and will be lost when you stop the container. By
default it runs a demo database and ontology is no data are provided. To solve this you can create a persistent volume
to store your actual data.

⚠️ 🚨 **This is only needed for fresh/clean/new installations. This WILL delete all your previous IMPatienT database and
ontology as this creates a new volume and overwrite its content with the content of the current directory `data/`.**  ⚠️
🚨

1. Before running the container, create the volume by running: `./docker/create_volume.sh`
2. Run the docker image: `./docker/run.sh`

* **NB1:** If you have issues with permissions on data folder inside the docker. You might have to `chown -R 1000 data/`
  before `./docker/create_volume.sh`
* **NB2:** This can also be used to deploy/inject/restore backup data to the container: as this script copy current
  `data/` folder content to the volume. Simply add your `app.db` backup in `data/database/` and `ontology.json` backup
  in `data/ontology` and your patient folders with images in `data/images/` before running the script.  
