import sqlite3
import requests
from bs4 import BeautifulSoup
from werkzeug.security import generate_password_hash
import xml.etree.ElementTree as ET

html = requests.get('http://chronos.iut-velizy.uvsq.fr/EDT/gindex.html').content
soup = BeautifulSoup(html, features='html.parser')
options = soup.find_all('option')#.text.strip().split('\n')

pages = [opt.get('value') for opt in options if opt.get('value') != None]
texts = [opt.text for opt in options if opt.get('value') != None]

profs = set()
matieres = set()
# Les matières dans lesquel un prof enseigne
matieres_prof = {}

# Pour chaque page de l'EDT (toutes les classes)
for page in pages:
    print(page)
    xml = page.split('.')[0] + ".xml"
    tree = ET.fromstring(requests.get(f'http://chronos.iut-velizy.uvsq.fr/EDT/{xml}').content)
    profs_classe = []
    # Récupère toutes les cases de l'EDT
    for ressource in tree.findall('.//resources'):
        staff = ressource.find('staff')
        module = ressource.find('module')
        if staff and module:
            prof = (list(staff)[0].text) # Récupère le nom du prof
            matiere = (list(module)[0].text) # Récupère le nom de la matière du prof
            profs.add(prof)
            matieres.add(matiere)
            if not prof in matieres_prof:
                matieres_prof[prof] = set()
            matieres_prof[prof].add(matiere)

#print(matieres_prof)
#print(sorted(list(profs)))
#print(sorted(list(matieres)))

db = sqlite3.connect('src/devoirs.db')
c = db.cursor()
sql_str = open('db.sql').read()
c.executescript(sql_str)

for classe in texts:
    c.execute('INSERT INTO classes (nom) VALUES (?);', [classe])

pwd = generate_password_hash('C')
c.execute("INSERT INTO enseignant VALUES (1,'a','b','c', ?, 1);", [pwd])

pwd = generate_password_hash('SQL')
c.execute("INSERT INTO enseignant VALUES (2,'s','q','l', ?, 0);", [pwd])

#('Programmation'), ('Algorithmie'),('Base de Donnée'),('Anglais'),('Expression communication'),('Mathématique'),('Economie Générale');
c.execute("INSERT INTO matiere_enseignant VALUES (1, 1);")
c.execute("INSERT INTO matiere_enseignant VALUES (1, 2);")
c.execute("INSERT INTO matiere_enseignant VALUES (2, 3);")

c.execute("INSERT INTO classe_enseignant VALUES (1, 1);")

c.close()
db.commit()
