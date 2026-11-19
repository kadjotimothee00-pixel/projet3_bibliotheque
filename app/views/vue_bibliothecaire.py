"""Vue de l'espace bibliothécaire : menus, formulaires et tableaux."""
from datetime import date

from app.models.livre import GENRES
from app.views import affichage as aff


# ----------------------------------------------------------------------
# Menus
# ----------------------------------------------------------------------

def menu_bibliothecaire():
    """Menu principal du bibliothécaire."""
    return aff.afficher_menu("ESPACE BIBLIOTHÉCAIRE", [
        ("1", "Gestion des livres"),
        ("2", "Gestion des exemplaires"),
        ("3", "Gestion des adhérents"),
        ("4", "Enregistrer un retour"),
        ("5", "Déclarer un livre perdu"),
        ("6", "Amendes"),
        ("7", "Emprunts en retard"),
        ("8", "Réservations"),
        ("9", "Statistiques"),
        ("10", "Paramètres"),
        ("0", "Retour"),
    ])


def menu_livres():
    """Sous-menu de gestion des livres."""
    return aff.afficher_menu("GESTION DES LIVRES", [
        ("1", "Ajouter un livre"),
        ("2", "Modifier un livre"),
        ("3", "Supprimer un livre"),
        ("4", "Rechercher un livre"),
        ("5", "Lister tous les livres"),
        ("0", "Retour"),
    ])


def menu_ajout_livre():
    """Choix de la méthode d'ajout d'un livre."""
    return aff.afficher_menu("AJOUTER UN LIVRE", [
        ("1", "Par ISBN avec Open Library"),
        ("2", "Saisie manuelle"),
        ("0", "Annuler"),
    ])


def menu_exemplaires():
    """Sous-menu de gestion des exemplaires."""
    return aff.afficher_menu("GESTION DES EXEMPLAIRES", [
        ("1", "Ajouter des exemplaires à un livre existant"),
        ("2", "Changer l'état d'un exemplaire"),
        ("3", "Lister les exemplaires d'un livre"),
        ("0", "Retour"),
    ])


def menu_adherents():
    """Sous-menu de gestion des adhérents."""
    return aff.afficher_menu("GESTION DES ADHÉRENTS", [
        ("1", "Inscrire un adhérent"),
        ("2", "Modifier un adhérent"),
        ("3", "Rechercher un adhérent"),
        ("4", "Lister les adhérents"),
        ("5", "Bloquer / débloquer un adhérent"),
        ("0", "Retour"),
    ])


def menu_amendes():
    """Sous-menu des amendes."""
    return aff.afficher_menu("AMENDES", [
        ("1", "Lister les amendes impayées"),
        ("2", "Encaisser une amende"),
        ("3", "Historique des amendes d'un adhérent"),
        ("0", "Retour"),
    ])


def menu_reservations():
    """Sous-menu des réservations."""
    return aff.afficher_menu("RÉSERVATIONS", [
        ("1", "Lister les réservations actives"),
        ("2", "Annuler une réservation"),
        ("0", "Retour"),
    ])


def menu_parametres():
    """Sous-menu des paramètres."""
    return aff.afficher_menu("PARAMÈTRES", [
        ("1", "Afficher les paramètres"),
        ("2", "Modifier une valeur"),
        ("3", "Changer le mot de passe"),
        ("4", "Changer l'identifiant"),
        ("0", "Retour"),
    ])


# ----------------------------------------------------------------------
# Compte bibliothécaire
# ----------------------------------------------------------------------

def afficher_creation_compte():
    """Message affiché au tout premier lancement."""
    aff.afficher_titre("CRÉATION DU COMPTE BIBLIOTHÉCAIRE")
    aff.afficher_info("Premier lancement : aucun compte bibliothécaire n'existe.")
    aff.afficher_info("Choisissez un identifiant et un mot de passe (4 caractères minimum).")


# ----------------------------------------------------------------------
# Livres
# ----------------------------------------------------------------------

