"""Modèle Bibliothecaire : requêtes SQL sur la table bibliothecaire."""
from database.connexion import executer, lire_un


class Bibliothecaire:
    """Accès au compte du bibliothécaire."""

    @staticmethod
    def chercher():
        """Renvoie le compte bibliothécaire (ou None s'il n'existe pas encore)."""
        return lire_un("SELECT * FROM bibliothecaire ORDER BY id LIMIT 1")

    @staticmethod
    def chercher_par_identifiant(identifiant):
        """Renvoie le compte correspondant à cet identifiant (ou None)."""
        return lire_un("SELECT * FROM bibliothecaire WHERE identifiant = ?", (identifiant,))

    @staticmethod
    def ajouter(identifiant, mot_de_passe_hash, sel):
        """Crée le compte bibliothécaire."""
        executer(
            "INSERT INTO bibliothecaire (identifiant, mot_de_passe_hash, sel) VALUES (?, ?, ?)",
            (identifiant, mot_de_passe_hash, sel),
        )

    @staticmethod
    def modifier_mot_de_passe(compte_id, mot_de_passe_hash, sel):
        """Remplace le mot de passe (haché) du compte."""
        executer(
            "UPDATE bibliothecaire SET mot_de_passe_hash = ?, sel = ? WHERE id = ?",
            (mot_de_passe_hash, sel, compte_id),
        )

    @staticmethod
    def modifier_identifiant(compte_id, identifiant):
        """Remplace l'identifiant de connexion du compte."""
        executer(
            "UPDATE bibliothecaire SET identifiant = ? WHERE id = ?",
            (identifiant, compte_id),
        )
