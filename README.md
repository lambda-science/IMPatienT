# How To Use For Developpement Purpose:

1. Install the Tesseract dependencies for OCR. Ubuntu example using apt:
`sudo apt install tesseract-ocr tesseract-ocr-fra tesseract-ocr-deu tesseract-ocr-spa tesseract-ocr-eng libgl1 libpq-dev python3-venv python3-dev python3-openslide openslide-tools`

2. Create Python virtual environment 
`python3 -m venv venv`  

3. Activate the environnement
`source venv/bin/activate`

4. Install the python dependencies
`pip install -r requirements.txt`  

5. Initialize databse:
```flask db upgrade```

6. Launch the app
`flask run`

7. Go to [127.0.0.1:5000/](http://127.0.0.1:5000/) in your web-browser and register your first user and upload images.
