"""Modèle Reservation : requêtes SQL sur la table reservations."""
from database.connexion import executer, lire_tous, lire_un

# La réservation avec le titre du livre, l'adhérent et l'exemplaire mis de côté
REQUETE_BASE = """
    SELECT r.*, l.titre, a.numero_carte, a.nom, a.prenom, ex.code AS code_exemplaire
    FROM reservations r
    JOIN livres l ON l.id = r.livre_id
    JOIN adherents a ON a.id = r.adherent_id
    LEFT JOIN exemplaires ex ON ex.id = r.exemplaire_id
"""


class Reservation:
    """Accès aux réservations (une réservation porte sur un LIVRE)."""

    @staticmethod
    def ajouter(livre_id, adherent_id, date_reservation):
        """Crée une réservation en attente et renvoie son id."""
        return executer(
            """INSERT INTO reservations (livre_id, adherent_id, date_reservation, statut)
               VALUES (?, ?, ?, 'en_attente')""",
            (livre_id, adherent_id, date_reservation),
        )

    @staticmethod
    def chercher_par_id(reservation_id):
        """Renvoie une réservation à partir de son id (ou None)."""
        return lire_un(REQUETE_BASE + " WHERE r.id = ?", (reservation_id,))

    @staticmethod
    def premiere_en_attente(livre_id):
        """Renvoie la plus ancienne réservation en attente d'un livre (ou None)."""
        return lire_un(
            REQUETE_BASE + """ WHERE r.livre_id = ? AND r.statut = 'en_attente'
                               ORDER BY r.date_reservation, r.id LIMIT 1""",
            (livre_id,),
        )

    @staticmethod
    def compter_en_attente(livre_id):
        """Renvoie le nombre de réservations en attente sur un livre."""
        ligne = lire_un(
            "SELECT COUNT(*) AS nombre FROM reservations WHERE livre_id = ? AND statut = 'en_attente'",
            (livre_id,),
        )
        return ligne["nombre"]

    @staticmethod
    def active_pour_adherent(adherent_id, livre_id):
        """Renvoie la réservation active (en attente ou disponible) de l'adhérent
        sur ce livre (ou None)."""
        return lire_un(
            REQUETE_BASE + """ WHERE r.adherent_id = ? AND r.livre_id = ?
                               AND r.statut IN ('en_attente', 'disponible')""",
            (adherent_id, livre_id),
        )

    @staticmethod
    def disponible_pour_adherent(adherent_id, livre_id):
        """Renvoie la réservation au statut 'disponible' de l'adhérent sur ce livre."""
        return lire_un(
            REQUETE_BASE + """ WHERE r.adherent_id = ? AND r.livre_id = ?
                               AND r.statut = 'disponible'""",
            (adherent_id, livre_id),
        )

    @staticmethod
    def disponible_pour_exemplaire(exemplaire_id):
        """Renvoie la réservation 'disponible' qui bloque cet exemplaire (ou None)."""
        return lire_un(
            REQUETE_BASE + " WHERE r.exemplaire_id = ? AND r.statut = 'disponible'",
            (exemplaire_id,),
        )

    @staticmethod
    def lister_actives():
        """Renvoie toutes les réservations en attente ou disponibles."""
        return lire_tous(
            REQUETE_BASE + """ WHERE r.statut IN ('en_attente', 'disponible')
                               ORDER BY r.date_reservation, r.id"""
        )

    @staticmethod
    def lister_par_adherent(adherent_id):
        """Renvoie toutes les réservations d'un adhérent (les plus récentes d'abord)."""
        return lire_tous(
            REQUETE_BASE + " WHERE r.adherent_id = ? ORDER BY r.date_reservation DESC, r.id DESC",
            (adherent_id,),
        )

    @staticmethod
    def changer_statut(reservation_id, statut):
        """Change le statut d'une réservation."""
        executer("UPDATE reservations SET statut = ? WHERE id = ?", (statut, reservation_id))

    @staticmethod
    def mettre_disponible(reservation_id, exemplaire_id):
        """Indique qu'un exemplaire a été mis de côté pour cette réservation."""
        executer(
            "UPDATE reservations SET statut = 'disponible', exemplaire_id = ? WHERE id = ?",
            (exemplaire_id, reservation_id),
        )
