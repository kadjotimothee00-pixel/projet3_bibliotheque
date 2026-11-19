"""Modèle Parametre : requêtes SQL sur la table parametres."""
from database.connexion import executer, lire_tous, lire_un


class Parametre:
    """Accès aux paramètres (règles de gestion modifiables)."""

    @staticmethod
    def ajouter(nom, valeur, description):
        """Ajoute un paramètre."""
        executer(
            "INSERT INTO parametres (nom, valeur, description) VALUES (?, ?, ?)",
            (nom, valeur, description),
        )

    @staticmethod
    def lire(nom):
        """Renvoie la valeur (texte) d'un paramètre, ou None s'il n'existe pas."""
        ligne = lire_un("SELECT valeur FROM parametres WHERE nom = ?", (nom,))
        if ligne is None:
            return None
        return ligne["valeur"]

    @staticmethod
    def lister():
        """Renvoie tous les paramètres."""
        return lire_tous("SELECT * FROM parametres ORDER BY nom")

    @staticmethod
    def modifier(nom, valeur):
        """Change la valeur d'un paramètre."""
        executer("UPDATE parametres SET valeur = ? WHERE nom = ?", (valeur, nom))

    @staticmethod
    def compter():
        """Renvoie le nombre de paramètres."""
        return lire_un("SELECT COUNT(*) AS nombre FROM parametres")["nombre"]
