"""Vue de l'espace 'Lire sur place'."""
from app.views import affichage as aff


def menu_lecture():
    """Affiche le menu de lecture sur place et renvoie le choix."""
    return aff.afficher_menu("LIRE SUR PLACE", [
        ("1", "Afficher les livres disponibles"),
        ("2", "Rechercher un livre"),
        ("3", "Voir la disponibilité d'un livre"),
        ("4", "Consulter un livre"),
        ("5", "Rendre le livre consulté"),
        ("0", "Retour"),
    ])


def afficher_disponibilite(livre, exemplaires):
    """Affiche la liste des exemplaires d'un livre avec leur statut."""
    aff.afficher_titre("DISPONIBILITÉ : " + aff.couper(livre["titre"], 50))
    lignes = [[e["code"], e["statut"], e["etat"]] for e in exemplaires]
    aff.afficher_tableau(["Code", "Statut", "État"], lignes)
    print()
    aff.afficher_info(str(livre["nb_disponibles"]) + " exemplaire(s) disponible(s) sur "
                      + str(livre["nb_total"]) + ".")


def afficher_consultation(exemplaire):
    """Indique au lecteur l'exemplaire qui lui est remis."""
    aff.afficher_ok("Vous pouvez lire « " + exemplaire["titre"] + " » sur place.")
    aff.afficher_info("Code de l'exemplaire : " + exemplaire["code"]
                      + " (à saisir pour le rendre, option 5).")
    
