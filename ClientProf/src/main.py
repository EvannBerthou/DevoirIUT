import requests, json, os, re, io
from flask import Flask, request, render_template, redirect, send_file
from admin import admin

app = Flask(__name__, template_folder='templates')
app.register_blueprint(admin, url_prefix='/admin')
app.secret_key = 'secret key'
def liste_classes():
    classes_r = requests.get('http://localhost:5000/api/classe')
    if classes_r.status_code == 200:
        return [''.join(classe) for classe in json.loads(classes_r.content)]
    return None

def liste_matires():
    matieres_r = requests.get('http://localhost:5000/api/matieres',
            params={'enseignant':'c'})
    if matieres_r.status_code == 200:
        return [''.join(matiere) for matiere in json.loads(matieres_r.content)]
    return None

@app.route('/')
def home():
    return redirect('/login')

@app.route('/nouveau', methods=['GET', 'POST'])
def nouveau_devoir():
    if request.method == 'GET':
        classes = liste_classes()
        matieres = liste_matires()
        if classes:
            return render_template('nouveau.html', user = 'c')
                classes=classes, matieres=matieres)
        else:
            return '<h1> Erreur </h1>'

    elif request.method == 'POST':
        classes = [key for key, val in request.form.items() if val == 'on']
        enonce = request.form['enonce']
        matiere = request.form['matiere']
        prof = 'c' #flask_login.current_user.id # Le nom du prof est l'id, devra être changé pour utiliser current_user.nom
        date = request.form['date']



        #files = {file.filename: file.stream.read() for file in request.files.getlist('file') if file.filename != ''}

        requests.post('http://localhost:5000/api/devoirs',
            params={'enonce': enonce,'matiere': matiere, 'prof': prof, 'classe': classes, 'date': date},
            files=files
        )

        return redirect('/devoirs')

@app.route('/devoirs',methods=['GET', 'POST'])
def affichage_devoirs():
    if request.method =='GET':
        devoirs_r = requests.get('http://localhost:5000/api/devoirs', params={'user': flask_hhogin.current_user.id})
        if devoirs_r.status_code == 200:
            devoirs = json.loads(devoirs_r.content)
            return render_template('devoirs.html', devoirs=devoirs, user = 'c')
        else:
            return '<h1> Erreur </h1>'
    elif request.method=='POST':
        if 'delete_button' in request.form:
            requests.post('http://localhost:5000/api/sup', params={'devoir_id':request.form['delete_button']})
        else:
            params = {'devoir_id': request.form['devoir_id'],
                      'enonce': request.form['enonce'],
                      'date': request.form['date']}
            requests.put('http://localhost:5000/api/modif', params=params)
        return redirect('/devoirs')


@app.route('/login',methods=['GET', 'POST'])
def connexion():
    if request.method=='GET':
        return render_template('login.html', Erreur=False)

    elif request.method == 'POST':
        email, pwd = request.form['username'], request.form['pwd']

        connect_data = requests.get('http://localhost:5000/api/login', params={'email': email, 'pwd': pwd})
        #recuperation des données de la personne conectée nom , prenom
        if connect_data.status_code == 200:
            #user = User()
            #user.id = email
            #flask_login.login_user(user)
            return redirect('/devoirs')
        else:
            return render_template('login.html', Erreur=True)

@app.route('/logout')
def logout():
    return redirect('/')

@app.route('/pj')
def pj():
    # Fait la requête au serveur pour récupérer le pj par id
    pj_r = requests.get('http://localhost:5000/api/pj', params={'id': request.args['pj']})
    # Récupère le nom dans le headers
    filename = re.findall("filename=(.+)", pj_r.headers['content-disposition'])[0].replace('"', '')
    # as_attachment signifie que le navigateur va télécharger le fichier au lieu d'essayer de l'afficher
    return send_file(io.BytesIO(pj_r.content), as_attachment=True, attachment_filename=filename), 200

