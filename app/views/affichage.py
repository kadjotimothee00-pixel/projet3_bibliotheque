"""Utilitaires d'affichage et de saisie communs à toutes les vues."""
import getpass
import os
import sys

LARGEUR = 70               # largeur des titres et des séparateurs
LARGEUR_MAX_COLONNE = 30   # au-delà, le texte d'une cellule est coupé

# Couleurs du texte (codes ANSI compris par les terminaux)
VERT = "\033[92m"
ROUGE = "\033[91m"
JAUNE = "\033[93m"
MAGENTA = "\033[95m"
REINITIALISER = "\033[0m"

# Les couleurs ne sont utilisées que dans un vrai terminal
# (pas si la sortie est redirigée vers un fichier).
COULEURS_ACTIVES = sys.stdout.isatty()
if COULEURS_ACTIVES and os.name == "nt":
    os.system("")  # active la prise en charge des couleurs dans la console Windows


def colorer(texte, couleur):
    """Renvoie le texte entouré du code couleur (ou tel quel si pas de couleurs)."""
    if not COULEURS_ACTIVES:
        return texte
    return couleur + texte + REINITIALISER


# ----------------------------------------------------------------------
# Affichage
# ----------------------------------------------------------------------

def afficher_titre(texte):
    """Affiche un titre encadré par des lignes de '='."""
    print()
    print("=" * LARGEUR)
    print(texte.center(LARGEUR))
    print("=" * LARGEUR)


def afficher_ligne():
    """Affiche une ligne de séparation."""
    print("-" * LARGEUR)


def afficher_ok(message):
    """Affiche un message de réussite (en vert)."""
    print(colorer("[OK] " + message, VERT))


def afficher_erreur(message):
    """Affiche un message d'erreur (en rouge)."""
    print(colorer("[ERREUR] " + message, ROUGE))


def afficher_info(message):
    """Affiche un message d'information (en jaune)."""
    print(colorer("[INFO] " + message, JAUNE))


def afficher_attention(message):
    """Affiche un avertissement (en magenta)."""
    print(colorer("[ATTENTION] " + message, MAGENTA))


def formater_valeur(valeur):
    """Transforme une valeur en texte (None ou vide devient '-')."""
    if valeur is None or valeur == "":
        return "-"
    return str(valeur)


def formater_date(date_iso):
    """Transforme 'AAAA-MM-JJ' en 'JJ/MM/AAAA'."""
    if not date_iso:
        return "-"
    morceaux = date_iso.split("-")
    if len(morceaux) != 3:
        return date_iso
    return morceaux[2] + "/" + morceaux[1] + "/" + morceaux[0]


def formater_prix(montant):
    """Transforme 12500 en '12 500 FCFA'."""
    if montant is None:
        return "-"
    return f"{montant:,}".replace(",", " ") + " FCFA"


def couper(texte, largeur):
    """Coupe un texte trop long et ajoute '...'."""
    if len(texte) > largeur:
        return texte[:largeur - 3] + "..."
    return texte


def formater_ligne_tableau(valeurs, largeurs):
    """Assemble les cellules d'une ligne de tableau, alignées à gauche."""
    cellules = []
    for i in range(len(valeurs)):
        cellules.append(valeurs[i].ljust(largeurs[i]))
    return " | ".join(cellules)


def afficher_tableau(entetes, lignes):
    """Affiche un tableau aligné.

    entetes : liste des titres de colonnes
    lignes  : liste de listes (une liste de valeurs par ligne)
    """
    if not lignes:
        afficher_info("Aucun élément à afficher.")
        return

    # On transforme toutes les valeurs en texte
    lignes_texte = []
    for ligne in lignes:
        lignes_texte.append([couper(formater_valeur(v), LARGEUR_MAX_COLONNE) for v in ligne])

    # Largeur de chaque colonne = plus long texte de la colonne
    largeurs = [len(entete) for entete in entetes]
    for ligne in lignes_texte:
        for i in range(len(ligne)):
            largeurs[i] = max(largeurs[i], len(ligne[i]))

    ligne_entete = formater_ligne_tableau(entetes, largeurs)
    print(ligne_entete)
    print("-" * len(ligne_entete))
    for ligne in lignes_texte:
        print(formater_ligne_tableau(ligne, largeurs))


def afficher_champs(champs):
    """Affiche une fiche sous la forme 'Libellé : valeur'.

    champs : liste de couples (libellé, valeur)
    """
    largeur = max(len(libelle) for libelle, _ in champs)
    for libelle, valeur in champs:
        print(libelle.ljust(largeur) + " : " + formater_valeur(valeur))


def afficher_menu(titre, options):
    """Affiche un menu et renvoie le choix (valide) de l'utilisateur.

    options : liste de couples (touche, libellé), par exemple ("1", "Ajouter")
    """
    afficher_titre(titre)
    for touche, libelle in options:
        print(touche + ". " + libelle)
    afficher_ligne()
    touches = [touche for touche, _ in options]
    return saisir_choix("Votre choix : ", touches)


