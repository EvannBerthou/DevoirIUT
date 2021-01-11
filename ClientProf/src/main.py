import requests, json, os, re, io
from typing import *
from flask import Flask, request, render_template, redirect, send_file, make_response, abort
from werkzeug.wrappers import Response
from admin import admin
from utils import *

app = Flask(__name__, template_folder='templates')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(utils)
app.secret_key = 'secret key'

@app.route('/')
def home() -> Response:
    if is_logged_in():
        return redirect('/devoirs')
    return redirect('/login')

@app.route('/nouveau', methods=['GET'])
def get_nouveau() -> Str_response:
    result_classes = liste_classes_prof()
    result_mat = liste_matieres_prof()
    if result_classes and result_mat:
        return render_template('nouveau.html', user = 'c', classes=result_classes, matieres=result_mat)

    # Forme un message d'erreur
    s = '<h1>'
    if not result_classes:
        s += "Aucune classe trouvée"
        s += '<br>'
    if not result_mat:
        s += "Aucune matière trouvée"
    s += '</h1>'
    return s

@app.route('/nouveau', methods=['POST'])
def post_nouveau() -> Response:
    classes = ''.join([key+',' for key, val in request.form.items() if val == 'on'])
    enonce = request.form['enonce']
    matiere = request.form['matiere']
    date = request.form['date']

    files = {file.filename: file.stream.read() for file in request.files.getlist('file') if file.filename != ''}

    backend_request(requests.post, 'http://localhost:5000/api/devoirs',
        params={'enonce': enonce,'matiere': matiere, 'classe': classes, 'date': date},
        files=files,
        cookies = request.cookies
    )
    return redirect('/devoirs')

@app.route('/devoirs',methods=['GET'])
def affichage_devoirs() -> Str_response:
    response = backend_request(requests.get, 'http://localhost:5000/api/devoirs', cookies=request.cookies)
    resp = json.loads(response.content)
    classes = liste_classes()
    return render_template('devoirs.html', devoirs=resp['devoirs'], user = resp['user'], classes=classes)

@app.route('/devoirs',methods=['POST'])
def post_devoirs() -> Response:
    if 'delete_button' in request.form:
        backend_request(requests.post, 'http://localhost:5000/api/sup', params={'devoir_id':request.form['delete_button']})
    else:
        backend_request(requests.put, 'http://localhost:5000/api/modif',
            params = {
                'devoir_id': request.form['devoir_id'],
                'enonce': request.form['enonce'],
                'date': request.form['date']
            }
        )
    return redirect('/devoirs')

@app.route('/login',methods=['GET'])
def get_login() -> Str_response:
    return render_template('login.html')

@app.route('/login',methods=['POST'])
def post_login() -> Str_or_Response:
    email, pwd = request.form['username'], request.form['pwd']
    # Fais une requete au back end afin de vérifier la connexion
    connect_data = backend_request(requests.post, 'http://localhost:5000/api/token/auth', json={'username': email, 'password': pwd})
    # Applique le jeton dans les cookies pour garder l'auth
    response = make_response(redirect('/devoirs'))
    response.set_cookie('access_token_cookie', connect_data.cookies.get('access_token_cookie'))
    return response

@app.route('/logout')
def logout() -> Response:
    requests.post('http://localhost:5000/api/token/remove')
    resp = make_response(redirect('/'))
    resp.delete_cookie('access_token_cookie')
    return resp

@app.route('/pj')
def download_pj() -> Response:
    # Fait la requête au serveur pour récupérer le pj par id
    pj_r = requests.get('http://localhost:5000/api/pj', params={'id': request.args['pj']})
    # Récupère le nom dans le headers
    filename = re.findall("filename=(.+)", pj_r.headers['content-disposition'])[0].replace('"', '')
    # as_attachment signifie que le navigateur va télécharger le fichier au lieu d'essayer de l'afficher
    return send_file(io.BytesIO(pj_r.content), as_attachment=True, attachment_filename=filename)
