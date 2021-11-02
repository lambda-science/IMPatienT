# MYO-xIA: Web-App to Format and Explore Patient Data

**MYO-xIA is a web application developed to format free text and images from patients’ data to machine-learning ready formats. It also generates several visualization as well as automatic diagnosis to accelerate research on diseases.**  
It features ontology, optical character recognition (OCR), natural language processing (NLP), image annotation using machine learning, interactive plots and explainable AI.

It is currently deployed at: https://myoxia.lbgi.fr/  
This project is free and open-source under the MIT license, feel free to fork and contribute to the development. Several guides are available at the bottom of this page for the production deployment and developer mode.

## Contact:

The main maintainer is:  
**Corentin Meyer** - PhD Student @ CSTB Team - iCube - University Of Strasbourg <corentin.meyer@etu.unsitra.fr>

## Citing MYO-xIA

[placeholder]

## MYO-xIA Abstract

**Background**  
Digitalization of patients’ data using ontologies such as Human Phenotype Ontology (HPO) is essential for clinical research for better diagnosis of diseases. However, ontology development requires a mix of domain expertise and technical knowledge, also multiple domains such as muscle histology do not have a standard ontology. Here we present MYO-xIA a web application developed to easily create a pseudo-ontology called standard vocabulary for domains that are missing one and use this ontology to digitalize free-text medical reports and annotate images. This tool also includes automatic visualization modules that generate graphs and tables on the data as well an automatic diagnosis prediction and assisted vocabulary keyword suggestion.  
**Results**  
As a use case of the platform, we analyzed 89 histology reports of patients with congenital myopathy, and we created a first draft of the muscle histology vocabulary. Automatically generated analysis was used to discover per disease and per gene patient profile and we obtained an accuracy 0.75 for congenital myopathy subtypes classification.  
**Conclusions**  
With MYO-xIA we created versatile applications that can be used to digitalize free-text data and image using controlled vocabulary and requiring no prior technical knowledge. As it is flexible, it can be used in any domains that lacks a well-defined free text formatting procedure.

## Setup guides

### (DOCKER) Developper Mode Setup (to contribute)

[See the wiki page: Developper Mode Setup (DOCKER)](<https://github.com/lambda-science/MYO-xIA-App/wiki/(DOCKER)-Developper-Mode-Setup-(to-contribute)>)

### (DOCKER) Deploy to production & Maintain MYO-xIA

[See the wiki page: Deploy and maintain (DOCKER)](<https://github.com/lambda-science/MYO-xIA-App/wiki/(DOCKER)-Deploy-&-Maintain-MYO-xIA>)

### (LINUX) Deploy to production & Maintain MYO-xIA

[See the wiki page: Deploy and maintain (LINUX)](<https://github.com/lambda-science/MYO-xIA-App/wiki/(LINUX)-Deploy-&-Maintain-MYO-xIA>)

### (LEGACY - Deprecated) Developper Mode Setup (non-docker)

[See the wiki page: Developper Mode Setup (non-docker)](<https://github.com/lambda-science/MYO-xIA-App/wiki/(LEGACY---Deprecated)-Developper-Mode-Setup-(non-docker)>)
