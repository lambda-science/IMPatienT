# Developper Mode Setup (Conda+Poetry):
1. Install Tesseract package:    
   `sudo apt install tesseract-ocr tesseract-ocr-osd tesseract-ocr-fra`  

2. Install Python if needed.
   ```bash
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   chmod +x Miniconda3-latest-Linux-x86_64.sh
   ./Miniconda3-latest-Linux-x86_64.sh
   conda activate base
   ```
   Install Poetry env manager (with dvc)  
   ```bash
   conda install mamba
   mamba install -c conda-forge poetry dvc-ssh
   ```
4. Clone the repository and create the environnement:  
   `git clone https://github.com/lambda-science/MYO-xIA-App.git myoxia`    
   `cd myoxia`  
   `poetry install`
   
4. Activate the environnement  & install NLP model  
   `poetry shell`  
   Aditionally install Spacy NLP Model using:  
   `python -m spacy download fr_core_news_lg`  

5. Run the app with the boot developper script
   `chmod +X dev_boot.sh`  
   `./dev_boot.sh`

6. Go to [127.0.0.1:5000/](http://127.0.0.1:5000/) in your web-browser and use the application.

### Optional:

You can pull our dev-data using dvc (in conda base env):
`dvc pull`

# (DOCKER) Deploy & Maintain MYO-xIA  
[See the wiki page: Deploy and maintain (DOCKER)](https://github.com/lambda-science/MYO-xIA-App/wiki/(DOCKER)-Deploy-&-Maintain-MYO-xIA)

# (LINUX) Deploy & Maintain MYO-xIA  
[See the wiki page: Deploy and maintain (LINUX)](https://github.com/lambda-science/MYO-xIA-App/wiki/(LINUX)-Deploy-&-Maintain-MYO-xIA)
