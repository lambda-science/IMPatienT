# How To Use For Developpement Purpose:
1. Install the python environnement
`pip install -r requirements.txt`  

2. Install the Tesseract dependencies for OCR. Ubuntu example using apt:
`sudo apt install tesseract-ocr tesseract-ocr-fra tesseract-ocr-deu tesseract-ocr-spa tesseract-ocr-eng`

3. Activate the environnement
`source venv/bin/activate`

4. Initialize databse:
```flask db upgrade```

5. Launch the app
`flask run`

6. Go to [127.0.0.1:5000/](http://127.0.0.1:5000/) in your web-browser and register your first user and upload images.