# How To Use For Developpement Purpose:

1. Install the Tesseract dependencies for OCR. Ubuntu example using apt:
   `sudo apt install tesseract-ocr tesseract-ocr-fra tesseract-ocr-deu tesseract-ocr-spa tesseract-ocr-eng libgl1 libpq-dev python3-venv python3-dev python3-openslide openslide-tools build-essential poppler-utils`

2. Create Python virtual environment
   `python3 -m venv venv`

3. Activate the environnement
   `source venv/bin/activate`

4. Install the python dependencies
   `pip install -r requirements.txt`

5. Download NLP models:
   `python -m spacy download fr_dep_news_trf`

6. Initialize databse:
   `flask db upgrade`

7. Launch the app
   `flask run`

8. Go to [127.0.0.1:5000/](http://127.0.0.1:5000/) in your web-browser and use the application.

### Optional:

You can register a base user using flask shell:

```bash
flask shell
> user = User(username=demo, email=demo@demo.demo)
> user.set_password("demo")
> db.session.add(user)
> db.session.commit()
```

# Looking to deploy and maintain MYO-xIA ? [See the wiki page: Deploy and maintain](https://github.com/lambda-science/MYO-xIA-App/wiki/MYO-xIA-Deployment,-update-and-maintainability.)
