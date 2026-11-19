"""Contrôleur des livres et des exemplaires."""
from datetime import date

from app.controllers.controleur_parametre import lire_entier
from app.models.categorie import Categorie
from app.models.exemplaire import Exemplaire
from app.models.livre import Livre
from app.models.reservation import Reservation
from services import open_library
from app.views import affichage as aff
from app.views import vue_bibliothecaire as vue

NB_MAX_EXEMPLAIRES = 50  # limite raisonnable pour une seule saisie


# ----------------------------------------------------------------------
# Menus
# ----------------------------------------------------------------------

def menu_livres():
    """Boucle du menu 'Gestion des livres'."""
    actions = {
        "1": ajouter_livre,
        "2": modifier_livre,
        "3": supprimer_livre,
        "4": rechercher_livres,
        "5": lister_livres,
    }
    while True:
        choix = vue.menu_livres()
        if choix == "0":
            return
        actions[choix]()
        aff.pause()


def menu_exemplaires():
    """Boucle du menu 'Gestion des exemplaires'."""
    actions = {
        "1": ajouter_exemplaires,
        "2": changer_etat_exemplaire,
        "3": lister_exemplaires,
    }
    while True:
        choix = vue.menu_exemplaires()
        if choix == "0":
            return
        actions[choix]()
        aff.pause()


# ----------------------------------------------------------------------
# Petites fonctions de saisie et de vérification
# ----------------------------------------------------------------------

def nettoyer_isbn(isbn):
    """Supprime les tirets et les espaces d'un ISBN."""
    return isbn.replace("-", "").replace(" ", "").upper()


def isbn_valide(isbn):
    """ISBN-13 : 13 chiffres. ISBN-10 : 9 chiffres puis un chiffre ou X."""
    if len(isbn) == 13:
        return isbn.isdigit()
    if len(isbn) == 10:
        return isbn[:9].isdigit() and (isbn[9].isdigit() or isbn[9] == "X")
    return False


def saisir_isbn(message):
    """Demande un ISBN au bon format.

    Renvoie l'ISBN nettoyé, ou None si l'utilisateur appuie sur Entrée.
    """
    while True:
        texte = aff.saisir_texte_optionnel(message)
        if texte == "":
            return None
        isbn = nettoyer_isbn(texte)
        if isbn_valide(isbn):
            return isbn
        aff.afficher_erreur("ISBN invalide : 10 ou 13 chiffres "
                            "(le dernier caractère d'un ISBN-10 peut être X).")


def saisir_isbn_unique():
    """Demande un ISBN optionnel qui n'existe pas encore dans la base."""
    while True:
        isbn = saisir_isbn("ISBN (optionnel, Entrée pour ignorer) : ")
        if isbn is None or Livre.chercher_par_isbn(isbn) is None:
            return isbn
        aff.afficher_erreur("Un livre avec cet ISBN existe déjà dans la base.")


def saisir_annee(message, defaut=None):
    """Demande une année optionnelle entre 1000 et l'année en cours."""
    return aff.saisir_entier_optionnel(message, defaut, 1000, date.today().year)


def saisir_prix():
    """Demande le prix. Entrée = prix par défaut lu dans les paramètres."""
    prix_defaut = lire_entier("prix_defaut")
    return aff.saisir_entier_optionnel(
        "Prix en FCFA (Entrée = " + str(prix_defaut) + ") : ", prix_defaut, 0
    )


def choisir_categorie():
    """Affiche les catégories et renvoie celle choisie."""
    categories = Categorie.lister()
    vue.afficher_categories(categories)
    while True:
        numero = aff.saisir_entier("Numéro de la catégorie : ", 1)
        for categorie in categories:
            if categorie["id"] == numero:
                return categorie
        aff.afficher_erreur("Cette catégorie n'existe pas.")


def creer_exemplaires(livre_id, nombre):
    """Crée plusieurs exemplaires d'un livre et renvoie la liste de leurs codes."""
    codes = []
    for _ in range(nombre):
        codes.append(Exemplaire.ajouter(livre_id))
    return codes


