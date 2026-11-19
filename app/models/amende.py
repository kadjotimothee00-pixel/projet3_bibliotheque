"""Modèle Amende : requêtes SQL sur la table amendes."""
from database.connexion import executer, lire_tous, lire_un

# L'amende avec l'adhérent et le livre concernés
REQUETE_BASE = """
    SELECT am.*, em.adherent_id, a.numero_carte, a.nom, a.prenom, l.titre, ex.code
    FROM amendes am
    JOIN emprunts em ON em.id = am.emprunt_id
    JOIN adherents a ON a.id = em.adherent_id
    JOIN exemplaires ex ON ex.id = em.exemplaire_id
    JOIN livres l ON l.id = ex.livre_id
"""


class Amende:
    """Accès aux amendes (retard, dégât, perte)."""

    @staticmethod
    def ajouter(emprunt_id, type_amende, montant, date_creation):
        """Crée une amende impayée et renvoie son id."""
        return executer(
            """INSERT INTO amendes (emprunt_id, type, montant, payee, date_creation)
               VALUES (?, ?, ?, 0, ?)""",
            (emprunt_id, type_amende, montant, date_creation),
        )

    @staticmethod
    def compter_impayees_adherent(adherent_id):
        """Renvoie le nombre d'amendes impayées d'un adhérent."""
        ligne = lire_un(
            """SELECT COUNT(*) AS nombre FROM amendes am
               JOIN emprunts em ON em.id = am.emprunt_id
               WHERE em.adherent_id = ? AND am.payee = 0""",
            (adherent_id,),
        )
        return ligne["nombre"]

    @staticmethod
    def lister_impayees():
        """Renvoie toutes les amendes impayées."""
        return lire_tous(REQUETE_BASE + " WHERE am.payee = 0 ORDER BY am.date_creation, am.id")

    @staticmethod
    def lister_par_adherent(adherent_id):
        """Renvoie toutes les amendes (payées ou non) d'un adhérent."""
        return lire_tous(
            REQUETE_BASE + " WHERE em.adherent_id = ? ORDER BY am.date_creation, am.id",
            (adherent_id,),
        )

    @staticmethod
    def encaisser(amende_id, date_paiement):
        """Marque une amende comme payée."""
        executer(
            "UPDATE amendes SET payee = 1, date_paiement = ? WHERE id = ?",
            (date_paiement, amende_id),
        )

    @staticmethod
    def total(payee):
        """Renvoie la somme des amendes payées (payee=1) ou impayées (payee=0)."""
        ligne = lire_un(
            "SELECT COALESCE(SUM(montant), 0) AS total FROM amendes WHERE payee = ?",
            (payee,),
        )
        return ligne["total"]
