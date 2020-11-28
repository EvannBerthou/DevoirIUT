import requests, json
from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    devoirs_r = requests.get('http://localhost:5000/api/devoirs')
    if devoirs_r.status_code == 200:
        sortie = '<li>'
        devoirs = json.loads(devoirs_r.content)
        return render_template('devoirs.html', devoirs=devoirs)
    else:
        return '<h1> Erreur </h1>'
