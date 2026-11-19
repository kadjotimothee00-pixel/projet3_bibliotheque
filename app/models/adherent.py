"""Modèle Adherent : requêtes SQL sur la table adherents."""
from database.connexion import executer, lire_tous, lire_un, normaliser


class Adherent:
    """Accès aux adhérents (lecteurs inscrits)."""

    @staticmethod
    def generer_numero():
        """Calcule le prochain numéro de carte libre : AD-0001, AD-0002, ..."""
        ligne = lire_un(
            "SELECT MAX(CAST(SUBSTR(numero_carte, 4) AS INTEGER)) AS maxi FROM adherents"
        )
        dernier = ligne["maxi"] or 0
        return "AD-" + str(dernier + 1).zfill(4)

    @staticmethod
    def ajouter(nom, prenom, telephone, email, date_inscription):
        """Inscrit un adhérent (statut actif) et renvoie son numéro de carte."""
        numero = Adherent.generer_numero()
        executer(
            """INSERT INTO adherents (numero_carte, nom, prenom, telephone, email,
                                      date_inscription, statut)
               VALUES (?, ?, ?, ?, ?, ?, 'actif')""",
            (numero, nom, prenom, telephone, email, date_inscription),
        )
        return numero

    @staticmethod
    def chercher_par_id(adherent_id):
        """Renvoie un adhérent à partir de son id (ou None)."""
        return lire_un("SELECT * FROM adherents WHERE id = ?", (adherent_id,))

    @staticmethod
    def chercher_par_numero(numero_carte):
        """Renvoie un adhérent à partir de son numéro de carte (ou None)."""
        return lire_un("SELECT * FROM adherents WHERE numero_carte = ?", (numero_carte,))

    @staticmethod
    def rechercher(texte):
        """Recherche par numéro de carte, nom ou prénom
        (sans tenir compte des majuscules ni des accents)."""
        motif = "%" + normaliser(texte) + "%"
        return lire_tous(
            """SELECT * FROM adherents
               WHERE NORMALISER(numero_carte) LIKE ? OR NORMALISER(nom) LIKE ?
                  OR NORMALISER(prenom) LIKE ?
               ORDER BY nom, prenom""",
            (motif, motif, motif),
        )

    @staticmethod
    def lister():
        """Renvoie tous les adhérents triés par nom."""
        return lire_tous("SELECT * FROM adherents ORDER BY nom, prenom")

    @staticmethod
    def modifier(adherent_id, nom, prenom, telephone, email):
        """Met à jour les coordonnées d'un adhérent."""
        executer(
            "UPDATE adherents SET nom = ?, prenom = ?, telephone = ?, email = ? WHERE id = ?",
            (nom, prenom, telephone, email, adherent_id),
        )

    @staticmethod
    def changer_statut(adherent_id, statut):
        """Passe un adhérent en 'actif' ou 'bloque'."""
        executer("UPDATE adherents SET statut = ? WHERE id = ?", (statut, adherent_id))

    @staticmethod
    def compter_par_statut():
        """Renvoie le nombre d'adhérents pour chaque statut."""
        return lire_tous("SELECT statut, COUNT(*) AS nombre FROM adherents GROUP BY statut")
