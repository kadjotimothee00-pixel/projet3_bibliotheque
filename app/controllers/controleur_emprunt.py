"""Contrôleur des emprunts : espace lecteur, retours, pertes, retards et réservations."""
from datetime import date, timedelta

from app.controllers import controleur_livre
from app.controllers.controleur_adherent import normaliser_numero_carte
from app.controllers.controleur_parametre import lire_entier
from app.models.adherent import Adherent
from app.models.amende import Amende
from app.models.emprunt import Emprunt
from app.models.exemplaire import Exemplaire
from app.models.livre import Livre
from app.models.reservation import Reservation
from app.views import affichage as aff
from app.views import vue_bibliothecaire
from app.views import vue_emprunt


# ----------------------------------------------------------------------
# Outils sur les dates
# ----------------------------------------------------------------------

def aujourdhui():
    """Renvoie la date du jour au format AAAA-MM-JJ."""
    return date.today().isoformat()


def ajouter_jours(date_iso, nb_jours):
    """Ajoute un nombre de jours à une date AAAA-MM-JJ."""
    return (date.fromisoformat(date_iso) + timedelta(days=nb_jours)).isoformat()


def jours_de_retard(date_retour_prevue):
    """Renvoie le nombre de jours de retard (0 si pas de retard)."""
    ecart = (date.today() - date.fromisoformat(date_retour_prevue)).days
    return max(ecart, 0)


# ----------------------------------------------------------------------
# Espace lecteur
# ----------------------------------------------------------------------

def menu_lecteur():
    """Identifie le lecteur par sa carte puis affiche son menu."""
    aff.afficher_titre("EMPRUNTER")
    texte = aff.saisir_texte_obligatoire("Votre numéro de carte (ex : AD-0001) : ")
    adherent = Adherent.chercher_par_numero(normaliser_numero_carte(texte))
    if adherent is None:
        aff.afficher_erreur("Aucun adhérent ne porte ce numéro de carte.")
        aff.afficher_info("Veuillez vous inscrire auprès du bibliothécaire.")
        aff.pause()
        return

    aff.afficher_ok("Bienvenue " + adherent["prenom"] + " " + adherent["nom"] + ".")
    while True:
        choix = vue_emprunt.menu_lecteur(adherent)
        if choix == "0":
            return
        # On relit l'adhérent dans la base pour avoir son statut à jour
        adherent = Adherent.chercher_par_id(adherent["id"])
        if choix == "1":
            controleur_livre.lister_livres_disponibles()
        elif choix == "2":
            controleur_livre.rechercher_livres()
        elif choix == "3":
            emprunter(adherent)
        elif choix == "4":
            prolonger(adherent)
        elif choix == "5":
            reserver(adherent)
        elif choix == "6":
            voir_mon_compte(adherent)
        aff.pause()


def verifier_compte(adherent):
    """Conditions communes à l'emprunt et à la réservation.

    Renvoie un message d'erreur, ou None si tout va bien.
    """
    if adherent["statut"] == "bloque":
        return "Votre compte est bloqué. Adressez-vous au bibliothécaire."
    if Amende.compter_impayees_adherent(adherent["id"]) > 0:
        return "Vous avez au moins une amende impayée. Réglez-la auprès du bibliothécaire."
    return None


def verifier_peut_emprunter(adherent):
    """Vérifie les conditions 1 à 4 d'un emprunt, dans l'ordre.

    Renvoie un message d'erreur, ou None si l'emprunt est possible.
    """
    message = verifier_compte(adherent)
    if message is not None:
        return message
    if Emprunt.compter_retards_adherent(adherent["id"], aujourdhui()) > 0:
        return "Vous avez un emprunt en retard. Rendez-le avant d'emprunter à nouveau."
    max_livres = lire_entier("max_livres")
    if Emprunt.compter_en_cours_adherent(adherent["id"]) >= max_livres:
        return ("Vous avez atteint le nombre maximum d'emprunts en cours ("
                + str(max_livres) + ").")
    return None


def emprunter(adherent):
    """Emprunt d'un livre (par recherche ou par code d'exemplaire)."""
    erreur = verifier_peut_emprunter(adherent)
    if erreur is not None:
        aff.afficher_erreur(erreur)
        return

    choix = vue_emprunt.choisir_mode_emprunt()
    if choix == "0":
        return
    if choix == "1":
        exemplaire, reservation = trouver_exemplaire_par_livre(adherent)
    else:
        exemplaire, reservation = trouver_exemplaire_par_code(adherent)

    if exemplaire is not None:
        enregistrer_emprunt(adherent, exemplaire, reservation)


