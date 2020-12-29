import requests, json, re, os, io
from flask import Flask, request, render_template, redirect, send_from_directory, send_file

app = Flask(__name__, template_folder='templates')

@app.route('/classe', methods=['GET'])
def devoir_classe():
    if not request.args:
        return redirect('/')

    classe = request.args['classe']
    classes = liste_classes()

    resp_r = requests.get('http://localhost:5000/api/devoirs', params={'classe': classe})
    if resp_r.status_code == 200:
        resp = json.loads(resp_r.content)
        print(resp)
        return render_template('devoirs.html', devoirs=resp['devoirs'])
    else:
        return '<h1> Erreur </h1>'

def liste_classes():
    classes_r = requests.get('http://localhost:5000/api/classe')
    if classes_r.status_code == 200:
        return [''.join(classe) for classe in json.loads(classes_r.content)]
    return None

@app.route('/', methods=['GET'])
def home():
    classes = liste_classes()
    if classes is not None:
        return render_template('index.html', classes=classes)
    else:
        return '<h1> Erreur </h1>'

@app.route('/pj')
def pj():
    # Fait la requête au serveur pour récupérer le pj par id
    pj_r = requests.get('http://localhost:5000/api/pj', params={'id': request.args['pj']})
    # Récupère le nom dans le headers
    filename = re.findall("filename=(.+)", pj_r.headers['content-disposition'])[0].replace('"', '')
    # as_attachment signifie que le navigateur va télécharger le fichier au lieu d'essayer de l'afficher
    return send_file(io.BytesIO(pj_r.content), as_attachment=True, attachment_filename=filename), 200

