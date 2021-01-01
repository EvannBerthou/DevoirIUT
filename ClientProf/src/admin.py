import requests, json
from flask import Blueprint, request, jsonify, render_template, redirect

admin = Blueprint('admin', __name__)

def valid_access():
    role_r = requests.get('http://localhost:5000/api/role', cookies=request.cookies)
    if role_r.status_code == 200:
        return json.loads(role_r.content)
    return None

def liste_classes():
    classes_r = requests.get('http://localhost:5000/api/classe')
    if classes_r.status_code == 200:
        return [''.join(classe) for classe in json.loads(classes_r.content)]
    return None

def liste_enseignants():
    enseignants_r = requests.get('http://localhost:5000/api/enseignant')
    if enseignants_r.status_code == 200:
        return [[str(v) for v in enseignant] for enseignant in json.loads(enseignants_r.content)]
    return None

def classe_enseignants():
    ce_r = requests.get('http://localhost:5000/api/classe_enseignant', cookies=request.cookies)
    if ce_r.status_code == 200:
        return json.loads(ce_r.content)
    return None

@admin.route('/')
def dashboard():
    if (resp := valid_access()):
        return render_template('admin.html', user = resp['user'])
    return 'Error', 404


"""
Pour chaque classse :
    Récupérer la liste de tous les enseignants
    Récupérer la liste de ses enseignants
    Afficher la liste de tous les enseignants
        Si l'enseignant est dans la liste des enseigantsn de la classe alors le marqué comme actif
    Lorsque le bouton enrengistrer est pressé, envoyer la liste des profs selectionnés (meme ceux qui étaient déjà selectionnées)
"""
@admin.route('/classes', methods=['GET'])
def gestion_classes():
    if (resp := valid_access()):
        classes = liste_classes()
        enseignants = liste_enseignants()
        ce = classe_enseignants()
        classe_avec_prof = dict(zip(classes, [[] for _ in range(len(classes))]))
        for x in ce:
            classe_avec_prof[x[0]].append(x[1])
        classe_avec_profs = list([list(x) for x in classe_avec_prof.items()])
        return render_template('classes.html', user = resp['user'], enseignants=enseignants, classes=classe_avec_profs)
    return 'Error', 403

@admin.route('/classes', methods=['POST'])
def suppr_classes():
    if (resp := valid_access()):
        if 'original' in request.form:
            requests.patch('http://localhost:5000/api/gestion_classe', cookies=request.cookies,
                    params={'old': request.form['original'], 'new': request.form['name']})
        elif 'new' in request.form:
            requests.post('http://localhost:5000/api/gestion_classe', cookies=request.cookies, params={'name': request.form['new']})
        else:
            requests.delete('http://localhost:5000/api/gestion_classe', cookies=request.cookies, params={'classe': request.form['suppr']})
        return redirect('/admin/classes')
    return 'Error', 404

@admin.route('/enseignants', methods=['GET'])
def gestion_enseignants():
    if (resp := valid_access()):
        enseignants = liste_enseignants()
        enseignants = [[str(i) for i in e] for e in enseignants]
        return render_template('enseignant.html', user = resp['user'], enseignants=enseignants)
    return 'Error', 404

@admin.route('/enseignants', methods=['POST'])
def suppr_enseignants():
    print(request.form)
    if (resp := valid_access()):
        if 'id' in request.form and request.form['id']:
            requests.patch('http://localhost:5000/api/gestion_enseignant', cookies=request.cookies,
                    params={
                        'id': request.form['id'],
                        'nom': request.form['nom'],
                        'prenom': request.form['prenom'],
                        'mail': request.form['mail'],
                        'mdp': request.form['mdp']
                    })
        elif 'new' in request.form:
            requests.post('http://localhost:5000/api/gestion_enseignant', cookies=request.cookies, params={
                    'nom': request.form['nom'],
                    'prenom': request.form['prenom'],
                    'mail': request.form['mail'],
                    'mdp': request.form['mdp']
                })
        else:
            requests.delete('http://localhost:5000/api/gestion_enseignant', cookies=request.cookies, params={'enseignant': request.form['suppr']})
        return redirect('/admin/enseignants')
    return 'Error', 404
