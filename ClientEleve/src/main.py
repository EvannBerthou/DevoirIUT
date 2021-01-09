import requests, json, re, os, io
from typing import *
from flask import Flask, request, render_template, redirect, send_file
from werkzeug.wrappers import Response

Str_response = Tuple[str, int]
Str_or_Response = Tuple[Union[str, Response], int]
Response_code = Tuple[Response, int]

app = Flask(__name__, template_folder='templates')

@app.route('/classe', methods=['GET'])
def devoir_classe() -> Str_or_Response:
    if not request.args:
        return redirect('/'), 200

    classe = request.args['classe']
    classes = liste_classes()

    resp_r = requests.get('http://localhost:5000/api/devoirs', params={'classe': classe})
    if resp_r.status_code == 200:
        resp = json.loads(resp_r.content)
        print(resp)
        return render_template('devoirs.html', devoirs=resp['devoirs']), 200
    return '<h1> Erreur </h1>', 404

def liste_classes() -> Optional[List[str]]:
    classes_r = requests.get('http://localhost:5000/api/classe')
    if classes_r.status_code == 200:
        return [''.join(classe) for classe in json.loads(classes_r.content)]
    return None

@app.route('/', methods=['GET'])
def home() -> Str_response:
    classes = liste_classes()
    if classes:
        return render_template('index.html', classes=classes), 200
    return '<h1> Erreur </h1>', 400

@app.route('/pj')
def download_pj() -> Response:
    # Fait la requête au serveur pour récupérer le pj par id
    pj_r = requests.get('http://localhost:5000/api/pj', params={'id': request.args['pj']})
    # Récupère le nom dans le headers
    filename = re.findall("filename=(.+)", pj_r.headers['content-disposition'])[0].replace('"', '')
    # as_attachment signifie que le navigateur va télécharger le fichier au lieu d'essayer de l'afficher
    return send_file(io.BytesIO(pj_r.content), as_attachment=True, attachment_filename=filename)
