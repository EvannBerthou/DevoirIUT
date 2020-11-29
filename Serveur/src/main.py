from flask import Flask
from api import api
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')

html = requests.get('http://chronos.iut-velizy.uvsq.fr/EDT/gindex.html').content

soup = BeautifulSoup(html, features='html.parser')
classes = soup.find('select').text.strip().split('\n')[2:]
