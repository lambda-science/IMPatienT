![Twitter Follow](https://img.shields.io/twitter/follow/corentinm_py?style=social) ![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/lambda-science/impatient) ![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/lambda-science/IMPatienT) [![Build](https://github.com/lambda-science/IMPatienT/actions/workflows/docker-build-push.yml/badge.svg)](https://github.com/lambda-science/IMPatienT/actions/workflows/docker-build-push.yml) ![GitHub last commit](https://img.shields.io/github/last-commit/lambda-science/impatient) ![GitHub](https://img.shields.io/github/license/lambda-science/IMPatienT)

# IMPatienT 🗂️: an integrated web application to digitize, process and explore multimodal patient data.

<p align="center">
  <img src="https://i.imgur.com/iH7UeUs.png" alt="IMPatienT Banner" style="border-radius: 25px;" />
</p>

**IMPatienT 🗂️** (**I**ntegrated digital **M**ultimodal **PATIEN**t da**T**a) **is a web application developped in the MYO-xIA project for patient data digitization and exploration.**
It features a standard vocabulary creator, optical character recognition (OCR), natural language processing (NLP), image annotation and segmentation using machine learning, interactive visualizations and automatic diagnosis suggestion.

A demo version is currently deployed at: https://impatient.lbgi.fr/
This project is free and open-source under the AGPL license, feel free to fork and contribute to the development. Several guides are available at the bottom of this page for the production deployment and developer mode.

## Contact:

The main maintainer is:
[**Corentin Meyer** - PhD Student @ CSTB Team - iCube - University Of Strasbourg](https://cmeyer.fr) <co.meyer@unistra.fr>

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
IMPatienT is a platform to digitize, process and explore patient data that can handle image and free-text data. As it relies on a user-designed vocabulary, it can be adapted to fit any domain of research and can be used as a patient registry for exploratory data analysis (EDA). A demo instance of the application is available at https://impatient.lbgi.fr.

## Setup guides

### (DOCKER) Developper Mode Setup (to contribute)

[See the wiki page: Developper Mode Setup (DOCKER)](<https://github.com/lambda-science/IMPatienT/wiki/(DOCKER)-Developper-Mode-Setup-(to-contribute)>)

### (DOCKER) Deploy to production & Maintain IMPatienT

[See the wiki page: Deploy and maintain (DOCKER)](<https://github.com/lambda-science/IMPatienT/wiki/(DOCKER)-Deploy-&-Maintain-IMPatienT>)

### (LINUX) Deploy to production & Maintain IMPatienT

[See the wiki page: Deploy and maintain (LINUX)](<https://github.com/lambda-science/IMPatienT/wiki/(LINUX)-Deploy-&-Maintain-IMPatienT>)

### (LINUX) Developper Mode Setup

[See the wiki page: Developper Mode Setup (LINUX)](<https://github.com/lambda-science/IMPatienT/wiki/(LINUX)-Developper-Mode-Setup>)
