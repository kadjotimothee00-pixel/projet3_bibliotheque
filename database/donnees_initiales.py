"""Insertion des données de départ (uniquement si les tables sont vides)."""
from datetime import date

from app.models.categorie import Categorie
from app.models.exemplaire import Exemplaire
from app.models.livre import Livre
from app.models.parametre import Parametre

CATEGORIES = [
    "Littérature", "Sciences", "Histoire", "Informatique", "Philosophie",
    "Droit", "Économie", "Jeunesse", "Religion", "Arts",
]

# (nom, valeur, description)
PARAMETRES = [
    ("max_livres", "3", "Nombre maximum d'emprunts en cours par adhérent"),
    ("duree_pret", "14", "Durée d'un prêt en jours"),
    ("duree_prolongation", "2", "Nombre de jours ajoutés par une prolongation"),
    ("max_prolongations", "1", "Nombre maximum de prolongations par emprunt"),
    ("amende_par_jour", "100", "Amende en FCFA par jour de retard et par livre"),
    ("prix_defaut", "5000", "Prix en FCFA utilisé si le livre n'a pas de prix saisi"),
    ("pourcentage_degat", "50", "Pourcentage du prix du livre payé pour un livre abîmé"),
]

# (titre, auteur, éditeur, année, catégorie, prix en FCFA, nombre d'exemplaires)
# Les ISBN sont laissés vides : on préfère ne pas en inventer.
LIVRES = [
    ("Climbié", "Bernard Dadié", "Seghers", 1956, "Littérature", 4000, 2),
    ("Un Nègre à Paris", "Bernard Dadié", "Présence Africaine", 1959, "Littérature", 3500, 1),
    ("Le Pagne noir", "Bernard Dadié", "Présence Africaine", 1955, "Jeunesse", 3000, 2),
    ("Les Soleils des indépendances", "Ahmadou Kourouma", "Seuil", 1970, "Littérature", 5000, 3),
    ("Allah n'est pas obligé", "Ahmadou Kourouma", "Seuil", 2000, "Littérature", 6000, 2),
    ("En attendant le vote des bêtes sauvages", "Ahmadou Kourouma", "Seuil", 1998,
     "Littérature", 6500, 1),
    ("L'Enfant noir", "Camara Laye", "Plon", 1953, "Littérature", 4000, 3),
    ("Le Regard du roi", "Camara Laye", "Plon", 1954, "Littérature", 4500, 1),
    ("Reine Pokou", "Véronique Tadjo", "Actes Sud", 2004, "Littérature", 5500, 2),
    ("L'Étrange Destin de Wangrin", "Amadou Hampâté Bâ", "10/18", 1973, "Littérature", 5000, 2),
    ("Amkoullel, l'enfant peul", "Amadou Hampâté Bâ", "Actes Sud", 1991, "Histoire", 6000, 1),
    ("Une si longue lettre", "Mariama Bâ", "Nouvelles Éditions Africaines", 1979,
     "Littérature", 3000, 2),
    ("Les Contes d'Amadou Koumba", "Birago Diop", "Présence Africaine", 1947, "Jeunesse", 3000, 2),
    ("Nations nègres et culture", "Cheikh Anta Diop", "Présence Africaine", 1954,
     "Histoire", 7000, 1),
    ("Discours sur le colonialisme", "Aimé Césaire", "Présence Africaine", 1950,
     "Philosophie", 2500, 2),
    ("Les Misérables", "Victor Hugo", None, 1862, "Littérature", 8000, 2),
    ("L'Étranger", "Albert Camus", "Gallimard", 1942, "Littérature", 3500, 3),
    ("La Peste", "Albert Camus", "Gallimard", 1947, "Littérature", 4000, 2),
    ("Le Mythe de Sisyphe", "Albert Camus", "Gallimard", 1942, "Philosophie", 3500, 1),
    ("Le Petit Prince", "Antoine de Saint-Exupéry", "Gallimard", 1943, "Jeunesse", 3500, 2),
    ("Discours de la méthode", "René Descartes", None, 1637, "Philosophie", 2500, 1),
    ("De l'esprit des lois", "Montesquieu", None, 1748, "Droit", 6000, 1),
    ("L'Origine des espèces", "Charles Darwin", None, 1859, "Sciences", 7000, 1),

    # --- Littérature ---
    ("Les Bouts de bois de Dieu", "Ousmane Sembène", None, 1960, "Littérature", 5000, 2),
    ("L'Aventure ambiguë", "Cheikh Hamidou Kane", "Julliard", 1961, "Littérature", 4000, 2),
    ("Le Pauvre Christ de Bomba", "Mongo Beti", "Robert Laffont", 1956, "Littérature", 4500, 1),
    ("Germinal", "Émile Zola", None, 1885, "Littérature", 5000, 2),
    ("Madame Bovary", "Gustave Flaubert", None, 1857, "Littérature", 4500, 2),

    # --- Sciences ---
    ("Physique nucléaire et chronologie absolue", "Cheikh Anta Diop", "IFAN", 1974,
     "Sciences", 8000, 1),
    ("Une brève histoire du temps", "Stephen Hawking", "Flammarion", 1988, "Sciences", 6000, 2),
    ("Le Hasard et la Nécessité", "Jacques Monod", "Seuil", 1970, "Sciences", 5000, 1),
    ("La Science et l'Hypothèse", "Henri Poincaré", "Flammarion", 1902, "Sciences", 4500, 1),
    ("Le Gène égoïste", "Richard Dawkins", None, 1976, "Sciences", 7000, 1),

    # --- Histoire ---
    ("Soundjata ou l'épopée mandingue", "Djibril Tamsir Niane", "Présence Africaine", 1960,
     "Histoire", 3500, 3),
    ("Histoire de l'Afrique noire", "Joseph Ki-Zerbo", "Hatier", 1972, "Histoire", 9000, 1),
    ("Antériorité des civilisations nègres", "Cheikh Anta Diop", "Présence Africaine", 1967,
     "Histoire", 7000, 1),
    ("L'Ancien Régime et la Révolution", "Alexis de Tocqueville", None, 1856, "Histoire", 5000, 1),
    ("La Méditerranée et le monde méditerranéen à l'époque de Philippe II", "Fernand Braudel",
     "Armand Colin", 1949, "Histoire", 12000, 1),

    # --- Informatique ---
    ("Algorithms + Data Structures = Programs", "Niklaus Wirth", "Prentice Hall", 1976,
     "Informatique", 10000, 1),
    ("A Discipline of Programming", "Edsger W. Dijkstra", "Prentice Hall", 1976,
     "Informatique", 10000, 1),
    ("Apprendre à programmer avec Python", "Gérard Swinnen", "Eyrolles", 2009,
     "Informatique", 8000, 3),
    ("Programmer en Java", "Claude Delannoy", "Eyrolles", 2000, "Informatique", 9000, 2),
    ("Réseaux", "Andrew Tanenbaum", None, 1981, "Informatique", 12000, 1),

    # --- Philosophie ---
    ("La Philosophie bantoue", "Placide Tempels", "Présence Africaine", 1949,
     "Philosophie", 3500, 1),
    ("Sur la « philosophie africaine »", "Paulin Hountondji", "Maspero", 1976,
     "Philosophie", 4500, 1),
    ("Pensées", "Blaise Pascal", None, 1670, "Philosophie", 3000, 2),
    ("Ainsi parlait Zarathoustra", "Friedrich Nietzsche", None, 1883, "Philosophie", 4000, 1),
    ("Du contrat social", "Jean-Jacques Rousseau", None, 1762, "Philosophie", 2500, 2),

    # --- Droit ---
    ("Des délits et des peines", "Cesare Beccaria", None, 1764, "Droit", 3000, 1),
    ("Les Droits de l'homme en Afrique", "Kéba Mbaye", "Pedone", 1992, "Droit", 9000, 1),
    ("Théorie pure du droit", "Hans Kelsen", None, 1934, "Droit", 8000, 1),
    ("La Lutte pour le droit", "Rudolf von Jhering", None, 1872, "Droit", 3500, 1),
    ("Flexible droit", "Jean Carbonnier", "LGDJ", 1969, "Droit", 7000, 1),

    # --- Économie ---
    ("La Richesse des nations", "Adam Smith", None, 1776, "Économie", 6000, 1),
    ("Le Capital", "Karl Marx", None, 1867, "Économie", 8000, 1),
    ("L'Accumulation à l'échelle mondiale", "Samir Amin", "Anthropos", 1970,
     "Économie", 7000, 1),
    ("Et si l'Afrique refusait le développement ?", "Axelle Kabou", "L'Harmattan", 1991,
     "Économie", 4500, 2),
    ("Le Capital au XXIe siècle", "Thomas Piketty", "Seuil", 2013, "Économie", 12000, 1),

    # --- Jeunesse ---
    ("La Belle Histoire de Leuk-le-Lièvre", "Léopold Sédar Senghor et Abdoulaye Sadji",
     "Hachette", 1953, "Jeunesse", 3000, 3),
    ("Akissi", "Marguerite Abouet et Mathieu Sapin", "Gallimard Jeunesse", 2010,
     "Jeunesse", 4000, 2),
    ("Le Petit Nicolas", "René Goscinny et Jean-Jacques Sempé", "Denoël", 1960,
     "Jeunesse", 3500, 2),
    ("Vingt mille lieues sous les mers", "Jules Verne", "Hetzel", 1870, "Jeunesse", 4000, 2),
    ("Les Malheurs de Sophie", "Comtesse de Ségur", "Hachette", 1858, "Jeunesse", 3000, 2),

    # --- Religion ---
    ("Dieu d'eau", "Marcel Griaule", "Éditions du Chêne", 1948, "Religion", 5000, 1),
    ("Religions et philosophie africaines", "John Mbiti", None, 1969, "Religion", 6000, 1),
    ("Vie et enseignement de Tierno Bokar, le sage de Bandiagara", "Amadou Hampâté Bâ",
     "Seuil", 1980, "Religion", 5000, 1),
    # Écrit vers l'an 400 : année laissée vide (l'application accepte 1000 minimum)
    ("Les Confessions", "Saint Augustin", None, None, "Religion", 4000, 1),
    ("Les Formes élémentaires de la vie religieuse", "Émile Durkheim", "Alcan", 1912,
     "Religion", 6000, 1),

    # --- Arts ---
    ("Histoire de l'art", "Ernst Gombrich", "Phaidon", 1950, "Arts", 15000, 1),
    ("Les Arts de l'Afrique noire", "Jean Laude", "Le Livre de Poche", 1966, "Arts", 5000, 1),
    ("Musique de l'Afrique", "Francis Bebey", "Horizons de France", 1969, "Arts", 6000, 1),
    ("Du spirituel dans l'art", "Wassily Kandinsky", None, 1911, "Arts", 4000, 1),
    ("Le Musée imaginaire", "André Malraux", "Skira", 1947, "Arts", 7000, 1),
]

