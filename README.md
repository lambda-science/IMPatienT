# EHRoes 🦸: an all-in-one web application for patients’ data digitalization and exploration

**EHRoes is a web application developped in the MYO-xIA project for patient data digitalization and exploration.**  
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
With a growing amount of patient data such as sequencing, imaging, and medical records, electronic health records (EHR) became central to drive research and improve diagnosis of patients by using multimodal data. But EHR usage is challenging as they require tools to format, digitalize and interpret data. Today’s EHR exploitation tools ecosystem is heavily fragmented among tools to create EHR (format and digitalize) and tools to interpret the data (exploration and diagnosis). Also most of the tools are specialized for one specific type of data, multiplying the number of different software needed for multimodal approaches. There is a strong need for a simple, all-rounder and flexible platform.  
**Results**  
In this paper we present EHRoes, an all-in-one web application for patients’ data digitalization and exploration. With its module-based architecture, we developed four modules to: (i) create a set of standard vocabulary for a domain, (ii) automatically digitalize free-text data to a set of standard terms, (iii) annotate images with standard vocabulary using automatic segmentation and (iv) generate an automatic visualization dashboard to provide insight on the data and perform automatic diagnosis suggestions. Using this platform, we successfully digitalized 89 muscle histology reports from patients with congenital myopathies and we obtained an accuracy 0.75 for congenital myopathy subtypes classification.  
**Conclusions**  
With EHRoes we created a platform for both patients data digitalization and exploration that can handle image data and free-text data. As it uses user designed standard vocabulary, it is highly flexible to fit any domain of research. It can be used both as a patient registry with automatic diagnosis or as a research tool to explore a cohort of patients.  
A demo instance of the application is available at https://ehroes.lbgi.fr.

## Setup guides

### (DOCKER) Developper Mode Setup (to contribute)

[See the wiki page: Developper Mode Setup (DOCKER)](<https://github.com/lambda-science/EHRoes-App/wiki/(DOCKER)-Developper-Mode-Setup-(to-contribute)>)

### (DOCKER) Deploy to production & Maintain EHRoes

[See the wiki page: Deploy and maintain (DOCKER)](<https://github.com/lambda-science/EHRoes-App/wiki/(DOCKER)-Deploy-&-Maintain-EHRoes>)

### (LINUX) Deploy to production & Maintain EHRoes

[See the wiki page: Deploy and maintain (LINUX)](<https://github.com/lambda-science/EHRoes-App/wiki/(LINUX)-Deploy-&-Maintain-EHRoes>)

### (LEGACY - Deprecated) Developper Mode Setup (non-docker)

[See the wiki page: Developper Mode Setup (non-docker)](<https://github.com/lambda-science/EHRoes-App/wiki/(LEGACY---Deprecated)-Developper-Mode-Setup-(non-docker)>)
