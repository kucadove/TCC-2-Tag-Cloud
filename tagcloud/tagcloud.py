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

    # print request.method
    if request.method == 'POST':

        file = request.files['file']

        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)

            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            file.save(path)

            pn = pre_processing(path)
            name = pn.getName()

            dateTime = datetime.now() #data atual

            selectIdExistente = ("SELECT idtagcloud FROM tagcloud WHERE nome_profissional = '%s'" % (name))
            #pega ids da tabela tagcloud cujo profissional ja exista no banco
            cursor.execute(selectIdExistente)
            IdExistente = cursor.fetchall()

            if(len(IdExistente) > 0):

                IdExistTag = IdExistente[0][0]

            selectTagCloud = ("SELECT nome_profissional FROM tagcloud WHERE nome_profissional = '%s'" % (name))
            #pega o nome do profissionnal que ja existe na tabela tagcloud
            cursor.execute(selectTagCloud)
            nomeExist = cursor.fetchall()

            if(len(nomeExist) > 0):

                nomeExistTag = nomeExist[0][0]
                # print nomeExistTag

                if(nomeExistTag):

                    dropIds = ("DELETE FROM tagcloud_has_palavras WHERE tagcloud_idtagcloud = %d" % (IdExistTag))
                    dropAutores = ("DELETE FROM autores WHERE tagcloud_idtagcloud = %d" % (IdExistTag))
                    dropTitulos = ("DELETE FROM titulos WHERE tagcloud_idtagcloud = %d" % (IdExistTag))
                    #caso ja exista profissional com o mesmo nome deleta todas as palavras associadas a sua tag cloud

                    cursor.execute(dropIds)
                    cursor.execute(dropAutores)
                    cursor.execute(dropTitulos)

                    dropArquivo = ("DELETE FROM tagcloud WHERE nome_profissional = '%s'" % (nomeExistTag))
                    #deleta do banco a tagcloud cujo nome do profissional ja exista

                    cursor.execute(dropArquivo)

                    insertNomeArquivo = ("INSERT INTO tagcloud (nome_profissional, data_criado, nome_arquivo) values ('%s', '%s', '%s')" %(name, dateTime.strftime('%Y/%m/%d %H:%M:%S'), str(filename)))
                    #depois faz a insercaoo normal

                    cursor.execute(insertNomeArquivo)

                    conn.commit()

                    id_tag = cursor.lastrowid

            else:

                insertNomeArquivo = ("INSERT INTO tagcloud (nome_profissional, data_criado, nome_arquivo) values ('%s', '%s', '%s')" %(name, dateTime.strftime('%Y/%m/%d %H:%M:%S'), str(filename)))
               
                cursor.execute(insertNomeArquivo)

                conn.commit()

                id_tag = cursor.lastrowid #pega id da ultima insercao

                # print id_tag

        response = pn.readXML()

        

        for obj in response: #para cada objeto no json

            selectPalavras = ("SELECT id_palavra FROM palavras WHERE palavras.text='%s'" % (obj['text']))
            cursor.execute(selectPalavras)
            data = cursor.fetchall()

            # print obj['text']

            # print data

            if(len(data) > 0):

                id_palavra_exist = data[0][0]
            
                if(id_palavra_exist):

                    insertIntermediarioExists = ("INSERT INTO tagcloud_has_palavras (tagcloud_idtagcloud, palavras_id_palavra, size) values (%d, %d, %d)" % (id_tag, id_palavra_exist, obj['size']))

                    cursor.execute(insertIntermediarioExists)

                    conn.commit()

            else:

                insertPalavra = ("INSERT INTO palavras (text, categoria) VALUES ('%s', 'geral')" % (obj['text'])) 

                cursor.execute(insertPalavra)

                conn.commit()

                id_palavra = cursor.lastrowid #pega id da ultima insercao

                insertIntermediario = ("INSERT INTO tagcloud_has_palavras (tagcloud_idtagcloud, palavras_id_palavra, size) values (%d, %d, %d)" % (id_tag, id_palavra, obj['size']))

                cursor.execute(insertIntermediario)

                conn.commit() 

        autores = pn.getAutores()
        for autor in autores:

            insertAutores = ("INSERT INTO autores (autor, tagcloud_idtagcloud) values ('%s', %d)" %(autor, id_tag)) 

            cursor.execute(insertAutores)

            conn.commit()

            id_autor = cursor.lastrowid

            data = cursor.fetchall()

        titulos = pn.getTitulos()
        for titulo in titulos:

            insertTitulos = ("INSERT INTO titulos (titulo, tagcloud_idtagcloud) values ('%s', %d)" %(titulo, id_tag)) 

            cursor.execute(insertTitulos)

            conn.commit()

            id_titulo = cursor.lastrowid

            data = cursor.fetchall()


    return jsonify(response) 