def saisir_recherche_livre(avec_isbn=True):
    """Demande le critère et le texte de recherche.

    Renvoie un couple (critere, texte) ou (None, None) si annulation.
    """
    options = [("1", "Par titre"), ("2", "Par auteur"), ("3", "Par genre"),
               ("4", "Par catégorie")]
    if avec_isbn:
        # Recherche par ISBN réservée à l'espace bibliothécaire
        options.append(("5", "Par ISBN"))
    options.append(("0", "Annuler"))

    choix = aff.afficher_menu("RECHERCHER UN LIVRE", options)
    if choix == "0":
        return None, None
    if choix == "3":
        genre = choisir_genre()
        if genre is None:
            return None, None
        return "genre", genre
    criteres = {"1": "titre", "2": "auteur", "4": "categorie", "5": "isbn"}
    if choix == "5":
        texte = aff.saisir_texte_obligatoire("ISBN recherché (tout ou partie) : ")
    else:
        texte = aff.saisir_texte_obligatoire("Texte recherché : ")
    return criteres[choix], texte


def choisir_genre(permettre_aucun=False):
    """Affiche la liste des genres et renvoie celui choisi.

    Renvoie None si l'utilisateur tape 0 (annuler, ou « aucun genre »
    quand permettre_aucun vaut True).
    """
    print("\nGenres disponibles :")
    for numero, genre in enumerate(GENRES, start=1):
        print("  " + str(numero) + ". " + genre)
    libelle_zero = "aucun genre" if permettre_aucun else "annuler"
    numero = aff.saisir_entier("Numéro du genre (0 = " + libelle_zero + ") : ",
                               0, len(GENRES))
    if numero == 0:
        return None
    return GENRES[numero - 1]


def afficher_livres(livres):
    """Affiche un tableau de livres."""
    lignes = []
    for l in livres:
        lignes.append([
            l["id"], l["titre"], l["auteur"], l["genre"], l["categorie"], l["annee"],
            aff.formater_prix(l["prix"]),
            str(l["nb_disponibles"]) + "/" + str(l["nb_total"]),
        ])
    aff.afficher_tableau(
        ["ID", "Titre", "Auteur", "Genre", "Catégorie", "Année", "Prix", "Dispo/Total"], lignes
    )
    if livres:
        aff.afficher_info(str(len(livres)) + " livre(s) trouvé(s).")


def afficher_livre(livre):
    """Affiche la fiche complète d'un livre."""
    aff.afficher_ligne()
    aff.afficher_champs([
        ("ID", livre["id"]),
        ("ISBN", livre["isbn"]),
        ("Titre", livre["titre"]),
        ("Auteur", livre["auteur"]),
        ("Éditeur", livre["editeur"]),
        ("Année", livre["annee"]),
        ("Genre", livre["genre"]),
        ("Catégorie", livre["categorie"]),
        ("Prix", aff.formater_prix(livre["prix"])),
        ("Source", livre["source"]),
        ("Ajouté le", aff.formater_date(livre["date_ajout"])),
        ("Exemplaires", str(livre["nb_disponibles"]) + " disponible(s) sur "
                        + str(livre["nb_total"])),
    ])
    aff.afficher_ligne()


def afficher_resultat_api(infos):
    """Affiche le livre trouvé sur Open Library."""
    aff.afficher_titre("RÉSULTAT OPEN LIBRARY")
    aff.afficher_champs([
        ("Titre", infos["titre"]),
        ("Auteur(s)", infos["auteur"]),
        ("Éditeur", infos["editeur"]),
        ("Année", infos["annee"]),
    ])
    aff.afficher_ligne()


def afficher_categories(categories):
    """Affiche la liste des catégories."""
    print("\nCatégories disponibles :")
    for categorie in categories:
        print("  " + str(categorie["id"]) + ". " + categorie["nom"])


def afficher_recapitulatif_livre(donnees, nom_categorie, nb_exemplaires):
    """Affiche le récapitulatif avant l'enregistrement d'un livre."""
    aff.afficher_titre("RÉCAPITULATIF")
    aff.afficher_champs([
        ("ISBN", donnees["isbn"]),
        ("Titre", donnees["titre"]),
        ("Auteur", donnees["auteur"]),
        ("Éditeur", donnees["editeur"]),
        ("Année", donnees["annee"]),
        ("Genre", donnees["genre"]),
        ("Catégorie", nom_categorie),
        ("Prix", aff.formater_prix(donnees["prix"])),
        ("Exemplaires", nb_exemplaires),
    ])
    aff.afficher_ligne()


