"""Vue du menu principal."""
from app.views import affichage as aff


def menu_principal():
    """Affiche le menu principal et renvoie le choix."""
    return aff.afficher_menu("GESTION DE BIBLIOTHÈQUE", [
        ("1", "Bibliothécaire"),
        ("2", "Lire sur place"),
        ("3", "Emprunter"),
        ("0", "Quitter"),
    ])
