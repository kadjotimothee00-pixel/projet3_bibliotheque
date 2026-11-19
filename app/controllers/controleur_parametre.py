"""Contrôleur des paramètres (règles de gestion modifiables)."""
from app.controllers import controleur_auth
from app.models.parametre import Parametre
from app.views import affichage as aff
from app.views import vue_bibliothecaire as vue

# Valeurs autorisées pour chaque paramètre : (minimum, maximum). None = pas de limite.
BORNES = {
    "max_livres": (1, None),
    "duree_pret": (1, None),
    "duree_prolongation": (1, None),
    "max_prolongations": (0, None),
    "amende_par_jour": (0, None),
    "prix_defaut": (0, None),
    "pourcentage_degat": (0, 100),
}


def lire_entier(nom):
    """Lit un paramètre dans la base, au moment où on en a besoin,
    et le renvoie sous forme d'entier."""
    valeur = Parametre.lire(nom)
    if valeur is None:
        raise ValueError("Paramètre introuvable dans la base : " + nom)
    return int(valeur)


def menu_parametres():
    """Boucle du menu Paramètres."""
    while True:
        choix = vue.menu_parametres()
        if choix == "0":
            return
        if choix == "1":
            afficher_parametres()
        elif choix == "2":
            modifier_parametre()
        elif choix == "3":
            controleur_auth.changer_mot_de_passe()
        elif choix == "4":
            controleur_auth.changer_identifiant()
        aff.pause()


def afficher_parametres():
    """Affiche tous les paramètres."""
    vue.afficher_parametres(Parametre.lister())


def modifier_parametre():
    """Modifie la valeur d'un paramètre choisi dans la liste."""
    parametres = Parametre.lister()
    vue.afficher_parametres(parametres)
    numero = aff.saisir_entier("N° du paramètre à modifier (0 pour annuler) : ", 0, len(parametres))
    if numero == 0:
        return

    parametre = parametres[numero - 1]
    minimum, maximum = BORNES.get(parametre["nom"], (0, None))
    message = ("Nouvelle valeur pour " + parametre["nom"]
               + " (actuelle : " + parametre["valeur"] + ") : ")
    nouvelle_valeur = aff.saisir_entier(message, minimum, maximum)

    Parametre.modifier(parametre["nom"], str(nouvelle_valeur))
    aff.afficher_ok("Paramètre " + parametre["nom"] + " = " + str(nouvelle_valeur) + ".")
    aff.afficher_info("Les emprunts déjà enregistrés ne sont pas modifiés.")