def trouver_exemplaire_par_livre(adherent):
    """Le lecteur choisit un livre, le programme lui attribue un exemplaire.

    Renvoie (exemplaire, reservation) ou (None, None).
    """
    livre = controleur_livre.choisir_livre()
    if livre is None:
        return None, None

    # Un exemplaire a peut-être été mis de côté pour ce lecteur
    reservation = Reservation.disponible_pour_adherent(adherent["id"], livre["id"])
    if reservation is not None:
        return Exemplaire.chercher_par_id(reservation["exemplaire_id"]), reservation

    exemplaire = Exemplaire.premier_disponible(livre["id"])
    if exemplaire is None:
        aff.afficher_attention("Aucun exemplaire de ce livre n'est disponible pour le moment.")
        if aff.confirmer("Voulez-vous réserver ce livre ?"):
            reserver(adherent, livre)
        return None, None
    return exemplaire, None


def trouver_exemplaire_par_code(adherent):
    """Le lecteur saisit le code d'un exemplaire (conditions 5 et 6).

    Renvoie (exemplaire, reservation) ou (None, None).
    """
    code = aff.saisir_texte_obligatoire("Code de l'exemplaire (ex : EX-0001) : ").upper()
    exemplaire = Exemplaire.chercher_par_code(code)
    if exemplaire is None:
        aff.afficher_erreur("Aucun exemplaire ne porte ce code.")
        return None, None
    if exemplaire["etat"] == "perdu":
        aff.afficher_erreur("Cet exemplaire est déclaré perdu.")
        return None, None
    if exemplaire["statut"] == "disponible":
        return exemplaire, None
    if exemplaire["statut"] == "reserve":
        reservation = Reservation.disponible_pour_exemplaire(exemplaire["id"])
        if reservation is not None and reservation["adherent_id"] == adherent["id"]:
            return exemplaire, reservation
        aff.afficher_erreur("Cet exemplaire est mis de côté pour un autre adhérent.")
        return None, None
    aff.afficher_erreur("Cet exemplaire n'est pas disponible (statut : "
                        + exemplaire["statut"] + ").")
    return None, None


def enregistrer_emprunt(adherent, exemplaire, reservation):
    """Enregistre l'emprunt après confirmation."""
    if not aff.confirmer("Emprunter « " + exemplaire["titre"] + " » (exemplaire "
                         + exemplaire["code"] + ") ?"):
        aff.afficher_info("Emprunt annulé.")
        return

    date_prevue = ajouter_jours(aujourdhui(), lire_entier("duree_pret"))
    Emprunt.ajouter(exemplaire["id"], adherent["id"], aujourdhui(), date_prevue)
    Exemplaire.changer_statut(exemplaire["id"], "emprunte")
    if reservation is not None:
        Reservation.changer_statut(reservation["id"], "terminee")

    aff.afficher_ok("Emprunt enregistré : « " + exemplaire["titre"] + " » ("
                    + exemplaire["code"] + ").")
    aff.afficher_info("Date de retour prévue : " + aff.formater_date(date_prevue))


def prolonger(adherent):
    """Prolonge un emprunt en cours du lecteur."""
    if adherent["statut"] == "bloque":
        aff.afficher_erreur("Votre compte est bloqué. Adressez-vous au bibliothécaire.")
        return
    emprunts = Emprunt.lister_en_cours_adherent(adherent["id"])
    if not emprunts:
        aff.afficher_info("Vous n'avez aucun emprunt en cours.")
        return
    vue_emprunt.afficher_emprunts(emprunts)
    emprunt = aff.choisir_par_id(emprunts, "ID de l'emprunt à prolonger (0 pour annuler) : ")
    if emprunt is None:
        return

    if jours_de_retard(emprunt["date_retour_prevue"]) > 0:
        aff.afficher_erreur("Prolongation impossible : cet emprunt est déjà en retard.")
        return
    max_prolongations = lire_entier("max_prolongations")
    if emprunt["nb_prolongations"] >= max_prolongations:
        aff.afficher_erreur("Prolongation impossible : nombre maximum de prolongations atteint ("
                            + str(max_prolongations) + ").")
        return
    if Reservation.compter_en_attente(emprunt["livre_id"]) > 0:
        aff.afficher_erreur("Prolongation impossible : un autre lecteur a réservé ce livre.")
        return

    nouvelle_date = ajouter_jours(emprunt["date_retour_prevue"], lire_entier("duree_prolongation"))
    Emprunt.prolonger(emprunt["id"], nouvelle_date)
    aff.afficher_ok("Emprunt prolongé. Nouvelle date de retour : "
                    + aff.formater_date(nouvelle_date))


