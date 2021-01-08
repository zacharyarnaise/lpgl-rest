""" LPGL - IUT Metz
Zachary Arnaise
"""

import json
import os
import pickle

import falcon
from dicttoxml import dicttoxml
from waitress import serve

from Utils import *


class User(object):
    """Représente un utilisateur."""

    def __init__(
        self, name: str, address: str, email: str, job: str, favoriteColour: str
    ):
        self.name = name
        self.address = address
        self.email = email
        self.job = job
        self.favoriteColour = favoriteColour


class UtilisateursResource(object):
    def __init__(self):
        open("./users.pkl", "a")
        try:
            self.usersList = pickle.load(open("./users.pkl", "rb"))
        except EOFError:
            self.usersList = list()

    def __del__(self):
        pickle.dump(self.usersList, open("./users.pkl", "wb"))

    def on_get(self, req, resp, id):
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
        for i, user in enumerate(self.usersList):
            if id == i:
                wantedUser = user
                break

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


def app():
    app = falcon.API()
    utilisateurs = UtilisateursResource()
    app.add_route("/api/utilisateurs/{id}", utilisateurs)
