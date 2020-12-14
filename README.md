# How To Use:
1. Install the python environnement
`conda env create -f environment.yml`

2. Activate the environnement
`conda activate histo`

3. Install additionnal non-conda and non-pip package in the conda environnement (Deepzoom.py)
```
cd ..
git clone https://github.com/openzoom/deepzoom.py.git
cd deepzoom.py
python setup.py install
```

4. Launch the app
`python main.py`

5. Go to [127.0.0.1:5011/](http://127.0.0.1:5010/) in your web-browser and upload your first histology image.