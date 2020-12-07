import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, session
from werkzeug.utils import secure_filename
from PIL import Image
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap
import pandas as pd
UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "results"
ALLOWED_EXTENSIONS = {'tif', 'tiff', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORT_FOLDER'] = REPORT_FOLDER
app.config['SECRET_KEY'] = 'myverylongsecretkey'
Bootstrap(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_thumbnail(image_path):
    image = Image.open(image_path)
    image.thumbnail((600, 600))
    image.save(image_path+'_thumbnail.jpg')

def create_feature_list(config_file):
    feature = open(config_file, "r")
    feature_list = [line.strip().replace(" ", "_") for line in feature.readlines()]
    return feature_list

@app.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/results/<filename>')
def get_report(filename):
    return send_from_directory(app.config['REPORT_FOLDER'], filename)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            create_thumbnail(UPLOAD_FOLDER+"/"+filename)
            return redirect(url_for('annot_page', filename=filename))
    return render_template('index.html')

@app.route('/annot', methods=['GET', 'POST'])
def annot_page():
    session.clear()
    filename = request.args.get("filename")
    feature_list = create_feature_list("config_ontology")
    if request.method=='POST':
        if 'submit_button' in request.form:
            data = request.form.to_dict()
            session["info_annot"] = data
            session["filename"] = filename
            return redirect(url_for('write_report'))
    return render_template('annot.html', filename=filename, thumbnail=filename+"_thumbnail.jpg", feature_list=feature_list)

@app.route('/results', methods=['GET', 'POST'])
def write_report():
    prenom_patient = session["info_annot"].pop("prenom_patient")
    nom_patient = session["info_annot"].pop("nom_patient")
    id_patient = session["info_annot"].pop("id_patient")
    redacteur_rapport = session["info_annot"].pop("redacteur_rapport")
    diag = session["info_annot"].pop("diag")
    del session["info_annot"]["submit_button"]
    filename = session["filename"]+"_"+prenom_patient+"_"+nom_patient+".txt"
    f = open("results/"+filename, "w")
    f.write("Prenom_Patient\t"+prenom_patient+"\n")
    f.write("Nom_Patient\t"+nom_patient+"\n")
    f.write("ID_Patient\t"+id_patient+"\n")
    f.write("Redacteur_histo\t"+redacteur_rapport+"\n")
    f.write("Diagnostic\t"+diag+"\n")
    for i in session["info_annot"]:
        f.write(i+"\t"+session["info_annot"][i]+"\n")
    return render_template('results.html', data=session["info_annot"], prenom_patient=prenom_patient, nom_patient=nom_patient, id_patient=id_patient, redacteur_rapport=redacteur_rapport, filename=filename)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5010)