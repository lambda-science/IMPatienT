# IMPatienT 🗂️: an integrated web application to digitize, process and explore multimodal patient data.

**IMPatienT** 🗂️ is a web application developped in the **MYO-xIA project** for patient data digitization and exploration.
It features a standard vocabulary creator, optical character recognition (OCR), natural language processing (NLP), image annotation and segmentation using machine learning, interactive visualizations and automatic diagnosis prediction.

## Demo Usage Instructions

If you are on the demo instance (https://impatient.lbgi.fr), you can login on top right with **login: demo ; password: demo**
The application is preloaded with a database of histology reports and a standard vocabulary for muscle biopsy. Data on this demo instance is reset once every day.
For the PDF automatic analysis, you can find a sample PDF [HERE](https://www.lbgi.fr/~meyer/IMPatienT/sample_demo_report.pdf) working with the preinstalled standard vocabulary. A sample image for image annotation can be found [HERE](https://www.lbgi.fr/~meyer/IMPatienT/sample_image_histo.jpg).
## Partners
IMPatienT is developped and used in collaboration with the [Morphological Unit of the Institute of Myology of Paris](https://www.institut-myologie.org/en/recherche-2/neuromuscular-exploration-and-evaluation-centre/laboratoire-dhistopathologie-dr-norma-b-romero/). A production instance is deployed to help discovering new relevant features for congenital myopathies classification and diagnosis.

## IMPatienT🗂️ Abstract

**Background**
Medical acts such as imaging leads most of the time to the production of several medical text reports to describe relevant findings. Such process induce multimodality in patient data by linking image data to free-text data. Multimodal data have become central to drive research and improve diagnosis of patients. Exploiting patients’ data is challenging as the ecosystem of tools is fragmented depending on the type of data to exploit (image, text, genetic), the task to perform (digitization, processing, exploration) and the domain of interest (clinical phenotype, histology…). There is a strong need for a simple, comprehensive, and flexible platform.
**Results**
In this paper, we present IMPatienT (dIgitize Multimodal PATIENt daTa), a free and open-source web application to digitize, process and explore multimodal patient data. IMPatienT has a modular architecture, composed of four components to: (i) create a standard vocabulary for a domain (ii) digitize and process free-text data by mapping it to a set of standard terms, (iii) annotate images and perform image segmentation and (iv) generate an automatic visualization dashboard to provide insight on the data and perform automatic diagnosis suggestions. Finally, we showcased IMPatienT on a corpus of 40 simulated muscle biopsy reports of congenital myopathy patients.
**Conclusions**
IMPatienT is a platform to digitize, process and explore patient data that can handle image and free-text data. As it relies on user-designed standard vocabulary, it is highly flexible to fit any domain of research and can be used as a patient registry for exploratory data analysis (EDA). A demo instance of the application is available at https://impatient.lbgi.fr.

## MYO-xIA Project

The MYO-xIA project aims to collect data from patients with **congenital myopathies** in order to analyse them using **explainable AI approaches**. In the field of congenital myopathies research, there is an important need for **digitization and standardization of patient data** in order to use modern data analysis methods.
This project has tree mains objectives:

- **Gather and format patient data** to be ready for automatic exploitation (patient histology-report form, image annotation, OCR/NLP)
- Help the **discovery of new phenotype-genotype-histology** association for each congenital myopathy subtype (standard vocabulary creation tool, per gene and per class histology feature statistics)
- Provide tools for **automatic diagnosis** based on patient data (live prediction of congenital myopathy subtype with histology reports, images, genetic data and phenotype)

## Contact:

The main maintainer is:
**Corentin Meyer** - PhD Student @ CSTB Team - iCube - University Of Strasbourg [co.meyer@unistra.fr](mailto:co.meyer@unistra.fr)

## Citing IMPatienT🗂️

[placeholder]