def liberer_exemplaire(exemplaire_id, livre_id):
    """Remet un exemplaire en circulation.

    S'il existe une réservation en attente sur le livre, l'exemplaire est
    mis de côté pour la plus ancienne (statut 'reserve') et cette
    réservation est renvoyée. Sinon l'exemplaire devient 'disponible'
    et la fonction renvoie None.
    """
    reservation = Reservation.premiere_en_attente(livre_id)
    if reservation is None:
        Exemplaire.changer_statut(exemplaire_id, "disponible")
        return None
    Exemplaire.changer_statut(exemplaire_id, "reserve")
    Reservation.mettre_disponible(reservation["id"], exemplaire_id)
    return reservation


# ----------------------------------------------------------------------
# Recherche et choix d'un livre (utilisé aussi par les autres contrôleurs)
# ----------------------------------------------------------------------

def rechercher_livres(avec_isbn=True):
    """Lance une recherche, affiche les résultats et les renvoie."""
    critere, texte = vue.saisir_recherche_livre(avec_isbn)
    if critere is None:
        return []
    if critere == "isbn":
        texte = nettoyer_isbn(texte)
    livres = Livre.rechercher(critere, texte)
    vue.afficher_livres(livres)
    return livres


def choisir_livre(avec_isbn=True):
    """Recherche un livre puis demande son ID. Renvoie le livre ou None."""
    livres = rechercher_livres(avec_isbn)
    if not livres:
        return None
    return aff.choisir_par_id(livres, "ID du livre (0 pour annuler) : ")


def lister_livres():
    """Affiche tous les livres avec leurs exemplaires disponibles / total."""
    aff.afficher_titre("LISTE DES LIVRES")
    vue.afficher_livres(Livre.lister())


def lister_livres_disponibles():
    """Affiche uniquement les livres ayant au moins un exemplaire disponible."""
    aff.afficher_titre("LIVRES DISPONIBLES")
    livres = Livre.lister_disponibles()
    if not livres:
        aff.afficher_info("Aucun livre n'est disponible pour le moment.")
        return
    vue.afficher_livres(livres)


# ----------------------------------------------------------------------
# Ajout d'un livre
# ----------------------------------------------------------------------

def ajouter_livre():
    """Propose l'ajout par ISBN (Open Library) ou la saisie manuelle."""
    choix = vue.menu_ajout_livre()
    if choix == "1":
        ajouter_par_isbn()
    elif choix == "2":
        ajouter_manuellement()


def ajouter_par_isbn():
    """Ajoute un livre en récupérant ses informations sur Open Library."""
    isbn = saisir_isbn("ISBN du livre (Entrée pour annuler) : ")
    if isbn is None:
        return

    # 1. Le livre existe déjà : on propose d'ajouter des exemplaires
    existant = Livre.chercher_par_isbn(isbn)
    if existant is not None:
        aff.afficher_attention("Ce livre existe déjà dans la base.")
        vue.afficher_livre(existant)
        if aff.confirmer("Voulez-vous lui ajouter des exemplaires ?"):
            ajouter_exemplaires_au_livre(existant)
        return

    # 2. Appel à Open Library
    aff.afficher_info("Recherche sur Open Library, veuillez patienter...")
    infos, erreur = open_library.rechercher_par_isbn(isbn)
    if infos is None:
        aff.afficher_erreur(erreur)
        aff.afficher_info("Passage à la saisie manuelle (l'ISBN est déjà rempli).")
        ajouter_manuellement(isbn)
        return

    vue.afficher_resultat_api(infos)
    if not aff.confirmer("Est-ce bien le livre recherché ?"):
        aff.afficher_info("Passage à la saisie manuelle (l'ISBN est déjà rempli).")
        ajouter_manuellement(isbn)
        return

    # 3. Le bibliothécaire complète les champs manquants
    donnees = {
        "isbn": isbn,
        "titre": infos["titre"] or aff.saisir_texte_obligatoire("Titre : "),
        "auteur": infos["auteur"] or aff.saisir_texte_obligatoire("Auteur (non fourni) : "),
        "editeur": infos["editeur"] or aff.saisir_texte_optionnel(
            "Éditeur (non fourni, Entrée pour ignorer) : ", None),
        "annee": infos["annee"] or saisir_annee("Année (non fournie, Entrée pour ignorer) : "),
    }
    completer_et_enregistrer(donnees, "api")


