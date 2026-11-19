"""Vue de l'espace lecteur (emprunts, prolongations, réservations)."""
from datetime import date

from app.views import affichage as aff


def menu_lecteur(adherent):
    """Affiche le menu du lecteur identifié et renvoie le choix."""
    titre = ("ESPACE LECTEUR : " + adherent["prenom"] + " " + adherent["nom"]
             + " (" + adherent["numero_carte"] + ")")
    return aff.afficher_menu(titre, [
        ("1", "Afficher les livres disponibles"),
        ("2", "Rechercher un livre"),
        ("3", "Emprunter un livre"),
        ("4", "Prolonger un emprunt"),
        ("5", "Réserver un livre indisponible"),
        ("6", "Voir mes emprunts, mes réservations et mes amendes"),
        ("0", "Retour"),
    ])


def choisir_mode_emprunt():
    """Demande comment le lecteur veut choisir son livre."""
    return aff.afficher_menu("EMPRUNTER UN LIVRE", [
        ("1", "Rechercher le livre (un exemplaire me sera attribué)"),
        ("2", "Saisir directement le code d'un exemplaire"),
        ("0", "Annuler"),
    ])


def afficher_emprunts(emprunts):
    """Affiche une liste d'emprunts en cours."""
    aujourdhui = date.today().isoformat()
    lignes = []
    for e in emprunts:
        situation = "En retard" if e["date_retour_prevue"] < aujourdhui else "En cours"
        lignes.append([
            e["id"], e["titre"], e["code"], aff.formater_date(e["date_sortie"]),
            aff.formater_date(e["date_retour_prevue"]), e["nb_prolongations"], situation,
        ])
    aff.afficher_tableau(
        ["ID", "Livre", "Exemplaire", "Sortie", "Retour prévu", "Prolong.", "Situation"], lignes
    )


def afficher_reservations(reservations):
    """Affiche les réservations d'un adhérent."""
    lignes = []
    for r in reservations:
        lignes.append([r["id"], r["titre"], aff.formater_date(r["date_reservation"]),
                       r["statut"], r["code_exemplaire"]])
    aff.afficher_tableau(["ID", "Livre", "Date", "Statut", "Exemplaire"], lignes)


def afficher_amendes(amendes):
    """Affiche les amendes d'un adhérent."""
    lignes = []
    for a in amendes:
        etat = "Payée le " + aff.formater_date(a["date_paiement"]) if a["payee"] else "Impayée"
        lignes.append([a["id"], a["type"], a["titre"], aff.formater_prix(a["montant"]),
                       aff.formater_date(a["date_creation"]), etat])
    aff.afficher_tableau(["ID", "Type", "Livre", "Montant", "Date", "Paiement"], lignes)


def afficher_mon_compte(adherent, emprunts, reservations, amendes, total_impaye):
    """Affiche le récapitulatif complet du compte d'un lecteur."""
    aff.afficher_titre("MON COMPTE")
    aff.afficher_champs([
        ("Numéro de carte", adherent["numero_carte"]),
        ("Nom", adherent["prenom"] + " " + adherent["nom"]),
        ("Statut", adherent["statut"]),
    ])
    print("\nMes emprunts en cours :")
    aff.afficher_ligne()
    afficher_emprunts(emprunts)
    print("\nMes réservations :")
    aff.afficher_ligne()
    afficher_reservations(reservations)
    print("\nMes amendes :")
    aff.afficher_ligne()
    afficher_amendes(amendes)
    print()
    aff.afficher_info("Total des amendes impayées : " + aff.formater_prix(total_impaye))
