import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, session
from werkzeug.utils import secure_filename
from PIL import Image
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'tif', 'tiff', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
    feature_list = [line.strip() for line in feature.readlines()]
    return feature_list

class ReportForm(FlaskForm):
    feature_list = create_feature_list("config_ontology")
    prenom_patient = TextAreaField('prenom_patient', validators=[DataRequired()])
    nom_patient = TextAreaField('nom_patient', validators=[DataRequired()])
    nom_clinicien = TextAreaField('nom_clinicien', validators=[DataRequired()])

@app.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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
    filename = request.args.get("filename")
    form = ReportForm()
    if form.is_submitted():
        session['prenom_patient'] = form.prenom_patient.data
        session['nom'] = form.nom_patient.data
        session['feature'] = form.feature_list
        submit = SubmitField('rapport')
        print(form.data)
        return redirect(url_for('write_report'))
    return render_template('annot.html', filename=filename, thumbnail=filename+"_thumbnail.jpg", feature_list=ReportForm.feature_list, form=form)

@app.route('/results', methods=['GET', 'POST'])
def write_report():
    print('session', session['prenom_patient'])
    #print("=======", request.form['prenom_patient'])
    return render_template('results.html', session=session)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5010)