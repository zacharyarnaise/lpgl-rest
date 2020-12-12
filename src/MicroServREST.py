""" TD REST - 12/12/2020
Zachary Arnaise
"""

import json

import falcon
from dicttoxml import dicttoxml
from faker import Faker
from waitress import serve

from Utils import *


class UtilisateursResource(object):
    def __init__(self):
        self.faker_en = Faker("en_US")
        self.faker_fr = Faker("fr_FR")

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

        # Génération de data bidon en fonction du langage voulu par le client
        faker = self.faker_en if contentLanguage == "en-US" else self.faker_fr
        fooUser = {
            "id": int(id),
            "name": faker.name(),
            "address": faker.address(),
            "email": faker.ascii_free_email(),
            "job": faker.job(),
            "favoriteColour": faker.color_name(),
        }

        # Données en JSON ou XML selon le Content-Type
        resp.body = (
            dicttoxml(fooUser, custom_root="user")
            if contentType == "application/xml"
            else json.dumps(fooUser)
        )
        resp.content_type = contentType
        resp.content_language = contentLanguage
        resp.status = falcon.HTTP_200


app = falcon.API()
utilisateurs = UtilisateursResource()
app.add_route("/api/utilisateurs/{id}", utilisateurs)
