# How To Use For Developpement Purpose (using PipEnv):
1. Install Tesseract package:    
   `sudo apt install tesseract-ocr tesseract-ocr-fra`  

2. Clone the repository and create the environnement:  
   `git clone https://github.com/lambda-science/MYO-xIA-App.git`  
   `python -m pip install pip --upgrade --user`  
   `python -m pip install pipenv --user`  
   `pipenv install`
   
3. Activate the environnement  & install NLP model
   `pipenv shell`  
   Aditionally install Spacy NLP Model using: `python -m spacy download fr_core_news_lg`

4. Initialize empty database:  
   `flask db upgrade`

5. Set Flask in development mode and launch the app  
   `export FLASK_ENV=development`  
   `flask run`

6. Go to [127.0.0.1:5000/](http://127.0.0.1:5000/) in your web-browser and use the application.

### Optional:

You can register a base user using flask shell:

```bash
flask shell
> user = User(username="demo", email="demo@demo.demo")
> user.set_password("demo")
> db.session.add(user)
> db.session.commit()
```

# Looking to deploy and maintain MYO-xIA ? [See the wiki page: Deploy and maintain](https://github.com/lambda-science/MYO-xIA-App/wiki/MYO-xIA-Deployment,-update-and-maintainability.)
