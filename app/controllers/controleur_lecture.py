"""Contrôleur de la lecture sur place (aucune identification)."""
from app.controllers import controleur_livre
from app.models.exemplaire import Exemplaire
from app.views import affichage as aff
from app.views import vue_lecture


def menu_lecture():
    """Boucle du menu 'Lire sur place'."""
    actions = {
        "1": controleur_livre.lister_livres_disponibles,
        "2": rechercher,
        "3": voir_disponibilite,
        "4": consulter_livre,
        "5": rendre_livre,
    }
    while True:
        choix = vue_lecture.menu_lecture()
        if choix == "0":
            return
        actions[choix]()
        aff.pause()


def rechercher():
    """Recherche par titre, auteur ou catégorie."""
    controleur_livre.rechercher_livres(avec_isbn=False)


def voir_disponibilite():
    """Affiche les exemplaires d'un livre et leur statut."""
    livre = controleur_livre.choisir_livre(avec_isbn=False)
    if livre is None:
        return
    vue_lecture.afficher_disponibilite(livre, Exemplaire.lister_par_livre(livre["id"]))


def consulter_livre():
    """Remet au lecteur un exemplaire disponible (statut 'en_consultation')."""
    livre = controleur_livre.choisir_livre(avec_isbn=False)
    if livre is None:
        return
    exemplaire = Exemplaire.premier_disponible(livre["id"])
    if exemplaire is None:
        aff.afficher_erreur("Aucun exemplaire de ce livre n'est disponible pour le moment.")
        return
    Exemplaire.changer_statut(exemplaire["id"], "en_consultation")
    vue_lecture.afficher_consultation(exemplaire)


def rendre_livre():
    """Le lecteur rend l'exemplaire qu'il consultait."""
    code = aff.saisir_texte_obligatoire("Code de l'exemplaire consulté (ex : EX-0001) : ").upper()
    exemplaire = Exemplaire.chercher_par_code(code)
    if exemplaire is None:
        aff.afficher_erreur("Aucun exemplaire ne porte ce code.")
        return
    if exemplaire["statut"] != "en_consultation":
        aff.afficher_erreur("Cet exemplaire n'est pas en consultation.")
        return

    reservation = controleur_livre.liberer_exemplaire(exemplaire["id"], exemplaire["livre_id"])
    aff.afficher_ok("Merci, « " + exemplaire["titre"] + " » a bien été rendu.")
    if reservation is not None:
        aff.afficher_info("Ce livre est réservé : merci de le remettre au bibliothécaire.")
