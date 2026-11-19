"""Contrôleur d'authentification du bibliothécaire."""
import hashlib
import secrets

from app.models.bibliothecaire import Bibliothecaire
from app.views import affichage as aff
from app.views import vue_bibliothecaire as vue

NB_TENTATIVES_MAX = 3
LONGUEUR_MIN_MOT_DE_PASSE = 4


def hacher_mot_de_passe(mot_de_passe, sel):
    """Renvoie l'empreinte SHA-256 du mot de passe précédé du sel."""
    return hashlib.sha256((sel + mot_de_passe).encode("utf-8")).hexdigest()


def mot_de_passe_correct(compte, mot_de_passe):
    """Compare le mot de passe saisi avec l'empreinte enregistrée."""
    return hacher_mot_de_passe(mot_de_passe, compte["sel"]) == compte["mot_de_passe_hash"]


def saisir_nouveau_mot_de_passe():
    """Demande un nouveau mot de passe et sa confirmation."""
    while True:
        mot_de_passe = aff.saisir_mot_de_passe("Mot de passe : ")
        if len(mot_de_passe) < LONGUEUR_MIN_MOT_DE_PASSE:
            aff.afficher_erreur("Le mot de passe doit contenir au moins "
                                + str(LONGUEUR_MIN_MOT_DE_PASSE) + " caractères.")
            continue
        confirmation = aff.saisir_mot_de_passe("Confirmez le mot de passe : ")
        if mot_de_passe != confirmation:
            aff.afficher_erreur("Les deux mots de passe ne correspondent pas. Recommencez.")
            continue
        return mot_de_passe


def enregistrer_mot_de_passe(mot_de_passe):
    """Génère un sel aléatoire et renvoie le couple (empreinte, sel)."""
    sel = secrets.token_hex(16)
    return hacher_mot_de_passe(mot_de_passe, sel), sel


def verifier_compte_bibliothecaire():
    """Au premier lancement, demande la création du compte bibliothécaire."""
    if Bibliothecaire.chercher() is not None:
        return
    vue.afficher_creation_compte()
    identifiant = aff.saisir_texte_obligatoire("Identifiant : ")
    mot_de_passe = saisir_nouveau_mot_de_passe()
    empreinte, sel = enregistrer_mot_de_passe(mot_de_passe)
    Bibliothecaire.ajouter(identifiant, empreinte, sel)
    aff.afficher_ok("Compte bibliothécaire créé. Conservez bien votre mot de passe.")


def connecter():
    """Demande identifiant et mot de passe (3 tentatives maximum).

    Renvoie True si la connexion réussit, False sinon.
    """
    aff.afficher_titre("CONNEXION BIBLIOTHÉCAIRE")
    for tentative in range(1, NB_TENTATIVES_MAX + 1):
        identifiant = aff.saisir_texte_obligatoire("Identifiant : ")
        mot_de_passe = aff.saisir_mot_de_passe("Mot de passe : ")
        compte = Bibliothecaire.chercher_par_identifiant(identifiant)
        if compte is not None and mot_de_passe_correct(compte, mot_de_passe):
            aff.afficher_ok("Connexion réussie. Bienvenue " + identifiant + ".")
            return True

        aff.afficher_erreur("Identifiant ou mot de passe incorrect.")
        restantes = NB_TENTATIVES_MAX - tentative
        if restantes > 0:
            aff.afficher_info("Il vous reste " + str(restantes) + " tentative(s).")

    aff.afficher_erreur("Trop de tentatives échouées. Retour au menu principal.")
    aff.pause()
    return False


def changer_mot_de_passe():
    """Change le mot de passe après vérification de l'ancien."""
    compte = Bibliothecaire.chercher()
    actuel = aff.saisir_mot_de_passe("Mot de passe actuel : ")
    if not mot_de_passe_correct(compte, actuel):
        aff.afficher_erreur("Mot de passe actuel incorrect.")
        return
    aff.afficher_info("Choisissez le nouveau mot de passe.")
    nouveau = saisir_nouveau_mot_de_passe()
    empreinte, sel = enregistrer_mot_de_passe(nouveau)
    Bibliothecaire.modifier_mot_de_passe(compte["id"], empreinte, sel)
    aff.afficher_ok("Mot de passe modifié.")


def changer_identifiant():
    """Change l'identifiant de connexion après vérification du mot de passe."""
    compte = Bibliothecaire.chercher()
    aff.afficher_info("Identifiant actuel : " + compte["identifiant"])
    mot_de_passe = aff.saisir_mot_de_passe("Mot de passe actuel : ")
    if not mot_de_passe_correct(compte, mot_de_passe):
        aff.afficher_erreur("Mot de passe incorrect.")
        return
    nouveau = aff.saisir_texte_obligatoire("Nouvel identifiant : ")
    if nouveau == compte["identifiant"]:
        aff.afficher_info("C'est déjà votre identifiant : rien n'a été modifié.")
        return
    if not aff.confirmer("Remplacer « " + compte["identifiant"] + " » par « " + nouveau + " » ?"):
        aff.afficher_info("Modification annulée.")
        return
    Bibliothecaire.modifier_identifiant(compte["id"], nouveau)
    aff.afficher_ok("Identifiant modifié. Utilisez « " + nouveau + " » à la prochaine connexion.")