def afficher_codes_exemplaires(codes):
    """Affiche les codes des exemplaires créés."""
    aff.afficher_ok(str(len(codes)) + " exemplaire(s) créé(s) : " + ", ".join(codes))
    aff.afficher_info("Collez ces codes sur les livres.")


def afficher_exemplaires(exemplaires):
    """Affiche un tableau d'exemplaires."""
    lignes = [[e["code"], e["titre"], e["etat"], e["statut"]] for e in exemplaires]
    aff.afficher_tableau(["Code", "Livre", "État", "Statut"], lignes)


def choisir_etat_exemplaire():
    """Demande le nouvel état d'un exemplaire. Renvoie None si annulation."""
    choix = aff.afficher_menu("NOUVEL ÉTAT", [
        ("1", "bon"), ("2", "abime"), ("3", "perdu"), ("0", "Annuler"),
    ])
    etats = {"1": "bon", "2": "abime", "3": "perdu"}
    return etats.get(choix)


# ----------------------------------------------------------------------
# Adhérents
# ----------------------------------------------------------------------

def afficher_adherents(adherents):
    """Affiche un tableau d'adhérents."""
    lignes = []
    for a in adherents:
        lignes.append([a["id"], a["numero_carte"], a["nom"], a["prenom"], a["telephone"],
                       a["email"], aff.formater_date(a["date_inscription"]), a["statut"]])
    aff.afficher_tableau(
        ["ID", "Carte", "Nom", "Prénom", "Téléphone", "Email", "Inscrit le", "Statut"], lignes
    )


def afficher_adherent(adherent):
    """Affiche la fiche d'un adhérent."""
    aff.afficher_ligne()
    aff.afficher_champs([
        ("Numéro de carte", adherent["numero_carte"]),
        ("Nom", adherent["nom"]),
        ("Prénom", adherent["prenom"]),
        ("Téléphone", adherent["telephone"]),
        ("Email", adherent["email"]),
        ("Inscrit le", aff.formater_date(adherent["date_inscription"])),
        ("Statut", adherent["statut"]),
    ])
    aff.afficher_ligne()


# ----------------------------------------------------------------------
# Retours, pertes, retards, réservations
# ----------------------------------------------------------------------

def afficher_emprunt(emprunt):
    """Affiche l'emprunt en cours d'un exemplaire."""
    aff.afficher_titre("EMPRUNT EN COURS")
    aff.afficher_champs([
        ("Livre", emprunt["titre"]),
        ("Exemplaire", emprunt["code"]),
        ("Adhérent", emprunt["prenom"] + " " + emprunt["nom"]
                     + " (" + emprunt["numero_carte"] + ")"),
        ("Date de sortie", aff.formater_date(emprunt["date_sortie"])),
        ("Retour prévu", aff.formater_date(emprunt["date_retour_prevue"])),
        ("Prix du livre", aff.formater_prix(emprunt["prix"])),
    ])
    aff.afficher_ligne()


def choisir_etat_retour():
    """Demande l'état constaté au retour : 'bon' ou 'abime'."""
    print("État constaté du livre :")
    print("1. bon")
    print("2. abime")
    choix = aff.saisir_choix("Votre choix : ", ["1", "2"])
    return "bon" if choix == "1" else "abime"


def afficher_amendes_creees(amendes_creees):
    """Affiche la liste des amendes créées et leur total.

    amendes_creees : liste de couples (libellé, montant)
    """
    if not amendes_creees:
        aff.afficher_info("Aucune amende.")
        return
    total = 0
    for libelle, montant in amendes_creees:
        print("  - " + libelle + " : " + aff.formater_prix(montant))
        total += montant
    aff.afficher_attention("Total des amendes créées : " + aff.formater_prix(total))