def reserver(adherent, livre=None):
    """Réserve un livre dont aucun exemplaire n'est disponible."""
    erreur = verifier_compte(adherent)
    if erreur is not None:
        aff.afficher_erreur(erreur)
        return
    if livre is None:
        livre = controleur_livre.choisir_livre()
        if livre is None:
            return

    livre = Livre.chercher_par_id(livre["id"])  # chiffres à jour
    if livre["nb_disponibles"] > 0:
        aff.afficher_erreur("Un exemplaire est disponible : vous pouvez l'emprunter directement.")
        return
    if Reservation.active_pour_adherent(adherent["id"], livre["id"]) is not None:
        aff.afficher_erreur("Vous avez déjà une réservation active sur ce livre.")
        return
    if Emprunt.a_livre_en_cours(adherent["id"], livre["id"]):
        aff.afficher_erreur("Vous avez déjà ce livre en emprunt.")
        return

    Reservation.ajouter(livre["id"], adherent["id"], aujourdhui())
    position = Reservation.compter_en_attente(livre["id"])
    aff.afficher_ok("Réservation enregistrée pour « " + livre["titre"] + " ».")
    aff.afficher_info("Vous êtes en position " + str(position) + " dans la file d'attente.")


def voir_mon_compte(adherent):
    """Affiche les emprunts, réservations et amendes du lecteur."""
    amendes = Amende.lister_par_adherent(adherent["id"])
    total_impaye = 0
    for amende in amendes:
        if not amende["payee"]:
            total_impaye += amende["montant"]
    vue_emprunt.afficher_mon_compte(
        adherent,
        Emprunt.lister_en_cours_adherent(adherent["id"]),
        Reservation.lister_par_adherent(adherent["id"]),
        amendes,
        total_impaye,
    )


# ----------------------------------------------------------------------
# Espace bibliothécaire : retours, pertes, retards
# ----------------------------------------------------------------------

def trouver_emprunt_en_cours():
    """Demande un code d'exemplaire et renvoie l'emprunt en cours (ou None)."""
    code = aff.saisir_texte_obligatoire("Code de l'exemplaire (ex : EX-0001) : ").upper()
    exemplaire = Exemplaire.chercher_par_code(code)
    if exemplaire is None:
        aff.afficher_erreur("Aucun exemplaire ne porte ce code.")
        return None
    emprunt = Emprunt.en_cours_par_exemplaire(exemplaire["id"])
    if emprunt is None:
        aff.afficher_erreur("Aucun emprunt en cours pour cet exemplaire.")
        return None
    vue_bibliothecaire.afficher_emprunt(emprunt)
    return emprunt


def creer_amende_retard(emprunt, amendes_creees):
    """Crée l'amende de retard si nécessaire et l'ajoute à la liste."""
    retard = jours_de_retard(emprunt["date_retour_prevue"])
    if retard == 0:
        return
    montant = retard * lire_entier("amende_par_jour")
    Amende.ajouter(emprunt["id"], "retard", montant, aujourdhui())
    amendes_creees.append(("Retard de " + str(retard) + " jour(s)", montant))


