""" LPGL - IUT Metz
Zachary Arnaise
"""


class Utils:
    """
    Classe d'utilitaires utilisés pour cet exercice.
    """

    def _parseAndOrder(content: str) -> list:
        """
        Parse le contenu d'un header `Accept` ou `Accept-Language` et retourne
        une list avec les valeurs ordonnées selon leur valeur de qualité (`q=`).

        Args:
            content (str): Contenu d'un header `Accept` ou `Accept-Language` à parser.
        Returns:
            list: List avec les valeurs ordonnées selon leur valeur de qualité extraites du header.
        """
        if content is None:
            return list()

        pairs = content.split(",")
        valuesWithQ = {}
        for pair in pairs:
            pair = pair.strip()
            if pair.split(";")[0] == pair:
                # pas de qualité affectée, donc défaut à 1.0
                valuesWithQ[pair] = float(1.0)
            else:
                value, q = pair.split(";")
                q = q.split("=")[1]
                valuesWithQ[value] = float(q)

        # Tri en fonction de la valeur de qualitée, en ordre décroissant
        result = {
            k: v
            for k, v in sorted(
                valuesWithQ.items(), key=lambda item: item[1], reverse=True
            )
        }
        return list(result.keys())

    def getAdequateContentType(accept: str, contentTypes: list) -> str:
        """
        Détermine le Content-Type à utiliser en fonction de la valeur de l'header Accept.

        Args:
            accept (str): Contenu d'un header `Accept`.
            contentTypes (list): List de `Content-Type`.
        Returns:
            str: Valeur `Content-Type` préférée ou `None` si aucune correspondance.

        Examples:
            >>> getPreferredContentType("text/html,application/xml;q=0.9,*/*;q=0.8", ["application/json", "application/xml"])
            "application/xml"
        """
        acceptOrderedByQuality = Utils._parseAndOrder(accept)
        if not acceptOrderedByQuality:
            return None

        # Recherche d'une correspondance exacte
        for _accept in acceptOrderedByQuality:
            if _accept in contentTypes:
                return _accept

        # Recherche d'une correspondance avec un wildcard pour le sous-type MIME tel que:
        # image/*, */*, ...
        acceptWildCard = [
            mime for mime in acceptOrderedByQuality if "/*" in mime
        ]  # MIME acceptés avec un wildcard
        mimeContentTypes = [
            contentType.split("/")[0] for contentType in contentTypes
        ]  # Extrait le type MIME de contentTypes
        for mime in acceptWildCard:
            # Wildcard */*, on renvoie le 1er Content-Type de la liste
            if mime == "*/*":
                return contentTypes[0]
            else:
                try:
                    idx = mimeContentTypes.index(mime)
                    return contentTypes[idx]
                except ValueError:
                    pass

        # Aucune correspondance
        return None

    def getAdequateLanguage(acceptLanguage: str, contentLanguages: list) -> str:
        """
        Détermine le Content-Language à utiliser en fonction de la valeur de l'header Accept-Language.

        Args:
            acceptLanguage (str): Contenu d'un header `Accept-Language`.
            contentLanguages (list): List de `Content-Language`.
        Returns:
            str: Valeur `Content-Language` préférée ou `None` si aucune correspondance.

        Examples:
            >>> getAdequateLanguage("fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5", ["fr-FR", "en-US"])
            "fr-FR"
        """
        acceptLanguageOrderedByQuality = Utils._parseAndOrder(acceptLanguage)
        if not acceptLanguageOrderedByQuality:
            return None

        # Recherche d'une correspondance
        for _acceptLanguage in acceptLanguageOrderedByQuality:
            # Correspondance exacte
            if _acceptLanguage in contentLanguages:
                return _acceptLanguage
            else:
                # Correspondance avec le langage principal
                for contentLanguage in contentLanguages:
                    primaryLanguage = contentLanguage.split("-")[0]
                    if _acceptLanguage == primaryLanguage:
                        return contentLanguage

        # Retourne le 1er Content-Language si le wildcard est présent
        if "*" in acceptLanguage:
            return contentLanguages[0]

        # Aucune correspondance
        return None
