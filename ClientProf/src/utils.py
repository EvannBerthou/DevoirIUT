import requests, json
from typing import *
from flask import Blueprint, request, jsonify, render_template, redirect, abort
from werkzeug.wrappers import Response
from functools import wraps

utils = Blueprint('app', __name__)

Str_response = str
Str_code = Tuple[str, int]
Str_or_Response = Union[str, Response]
Response_code = Tuple[Response, int]

@utils.app_errorhandler(503)
def server_error(e: Any) -> Str_code:
    return render_template('error.html', msg = "Echec de la connexion au serveur"), 503

@utils.app_errorhandler(404)
def resource_not_found(e: Any) -> Str_code:
    return render_template('error.html', msg = "Page introuvable"), 404

@utils.app_errorhandler(401)
def access_forbidden(e: Any) -> Str_code:
    return render_template('error.html', msg = "Accès non autorisé"), 404

# Fais une requête au back-end avec gestion des erreurs
def backend_request(f: Callable, url: str, **params: Any) -> Any:
    try:
        response = f(url, **params)
    except:
        abort(503)

    if response.status_code != 200:
        abort(response.status_code)

    return response

# Vérifie si l'utilisateur connecté à le rôle d'admin
def get_username() -> Any:
    response = backend_request(requests.get, 'http://localhost:5000/api/role', cookies=request.cookies)
    return json.loads(response.content)['user']

# Liste de toutes les classes
def liste_classes() -> List[Tuple[int, str]]:
    response = backend_request(requests.get, 'http://localhost:5000/api/classe')
    return list(json.loads(response.content))

# Liste des classes d'un prof ou message d'erreur + erreur
def liste_classes_prof() -> List[str]:
    response = backend_request(requests.get, 'http://localhost:5000/api/classe', cookies=request.cookies)
    return [x[0] for x in json.loads(response.content)]

# Liste de toutes les matières
def liste_matieres() -> Any:
    matieres_r = requests.get('http://localhost:5000/api/matieres')
    return json.loads(matieres_r.content)

# Liste de toutes les matières
def liste_matieres_prof() -> List[str]:
    response = backend_request(requests.get, 'http://localhost:5000/api/matieres', cookies=request.cookies)
    return [x[0] for x in json.loads(response.content)]

# Liste des enseignants
def liste_enseignants() -> Any:
    response = requests.get('http://localhost:5000/api/enseignant')
    return json.loads(response.content)

# Liste des classes d'un enseignant
def classe_enseignants() -> Any:
    ce_r = backend_request(requests.get, 'http://localhost:5000/api/classe_enseignant', cookies=request.cookies)
    return json.loads(ce_r.content)

# Liste des matières d'un enseignant
def matiere_enseignants() -> Any:
    r = requests.get('http://localhost:5000/api/matiere_enseignant', cookies=request.cookies)
    return json.loads(r.content)

def merge_with_prof(d: List[Tuple[int, str]], profs: List[str]) -> List:
    id_d = {v:i for i,v in d}
    d_avec_profs: Dict = {k:[] for k in [c[1] for c in d]}

    for x in profs:
        d_avec_profs[x[0]].append(x[1:])

    # Ajoute l'id au début de la liste pour passer de [nom, [profs]] à [id, nom, [profs]]
    d_avec_profs_et_id = [[id_d[d[0]]] + list(d) for d in d_avec_profs.items()]
    return d_avec_profs_et_id

def send_form_to(url: str) -> None:
    # Modification
    if 'id' in request.form:
        requests.patch(url, cookies=request.cookies,
            params = {
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

def require_admin(f: Callable) -> Callable:
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        response = backend_request(requests.get, 'http://localhost:5000/api/is_admin', cookies=request.cookies)
        if json.loads(response.content) != "ok":
            return render_template('error.html', msg = "Vous n'êtes pas admin")
        return f(*args, **kwargs)
    return decorated_function