def ajouter_manuellement(isbn=None):
    """Ajoute un livre en saisissant toutes ses informations."""
    aff.afficher_titre("SAISIE MANUELLE D'UN LIVRE")
    if isbn is None:
        isbn = saisir_isbn_unique()
    else:
        aff.afficher_info("ISBN : " + isbn)

    donnees = {
        "isbn": isbn,
        "titre": aff.saisir_texte_obligatoire("Titre : "),
        "auteur": aff.saisir_texte_obligatoire("Auteur : "),
        "editeur": aff.saisir_texte_optionnel("Éditeur (Entrée pour ignorer) : ", None),
        "annee": saisir_annee("Année (Entrée pour ignorer) : "),
    }
    completer_et_enregistrer(donnees, "manuel")


def completer_et_enregistrer(donnees, source):
    """Demande catégorie, genre, prix et nombre d'exemplaires, affiche un
    récapitulatif puis enregistre le livre après confirmation."""
    categorie = choisir_categorie()
    donnees["categorie_id"] = categorie["id"]
    donnees["genre"] = vue.choisir_genre(permettre_aucun=True)
    donnees["prix"] = saisir_prix()
    nb_exemplaires = aff.saisir_entier("Nombre d'exemplaires (au moins 1) : ",
                                       1, NB_MAX_EXEMPLAIRES)

    vue.afficher_recapitulatif_livre(donnees, categorie["nom"], nb_exemplaires)
    if not aff.confirmer("Enregistrer ce livre ?"):
        aff.afficher_info("Ajout annulé.")
        return

    livre_id = Livre.ajouter(donnees["isbn"], donnees["titre"], donnees["auteur"],
                             donnees["editeur"], donnees["annee"], donnees["categorie_id"],
                             donnees["prix"], source, date.today().isoformat(),
                             donnees["genre"])
    codes = creer_exemplaires(livre_id, nb_exemplaires)
    aff.afficher_ok("Livre enregistré (ID " + str(livre_id) + ").")
    vue.afficher_codes_exemplaires(codes)


# ----------------------------------------------------------------------
# Modification et suppression
# ----------------------------------------------------------------------

def saisir_isbn_modification(livre):
    """Demande le nouvel ISBN d'un livre (Entrée = garder l'actuel)."""
    while True:
        actuel = livre["isbn"] or "-"
        texte = aff.saisir_texte_optionnel("ISBN [" + actuel + "] : ")
        if texte == "":
            return livre["isbn"]
        isbn = nettoyer_isbn(texte)
        if not isbn_valide(isbn):
            aff.afficher_erreur("ISBN invalide : 10 ou 13 chiffres.")
            continue
        autre = Livre.chercher_par_isbn(isbn)
        if autre is not None and autre["id"] != livre["id"]:
            aff.afficher_erreur("Cet ISBN appartient déjà à un autre livre.")
            continue
        return isbn


def modifier_livre():
    """Modifie les informations d'un livre (Entrée = garder la valeur)."""
    livre = choisir_livre()
    if livre is None:
        return
    vue.afficher_livre(livre)
    aff.afficher_info("Appuyez sur Entrée pour garder la valeur entre crochets.")

    isbn = saisir_isbn_modification(livre)
    titre = aff.saisir_texte_optionnel("Titre [" + livre["titre"] + "] : ", livre["titre"])
    auteur = aff.saisir_texte_optionnel("Auteur [" + livre["auteur"] + "] : ", livre["auteur"])
    editeur = aff.saisir_texte_optionnel(
        "Éditeur [" + aff.formater_valeur(livre["editeur"]) + "] : ", livre["editeur"])
    annee = saisir_annee("Année [" + aff.formater_valeur(livre["annee"]) + "] : ", livre["annee"])
    prix = aff.saisir_entier_optionnel("Prix en FCFA [" + str(livre["prix"]) + "] : ",
                                       livre["prix"], 0)

    categorie_id = livre["categorie_id"]
    if aff.confirmer("Changer la catégorie (actuelle : "
                     + aff.formater_valeur(livre["categorie"]) + ") ?"):
        categorie_id = choisir_categorie()["id"]

    genre = livre["genre"]
    if aff.confirmer("Changer le genre (actuel : " + aff.formater_valeur(genre) + ") ?"):
        genre = vue.choisir_genre(permettre_aucun=True)

    if aff.confirmer("Enregistrer les modifications ?"):
        Livre.modifier(livre["id"], isbn, titre, auteur, editeur, annee, categorie_id,
                       genre, prix)
        aff.afficher_ok("Livre modifié.")
    else:
        aff.afficher_info("Modification annulée.")


