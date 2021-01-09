import requests, json
from typing import *
from flask import Blueprint, request, jsonify, render_template, redirect, abort
from werkzeug.wrappers import Response

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

# Liste de toutes les classes
def liste_classes() -> List[str]:
    response = backend_request(requests.get, 'http://localhost:5000/api/classe')
    return list(json.loads(response.content))

# Liste des classes d'un prof ou message d'erreur + erreur
def liste_classes_prof() -> List[str]:
    response = backend_request(requests.get, 'http://localhost:5000/api/classe', cookies=request.cookies)
    return list(json.loads(response.content))

# Liste de toutes les matières
def liste_matieres() -> List[str]:
    response = backend_request(requests.get, 'http://localhost:5000/api/matieres', cookies=request.cookies)
    return list(json.loads(response.content))
