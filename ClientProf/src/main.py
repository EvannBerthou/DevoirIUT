import requests, json, os, re, io
from flask import Flask, request, render_template, redirect, send_file, make_response
from admin import admin

app = Flask(__name__, template_folder='templates')
app.register_blueprint(admin, url_prefix='/admin')
app.secret_key = 'secret key'

# Liste de toutes les classes
def liste_classes():
    classes_r = requests.get('http://localhost:5000/api/classe')
    if classes_r.status_code == 200:
        return [''.join(classe) for classe in json.loads(classes_r.content)]
    return None

# Liste des classes d'un prof ou message d'erreur + 0 si pas d'erreur sinon 1
def liste_classes_prof():
    classes_r = requests.get('http://localhost:5000/api/classe', cookies=request.cookies)
    content = json.loads(classes_r.content)
    if classes_r.status_code == 200:
        return [''.join(classe) for classe in content], 0
    return content['msg'], 1

# Liste de toutes les matières
def liste_matieres():
    matieres_r = requests.get('http://localhost:5000/api/matieres', cookies=request.cookies)
    content = json.loads(matieres_r.content)
    if matieres_r.status_code == 200:
        return [''.join(classe) for classe in content], 0
    return content['msg'], 1

@app.route('/')
def home():
    return redirect('/login')

@app.route('/nouveau', methods=['GET'])
def get_nouveau():
    result_classe, err_classe = liste_classes_prof()
    result_mat, err_mat = liste_matieres()
    if not err_classe and not err_mat:
        return render_template('nouveau.html', user = 'c', classes=result_classe, matieres=result_mat)
    print(err_classe, err_mat)
    # Forme un message d'erreur
    s = '<h1>'
    if err_classe:
        s += result_classes
        s += '<br>'
    if err_mat:
        s += result_mat
    s += '</h1>'
    return s

@app.route('/nouveau', methods=['POST'])
def post_nouveau():
    classes = ''.join([key+',' for key, val in request.form.items() if val == 'on'])
    enonce = request.form['enonce']
    matiere = request.form['matiere']
    date = request.form['date']

    files = {file.filename: file.stream.read() for file in request.files.getlist('file') if file.filename != ''}

    requests.post('http://localhost:5000/api/devoirs',
        params={'enonce': enonce,'matiere': matiere, 'classe': classes, 'date': date},
        files=files,
        cookies = request.cookies
    )
    return redirect('/devoirs')

@app.route('/devoirs',methods=['GET'])
def affichage_devoirs():
    resp_r = requests.get('http://localhost:5000/api/devoirs', cookies=request.cookies)
    if resp_r.status_code == 200:
        resp = json.loads(resp_r.content)
        classes=liste_classes()
        return render_template('devoirs.html', devoirs=resp['devoirs'], user = resp['user'], classes=classes)
    return '<h1> Erreur </h1>'

@app.route('/devoirs',methods=['POST'])
def post_devirs():
    if 'delete_button' in request.form:
        requests.post('http://localhost:5000/api/sup', params={'devoir_id':request.form['delete_button']})
    else:
            requests.put('http://localhost:5000/api/modif',
                params = {
                    'devoir_id': request.form['devoir_id'],
                    'enonce': request.form['enonce'],
                    'date': request.form['date']
                }
            )
    return redirect('/devoirs')

@app.route('/login',methods=['GET'])
def get_login():
    return render_template('login.html', Erreur=False)

@app.route('/login',methods=['POST'])
def post_login():
    email, pwd = request.form['username'], request.form['pwd']
    connect_data = requests.post('http://localhost:5000/api/token/auth', json={'username': email, 'password': pwd})
    #recuperation des données de la personne conectée nom , prenom
    if connect_data.status_code == 200:
        response = make_response(redirect('/devoirs'))
        response.set_cookie('access_token_cookie', connect_data.cookies.get('access_token_cookie'))
        return response
    return render_template('login.html', Erreur=True)

@app.route('/logout')
def logout():
    requests.post('http://localhost:5000/api/token/remove')
    resp = make_response(redirect('/'))
    resp.delete_cookie('access_token_cookie')
    return resp

@app.route('/pj')
def download_pj():
    # Fait la requête au serveur pour récupérer le pj par id
    pj_r = requests.get('http://localhost:5000/api/pj', params={'id': request.args['pj']})
    # Récupère le nom dans le headers
    filename = re.findall("filename=(.+)", pj_r.headers['content-disposition'])[0].replace('"', '')
    # as_attachment signifie que le navigateur va télécharger le fichier au lieu d'essayer de l'afficher
    return send_file(io.BytesIO(pj_r.content), as_attachment=True, attachment_filename=filename), 200

