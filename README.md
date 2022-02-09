![Twitter Follow](https://img.shields.io/twitter/follow/corentinm_py?style=social) ![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/lambda-science/ehroes) ![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/lambda-science/EHRoes) [![Build](https://github.com/lambda-science/EHRoes/actions/workflows/docker-build-push.yml/badge.svg)](https://github.com/lambda-science/EHRoes/actions/workflows/docker-build-push.yml) ![GitHub last commit](https://img.shields.io/github/last-commit/lambda-science/ehroes) ![GitHub](https://img.shields.io/github/license/lambda-science/ehroes)

# EHRoes 🦸: an all-in-one web application for patients’ data digitization and exploration

<p align="center">
  <img src="https://i.imgur.com/exuYlt4.png" alt="EHRoes Banner" style="border-radius: 25px;" />
</p>

**EHRoes 🦸 is a web application developped in the MYO-xIA project for patient data digitization and exploration.**
It features a standard vocabulary creator, optical character recognition (OCR), natural language processing (NLP), image annotation and segmentation using machine learning, interactive visualizations and automatic diagnosis prediction.

A demo version is currently deployed at: https://ehroes.lbgi.fr/
This project is free and open-source under the MIT license, feel free to fork and contribute to the development. Several guides are available at the bottom of this page for the production deployment and developer mode.

## Contact:

The main maintainer is:
**Corentin Meyer** - PhD Student @ CSTB Team - iCube - University Of Strasbourg <co.meyer@unistra.fr>

## Citing EHRoes

[placeholder]

## EHRoes Abstract

**Background**
With a growing amount of patient data such as sequencing, imaging, and medical records, electronic health records (EHR) are now central to drive research and improve diagnosis of patients by using multimodal data. Exploiting patient data is a challenge as patient data exploitation tools ecosystem is often fragmented into tools to digitize and format the data and those interpreting the data (exploration, diagnosis). Furthermore, as most of the tools are specialized in one type of data, a multitude of software is needed for multimodal approaches. There is a strong need for a simple, all-rounder and flexible platform.
**Results**
In this paper we present EHRoes, an all-in-one web application to digitize and explore patient data. EHRoes has a module-based architecture, composed of four modules to: (i) create a standard vocabulary for a domain (ii) automatically digitize free-text data to a set of standard terms (iii) annotate images with standard vocabulary using automatic segmentation and (iv) generate an automatic visualization dashboard to provide insight on the data and perform automatic diagnosis suggestions. We demonstrated the utility of EHRoes by digitizing 40 artificial muscle histology reports of patients with congenital myopathies.
**Conclusions**
With EHRoes we created a platform for both digitization and exploration of patient data that can handle image data and free-text data. As it uses user-designed standard vocabulary, it is highly flexible to fit any domain of research. It can be used both as a patient registry with automatic diagnosis or as a research tool to explore a cohort of patients.
A demo instance of the application is available at https://ehroes.lbgi.fr.

## Setup guides

### (DOCKER) Developper Mode Setup (to contribute)

[See the wiki page: Developper Mode Setup (DOCKER)](<https://github.com/lambda-science/EHRoes/wiki/(DOCKER)-Developper-Mode-Setup-(to-contribute)>)

### (DOCKER) Deploy to production & Maintain EHRoes

[See the wiki page: Deploy and maintain (DOCKER)](<https://github.com/lambda-science/EHRoes/wiki/(DOCKER)-Deploy-&-Maintain-EHRoes>)

### (LINUX) Deploy to production & Maintain EHRoes

[See the wiki page: Deploy and maintain (LINUX)](<https://github.com/lambda-science/EHRoes/wiki/(LINUX)-Deploy-&-Maintain-EHRoes>)

### (LEGACY - Deprecated) Developper Mode Setup (non-docker)

[See the wiki page: Developper Mode Setup (non-docker)](<https://github.com/lambda-science/EHRoes/wiki/(LEGACY---Deprecated)-Developper-Mode-Setup-(non-docker)>)
