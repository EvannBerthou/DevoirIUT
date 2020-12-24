from flask import Flask
from api import api
import flask_login

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
login_manager = flask_login.LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def user_loader():
    user = User()
    user.id = 0
    return user

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Accès refusé'
