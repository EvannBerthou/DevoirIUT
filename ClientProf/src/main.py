import requests, json, os
from flask import Flask, request, render_template, redirect

app = Flask(__name__, template_folder='templates')

def liste_classes():
    classes_r = requests.get('http://localhost:5000/api/classe')
    if classes_r.status_code == 200:
        return [''.join(classe) for classe in json.loads(classes_r.content)]
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
        matiere = request.form['matiere']
        prof = request.form['prof']
        date = request.form['date']

        files = {}
        for file in request.files.getlist('file'):
            if file.filename != '':
                files[file.filename] = file.stream.read()

        requests.post('http://localhost:5000/api/devoirs', 
            params={'enonce': enonce,'matiere': matiere, 'prof': prof, 'classe': classes, 'date': date},
            files=files
        )
        
        return redirect('/')
