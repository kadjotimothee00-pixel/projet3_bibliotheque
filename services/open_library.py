"""Appel à l'API Open Library pour retrouver un livre à partir de son ISBN.

Ce module ne touche ni à la base de données ni à l'affichage.

Exemple d'appel :
    https://openlibrary.org/api/books?bibkeys=ISBN:9782070360024&format=json&jscmd=data

Exemple de réponse (simplifiée) :
    {"ISBN:9782070360024": {"title": "L'étranger",
                            "authors": [{"name": "Albert Camus"}],
                            "publishers": [{"name": "Gallimard"}],
                            "publish_date": "1972"}}
Si l'ISBN est inconnu, la réponse est un dictionnaire vide : {}
"""
from config import TIMEOUT_RESEAU, URL_OPEN_LIBRARY

try:
    import requests
except ImportError:  # la bibliothèque n'est pas installée
    requests = None


def extraire_annee(date_publication):
    """Cherche une année (4 chiffres) dans un texte comme 'June 1, 1942'
    ou '07-01-1972'.

    Renvoie l'année sous forme d'entier, ou None si aucune n'est trouvée.
    """
    # On remplace tout ce qui n'est pas un chiffre par un espace,
    # puis on cherche un groupe de 4 chiffres.
    texte = ""
    for caractere in date_publication:
        texte += caractere if caractere.isdigit() else " "
    for mot in texte.split():
        if len(mot) == 4:
            return int(mot)
    return None


def extraire_infos(livre):
    """Transforme la fiche renvoyée par Open Library en un dictionnaire simple."""
    noms_auteurs = [auteur.get("name", "") for auteur in livre.get("authors", [])]
    editeurs = [editeur.get("name", "") for editeur in livre.get("publishers", [])]

    return {
        "titre": livre.get("title") or "",
        "auteur": ", ".join(noms_auteurs),
        "editeur": editeurs[0] if editeurs else "",
        "annee": extraire_annee(livre.get("publish_date") or ""),
    }


def rechercher_par_isbn(isbn):
    """Interroge Open Library avec un ISBN.

    Renvoie un couple (infos, message_erreur) :
    - en cas de succès : (dictionnaire du livre, None)
    - en cas d'échec   : (None, message expliquant le problème)
    """
    if requests is None:
        return None, "La bibliothèque 'requests' n'est pas installée (pip install -r requirements.txt)."

    cle = "ISBN:" + isbn
    parametres = {"bibkeys": cle, "format": "json", "jscmd": "data"}

    try:
        reponse = requests.get(URL_OPEN_LIBRARY, params=parametres, timeout=TIMEOUT_RESEAU)
    except requests.exceptions.Timeout:
        return None, "Le serveur Open Library n'a pas répondu à temps (délai dépassé)."
    except requests.exceptions.ConnectionError:
        return None, "Impossible de joindre Open Library (pas de connexion internet ?)."
    except requests.exceptions.RequestException:
        return None, "Erreur réseau lors de l'appel à Open Library."

    if reponse.status_code == 429:
        return None, "Trop de demandes envoyées à Open Library. Réessayez plus tard."
    if reponse.status_code != 200:
        return None, "Open Library a renvoyé une erreur (code " + str(reponse.status_code) + ")."

    try:
        donnees = reponse.json()
    except ValueError:
        return None, "La réponse d'Open Library est illisible (JSON invalide)."

    if cle not in donnees:
        return None, "ISBN introuvable sur Open Library."

    return extraire_infos(donnees[cle]), None
