"""Modèle Exemplaire : requêtes SQL sur la table exemplaires."""
from database.connexion import executer, lire_tous, lire_un

# L'exemplaire avec quelques informations sur son livre
REQUETE_BASE = """
    SELECT e.*, l.titre, l.auteur, l.prix
    FROM exemplaires e
    JOIN livres l ON l.id = e.livre_id
"""


class Exemplaire:
    """Accès aux exemplaires (copies physiques d'un livre)."""

    @staticmethod
    def generer_code():
        """Calcule le prochain code libre : EX-0001, EX-0002, ..."""
        ligne = lire_un("SELECT MAX(CAST(SUBSTR(code, 4) AS INTEGER)) AS maxi FROM exemplaires")
        dernier = ligne["maxi"] or 0
        return "EX-" + str(dernier + 1).zfill(4)

    @staticmethod
    def ajouter(livre_id):
        """Crée un exemplaire en bon état et disponible. Renvoie son code."""
        code = Exemplaire.generer_code()
        executer(
            "INSERT INTO exemplaires (code, livre_id, etat, statut) VALUES (?, ?, 'bon', 'disponible')",
            (code, livre_id),
        )
        return code

    @staticmethod
    def chercher_par_id(exemplaire_id):
        """Renvoie un exemplaire à partir de son id (ou None)."""
        return lire_un(REQUETE_BASE + " WHERE e.id = ?", (exemplaire_id,))

    @staticmethod
    def chercher_par_code(code):
        """Renvoie un exemplaire à partir de son code (ou None)."""
        return lire_un(REQUETE_BASE + " WHERE e.code = ?", (code,))

    @staticmethod
    def lister_par_livre(livre_id):
        """Renvoie tous les exemplaires d'un livre."""
        return lire_tous(REQUETE_BASE + " WHERE e.livre_id = ? ORDER BY e.code", (livre_id,))

    @staticmethod
    def premier_disponible(livre_id):
        """Renvoie le premier exemplaire disponible d'un livre (ou None)."""
        return lire_un(
            REQUETE_BASE + " WHERE e.livre_id = ? AND e.statut = 'disponible' ORDER BY e.code",
            (livre_id,),
        )

    @staticmethod
    def changer_statut(exemplaire_id, statut):
        """Change le statut (disponible, emprunte, ...) d'un exemplaire."""
        executer("UPDATE exemplaires SET statut = ? WHERE id = ?", (statut, exemplaire_id))

    @staticmethod
    def changer_etat(exemplaire_id, etat):
        """Change l'état physique (bon, abime, perdu) d'un exemplaire."""
        executer("UPDATE exemplaires SET etat = ? WHERE id = ?", (etat, exemplaire_id))

    @staticmethod
    def compter_par_statut():
        """Renvoie le nombre d'exemplaires pour chaque statut."""
        return lire_tous(
            "SELECT statut, COUNT(*) AS nombre FROM exemplaires GROUP BY statut ORDER BY statut"
        )
