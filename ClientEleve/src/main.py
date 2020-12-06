import requests, json, re, os
from flask import Flask, request, render_template, redirect, send_from_directory

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

@app.route('/pj')
def pj():
    # Fait la requête au serveur pour récupérer le pj par id
    pj_r = requests.get('http://localhost:5000/api/pj', params={'id': request.args['pj']})
    # Récupère le nom dans le headers
    filename = re.findall("filename=(.+)", pj_r.headers['content-disposition'])[0].replace('"', '')
    # send_from_directory a besoin d'un chemin de fichier, on doit donc écrire le fichier
    # avant de l'envoyer puis le supprimer
    path = os.path.join('src', filename)
    open(path, 'wb').write(pj_r.content)
    # as_attachment signifie que le navigateur va télécharger le fichier au lieu d'essayer de l'afficher
    res = send_from_directory(directory='.', filename=filename, 
        as_attachment=True, cache_timeout=0)
    os.remove(path)
    return res, 200

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
            return redirect('/')
        else:
            return render_template('connexion.html', Erreur=True)
