"""Modèle Categorie : requêtes SQL sur la table categories."""
from database.connexion import executer, lire_tous, lire_un


class Categorie:
    """Accès aux catégories de livres."""

    @staticmethod
    def ajouter(nom):
        """Ajoute une catégorie et renvoie son id."""
        return executer("INSERT INTO categories (nom) VALUES (?)", (nom,))

    @staticmethod
    def lister():
        """Renvoie toutes les catégories triées par nom."""
        return lire_tous("SELECT * FROM categories ORDER BY nom")

    @staticmethod
    def chercher_par_id(categorie_id):
        """Renvoie une catégorie à partir de son id (ou None)."""
        return lire_un("SELECT * FROM categories WHERE id = ?", (categorie_id,))

    @staticmethod
    def chercher_par_nom(nom):
        """Renvoie une catégorie à partir de son nom (ou None)."""
        return lire_un("SELECT * FROM categories WHERE nom = ?", (nom,))

    @staticmethod
    def compter():
        """Renvoie le nombre de catégories."""
        return lire_un("SELECT COUNT(*) AS nombre FROM categories")["nombre"]

    @staticmethod
    def repartition_livres():
        """Renvoie, pour chaque catégorie, le nombre de livres."""
        return lire_tous(
            """SELECT c.nom, COUNT(l.id) AS nombre
               FROM categories c LEFT JOIN livres l ON l.categorie_id = c.id
               GROUP BY c.id ORDER BY nombre DESC, c.nom"""
        )
