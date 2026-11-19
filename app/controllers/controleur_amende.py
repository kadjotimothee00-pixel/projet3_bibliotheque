"""Contrôleur des amendes."""
from datetime import date

from app.controllers.controleur_adherent import choisir_adherent
from app.models.amende import Amende
from app.views import affichage as aff
from app.views import vue_bibliothecaire as vue


def menu_amendes():
    """Boucle du menu 'Amendes'."""
    actions = {
        "1": lister_impayees,
        "2": encaisser_amende,
        "3": historique_adherent,
    }
    while True:
        choix = vue.menu_amendes()
        if choix == "0":
            return
        actions[choix]()
        aff.pause()


def total_montants(amendes):
    """Additionne le montant d'une liste d'amendes."""
    total = 0
    for amende in amendes:
        total += amende["montant"]
    return total


def lister_impayees():
    """Affiche toutes les amendes impayées et leur total. Renvoie la liste."""
    aff.afficher_titre("AMENDES IMPAYÉES")
    amendes = Amende.lister_impayees()
    vue.afficher_amendes(amendes)
    if amendes:
        aff.afficher_info("Total impayé : " + aff.formater_prix(total_montants(amendes)))
    return amendes


def encaisser_amende():
    """Marque une amende comme payée."""
    amendes = lister_impayees()
    if not amendes:
        return
    amende = aff.choisir_par_id(amendes, "ID de l'amende à encaisser (0 pour annuler) : ")
    if amende is None:
        return
    question = ("Encaisser " + aff.formater_prix(amende["montant"]) + " auprès de "
                + amende["prenom"] + " " + amende["nom"] + " ?")
    if not aff.confirmer(question):
        aff.afficher_info("Encaissement annulé.")
        return
    Amende.encaisser(amende["id"], date.today().isoformat())
    aff.afficher_ok("Amende encaissée.")


def historique_adherent():
    """Affiche toutes les amendes d'un adhérent."""
    adherent = choisir_adherent()
    if adherent is None:
        return
    aff.afficher_titre("AMENDES DE " + adherent["prenom"] + " " + adherent["nom"]
                       + " (" + adherent["numero_carte"] + ")")
    amendes = Amende.lister_par_adherent(adherent["id"])
    vue.afficher_amendes(amendes)
    if amendes:
        payees = [a for a in amendes if a["payee"]]
        impayees = [a for a in amendes if not a["payee"]]
        aff.afficher_info("Payé : " + aff.formater_prix(total_montants(payees))
                          + "  /  Impayé : " + aff.formater_prix(total_montants(impayees)))
