from flask import Flask
from flask_jwt_extended import JWTManager

from classes import classes_bp
from devoirs import devoirs_bp
from enseignants import enseignants_bp
from matieres import matieres_bp
from auth import auth_bp


app = Flask(__name__)
# Blueprints
app.register_blueprint(classes_bp, url_prefix='/api')
app.register_blueprint(devoirs_bp, url_prefix='/api')
app.register_blueprint(enseignants_bp, url_prefix='/api')
app.register_blueprint(matieres_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api')

# Config
app.secret_key = 'secret key'
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
#app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
#app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

jwt = JWTManager(app)
