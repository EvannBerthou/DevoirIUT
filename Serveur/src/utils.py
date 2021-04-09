import json, sqlite3
from typing import *
from werkzeug.wrappers import Response

Str_response = str
Str_code = Tuple[str, int]
Str_or_Response = Tuple[Union[str, Response], int]
Response_code = Tuple[Response, int]

def safe_name(name: str) -> str:
    keep = (' ','.','_')
    return "".join(c for c in name if c.isalnum() or c in keep).rstrip()

# Reécriture du jsonify de Flask afin d'avoir Response en type
def jsonify(*args: Any, **kwargs: Any) -> Response:
    if args and kwargs:
        raise TypeError("jsonify() behavior undefined when passed both args and kwargs")
    elif len(args) == 1:  # single args are passed directly to dumps()
        data = args[0]
    else:
        data = args or kwargs
    data = f"{json.dumps(data)}\n"
    return Response(data, mimetype='application/json')

def devoir_classe(classe: str) -> List[str]:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    return c.execute("""
        SELECT * FROM (
            SELECT
                devoirs.id as did, enonce, matiere, prof, jour, null, null,
                REPLACE(REPLACE(a_rendre, 0, 'Non'), 1, 'Oui')
            FROM
                devoirs
            WHERE
                devoirs.id NOT IN (SELECT devoir_id FROM devoir_pj)
            UNION
            SELECT
                devoirs.id as did, enonce, matiere, prof, jour, pj.id, pj.nom,
                REPLACE(REPLACE(a_rendre, 0, 'Non'), 1, 'Oui')
            FROM
                devoirs, pj, devoir_pj
            WHERE
                devoir_pj.devoir_id = devoirs.id AND devoir_pj.pj_id = pj.id
        )
        WHERE (
            did IN (SELECT devoir_id FROM devoir_classe, classes WHERE classe_id = classes.id AND classes.nom = ?)
            AND jour >= DATE('now')
        );
    """,
    [classe]).fetchall()

def devoir_enseignant(username: str) -> List[str]:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    return c.execute("""
        SELECT *
        FROM (
            SELECT
                devoirs.id as did, enonce, matiere, prof, jour, null, null,
                REPLACE(REPLACE(a_rendre, 0, 'Non'), 1, 'Oui')
            FROM
                devoirs
            WHERE
                devoirs.id NOT IN (SELECT devoir_id FROM devoir_pj)
            UNION
            SELECT
                devoirs.id as did, enonce, matiere, prof, jour, pj.id, pj.nom,
                REPLACE(REPLACE(a_rendre, 0, 'Non'), 1, 'Oui')
            FROM
                devoirs, pj, devoir_pj
            WHERE
                devoir_pj.devoir_id = devoirs.id AND devoir_pj.pj_id = pj.id
       )
       WHERE prof = ?;
    """,
    [username]).fetchall()

def get_class(id_devoir: int) -> List[str]:
    db = sqlite3.connect('src/devoirs.db')
    c = db.cursor()
    return c.execute("""
        SELECT nom
        FROM classes
        WHERE id IN (SELECT classe_id
                     FROM devoir_classe
                     WHERE devoir_id=? );
        """,
        [id_devoir]).fetchall()

# Fusionne les colonnes afin d'avoir les pièces jointes dans une liste
def merge_pj(devoirs: List, prof: bool = False) -> List:
    parsed = {}
    for row in devoirs:
        devoir_id = row[0]
        if not devoir_id in parsed: # Si c'est la première fois qu'on rencontre un devoir avec cet id
            parsed[devoir_id] = list(row[0:5]) + [[]] + list(row[7:]) + [[classe[0] for classe in get_class(devoir_id) if prof]]
        # S'il y a une pièce jointe
        if row[5]:
            parsed[devoir_id][5].append((str(row[5]), row[6]))
    return list(parsed.values())
