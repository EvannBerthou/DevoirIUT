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
        # S'il y a au moins un prof et une matière
        if staff and module:
            # Ajoute chaque prof et chaque matière à chaqueprof
            for prof in list(staff):
                p = prof.text
                profs.add(p)
                if not p in matieres_prof:
                    matieres_prof[p] = set()
                for mat in list(module):
                    m = mat.text
                    matieres.add(m)
                    matieres_prof[p].add(m)

db = sqlite3.connect('src/devoirs.db')
c = db.cursor()
sql_str = open('db.sql').read()
c.executescript(sql_str)

print('Insertion classes')
for classe in texts:
    c.execute('INSERT INTO classes (nom) VALUES (?);', [classe])

print('Insertion matieres')
for matiere in matieres:
    c.execute('INSERT INTO matiere (nom) VALUES (?);', [matiere])

print('Insertion profs')
for prof in profs:
    pwd = generate_password_hash('azerty')
    c.execute("""
        INSERT INTO enseignant (nom,prenom,mail,pwd,admin)
        VALUES (?,'','', ?, 0);
    """, [prof, pwd])

print('Insertion matiere prof')
for prof, mats in matieres_prof.items():
    for mat in mats:
        c.execute("""
            INSERT INTO matiere_enseignant (enseignant_id, matiere_id)
            VALUES ((SELECT id FROM enseignant WHERE nom = ?),
                    (SELECT id FROM matiere WHERE nom = ?));
        """, [prof, mat])


pwd = generate_password_hash('C')
c.execute("INSERT INTO enseignant (nom,prenom,mail,pwd,admin)VALUES ('a','b','c', ?, 1);", [pwd])

pwd = generate_password_hash('SQL')
c.execute("INSERT INTO enseignant (nom,prenom,mail,pwd,admin) VALUES ('s','q','l', ?, 0);", [pwd])

#('Programmation'), ('Algorithmie'),('Base de Donnée'),('Anglais'),('Expression communication'),('Mathématique'),('Economie Générale');
c.execute("INSERT INTO matiere_enseignant VALUES (1, 1);")
c.execute("INSERT INTO matiere_enseignant VALUES (1, 2);")
c.execute("INSERT INTO matiere_enseignant VALUES (2, 3);")

c.close()
db.commit()