@app.route('/wordsdb', methods = ['POST'])
def word_db():

    conn = mysql.connect()
    cursor = conn.cursor()

    getPalavras = ("SELECT * FROM palavras")
    cursor.execute(getPalavras)
    palavras = cursor.fetchall()

    words = []

    for x in palavras:
        words.append({'text': x[1], 'id': x[0]})
        
    return jsonify(words)


@app.route('/options', methods = ['POST'])
def options():

    conn = mysql.connect()
    cursor = conn.cursor()

    if request.method == 'POST':

        hello = request.form.getlist('valor[]')

    palavrasID = []

    for x in hello:
        palavrasID.append(x)

    in_clause = ",".join(palavrasID)

    tagsContem = ("SELECT t.idtagcloud, t.nome_profissional, p.text FROM tagcloud AS t \
                    INNER JOIN tagcloud_has_palavras AS tp ON (tp.tagcloud_idtagcloud = t.idtagcloud) \
                    INNER JOIN palavras AS p ON (p.id_palavra = tp.palavras_id_palavra) \
                    WHERE tp.palavras_id_palavra IN (%s)" % in_clause)
    cursor.execute(tagsContem)
    tagclouds = cursor.fetchall()

    ids = { l[0] : [l[0]] for l in tagclouds }  # create a dictionary mapped to each "name" in the CSV
    names = { l[0] : l[1] for l in tagclouds }  # create a dictionary mapped to each "name" in the CSV
    for l in tagclouds:
        if len(ids[l[0]]) > 1:
            ids[l[0]][1] = ids[l[0]][1]+','+l[2]
        else:
            ids[l[0]].append('')
            ids[l[0]][1] = l[2]

    for key, value in names.iteritems():
        ids[key].append(value)

    list2 = ids.values()

    return jsonify(list2)

@app.route('/render', methods = ['POST'])
def renderTag():

    conn = mysql.connect()
    cursor = conn.cursor()

    if request.method == 'POST':

        idtagcloud = request.form['valor']

        tagcloud = ("SELECT p.text, tp.size FROM palavras AS p \
                    INNER JOIN tagcloud_has_palavras AS tp ON (tp.palavras_id_palavra = p.id_palavra) \
                    WHERE  tp.tagcloud_idtagcloud = %d ORDER BY tp.size DESC" % int(idtagcloud))

        cursor.execute(tagcloud)
        cloud = cursor.fetchall()

        # print cloud
        response = []
        

        for item in cloud:
            response.append({'text': item[0], 'size': item[1]})

        # print response
        return jsonify(response)

@app.route('/listagem', methods = ['POST'])
def listar():

    conn = mysql.connect()
    cursor = conn.cursor()

    getTags = ("SELECT * FROM tagcloud")
    cursor.execute(getTags)
    clouds = cursor.fetchall()

    words = []

    for x in clouds:
        words.append(x)

    # print words

    return jsonify(words)


@app.route('/autores', methods = ['POST'])
def autores():

    conn = mysql.connect()
    cursor = conn.cursor()

    if request.method == 'POST':

        idtagcloud = request.form['valor']
        print idtagcloud

    getAutores = ("SELECT *  FROM autores AS a INNER JOIN tagcloud AS t ON (t.idtagcloud = a.tagcloud_idtagcloud) WHERE t.idtagcloud = %d" %int(idtagcloud)) 
    
    print getAutores

    cursor.execute(getAutores)
    conn.commit()
    autores = cursor.fetchall()

    autor = []

    for x in autores:
        autor.append(x)

    print autor

    return jsonify(autor)

@app.route('/titulos', methods = ['POST'])
def titulos():

    conn = mysql.connect()
    cursor = conn.cursor()

    if request.method == 'POST':

        idtagcloud = request.form['valor']
        print idtagcloud

    getTitulos = ("SELECT *  FROM titulos AS a INNER JOIN tagcloud AS t ON (t.idtagcloud = a.tagcloud_idtagcloud) WHERE t.idtagcloud = %d" %int(idtagcloud)) 
    
    print getTitulos

    cursor.execute(getTitulos)
    conn.commit()
    titulos = cursor.fetchall()

    titulo = []

    for x in titulos:
        titulo.append(x)

    print titulo

    return jsonify(titulo)
