def supprimer_livre():
    """Supprime un livre et ses exemplaires, si c'est autorisé."""
    livre = choisir_livre()
    if livre is None:
        return
    vue.afficher_livre(livre)

    # Refus si un exemplaire est emprunté, en consultation ou réservé
    occupes = 0
    for exemplaire in Exemplaire.lister_par_livre(livre["id"]):
        if exemplaire["statut"] in ("emprunte", "en_consultation", "reserve"):
            occupes += 1
    if occupes > 0:
        aff.afficher_erreur("Suppression impossible : " + str(occupes)
                            + " exemplaire(s) emprunté(s), en consultation ou réservé(s).")
        return
    if Reservation.compter_en_attente(livre["id"]) > 0:
        aff.afficher_erreur("Suppression impossible : des réservations sont en attente.")
        return
    if Livre.a_des_emprunts(livre["id"]):
        aff.afficher_erreur("Suppression impossible : ce livre a un historique d'emprunts "
                            "(il est conservé pour le suivi des amendes).")
        aff.afficher_info("Vous pouvez plutôt passer ses exemplaires à l'état 'perdu'.")
        return

    if aff.confirmer("Supprimer définitivement ce livre et ses exemplaires ?"):
        Livre.supprimer(livre["id"])
        aff.afficher_ok("Livre supprimé.")
    else:
        aff.afficher_info("Suppression annulée.")


# ----------------------------------------------------------------------
# Exemplaires
# ----------------------------------------------------------------------

def ajouter_exemplaires():
    """Ajoute des exemplaires à un livre choisi par recherche."""
    livre = choisir_livre()
    if livre is not None:
        ajouter_exemplaires_au_livre(livre)


def ajouter_exemplaires_au_livre(livre):
    """Crée de nouveaux exemplaires pour ce livre.

    Si des lecteurs attendent ce livre, les nouveaux exemplaires
    leur sont mis de côté.
    """
    nombre = aff.saisir_entier("Nombre d'exemplaires à ajouter : ", 1, NB_MAX_EXEMPLAIRES)
    codes = creer_exemplaires(livre["id"], nombre)
    vue.afficher_codes_exemplaires(codes)
    for code in codes:
        exemplaire = Exemplaire.chercher_par_code(code)
        reservation = liberer_exemplaire(exemplaire["id"], livre["id"])
        if reservation is not None:
            vue.afficher_mise_de_cote(reservation, code)


def changer_etat_exemplaire():
    """Change l'état (bon, abime, perdu) d'un exemplaire présent en rayon."""
    code = aff.saisir_texte_obligatoire("Code de l'exemplaire (ex : EX-0001) : ").upper()
    exemplaire = Exemplaire.chercher_par_code(code)
    if exemplaire is None:
        aff.afficher_erreur("Aucun exemplaire ne porte ce code.")
        return
    vue.afficher_exemplaires([exemplaire])

    if exemplaire["statut"] not in ("disponible", "indisponible"):
        aff.afficher_erreur("Impossible : l'exemplaire est actuellement '" + exemplaire["statut"]
                            + "'. Utilisez 'Enregistrer un retour' ou 'Déclarer un livre perdu'.")
        return

    etat = vue.choisir_etat_exemplaire()
    if etat is None:
        return
    if etat == exemplaire["etat"]:
        aff.afficher_info("L'état est inchangé.")
        return

    Exemplaire.changer_etat(exemplaire["id"], etat)
    if etat == "perdu":
        Exemplaire.changer_statut(exemplaire["id"], "indisponible")
    elif exemplaire["statut"] == "indisponible":
        # L'exemplaire est retrouvé : il revient en circulation
        reservation = liberer_exemplaire(exemplaire["id"], exemplaire["livre_id"])
        if reservation is not None:
            vue.afficher_mise_de_cote(reservation, exemplaire["code"])
    aff.afficher_ok("État de l'exemplaire " + exemplaire["code"] + " : " + etat + ".")


def lister_exemplaires():
    """Affiche les exemplaires d'un livre choisi par recherche."""
    livre = choisir_livre()
    if livre is None:
        return
    aff.afficher_titre("EXEMPLAIRES : " + aff.couper(livre["titre"], 50))
    vue.afficher_exemplaires(Exemplaire.lister_par_livre(livre["id"]))
