"""Modèle Livre : requêtes SQL sur la table livres."""
from database.connexion import executer, lire_tous, lire_un, normaliser, obtenir_connexion

# Requête commune : le livre, le nom de sa catégorie
# et le nombre d'exemplaires (total et disponibles).
REQUETE_BASE = """
    SELECT l.*, c.nom AS categorie,
        (SELECT COUNT(*) FROM exemplaires e WHERE e.livre_id = l.id) AS nb_total,
        (SELECT COUNT(*) FROM exemplaires e
            WHERE e.livre_id = l.id AND e.statut = 'disponible') AS nb_disponibles
    FROM livres l
    LEFT JOIN categories c ON c.id = l.categorie_id
"""

# Genres possibles d'un livre (genres littéraires puis genres romanesques)
GENRES = [
    "Narratif", "Théâtral", "Poétique", "Épistolaire", "Argumentatif",
    "Science-fiction", "Romance", "Thriller",
]

# Colonnes utilisables pour la recherche
COLONNES_RECHERCHE = {
    "titre": "l.titre",
    "auteur": "l.auteur",
    "genre": "l.genre",
    "categorie": "c.nom",
    "isbn": "l.isbn",
}


class Livre:
    """Accès aux livres."""

    @staticmethod
    def ajouter(isbn, titre, auteur, editeur, annee, categorie_id, prix, source, date_ajout,
                genre=None):
        """Ajoute un livre et renvoie son id."""
        return executer(
            """INSERT INTO livres (isbn, titre, auteur, editeur, annee, categorie_id,
                                   genre, prix, source, date_ajout)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (isbn, titre, auteur, editeur, annee, categorie_id, genre, prix, source,
             date_ajout),
        )

    @staticmethod
    def chercher_par_id(livre_id):
        """Renvoie un livre à partir de son id (ou None)."""
        return lire_un(REQUETE_BASE + " WHERE l.id = ?", (livre_id,))

    @staticmethod
    def chercher_par_isbn(isbn):
        """Renvoie un livre à partir de son ISBN (ou None)."""
        return lire_un(REQUETE_BASE + " WHERE l.isbn = ?", (isbn,))

    @staticmethod
    def lister():
        """Renvoie tous les livres triés par titre."""
        return lire_tous(REQUETE_BASE + " ORDER BY l.titre")

    @staticmethod
    def lister_disponibles():
        """Renvoie les livres ayant au moins un exemplaire disponible, triés par titre."""
        return lire_tous(
            REQUETE_BASE + """ WHERE EXISTS (SELECT 1 FROM exemplaires e
                                  WHERE e.livre_id = l.id AND e.statut = 'disponible')
                               ORDER BY l.titre"""
        )

    @staticmethod
    def rechercher(critere, texte):
        """Recherche les livres dont le critère (titre, auteur, genre, categorie, isbn)
        contient le texte donné (sans tenir compte des majuscules ni des accents)."""
        colonne = COLONNES_RECHERCHE[critere]
        if critere == "genre":
            # Le genre est choisi dans une liste : on cherche la valeur exacte
            return lire_tous(REQUETE_BASE + " WHERE l.genre = ? ORDER BY l.titre", (texte,))
        return lire_tous(
            REQUETE_BASE + " WHERE NORMALISER(" + colonne + ") LIKE ? ORDER BY l.titre",
            ("%" + normaliser(texte) + "%",),
        )

    @staticmethod
    def modifier(livre_id, isbn, titre, auteur, editeur, annee, categorie_id, genre, prix):
        """Met à jour les informations d'un livre."""
        executer(
            """UPDATE livres SET isbn = ?, titre = ?, auteur = ?, editeur = ?, annee = ?,
                                 categorie_id = ?, genre = ?, prix = ?
               WHERE id = ?""",
            (isbn, titre, auteur, editeur, annee, categorie_id, genre, prix, livre_id),
        )

    @staticmethod
    def definir_genre_si_vide(titre, auteur, genre):
        """Donne un genre à un livre existant qui n'en a pas encore."""
        executer(
            "UPDATE livres SET genre = ? WHERE titre = ? AND auteur = ? AND genre IS NULL",
            (genre, titre, auteur),
        )

    @staticmethod
    def a_des_emprunts(livre_id):
        """Indique si au moins un exemplaire du livre a déjà été emprunté."""
        ligne = lire_un(
            """SELECT COUNT(*) AS nombre FROM emprunts em
               JOIN exemplaires ex ON ex.id = em.exemplaire_id
               WHERE ex.livre_id = ?""",
            (livre_id,),
        )
        return ligne["nombre"] > 0

    @staticmethod
    def supprimer(livre_id):
        """Supprime un livre, ses exemplaires et ses anciennes réservations.

        Les trois suppressions sont faites dans une seule transaction.
        """
        connexion = obtenir_connexion()
        try:
            connexion.execute("DELETE FROM reservations WHERE livre_id = ?", (livre_id,))
            connexion.execute("DELETE FROM exemplaires WHERE livre_id = ?", (livre_id,))
            connexion.execute("DELETE FROM livres WHERE id = ?", (livre_id,))
            connexion.commit()
        finally:
            connexion.close()

    @staticmethod
    def compter():
        """Renvoie le nombre de livres."""
        return lire_un("SELECT COUNT(*) AS nombre FROM livres")["nombre"]

    @staticmethod
    def top_empruntes(limite):
        """Renvoie les livres les plus empruntés."""
        return lire_tous(
            """SELECT l.titre, l.auteur, COUNT(em.id) AS nombre
               FROM emprunts em
               JOIN exemplaires ex ON ex.id = em.exemplaire_id
               JOIN livres l ON l.id = ex.livre_id
               GROUP BY l.id ORDER BY nombre DESC, l.titre LIMIT ?""",
            (limite,),
        )