def enregistrer_retour():
    """Enregistre le retour d'un exemplaire emprunté."""
    aff.afficher_titre("ENREGISTRER UN RETOUR")
    emprunt = trouver_emprunt_en_cours()
    if emprunt is None:
        return
    etat = vue_bibliothecaire.choisir_etat_retour()
    if not aff.confirmer("Valider le retour ?"):
        aff.afficher_info("Retour annulé.")
        return

    amendes_creees = []
    creer_amende_retard(emprunt, amendes_creees)
    if etat == "abime":
        pourcentage = lire_entier("pourcentage_degat")
        montant = int(emprunt["prix"] * pourcentage / 100 + 0.5)  # arrondi à l'entier
        Amende.ajouter(emprunt["id"], "degat", montant, aujourdhui())
        Exemplaire.changer_etat(emprunt["exemplaire_id"], "abime")
        amendes_creees.append(("Livre abîmé (" + str(pourcentage) + " % du prix)", montant))

    Emprunt.terminer(emprunt["id"], aujourdhui())
    reservation = controleur_livre.liberer_exemplaire(emprunt["exemplaire_id"], emprunt["livre_id"])

    aff.afficher_ok("Retour enregistré : « " + emprunt["titre"] + " » rendu par "
                    + emprunt["prenom"] + " " + emprunt["nom"] + ".")
    vue_bibliothecaire.afficher_amendes_creees(amendes_creees)
    if reservation is not None:
        vue_bibliothecaire.afficher_mise_de_cote(reservation, emprunt["code"])
    else:
        aff.afficher_info("L'exemplaire " + emprunt["code"] + " est de nouveau disponible.")


def declarer_perte():
    """Déclare perdu un exemplaire emprunté."""
    aff.afficher_titre("DÉCLARER UN LIVRE PERDU")
    emprunt = trouver_emprunt_en_cours()
    if emprunt is None:
        return
    if not aff.confirmer("Confirmer la perte de ce livre ?"):
        aff.afficher_info("Déclaration annulée.")
        return

    amendes_creees = []
    Amende.ajouter(emprunt["id"], "perte", emprunt["prix"], aujourdhui())
    amendes_creees.append(("Livre perdu (100 % du prix)", emprunt["prix"]))
    creer_amende_retard(emprunt, amendes_creees)

    Exemplaire.changer_etat(emprunt["exemplaire_id"], "perdu")
    Exemplaire.changer_statut(emprunt["exemplaire_id"], "indisponible")
    Emprunt.terminer(emprunt["id"], aujourdhui())

    aff.afficher_ok("Perte enregistrée. L'exemplaire " + emprunt["code"] + " est retiré du prêt.")
    vue_bibliothecaire.afficher_amendes_creees(amendes_creees)


def lister_retards():
    """Affiche les emprunts en retard avec l'amende qu'ils coûteraient aujourd'hui."""
    aff.afficher_titre("EMPRUNTS EN RETARD")
    amende_par_jour = lire_entier("amende_par_jour")
    retards = []
    for emprunt in Emprunt.lister_retards(aujourdhui()):
        ligne = dict(emprunt)
        ligne["jours_retard"] = jours_de_retard(emprunt["date_retour_prevue"])
        ligne["amende_estimee"] = ligne["jours_retard"] * amende_par_jour
        retards.append(ligne)
    vue_bibliothecaire.afficher_retards(retards)


# ----------------------------------------------------------------------
# Espace bibliothécaire : réservations
# ----------------------------------------------------------------------

def menu_reservations():
    """Boucle du menu 'Réservations'."""
    while True:
        choix = vue_bibliothecaire.menu_reservations()
        if choix == "0":
            return
        if choix == "1":
            lister_reservations()
        elif choix == "2":
            annuler_reservation()
        aff.pause()


def lister_reservations():
    """Affiche les réservations en attente ou disponibles."""
    aff.afficher_titre("RÉSERVATIONS ACTIVES")
    vue_bibliothecaire.afficher_reservations(Reservation.lister_actives())


def annuler_reservation():
    """Annule une réservation active.

    Si un exemplaire était mis de côté, il passe au lecteur suivant
    ou redevient disponible.
    """
    reservations = Reservation.lister_actives()
    vue_bibliothecaire.afficher_reservations(reservations)
    if not reservations:
        return
    reservation = aff.choisir_par_id(reservations, "ID de la réservation (0 pour annuler) : ")
    if reservation is None:
        return
    if not aff.confirmer("Annuler cette réservation ?"):
        return

    Reservation.changer_statut(reservation["id"], "annulee")
    aff.afficher_ok("Réservation annulée.")

    if reservation["statut"] == "disponible" and reservation["exemplaire_id"] is not None:
        suivante = controleur_livre.liberer_exemplaire(reservation["exemplaire_id"],
                                                       reservation["livre_id"])
        if suivante is not None:
            vue_bibliothecaire.afficher_mise_de_cote(suivante, reservation["code_exemplaire"])
        else:
            aff.afficher_info("L'exemplaire " + reservation["code_exemplaire"]
                              + " est de nouveau disponible.")
