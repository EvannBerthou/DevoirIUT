import requests, json, os
from flask import Flask, request, render_template, redirect
import flask_login

app = Flask(__name__, template_folder='templates')
app.secret_key = 'secret key'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass

def liste_classes():
    classes_r = requests.get('http://localhost:5000/api/classe')
    if classes_r.status_code == 200:
        return [''.join(classe) for classe in json.loads(classes_r.content)]
    return None

@app.route('/')
def home():
    return redirect('/nouveau')

@app.route('/nouveau', methods=['GET', 'POST'])
@flask_login.login_required
def nouveau_devoir():
    if request.method == 'GET':
        classes = liste_classes()
        if classes:
            return render_template('nouveau.html', user = flask_login.current_user, classes=classes)
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

@app.route('/login',methods=['GET', 'POST'])
def connexion():
    print(request.method)
    if request.method=='GET':
        return render_template('login.html', Erreur=False)
    
    elif request.method == 'POST':
        email, pwd = request.form['username'], request.form['pwd']

        connect_data = requests.get('http://localhost:5000/api/login', params={'email': email, 'pwd': pwd})
        #  recuperation des donne de la personne conecteé nom , prenom 
        if connect_data.status_code == 200:
            user = User()
            user.id = email
            flask_login.login_user(user)
            return redirect('/')
        else:
            print('invalide')
            return render_template('login.html', Erreur=True)

@login_manager.user_loader
def user_loader(email):
    if not email:
        return

    user_data = requests.get('http://localhost:5000/api/user', params={'email': email})
    if user_data.status_code != 200:
        return None

    user = User()
    user.id = email
    return user

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect('/')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Accès refusé'


