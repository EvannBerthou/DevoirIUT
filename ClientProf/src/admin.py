import requests, json
from flask import Blueprint, request, jsonify, render_template, redirect

admin = Blueprint('admin', __name__)

# Vérifie si l'utilisateur connecté à le rôle d'admin
def valid_access():
    role_r = requests.get('http://localhost:5000/api/role', cookies=request.cookies)
    if role_r.status_code == 200:
        return json.loads(role_r.content)
    return None

# Liste des classes
def liste_classes():
    classes_r = requests.get('http://localhost:5000/api/classe')
    if classes_r.status_code == 200:
        return [classe[0] for classe in json.loads(classes_r.content)]
    return None

# Liste des enseignants
def liste_enseignants():
    enseignants_r = requests.get('http://localhost:5000/api/enseignant')
    if enseignants_r.status_code == 200:
        return [[str(v) for v in enseignant] for enseignant in json.loads(enseignants_r.content)]
    return None

# Liste de toutes les matières
def liste_matieres():
    matieres_r = requests.get('http://localhost:5000/api/matieres')
    if matieres_r.status_code == 200:
        return [''.join(matiere) for matiere in json.loads(matieres_r.content)]
    return None

# Liste des classes d'un enseignant
def classe_enseignants():
    ce_r = requests.get('http://localhost:5000/api/classe_enseignant', cookies=request.cookies)
    if ce_r.status_code == 200:
        return json.loads(ce_r.content)
    return None

# Liste des matières d'un enseignant
def matiere_enseignants():
    ce_r = requests.get('http://localhost:5000/api/matiere_enseignant', cookies=request.cookies)
    if ce_r.status_code == 200:
        return json.loads(ce_r.content)
    return None

@admin.route('/')
def dashboard():
    if (resp := valid_access()):
        return render_template('admin.html', user = resp['user'])
    return render_template('error.html', msg="Accès refusé"), 404

@admin.route('/classes', methods=['GET'])
def gestion_classes():
    if (resp := valid_access()):
        classes = liste_classes()
        enseignants = liste_enseignants()
        ce = classe_enseignants()
        # Dictionnaire contenant chaque prof en clé et les classes dans lequelles il est en valeur
        classe_avec_prof = dict(zip(classes, [[] for _ in range(len(classes))]))
        for x in ce:
            classe_avec_prof[x[0]].append(x[1])
        # Convertie en liste
        classe_avec_profs = list([list(x) for x in classe_avec_prof.items()])
        return render_template('classes.html', user = resp['user'], enseignants=enseignants, classes=classe_avec_profs)
    return render_template('error.html', msg="Accès refusé"), 404

@admin.route('/classes', methods=['POST'])
def suppr_classes():
    if (resp := valid_access()):
        # Modification
        if 'id' in request.form:
            requests.patch('http://localhost:5000/api/gestion_classe', cookies=request.cookies,
                params={
                    'id': request.form['id'],
                    'nom': request.form['nom'],
                    'enseignants': request.form.getlist('select')
                }
            )
        # Ajout
        elif 'new' in request.form:
            requests.post('http://localhost:5000/api/gestion_classe', cookies=request.cookies, params={'name': request.form['new']})
        # Suppression
        else:
            requests.delete('http://localhost:5000/api/gestion_classe', cookies=request.cookies, params={'classe': request.form['suppr']})
        return redirect('/admin/classes')
    return render_template('error.html', msg="Accès refusé"), 404

@admin.route('/matieres', methods=['GET'])
def get_matieres():
    if (resp := valid_access()):
        matieres = liste_matieres()
        enseignants = liste_enseignants()
        ce = matiere_enseignants()
        # Dictionnaire contenant chaque prof en clé et les matieres dans lequelles il est en valeur
        matiere_avec_prof = dict(zip(matieres, [[] for _ in range(len(matieres))]))
        for x in ce:
            matiere_avec_prof[x[0]].append(x[1])
        # Convertie en liste
        matiere_avec_profs = list([list(x) for x in matiere_avec_prof.items()])
        return render_template('matieres.html', user = resp['user'], enseignants=enseignants, matieres=matiere_avec_profs)
    return render_template('error.html', msg="Accès refusé"), 404


@admin.route('/matieres', methods=['POST'])
def post_matieres():
    if (resp := valid_access()):
        # Modification
        if 'id' in request.form:
            requests.patch('http://localhost:5000/api/gestion_matieres', cookies=request.cookies,
                params={
                    'id': request.form['id'],
                    'nom': request.form['nom'],
                    'enseignants': request.form.getlist('select')
                }
            )
        # Ajout
        elif 'new' in request.form:
            requests.post('http://localhost:5000/api/gestion_matieres', cookies=request.cookies, params={'name': request.form['new']})
        # Suppression
        else:
            requests.delete('http://localhost:5000/api/gestion_matieres', cookies=request.cookies, params={'classe': request.form['suppr']})
        return redirect('/admin/matieres')
    return render_template('error.html', msg="Accès refusé"), 404

@admin.route('/enseignants', methods=['GET'])
def get_enseignants():
    if (resp := valid_access()):
        enseignants = liste_enseignants()
        enseignants = [[str(i) for i in e] for e in enseignants]
        return render_template('enseignant.html', user = resp['user'], enseignants=enseignants)
    return render_template('error.html', msg="Accès refusé"), 404

@admin.route('/enseignants', methods=['POST'])
def post_enseignants():
    if (resp := valid_access()):
        # Modification
        if 'id' in request.form and request.form['id']:
            requests.patch('http://localhost:5000/api/gestion_enseignant', cookies=request.cookies,
                params = {
                    'id': request.form['id'],
                    'nom': request.form['nom'],
                    'prenom': request.form['prenom'],
                    'mail': request.form['mail'],
                    'mdp': request.form['mdp']
                }
            )
        # Ajout
        elif 'new' in request.form:
            requests.post('http://localhost:5000/api/gestion_enseignant', cookies=request.cookies,
                params = {
                    'nom': request.form['nom'],
                    'prenom': request.form['prenom'],
                    'mail': request.form['mail'],
                    'mdp': request.form['mdp']
                }
            )
        # Suppression
        else:
            requests.delete('http://localhost:5000/api/gestion_enseignant', cookies=request.cookies, params={'enseignant': request.form['suppr']})
        return redirect('/admin/enseignants')
    return render_template('error.html', msg="Accès refusé"), 404