# Genre de chaque livre de départ (clé = titre).
# Les manuels d'informatique n'ont pas de genre littéraire : ils restent sans genre.
GENRES_LIVRES = {
    # Narratif : romans, récits, contes, épopées, autobiographies
    "Climbié": "Narratif",
    "Le Pagne noir": "Narratif",
    "Les Soleils des indépendances": "Narratif",
    "Allah n'est pas obligé": "Narratif",
    "En attendant le vote des bêtes sauvages": "Narratif",
    "L'Enfant noir": "Narratif",
    "Le Regard du roi": "Narratif",
    "Reine Pokou": "Narratif",
    "L'Étrange Destin de Wangrin": "Narratif",
    "Amkoullel, l'enfant peul": "Narratif",
    "Les Contes d'Amadou Koumba": "Narratif",
    "Les Misérables": "Narratif",
    "L'Étranger": "Narratif",
    "La Peste": "Narratif",
    "Le Petit Prince": "Narratif",
    "Les Bouts de bois de Dieu": "Narratif",
    "L'Aventure ambiguë": "Narratif",
    "Le Pauvre Christ de Bomba": "Narratif",
    "Germinal": "Narratif",
    "Madame Bovary": "Narratif",
    "Soundjata ou l'épopée mandingue": "Narratif",
    "Histoire de l'Afrique noire": "Narratif",
    "La Belle Histoire de Leuk-le-Lièvre": "Narratif",
    "Akissi": "Narratif",
    "Le Petit Nicolas": "Narratif",
    "Les Malheurs de Sophie": "Narratif",
    "Dieu d'eau": "Narratif",
    "Vie et enseignement de Tierno Bokar, le sage de Bandiagara": "Narratif",
    "Les Confessions": "Narratif",

    # Épistolaire : œuvres écrites sous forme de lettres
    "Une si longue lettre": "Épistolaire",
    "Un Nègre à Paris": "Épistolaire",

    # Poétique : prose poétique
    "Ainsi parlait Zarathoustra": "Poétique",

    # Science-fiction
    "Vingt mille lieues sous les mers": "Science-fiction",

    # Argumentatif : essais, traités, discours
    "Nations nègres et culture": "Argumentatif",
    "Discours sur le colonialisme": "Argumentatif",
    "Le Mythe de Sisyphe": "Argumentatif",
    "Discours de la méthode": "Argumentatif",
    "De l'esprit des lois": "Argumentatif",
    "L'Origine des espèces": "Argumentatif",
    "Physique nucléaire et chronologie absolue": "Argumentatif",
    "Une brève histoire du temps": "Argumentatif",
    "Le Hasard et la Nécessité": "Argumentatif",
    "La Science et l'Hypothèse": "Argumentatif",
    "Le Gène égoïste": "Argumentatif",
    "Antériorité des civilisations nègres": "Argumentatif",
    "L'Ancien Régime et la Révolution": "Argumentatif",
    "La Méditerranée et le monde méditerranéen à l'époque de Philippe II": "Argumentatif",
    "La Philosophie bantoue": "Argumentatif",
    "Sur la « philosophie africaine »": "Argumentatif",
    "Pensées": "Argumentatif",
    "Du contrat social": "Argumentatif",
    "Des délits et des peines": "Argumentatif",
    "Les Droits de l'homme en Afrique": "Argumentatif",
    "Théorie pure du droit": "Argumentatif",
    "La Lutte pour le droit": "Argumentatif",
    "Flexible droit": "Argumentatif",
    "La Richesse des nations": "Argumentatif",
    "Le Capital": "Argumentatif",
    "L'Accumulation à l'échelle mondiale": "Argumentatif",
    "Et si l'Afrique refusait le développement ?": "Argumentatif",
    "Le Capital au XXIe siècle": "Argumentatif",
    "Religions et philosophie africaines": "Argumentatif",
    "Les Formes élémentaires de la vie religieuse": "Argumentatif",
    "Histoire de l'art": "Argumentatif",
    "Les Arts de l'Afrique noire": "Argumentatif",
    "Musique de l'Afrique": "Argumentatif",
    "Du spirituel dans l'art": "Argumentatif",
    "Le Musée imaginaire": "Argumentatif",
}


