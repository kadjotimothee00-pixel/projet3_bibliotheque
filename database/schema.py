"""Création des tables de la base de données."""
from database.connexion import obtenir_connexion

TABLES = [
    """
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS livres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        isbn TEXT UNIQUE,
        titre TEXT NOT NULL,
        auteur TEXT NOT NULL,
        editeur TEXT,
        annee INTEGER,
        categorie_id INTEGER REFERENCES categories(id),
        genre TEXT,
        prix INTEGER NOT NULL,
        source TEXT NOT NULL DEFAULT 'manuel' CHECK (source IN ('manuel', 'api')),
        date_ajout TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS exemplaires (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        livre_id INTEGER NOT NULL REFERENCES livres(id),
        etat TEXT NOT NULL DEFAULT 'bon'
            CHECK (etat IN ('bon', 'abime', 'perdu')),
        statut TEXT NOT NULL DEFAULT 'disponible'
            CHECK (statut IN ('disponible', 'emprunte', 'en_consultation',
                              'reserve', 'indisponible'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS adherents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_carte TEXT NOT NULL UNIQUE,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        telephone TEXT NOT NULL,
        email TEXT,
        date_inscription TEXT NOT NULL,
        statut TEXT NOT NULL DEFAULT 'actif' CHECK (statut IN ('actif', 'bloque'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS emprunts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exemplaire_id INTEGER NOT NULL REFERENCES exemplaires(id),
        adherent_id INTEGER NOT NULL REFERENCES adherents(id),
        date_sortie TEXT NOT NULL,
        date_retour_prevue TEXT NOT NULL,
        date_retour_reelle TEXT,
        nb_prolongations INTEGER NOT NULL DEFAULT 0,
        statut TEXT NOT NULL DEFAULT 'en_cours' CHECK (statut IN ('en_cours', 'termine'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        livre_id INTEGER NOT NULL REFERENCES livres(id),
        adherent_id INTEGER NOT NULL REFERENCES adherents(id),
        exemplaire_id INTEGER REFERENCES exemplaires(id),
        date_reservation TEXT NOT NULL,
        statut TEXT NOT NULL DEFAULT 'en_attente'
            CHECK (statut IN ('en_attente', 'disponible', 'terminee', 'annulee'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS amendes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emprunt_id INTEGER NOT NULL REFERENCES emprunts(id),
        type TEXT NOT NULL CHECK (type IN ('retard', 'degat', 'perte')),
        montant INTEGER NOT NULL,
        payee INTEGER NOT NULL DEFAULT 0,
        date_creation TEXT NOT NULL,
        date_paiement TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS parametres (
        nom TEXT PRIMARY KEY,
        valeur TEXT NOT NULL,
        description TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS bibliothecaire (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        identifiant TEXT NOT NULL UNIQUE,
        mot_de_passe_hash TEXT NOT NULL,
        sel TEXT NOT NULL
    )
    """,
]


def ajouter_colonne_genre(connexion):
    """Ajoute la colonne genre à une ancienne base qui ne l'a pas encore."""
    colonnes = [ligne["name"] for ligne in connexion.execute("PRAGMA table_info(livres)")]
    if "genre" not in colonnes:
        connexion.execute("ALTER TABLE livres ADD COLUMN genre TEXT")


def creer_tables():
    """Crée toutes les tables si elles n'existent pas encore."""
    connexion = obtenir_connexion()
    try:
        for requete in TABLES:
            connexion.execute(requete)
        ajouter_colonne_genre(connexion)
        connexion.commit()
    finally:
        connexion.close()
