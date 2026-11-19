"""Configuration générale de l'application."""
import os

# Dossier où se trouve ce fichier (racine du projet)
DOSSIER_PROJET = os.path.dirname(os.path.abspath(__file__))

# Base de données SQLite
DOSSIER_DATA = os.path.join(DOSSIER_PROJET, "data")
CHEMIN_BASE = os.path.join(DOSSIER_DATA, "bibliotheque.db")

# API Open Library (gratuite, aucune clé nécessaire)
URL_OPEN_LIBRARY = "https://openlibrary.org/api/books"
TIMEOUT_RESEAU = 5  # en secondes
