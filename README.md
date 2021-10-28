# How To Use For Developpement Purpose (Conda+Poetry):
1. Install Tesseract package:    
   `sudo apt install tesseract-ocr tesseract-ocr-osd tesseract-ocr-fra`  

2. Install Python with Conda
   ```bash
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   chmod +x Miniconda3-latest-Linux-x86_64.sh
   ./Miniconda3-latest-Linux-x86_64.sh
   conda activate base
   conda install -c conda-forge poetry dvc-ssh
   ```
4. Clone the repository and create the environnement:  
   `git clone https://github.com/lambda-science/MYO-xIA-App.git`  
   `conda install -c conda-forge poetry dvc-ssh`  
   `poetry config virtualenvs.in-project true`  
   `poetry install`
   
4. Activate the environnement  & install NLP model  
   `poetry shell`  
   Aditionally install Spacy NLP Model using: `python -m spacy download fr_core_news_lg`

5. Initialize empty database:  
   `flask db upgrade`

6. Set Flask in development mode and launch the app  
   `export FLASK_ENV=development`  
   `flask run`

7. Go to [127.0.0.1:5000/](http://127.0.0.1:5000/) in your web-browser and use the application.

### Optional:

You can register a base user using flask shell:
```bash
flask shell
> user = User(username="demo", email="demo@demo.demo")
> user.set_password("demo")
> db.session.add(user)
> db.session.commit()
```

You can pull our dev-data using dvc:
`dvc pull`

# Looking to deploy and maintain MYO-xIA ? [See the wiki page: Deploy and maintain](https://github.com/lambda-science/MYO-xIA-App/wiki/MYO-xIA-Deployment,-update-and-maintainability.)
