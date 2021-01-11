import requests, json
from typing import *
from flask import Blueprint, request, jsonify, render_template, redirect
from werkzeug.wrappers import Response
from utils import *

admin = Blueprint('admin', __name__)

@admin.route('/')
@require_admin
def dashboard() -> Str_response:
    username = get_username()
    return render_template('admin.html', user = username)

"""
Classes
"""

# Affiche la liste de toutes les classes (+ les profs dans chaque classe)
@admin.route('/classes', methods=['GET'])
@require_admin
def get_classes() -> Str_response:
    username = get_username()
    classes = liste_classes()
    enseignants = liste_enseignants()
    ce = classe_enseignants()
    merged = merge_with_prof(classes, ce)
    return render_template('classes.html', user = username, enseignants=enseignants, classes=merged)

# Modification d'une classe
@admin.route('/classes', methods=['POST'])
@require_admin
def post_classes() -> Str_or_Response:
    username = get_username()
    send_form_to('http://localhost:5000/api/gestion_classe')
    return redirect('/admin/classes')

"""
Matières
"""

# Affiche la liste de toutes les matières (+ les profs dans chaque matières)
@admin.route('/matieres', methods=['GET'])
@require_admin
def get_matieres() -> Str_response:
    username = get_username()
    matieres = liste_matieres()
    enseignants = liste_enseignants()
    ce = matiere_enseignants()
    merged = merge_with_prof(matieres, ce)
    return render_template('matieres.html', user = username, enseignants=enseignants, matieres=merged)


@admin.route('/matieres', methods=['POST'])
@require_admin
def post_matieres() -> Str_or_Response:
    username = get_username()
    send_form_to('http://localhost:5000/api/gestion_matieres')
    return redirect('/admin/matieres')

"""
Enseignants
"""

# Affiche la liste de tous les profs (+ leurs infos : nom, prenom, mail)
@admin.route('/enseignants', methods=['GET'])
@require_admin
def get_enseignants() -> Str_response:
    username = get_username()
    enseignants = liste_enseignants()
    return render_template('enseignant.html', user = username, enseignants=enseignants)

@admin.route('/enseignants', methods=['POST'])
@require_admin
def post_enseignants() -> Str_or_Response:
    username = get_username()
    send_form_to('http://localhost:5000/api/gestion_enseignant')
    return redirect('/admin/enseignants')
