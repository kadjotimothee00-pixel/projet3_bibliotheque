"""Modèle Emprunt : requêtes SQL sur la table emprunts."""
from database.connexion import executer, lire_tous, lire_un

# L'emprunt avec les informations utiles sur l'exemplaire, le livre et l'adhérent
REQUETE_BASE = """
    SELECT em.*, ex.code, ex.livre_id, l.titre, l.prix,
           a.numero_carte, a.nom, a.prenom
    FROM emprunts em
    JOIN exemplaires ex ON ex.id = em.exemplaire_id
    JOIN livres l ON l.id = ex.livre_id
    JOIN adherents a ON a.id = em.adherent_id
"""


class Emprunt:
    """Accès aux emprunts.

    Remarque : les dates sont au format AAAA-MM-JJ, on peut donc
    les comparer directement comme des textes.
    """

    @staticmethod
    def ajouter(exemplaire_id, adherent_id, date_sortie, date_retour_prevue):
        """Enregistre un nouvel emprunt en cours et renvoie son id."""
        return executer(
            """INSERT INTO emprunts (exemplaire_id, adherent_id, date_sortie,
                                     date_retour_prevue, nb_prolongations, statut)
               VALUES (?, ?, ?, ?, 0, 'en_cours')""",
            (exemplaire_id, adherent_id, date_sortie, date_retour_prevue),
        )

    @staticmethod
    def en_cours_par_exemplaire(exemplaire_id):
        """Renvoie l'emprunt en cours d'un exemplaire (ou None)."""
        return lire_un(
            REQUETE_BASE + " WHERE em.exemplaire_id = ? AND em.statut = 'en_cours'",
            (exemplaire_id,),
        )

    @staticmethod
    def lister_en_cours_adherent(adherent_id):
        """Renvoie les emprunts en cours d'un adhérent."""
        return lire_tous(
            REQUETE_BASE + """ WHERE em.adherent_id = ? AND em.statut = 'en_cours'
                               ORDER BY em.date_retour_prevue""",
            (adherent_id,),
        )

    @staticmethod
    def compter_en_cours_adherent(adherent_id):
        """Renvoie le nombre d'emprunts en cours d'un adhérent."""
        ligne = lire_un(
            "SELECT COUNT(*) AS nombre FROM emprunts WHERE adherent_id = ? AND statut = 'en_cours'",
            (adherent_id,),
        )
        return ligne["nombre"]

    @staticmethod
    def compter_retards_adherent(adherent_id, aujourdhui):
        """Renvoie le nombre d'emprunts en retard d'un adhérent."""
        ligne = lire_un(
            """SELECT COUNT(*) AS nombre FROM emprunts
               WHERE adherent_id = ? AND statut = 'en_cours' AND date_retour_prevue < ?""",
            (adherent_id, aujourdhui),
        )
        return ligne["nombre"]

    @staticmethod
    def a_livre_en_cours(adherent_id, livre_id):
        """Indique si l'adhérent a déjà un exemplaire de ce livre en emprunt."""
        ligne = lire_un(
            """SELECT COUNT(*) AS nombre FROM emprunts em
               JOIN exemplaires ex ON ex.id = em.exemplaire_id
               WHERE em.adherent_id = ? AND ex.livre_id = ? AND em.statut = 'en_cours'""",
            (adherent_id, livre_id),
        )
        return ligne["nombre"] > 0

    @staticmethod
    def lister_retards(aujourdhui):
        """Renvoie tous les emprunts en cours dont la date de retour est dépassée."""
        return lire_tous(
            REQUETE_BASE + """ WHERE em.statut = 'en_cours' AND em.date_retour_prevue < ?
                               ORDER BY em.date_retour_prevue""",
            (aujourdhui,),
        )

    @staticmethod
    def prolonger(emprunt_id, nouvelle_date):
        """Repousse la date de retour et ajoute 1 au nombre de prolongations."""
        executer(
            """UPDATE emprunts SET date_retour_prevue = ?, nb_prolongations = nb_prolongations + 1
               WHERE id = ?""",
            (nouvelle_date, emprunt_id),
        )

    @staticmethod
    def terminer(emprunt_id, date_retour):
        """Clôture un emprunt (retour ou perte)."""
        executer(
            "UPDATE emprunts SET date_retour_reelle = ?, statut = 'termine' WHERE id = ?",
            (date_retour, emprunt_id),
        )

    @staticmethod
    def compter_en_cours():
        """Renvoie le nombre total d'emprunts en cours."""
        return lire_un(
            "SELECT COUNT(*) AS nombre FROM emprunts WHERE statut = 'en_cours'"
        )["nombre"]

    @staticmethod
    def compter_retards(aujourdhui):
        """Renvoie le nombre total d'emprunts en retard."""
        return lire_un(
            """SELECT COUNT(*) AS nombre FROM emprunts
               WHERE statut = 'en_cours' AND date_retour_prevue < ?""",
            (aujourdhui,),
        )["nombre"]
