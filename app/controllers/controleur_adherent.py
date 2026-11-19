"""Contrôleur des adhérents."""
from datetime import date

from app.models.adherent import Adherent
from app.views import affichage as aff
from app.views import vue_bibliothecaire as vue


def menu_adherents():
    """Boucle du menu 'Gestion des adhérents'."""
    actions = {
        "1": inscrire_adherent,
        "2": modifier_adherent,
        "3": rechercher_adherent,
        "4": lister_adherents,
        "5": bloquer_debloquer,
    }
    while True:
        choix = vue.menu_adherents()
        if choix == "0":
            return
        actions[choix]()
        aff.pause()


def normaliser_numero_carte(texte):
    """Accepte 'ad-0001', 'AD-0001' ou simplement '1' et renvoie 'AD-0001'."""
    texte = texte.strip().upper()
    if texte.isdigit():
        return "AD-" + texte.zfill(4)
    return texte


def inscrire_adherent():
    """Inscrit un nouvel adhérent et affiche son numéro de carte."""
    aff.afficher_titre("INSCRIPTION D'UN ADHÉRENT")
    nom = aff.saisir_texte_obligatoire("Nom : ").upper()
    prenom = aff.saisir_texte_obligatoire("Prénom : ")
    telephone = aff.saisir_telephone("Téléphone : ")
    email = aff.saisir_email("Email (optionnel, Entrée pour ignorer) : ", None)

    aff.afficher_ligne()
    aff.afficher_champs([("Nom", nom), ("Prénom", prenom),
                         ("Téléphone", telephone), ("Email", email)])
    if not aff.confirmer("Confirmer l'inscription ?"):
        aff.afficher_info("Inscription annulée.")
        return

    numero = Adherent.ajouter(nom, prenom, telephone, email, date.today().isoformat())
    aff.afficher_ok("Adhérent inscrit. Numéro de carte : " + numero)
    aff.afficher_info("Remettez ce numéro au lecteur : il lui servira pour emprunter.")


def choisir_adherent():
    """Recherche un adhérent (carte ou nom) et renvoie celui choisi, ou None."""
    texte = aff.saisir_texte_obligatoire("Numéro de carte ou nom de l'adhérent : ")
    adherent = Adherent.chercher_par_numero(normaliser_numero_carte(texte))
    if adherent is not None:
        return adherent

    resultats = Adherent.rechercher(texte)
    vue.afficher_adherents(resultats)
    if not resultats:
        return None
    return aff.choisir_par_id(resultats, "ID de l'adhérent (0 pour annuler) : ")


def modifier_adherent():
    """Modifie les coordonnées d'un adhérent (Entrée = garder la valeur)."""
    adherent = choisir_adherent()
    if adherent is None:
        return
    vue.afficher_adherent(adherent)
    aff.afficher_info("Appuyez sur Entrée pour garder la valeur entre crochets.")

    nom = aff.saisir_texte_optionnel("Nom [" + adherent["nom"] + "] : ", adherent["nom"]).upper()
    prenom = aff.saisir_texte_optionnel("Prénom [" + adherent["prenom"] + "] : ",
                                        adherent["prenom"])
    telephone = aff.saisir_telephone("Téléphone [" + adherent["telephone"] + "] : ",
                                     adherent["telephone"])
    email = aff.saisir_email("Email [" + aff.formater_valeur(adherent["email"]) + "] : ",
                             adherent["email"])

    if aff.confirmer("Enregistrer les modifications ?"):
        Adherent.modifier(adherent["id"], nom, prenom, telephone, email)
        aff.afficher_ok("Adhérent modifié.")
    else:
        aff.afficher_info("Modification annulée.")


def rechercher_adherent():
    """Recherche un adhérent et affiche sa fiche."""
    adherent = choisir_adherent()
    if adherent is not None:
        vue.afficher_adherent(adherent)


def lister_adherents():
    """Affiche tous les adhérents."""
    aff.afficher_titre("LISTE DES ADHÉRENTS")
    vue.afficher_adherents(Adherent.lister())


def bloquer_debloquer():
    """Bloque un adhérent actif ou débloque un adhérent bloqué."""
    adherent = choisir_adherent()
    if adherent is None:
        return
    vue.afficher_adherent(adherent)

    if adherent["statut"] == "actif":
        nouveau_statut, action = "bloque", "Bloquer"
    else:
        nouveau_statut, action = "actif", "Débloquer"

    if aff.confirmer(action + " cet adhérent ?"):
        Adherent.changer_statut(adherent["id"], nouveau_statut)
        aff.afficher_ok("Statut de l'adhérent : " + nouveau_statut + ".")
    else:
        aff.afficher_info("Aucun changement.")