def inserer_categories():
    """Insère les catégories de départ si la table est vide."""
    if Categorie.compter() > 0:
        return
    for nom in CATEGORIES:
        Categorie.ajouter(nom)


def inserer_parametres():
    """Insère les paramètres par défaut si la table est vide."""
    if Parametre.compter() > 0:
        return
    for nom, valeur, description in PARAMETRES:
        Parametre.ajouter(nom, valeur, description)


def inserer_livres():
    """Insère les livres de départ et leurs exemplaires si la table est vide."""
    if Livre.compter() > 0:
        return
    aujourdhui = date.today().isoformat()
    for titre, auteur, editeur, annee, nom_categorie, prix, nb_exemplaires in LIVRES:
        categorie = Categorie.chercher_par_nom(nom_categorie)
        categorie_id = categorie["id"] if categorie else None
        livre_id = Livre.ajouter(None, titre, auteur, editeur, annee, categorie_id,
                                 prix, "manuel", aujourdhui, GENRES_LIVRES.get(titre))
        for _ in range(nb_exemplaires):
            Exemplaire.ajouter(livre_id)


def completer_genres():
    """Donne leur genre aux livres de départ d'une ancienne base
    (créée avant l'ajout des genres). Ne modifie pas un genre déjà défini."""
    for titre, auteur, _, _, _, _, _ in LIVRES:
        genre = GENRES_LIVRES.get(titre)
        if genre is not None:
            Livre.definir_genre_si_vide(titre, auteur, genre)


def inserer_donnees_initiales():
    """Insère toutes les données de départ (sans jamais créer de doublons)."""
    inserer_categories()
    inserer_parametres()
    inserer_livres()
    completer_genres()
