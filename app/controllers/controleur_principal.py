"""Contrôleur principal : menu d'accueil et menu du bibliothécaire."""
import sqlite3
from datetime import date

from app.controllers import (controleur_adherent, controleur_amende, controleur_auth,
                         controleur_emprunt, controleur_lecture, controleur_livre,
                         controleur_parametre)
from app.models.adherent import Adherent
from app.models.amende import Amende
from app.models.categorie import Categorie
from app.models.emprunt import Emprunt
from app.models.exemplaire import Exemplaire
from app.models.livre import Livre
from app.views import affichage as aff
from app.views import vue_bibliothecaire, vue_principale


def lancer():
    """Boucle du menu principal (s'arrête quand l'utilisateur choisit 0)."""
    while True:
        choix = vue_principale.menu_principal()
        if choix == "0":
            aff.afficher_info("Merci d'avoir utilisé l'application. Au revoir.")
            return
        if choix == "1":
            executer_sans_planter(espace_bibliothecaire)
        elif choix == "2":
            executer_sans_planter(controleur_lecture.menu_lecture)
        elif choix == "3":
            executer_sans_planter(controleur_emprunt.menu_lecteur)


def executer_sans_planter(fonction):
    """Lance une fonction en attrapant les erreurs pour que le programme continue.

    Ctrl+C (KeyboardInterrupt) n'est pas attrapé ici : il remonte jusqu'à
    main.py qui ferme le programme proprement.
    """
    try:
        fonction()
    except sqlite3.Error as erreur:
        aff.afficher_erreur("Problème avec la base de données : " + str(erreur))
        aff.pause()
    except EOFError:
        raise
    except Exception as erreur:
        aff.afficher_erreur("Erreur inattendue : " + str(erreur))
        aff.pause()


def espace_bibliothecaire():
    """Connexion puis menu du bibliothécaire."""
    if controleur_auth.connecter():
        menu_bibliothecaire()


def menu_bibliothecaire():
    """Boucle du menu du bibliothécaire."""
    while True:
        choix = vue_bibliothecaire.menu_bibliothecaire()
        if choix == "0":
            return
        if choix == "1":
            controleur_livre.menu_livres()
        elif choix == "2":
            controleur_livre.menu_exemplaires()
        elif choix == "3":
            controleur_adherent.menu_adherents()
        elif choix == "4":
            controleur_emprunt.enregistrer_retour()
            aff.pause()
        elif choix == "5":
            controleur_emprunt.declarer_perte()
            aff.pause()
        elif choix == "6":
            controleur_amende.menu_amendes()
        elif choix == "7":
            controleur_emprunt.lister_retards()
            aff.pause()
        elif choix == "8":
            controleur_emprunt.menu_reservations()
        elif choix == "9":
            afficher_statistiques()
            aff.pause()
        elif choix == "10":
            controleur_parametre.menu_parametres()


def afficher_statistiques():
    """Rassemble les chiffres de la bibliothèque et les affiche."""
    exemplaires_par_statut = Exemplaire.compter_par_statut()
    nb_exemplaires = 0
    for ligne in exemplaires_par_statut:
        nb_exemplaires += ligne["nombre"]

    adherents_actifs = 0
    adherents_bloques = 0
    for ligne in Adherent.compter_par_statut():
        if ligne["statut"] == "actif":
            adherents_actifs = ligne["nombre"]
        else:
            adherents_bloques = ligne["nombre"]

    stats = {
        "nb_livres": Livre.compter(),
        "nb_exemplaires": nb_exemplaires,
        "exemplaires_par_statut": exemplaires_par_statut,
        "adherents_actifs": adherents_actifs,
        "adherents_bloques": adherents_bloques,
        "emprunts_en_cours": Emprunt.compter_en_cours(),
        "emprunts_retard": Emprunt.compter_retards(date.today().isoformat()),
        "amendes_impayees": Amende.total(0),
        "amendes_encaissees": Amende.total(1),
        "top_livres": Livre.top_empruntes(5),
        "par_categorie": Categorie.repartition_livres(),
    }
    vue_bibliothecaire.afficher_statistiques(stats)
