# all the imports
import xml.etree.ElementTree as ET
import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from werkzeug.utils import secure_filename
from processing import pre_processing

ALLOWED_EXTENSIONS = set(['xml'])
UPLOAD_FOLDER = 'tagcloud/static/uploads'

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods = ['GET'])
def render():
    return render_template("index.html")


@app.route('/upload', methods = ['POST'])
def upload_file():
    print request.method
    if request.method == 'POST':

        file = request.files['file']

        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)

            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            file.save(path)
        
        pr = pre_processing(path)

        response = pr.readXML()
        print response
        return jsonify(response)  


@app.route('/teste', methods = ['GET'])
def teste():
    return render_template("teste.html")






