import sqlite3
from flask import Flask, request, jsonify
from api import api
from flask_jwt_extended import (
    JWTManager, jwt_required, get_jwt_identity
)

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
app.secret_key = 'secret key'
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
#app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
#app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

jwt = JWTManager(app)