def pause():
    """Attend que l'utilisateur appuie sur Entrée."""
    input("\nAppuyez sur Entrée pour continuer...")


# ----------------------------------------------------------------------
# Saisies
# ----------------------------------------------------------------------

def saisir_choix(message, choix_valides):
    """Redemande tant que la saisie ne fait pas partie des choix valides."""
    while True:
        choix = input(message).strip()
        if choix in choix_valides:
            return choix
        afficher_erreur("Choix invalide. Choix possibles : " + ", ".join(choix_valides))


def saisir_texte_obligatoire(message):
    """Redemande tant que la saisie est vide."""
    while True:
        texte = input(message).strip()
        if texte != "":
            return texte
        afficher_erreur("Ce champ est obligatoire.")


def saisir_texte_optionnel(message, defaut=""):
    """Renvoie la saisie, ou la valeur par défaut si l'utilisateur appuie sur Entrée."""
    texte = input(message).strip()
    if texte == "":
        return defaut
    return texte


def nombre_dans_les_bornes(nombre, minimum, maximum):
    """Vérifie qu'un nombre est entre minimum et maximum (bornes facultatives)."""
    if minimum is not None and nombre < minimum:
        afficher_erreur("La valeur doit être supérieure ou égale à " + str(minimum) + ".")
        return False
    if maximum is not None and nombre > maximum:
        afficher_erreur("La valeur doit être inférieure ou égale à " + str(maximum) + ".")
        return False
    return True


def saisir_entier(message, minimum=None, maximum=None):
    """Redemande tant que la saisie n'est pas un entier entre minimum et maximum."""
    while True:
        texte = input(message).strip()
        try:
            nombre = int(texte)
        except ValueError:
            afficher_erreur("Veuillez saisir un nombre entier.")
            continue
        if nombre_dans_les_bornes(nombre, minimum, maximum):
            return nombre


def saisir_entier_optionnel(message, defaut=None, minimum=None, maximum=None):
    """Comme saisir_entier, mais Entrée renvoie la valeur par défaut."""
    while True:
        texte = input(message).strip()
        if texte == "":
            return defaut
        try:
            nombre = int(texte)
        except ValueError:
            afficher_erreur("Veuillez saisir un nombre entier (ou Entrée).")
            continue
        if nombre_dans_les_bornes(nombre, minimum, maximum):
            return nombre


def confirmer(question):
    """Pose une question O/N et renvoie True pour oui, False pour non."""
    while True:
        reponse = input(question + " (O/N) : ").strip().upper()
        if reponse in ("O", "OUI"):
            return True
        if reponse in ("N", "NON"):
            return False
        afficher_erreur("Répondez par O (oui) ou N (non).")


def saisir_mot_de_passe(message):
    """Saisie masquée d'un mot de passe (obligatoire)."""
    while True:
        mot_de_passe = getpass.getpass(message)
        if mot_de_passe != "":
            return mot_de_passe
        afficher_erreur("Le mot de passe ne peut pas être vide.")


def telephone_valide(telephone):
    """Un téléphone valide contient 8 à 15 chiffres (espaces et '+' acceptés)."""
    for caractere in telephone:
        if not (caractere.isdigit() or caractere in " +"):
            return False
    nb_chiffres = sum(1 for caractere in telephone if caractere.isdigit())
    return 8 <= nb_chiffres <= 15


def saisir_telephone(message, defaut=None):
    """Saisie d'un téléphone. Si defaut est donné, Entrée garde cette valeur."""
    while True:
        telephone = input(message).strip()
        if telephone == "" and defaut is not None:
            return defaut
        if telephone_valide(telephone):
            return telephone
        afficher_erreur("Téléphone invalide (8 à 15 chiffres, ex : 07 01 02 03 04).")


def email_valide(email):
    """Vérification simple : un seul '@', du texte avant, un point après."""
    if " " in email or email.count("@") != 1:
        return False
    avant, apres = email.split("@")
    return avant != "" and "." in apres and not apres.startswith(".") and not apres.endswith(".")


def saisir_email(message, defaut=""):
    """Saisie d'un email optionnel. Entrée renvoie la valeur par défaut."""
    while True:
        email = input(message).strip()
        if email == "":
            return defaut
        if email_valide(email):
            return email
        afficher_erreur("Email invalide (exemple : nom@domaine.com).")


def choisir_par_id(elements, message):
    """Demande l'id d'un élément de la liste affichée. 0 pour annuler.

    Renvoie l'élément choisi ou None si l'utilisateur annule.
    """
    while True:
        numero = saisir_entier(message, minimum=0)
        if numero == 0:
            return None
        for element in elements:
            if element["id"] == numero:
                return element
        afficher_erreur("Cet ID ne fait pas partie de la liste affichée.")
