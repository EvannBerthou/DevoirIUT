import requests, json
from flask import Flask, request, render_template, redirect

app = Flask(__name__, template_folder='templates')

def liste_classes():
    classes_r = requests.get('http://localhost:5000/api/classe')
    if classes_r.status_code == 200:
        classes = [''.join(classe) for classe in json.loads(classes_r.content)]
        return classes
    return None

@app.route('/')
def home():
    return redirect('/nouveau')

@app.route('/nouveau', methods=['GET', 'POST'])
def nouveau_devoir():
    if request.method == 'GET':
        classes = liste_classes()
        if classes:
            return render_template('nouveau.html', classes=classes)
        else:
            return '<h1> Erreur </h1>'

    elif request.method == 'POST':
        classes = [key for key, val in request.form.items() if val == 'on']
        enonce = request.form['enonce']
        matiere=request.form['matiere']
        prof = request.form['prof']
        requests.post('http://localhost:5000/api/devoirs', params={'enonce': enonce,'matiere':matiere, 'prof': prof, 'classe': classes})
        return redirect('/')
