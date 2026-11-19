"""Connexion à la base SQLite et petites fonctions d'exécution de requêtes."""
import os
import sqlite3
import unicodedata

from config import CHEMIN_BASE, DOSSIER_DATA


def normaliser(texte):
    """Met le texte en minuscules et retire les accents
    (ex. : "Climbié" -> "climbie"), pour des recherches insensibles
    à la casse et aux accents."""
    if texte is None:
        return None
    decompose = unicodedata.normalize("NFD", str(texte))
    sans_accents = "".join(c for c in decompose if unicodedata.category(c) != "Mn")
    return sans_accents.casefold()


def obtenir_connexion():
    """Ouvre et renvoie une connexion à la base de données.

    Le dossier data/ est créé s'il n'existe pas encore.
    """
    os.makedirs(DOSSIER_DATA, exist_ok=True)
    connexion = sqlite3.connect(CHEMIN_BASE)
    connexion.row_factory = sqlite3.Row  # accès aux colonnes par leur nom
    connexion.execute("PRAGMA foreign_keys = ON")
    # Fonction utilisable dans les requêtes SQL : NORMALISER(colonne)
    connexion.create_function("NORMALISER", 1, normaliser, deterministic=True)
    return connexion


def executer(requete, parametres=()):
    """Exécute une requête qui modifie la base, fait le commit
    et renvoie l'identifiant de la ligne insérée (s'il y en a une)."""
    connexion = obtenir_connexion()
    try:
        curseur = connexion.execute(requete, parametres)
        connexion.commit()
        return curseur.lastrowid
    finally:
        connexion.close()


def lire_un(requete, parametres=()):
    """Exécute une requête SELECT et renvoie la première ligne (ou None)."""
    connexion = obtenir_connexion()
    try:
        return connexion.execute(requete, parametres).fetchone()
    finally:
        connexion.close()


def lire_tous(requete, parametres=()):
    """Exécute une requête SELECT et renvoie la liste de toutes les lignes."""
    connexion = obtenir_connexion()
    try:
        return connexion.execute(requete, parametres).fetchall()
    finally:
        connexion.close()
