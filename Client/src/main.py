import requests, json
from flask import Flask, request, render_template, redirect, url_for, make_response

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

def liste_classes():
    classes_r = requests.get('http://localhost:5000/api/classe')
    if classes_r.status_code == 200:
        classes = [''.join(classe) for classe in json.loads(classes_r.content)]
        return classes
    return None

@app.route('/', methods=['GET'])
def home():
    classes = liste_classes()
    if classes is not None:
        return render_template('index.html', classes=classes)
    else:
        return '<h1> Erreur </h1>'

@app.route('/connexion',methods=['GET', 'POST'])
def connexion():
    if request.method=='GET':
        return render_template('connexion.html', Erreur=False)
    
    elif request.method == 'POST':
        email = request.form['email']
        pwd=request.form['pwd']

        connect_data= requests.get('http://localhost:5000/api/connexion', params={'email': email,'pwd':pwd})
        connect_data=json.loads(connect_data.content)
        #  recuperation des donne de la personne conecteé nom , prenom 
        if connect_data:
            return redirect('/nouveau')
        else:
            return render_template('connexion.html', Erreur=True)



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
