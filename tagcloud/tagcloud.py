import xml.etree.ElementTree as ET
import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from werkzeug.utils import secure_filename
from processing import pre_processing
from flaskext.mysql import MySQL
from datetime import datetime

ALLOWED_EXTENSIONS = set(['xml'])
UPLOAD_FOLDER = 'tagcloud/static/uploads'

mysql = MySQL()

app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'tcc'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods = ['GET'])
def render():
    return render_template("index.html")


@app.route('/upload', methods = ['POST'])
def upload_file():

    conn = mysql.connect()
    cursor = conn.cursor()

    print request.method
    if request.method == 'POST':

        file = request.files['file']

        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)

            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            file.save(path)

            pn = pre_processing(path)
            name = pn.getName()

            dateTime = datetime.now() #data atual

            insertNomeArquivo = ("INSERT INTO tagcloud (nome_profissional, data_criado, nome_arquivo) values ('%s', '%s', '%s')" %(name, dateTime.strftime('%Y/%m/%d %H:%M:%S'), str(filename)))
           
            cursor.execute(insertNomeArquivo)

            conn.commit()

            id_tag = cursor.lastrowid #pega id da ultima insercao

            print id_tag

        response = pn.readXML()

        for obj in response: #para cada objeto no json

            selectPalavras = ("SELECT id_palavra FROM palavras WHERE palavras.text='%s'" % (obj['text']))
            cursor.execute(selectPalavras)
            data = cursor.fetchall()

            print obj['text']

            print data

            if(len(data) > 0):

                id_palavra_exist = data[0][0]
            
                if(id_palavra_exist):

                    insertIntermediarioExists = ("INSERT INTO tagcloud_has_palavras (tagcloud_idtagcloud, palavras_id_palavra, size) values (%d, %d, %d)" % (id_tag, id_palavra_exist, obj['size']))

                    cursor.execute(insertIntermediarioExists)

                    conn.commit()

            else:

                insertPalavra = ("INSERT INTO palavras (text) VALUES ('%s')" % (obj['text'])) 

                cursor.execute(insertPalavra)

                conn.commit()

                id_palavra = cursor.lastrowid #pega id da ultima insercao

                insertIntermediario = ("INSERT INTO tagcloud_has_palavras (tagcloud_idtagcloud, palavras_id_palavra, size) values (%d, %d, %d)" % (id_tag, id_palavra, obj['size']))

                cursor.execute(insertIntermediario)

                conn.commit()

    return jsonify(response)  









