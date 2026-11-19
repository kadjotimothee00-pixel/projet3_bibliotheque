"""Point d'entrée de l'application de gestion de bibliothèque.

Lancement : python main.py
"""
import sqlite3

from app.controllers import controleur_auth, controleur_principal
from database.donnees_initiales import inserer_donnees_initiales
from database.schema import creer_tables
from app.views import affichage as aff


def initialiser_base():
    """Crée les tables et insère les données de départ si besoin."""
    creer_tables()
    inserer_donnees_initiales()


def main():
    """Initialise la base puis lance le menu principal."""
    try:
        initialiser_base()
        controleur_auth.verifier_compte_bibliothecaire()
        controleur_principal.lancer()
    except (KeyboardInterrupt, EOFError):
        print()
        aff.afficher_info("Fermeture du programme demandée. Au revoir.")
    except sqlite3.Error as erreur:
        aff.afficher_erreur("Impossible d'utiliser la base de données : " + str(erreur))


if __name__ == "__main__":
    main()
