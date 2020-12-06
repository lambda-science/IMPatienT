import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'tif', 'tiff', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
            feature_list = create_feature_list("config_ontology")
            return render_template('annot.html', filename=filename, thumbnail=filename+"_thumbnail.jpg", feature_list=feature_list)
    return render_template('index.html')

#@app.route('/results/', methods=['GET', 'POST'])
#def write_report():
#    print("=======", request.form['prenom_patient'])
#    return render_template('results.html')

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5010)