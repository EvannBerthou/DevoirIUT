import requests, json
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__, template_folder='templates')

@app.route('/classe', methods=['GET'])
def devoir_classe():
    if not request.args:
        return redirect('/')

    classe = request.args['classe']
    devoirs_r = requests.get('http://localhost:5000/api/devoirs', params={'classe': classe})
    if devoirs_r.status_code == 200:
        devoirs = json.loads(devoirs_r.content)
        return render_template('devoirs.html', devoirs=devoirs, classe=classe)
    else:
        return '<h1> Erreur </h1>'

@app.route('/', methods=['GET'])
def home():
    classes_r = requests.get('http://localhost:5000/api/classe')
    if classes_r.status_code == 200:
        classes = [''.join(classe) for classe in json.loads(classes_r.content)]
        return render_template('index.html', classes=classes)
    else:
        return '<h1> Erreur </h1>'
