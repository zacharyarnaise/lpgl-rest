""" LPGL - IUT Metz
Zachary Arnaise
"""

import json
import os
import pickle
from threading import Lock

import falcon
from dicttoxml import dicttoxml
from waitress import serve

from Utils import *


class User(object):
    """Représente un utilisateur."""

    def __init__(self, dataDict):
        self.name = ""
        self.address = ""
        self.email = ""
        self.job = ""
        self.favoriteColour = ""
        for k, v in dataDict.items():
            if hasattr(self, k):
                setattr(self, k, v)


# C'est sale mais dans le cadre de cet exercice c'est suffsiant.
# Une solution bien plus propre pour le projet serait d'utiliser un SGBD et un ORM (SQLite et SQLAlchemy par ex.).
USERS_LIST = None
USERS_LIST_LOCK = Lock()


class UtilisateursCollection(object):
    def __init__(self):
        global USERS_LIST
        USERS_LIST_LOCK.acquire()
        if not USERS_LIST:
            open("./users.pkl", "a")
            try:
                USERS_LIST = pickle.load(open("./users.pkl", "rb"))
            except EOFError:
                USERS_LIST = list()
        USERS_LIST_LOCK.release()

    def on_post(self, req, resp):
        global USERS_LIST
        try:
            data = json.load(req.stream)
        except json.decoder.JSONDecodeError:
            resp.status = falcon.HTTP_400
            return

        USERS_LIST_LOCK.acquire()
        USERS_LIST.append(User(data))
        pickle.dump(USERS_LIST, open("./users.pkl", "wb"))
        USERS_LIST_LOCK.release()
        resp.status = falcon.HTTP_200


class UtilisateurResource(object):
    def __init__(self):
        global USERS_LIST
        USERS_LIST_LOCK.acquire()
        if not USERS_LIST:
            open("./users.pkl", "a")
            try:
                USERS_LIST = pickle.load(open("./users.pkl", "rb"))
            except EOFError:
                USERS_LIST = list()
        USERS_LIST_LOCK.release()

    def on_get(self, req, resp, id):
        global USERS_LIST
        # Détermination du Content-Type et Content-Language à utiliser
        accept = req.get_header("Accept")
        contentType = Utils.getAdequateContentType(
            accept, ["application/json", "application/xml"]
        )
        acceptLanguage = req.get_header("Accept-Language")
        contentLanguage = Utils.getAdequateLanguage(acceptLanguage, ["fr-FR", "en-US"])

        # Content-Type et/ou Content-Language non supportés, l'app retourne un code 406 (Not Acceptable)
        if contentType is None or contentLanguage is None:
            resp.status = falcon.HTTP_406
            return

        wantedUser = None
        USERS_LIST_LOCK.acquire()
        for i, user in enumerate(USERS_LIST):
            if id == i:
                wantedUser = user
                break
        USERS_LIST_LOCK.release()

        if not wantedUser:
            # Pas d'utilisateur avec l'id donné trouvé
            body = {"error": "No user matches the given ID"}
            resp.body = (
                dicttoxml(body, root=False)
                if contentType == "application/xml"
                else json.dumps(body)
            )
            resp.content_type = contentType
            resp.status = falcon.HTTP_404
        else:
            resp.body = (
                dicttoxml(wantedUser, custom_root="user")
                if contentType == "application/xml"
                else json.dumps(wantedUser)
            )
            resp.content_type = contentType
            resp.content_language = contentLanguage
            resp.status = falcon.HTTP_200


app = falcon.API()
utilisateursCollection = UtilisateursCollection()
app.add_route("/api/utilisateurs", utilisateursCollection)
utilisateur = UtilisateurResource()
app.add_route("/api/utilisateurs/{id}", utilisateur)
