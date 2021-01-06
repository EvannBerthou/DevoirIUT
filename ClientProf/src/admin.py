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
        return [classe for classe in json.loads(classes_r.content)]
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
        return [matieres for matieres in json.loads(matieres_r.content)]
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

def merge_with_prof(d, profs):
    id_d = {v:i for i,v in d}
    d_avec_profs = {k:[] for k in [c[1] for c in d]}

    for x in profs:
        d_avec_profs[x[0]].append(x[1:])

    # Ajoute l'id au début de la liste pour passer de [nom, [profs]] à [id, nom, [profs]]
    d_avec_profs_et_id = [[id_d[d[0]]] + list(d) for d in d_avec_profs.items()]
    return d_avec_profs_et_id

def send_form_to(url):
    # Modification
    if 'id' in request.form:
        requests.patch(url, cookies=request.cookies,
            params={
                'id': request.form['id'],
                'nom': request.form['nom'],
                'enseignants': request.form.getlist('select')
            }
        )
    # Ajout
    elif 'new' in request.form:
        requests.post(url, cookies=request.cookies, params={'name': request.form['new']})
    # Suppression
    else:
        requests.delete(url, cookies=request.cookies, params={'id': request.form['suppr']})

@admin.route('/')
def dashboard():
    if (resp := valid_access()):
        return render_template('admin.html', user = resp['user'])
    return render_template('error.html', msg="Accès refusé"), 404

"""
Classes
"""

# Affiche la liste de toutes les classes (+ les profs dans chaque classe)
@admin.route('/classes', methods=['GET'])
def get_classes():
    if (resp := valid_access()):
        classes = liste_classes()
        enseignants = liste_enseignants()
        ce = classe_enseignants()
        merged = merge_with_prof(classes, ce)
        return render_template('classes.html', user = resp['user'], enseignants=enseignants, classes=merged)
    return render_template('error.html', msg="Accès refusé"), 404

# Modification d'une classe
@admin.route('/classes', methods=['POST'])
def post_classes():
    if (resp := valid_access()):
        send_form_to('http://localhost:5000/api/gestion_classe')
        return redirect('/admin/classes')
    return render_template('error.html', msg="Accès refusé"), 404

"""
Matières
"""

# Affiche la liste de toutes les matières (+ les profs dans chaque matières)
@admin.route('/matieres', methods=['GET'])
def get_matieres():
    if (resp := valid_access()):
        matieres = liste_matieres()
        enseignants = liste_enseignants()
        ce = matiere_enseignants()
        merged = merge_with_prof(matieres, ce)
        return render_template('matieres.html', user = resp['user'], enseignants=enseignants, matieres=merged)
    return render_template('error.html', msg="Accès refusé"), 404


@admin.route('/matieres', methods=['POST'])
def post_matieres():
    if (resp := valid_access()):
        send_form_to('http://localhost:5000/api/gestion_matieres')
        return redirect('/admin/matieres')
    return render_template('error.html', msg="Accès refusé"), 404

"""
Enseignants
"""

# Affiche la liste de tous les profs (+ leurs infos : nom, prenom, mail)
@admin.route('/enseignants', methods=['GET'])
def get_enseignants():
    if (resp := valid_access()):
        enseignants = liste_enseignants()
        return render_template('enseignant.html', user = resp['user'], enseignants=enseignants)
    return render_template('error.html', msg="Accès refusé"), 404

@admin.route('/enseignants', methods=['POST'])
def post_enseignants():
    if (resp := valid_access()):
        send_form_to('http://localhost:5000/api/gestion_enseignant')
        return redirect('/admin/enseignants')
    return render_template('error.html', msg="Accès refusé"), 404
