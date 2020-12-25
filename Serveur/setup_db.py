import sqlite3
import requests
from bs4 import BeautifulSoup
from werkzeug.security import generate_password_hash

html = requests.get('http://chronos.iut-velizy.uvsq.fr/EDT/gindex.html').content
soup = BeautifulSoup(html, features='html.parser')
classes = soup.find('select').text.strip().split('\n')[2:]

db = sqlite3.connect('src/devoirs.db')
c = db.cursor()
sql_str = open('db.sql').read()
c.executescript(sql_str)

for classe in classes:
    c.execute('INSERT INTO classes (nom) VALUES (?);', [classe])

pwd = generate_password_hash('C')
c.execute("INSERT INTO enseignant VALUES (1,'a','b','c', ?, 1);", [pwd])

pwd = generate_password_hash('SQL')
c.execute("INSERT INTO enseignant VALUES (2,'s','q','l', ?, 0);", [pwd])

#('Programmation'), ('Algorithmie'),('Base de Donnée'),('Anglais'),('Expression communication'),('Mathématique'),('Economie Générale');
c.execute("INSERT INTO matiere_enseignant VALUES (1, 1);")
c.execute("INSERT INTO matiere_enseignant VALUES (1, 2);")
c.execute("INSERT INTO matiere_enseignant VALUES (2, 3);")
c.close()
db.commit()