def afficher_mise_de_cote(reservation, code):
    """Indique au bibliothécaire de mettre le livre de côté."""
    aff.afficher_attention("Ce livre est réservé ! Mettez l'exemplaire " + code + " de côté pour "
                           + reservation["prenom"] + " " + reservation["nom"]
                           + " (" + reservation["numero_carte"] + ").")


def afficher_retards(retards):
    """Affiche les emprunts en retard.

    retards : liste de dictionnaires avec en plus 'jours_retard' et 'amende_estimee'.
    """
    lignes = []
    for r in retards:
        lignes.append([
            r["code"], r["titre"], r["prenom"] + " " + r["nom"], r["numero_carte"],
            aff.formater_date(r["date_retour_prevue"]), r["jours_retard"],
            aff.formater_prix(r["amende_estimee"]),
        ])
    aff.afficher_tableau(
        ["Exemplaire", "Livre", "Adhérent", "Carte", "Retour prévu", "Jours", "Amende"], lignes
    )


def afficher_reservations(reservations):
    """Affiche les réservations actives."""
    lignes = []
    for r in reservations:
        lignes.append([r["id"], r["titre"], r["prenom"] + " " + r["nom"], r["numero_carte"],
                       aff.formater_date(r["date_reservation"]), r["statut"],
                       r["code_exemplaire"]])
    aff.afficher_tableau(
        ["ID", "Livre", "Adhérent", "Carte", "Date", "Statut", "Exemplaire"], lignes
    )


# ----------------------------------------------------------------------
# Amendes
# ----------------------------------------------------------------------

def afficher_amendes(amendes):
    """Affiche un tableau d'amendes."""
    lignes = []
    for a in amendes:
        paiement = aff.formater_date(a["date_paiement"]) if a["payee"] else "Impayée"
        lignes.append([a["id"], a["prenom"] + " " + a["nom"], a["numero_carte"], a["type"],
                       a["titre"], aff.formater_prix(a["montant"]),
                       aff.formater_date(a["date_creation"]), paiement])
    aff.afficher_tableau(
        ["ID", "Adhérent", "Carte", "Type", "Livre", "Montant", "Date", "Payée le"], lignes
    )


# ----------------------------------------------------------------------
# Paramètres et statistiques
# ----------------------------------------------------------------------

def afficher_parametres(parametres):
    """Affiche les paramètres avec un numéro devant chacun."""
    lignes = []
    numero = 1
    for p in parametres:
        lignes.append([numero, p["nom"], p["valeur"], p["description"]])
        numero += 1
    aff.afficher_tableau(["N°", "Nom", "Valeur", "Description"], lignes)


def afficher_statistiques(stats):
    """Affiche les statistiques générales (stats est un dictionnaire)."""
    aff.afficher_titre("STATISTIQUES  (au " + aff.formater_date(date.today().isoformat()) + ")")
    aff.afficher_champs([
        ("Nombre de livres", stats["nb_livres"]),
        ("Nombre d'exemplaires", stats["nb_exemplaires"]),
        ("Adhérents actifs", stats["adherents_actifs"]),
        ("Adhérents bloqués", stats["adherents_bloques"]),
        ("Emprunts en cours", stats["emprunts_en_cours"]),
        ("Emprunts en retard", stats["emprunts_retard"]),
        ("Amendes impayées", aff.formater_prix(stats["amendes_impayees"])),
        ("Amendes encaissées", aff.formater_prix(stats["amendes_encaissees"])),
    ])

    print("\nExemplaires par statut :")
    aff.afficher_ligne()
    aff.afficher_tableau(["Statut", "Nombre"],
                         [[s["statut"], s["nombre"]] for s in stats["exemplaires_par_statut"]])

    print("\nTop 5 des livres les plus empruntés :")
    aff.afficher_ligne()
    aff.afficher_tableau(["Titre", "Auteur", "Emprunts"],
                         [[t["titre"], t["auteur"], t["nombre"]] for t in stats["top_livres"]])

    print("\nRépartition des livres par catégorie :")
    aff.afficher_ligne()
    aff.afficher_tableau(["Catégorie", "Livres"],
                         [[c["nom"], c["nombre"]] for c in stats["par_categorie"]])
