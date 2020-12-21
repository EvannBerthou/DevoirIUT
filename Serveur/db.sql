DROP TABLE IF EXISTS classes;
CREATE TABLE classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    nom TEXT NOT NULL
);

DROP TABLE IF EXISTS devoirs;
CREATE TABLE devoirs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enonce TEXT,
    matiere INTEGER,
    prof INTEGER,
    jour date,
    a_rendre INT DEFAULT 0,
    FOREIGN KEY (matiere) REFERENCES matiere(id),
    FOREIGN KEY (prof) REFERENCES enseignant(id)
);

DROP TABLE IF EXISTS pj;
CREATE TABLE pj (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    devoir_id INT,
    nom TEXT NOT NULL,
    contenue BLOB NOT NULL,
    FOREIGN KEY (devoir_id) REFERENCES devoirs(id)
);

DROP TABLE IF EXISTS devoir_pj;
CREATE TABLE devoir_pj (
    devoir_id INTEGER,
    pj_id INTEGER,
    FOREIGN KEY (devoir_id) REFERENCES devoirs(id),
    FOREIGN KEY (pj_id)     REFERENCES pj(id)
);

DROP TABLE IF EXISTS devoir_classe;
CREATE TABLE devoir_classe (
    devoir_id INTEGER,
    classe_id INTEGER,
    FOREIGN KEY (devoir_id) REFERENCES devoirs(id),
    FOREIGN KEY (classe_id) REFERENCES classes(id)
);

DROP TABLE IF EXISTS enseignant;
CREATE TABLE enseignant (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    mail TEXT NOT NULL,
    pwd TEXT NOT NULL
);

DROP TABLE IF EXISTS matiere;
CREATE TABLE matiere (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL
);

DROP TABLE IF EXISTS matiere_enseignant;
CREATE TABLE matiere_enseignant (
    enseignant_id INTEGER,
    matiere_id INTEGER,
    FOREIGN KEY (enseignant_id) REFERENCES enseignant(id),
    FOREIGN KEY (matiere_id) REFERENCES matiere(id)
);

INSERT INTO matiere (nom) VALUES ('prog'), ('algo'),('db'),('anglais');
