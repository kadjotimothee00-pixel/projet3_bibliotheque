# Gestion de bibliothèque

Application console de gestion de bibliothèque écrite en Python 3, avec une base de données SQLite et une architecture MVC (Modèle, Vue, Contrôleur).

---

## 1. Présentation du projet

Ce programme permet de gérer une petite bibliothèque depuis un terminal :

- le **bibliothécaire** gère le catalogue (livres et exemplaires), les adhérents, les retours, les pertes, les amendes, les réservations et les paramètres ;
- n'importe quel visiteur peut **lire sur place** sans s'identifier ;
- un **adhérent** inscrit peut emprunter, prolonger, réserver et consulter son compte avec son numéro de carte.

Toutes les données sont enregistrées dans un fichier SQLite : rien n'est perdu quand on quitte le programme. Les livres peuvent être ajoutés automatiquement à partir de leur ISBN grâce à l'API Open Library (gratuite, sans clé).

---

## 2. Installation et lancement

**Prérequis** : Python 3.8 ou plus récent, et une connexion internet (seulement pour l'ajout de livres par ISBN).

```
cd bibliotheque
python -m venv .venv
.venv\Scripts\activate            (Windows)
source .venv/bin/activate         (Linux / macOS)
pip install -r requirements.txt
python main.py
```

**Au premier lancement**, le programme crée le fichier `data/bibliotheque.db` et ses tables, puis insère les données de départ : 10 catégories, 7 paramètres et 73 livres (auteurs ivoiriens, africains et classiques), soit 109 exemplaires. Il demande ensuite de créer le compte bibliothécaire (identifiant et mot de passe de 4 caractères minimum, saisie masquée).

Aux lancements suivants, rien n'est recréé ni dupliqué. Si la base date d'une ancienne version, la colonne `genre` est ajoutée automatiquement et les livres de départ reçoivent leur genre.

---

## 3. Fonctionnalités

### Menu principal

```
==========================================
     GESTION DE BIBLIOTHÈQUE
==========================================
1. Bibliothécaire
2. Lire sur place
3. Emprunter
0. Quitter
```

### 3.1 Espace Bibliothécaire (identifiant + mot de passe, 3 tentatives)

| N° | Menu | Contenu |
|---|---|---|
| 1 | Gestion des livres | Ajouter (par ISBN avec Open Library ou saisie manuelle), modifier, supprimer, rechercher, lister |
| 2 | Gestion des exemplaires | Ajouter des exemplaires, changer l'état, lister les exemplaires d'un livre |
| 3 | Gestion des adhérents | Inscrire, modifier, rechercher, lister, bloquer / débloquer |
| 4 | Enregistrer un retour | Code de l'exemplaire, état constaté, calcul automatique des amendes |
| 5 | Déclarer un livre perdu | Amende de perte (+ retard éventuel) |
| 6 | Amendes | Impayées, encaissement, historique d'un adhérent |
| 7 | Emprunts en retard | Jours de retard et amende due aujourd'hui |
| 8 | Réservations | Lister, annuler |
| 9 | Statistiques | Livres, exemplaires, adhérents, emprunts, amendes, top 5, répartition par catégorie |
| 10 | Paramètres | Modifier les règles, changer le mot de passe ou l'identifiant |

### 3.2 Recherche d'un livre

```
1. Par titre
2. Par auteur
3. Par genre
4. Par catégorie
5. Par ISBN          (espace bibliothécaire uniquement)
0. Annuler
```

- La recherche ne tient compte ni des majuscules ni des accents (`climbie` trouve *Climbié*).
- **Par genre** : on choisit dans une liste : Narratif, Théâtral, Poétique, Épistolaire, Argumentatif, Science-fiction, Romance, Thriller.
- **Par ISBN** : tout ou partie de l'ISBN, avec ou sans tirets. Cette option n'apparaît pas côté lecteur.

### 3.3 Lire sur place (sans identification)

1. Afficher les livres disponibles
2. Rechercher un livre
3. Voir la disponibilité d'un livre (exemplaires et statut)
4. Consulter un livre : un exemplaire disponible passe en `en_consultation` et son code est affiché
5. Rendre le livre consulté : saisie du code, l'exemplaire redevient `disponible` (ou est mis de côté s'il est réservé)

### 3.4 Emprunter (numéro de carte `AD-0001` ou simplement `1`)

1. Afficher les livres disponibles
2. Rechercher un livre
3. Emprunter un livre (par recherche ou par code d'exemplaire)
4. Prolonger un emprunt
5. Réserver un livre indisponible
6. Voir mes emprunts, réservations et amendes

Le retour d'un livre emprunté est toujours enregistré par le bibliothécaire, qui juge son état.

---

## 4. Technologies utilisées

- **Python 3** et **SQLite** (module standard `sqlite3`)
- **requests** (seule dépendance externe) pour l'**API Open Library**
- Modules standard : `hashlib` et `secrets` (mot de passe), `getpass`, `datetime`, `unicodedata` (recherche sans accents)

---

## 5. Architecture MVC

```
bibliotheque/
├── main.py                 point d'entrée
├── config.py               chemin de la base, URL de l'API
├── requirements.txt
├── app/
│   ├── models/             requêtes SQL (une classe par table)
│   ├── views/              menus, saisies, tableaux
│   └── controllers/        règles de gestion
├── database/               connexion, création des tables, données de départ
├── services/
│   └── open_library.py     appel à l'API Open Library
└── data/
    └── bibliotheque.db     créé automatiquement
```

```
 Utilisateur  <-->  VUE  <-->  CONTRÔLEUR  <-->  MODÈLE  <-->  Base SQLite
                                   |
                                   +-->  SERVICE (Open Library)
```

- La **vue** affiche et lit le clavier, sans SQL ni règle de gestion.
- Le **contrôleur** applique les règles (peut-on emprunter ? combien coûte l'amende ?).
- Le **modèle** contient uniquement les requêtes SQL, sans `print` ni `input`.

---

## 6. Base de données

Dates au format `AAAA-MM-JJ` (affichées `JJ/MM/AAAA`), montants en FCFA (entiers).

| Table | Colonnes principales | Remarques |
|---|---|---|
| `categories` | id, nom | nom unique |
| `livres` | id, isbn, titre, auteur, editeur, annee, categorie_id, genre, prix, source, date_ajout | isbn unique (peut être vide), genre peut être vide, source = `manuel` / `api` |
| `exemplaires` | id, code, livre_id, etat, statut | code `EX-0001` ; etat = `bon` / `abime` / `perdu` ; statut = `disponible` / `emprunte` / `en_consultation` / `reserve` / `indisponible` |
| `adherents` | id, numero_carte, nom, prenom, telephone, email, date_inscription, statut | carte `AD-0001`, statut = `actif` / `bloque` |
| `emprunts` | id, exemplaire_id, adherent_id, dates, nb_prolongations, statut | `en_cours` / `termine` |
| `reservations` | id, livre_id, adherent_id, exemplaire_id, date_reservation, statut | `en_attente` / `disponible` / `terminee` / `annulee` |
| `amendes` | id, emprunt_id, type, montant, payee, dates | type = `retard` / `degat` / `perte` |
| `parametres` | nom, valeur, description | règles modifiables |
| `bibliothecaire` | id, identifiant, mot_de_passe_hash, sel | mot de passe jamais stocké en clair |

```
categories 1 ---- n livres 1 ---- n exemplaires 1 ---- n emprunts n ---- 1 adherents
                     |                                     |
                     n reservations n ---- 1 adherents     n amendes
```

---

## 7. Règles de gestion

### 7.1 Paramètres par défaut (modifiables dans le menu Paramètres)

| Nom | Valeur | Description |
|---|---|---|
| max_livres | 3 | emprunts en cours maximum par adhérent |
| duree_pret | 14 | durée d'un prêt (jours) |
| duree_prolongation | 2 | jours ajoutés par prolongation |
| max_prolongations | 1 | prolongations maximum par emprunt |
| amende_par_jour | 100 | amende par jour de retard (FCFA) |
| prix_defaut | 5000 | prix si aucun prix n'est saisi (FCFA) |
| pourcentage_degat | 50 | part du prix payée pour un livre abîmé |

Ces valeurs sont relues à chaque opération ; les modifier ne change pas les emprunts déjà enregistrés.

### 7.2 Emprunt

L'adhérent doit être `actif`, sans amende impayée, sans emprunt en retard et avoir moins de `max_livres` emprunts. L'exemplaire doit être `disponible` (ou `reserve` pour cet adhérent). Date de retour prévue = aujourd'hui + `duree_pret`.

### 7.3 Amendes

| Situation | Calcul | Exemple |
|---|---|---|
| Retard | jours de retard x `amende_par_jour` | 5 jours : **500 FCFA** |
| Livre abîmé | prix x `pourcentage_degat` / 100 | livre à 4 000 FCFA : **2 000 FCFA** |
| Livre perdu | 100 % du prix (+ retard éventuel) | livre à 6 000 FCFA : **6 000 FCFA** |

Tant qu'une amende n'est pas payée, l'adhérent ne peut ni emprunter ni réserver.

### 7.4 Prolongations et réservations

- **Prolongation** : refusée si l'adhérent est bloqué, si l'emprunt est en retard, si `max_prolongations` est atteint ou si un autre lecteur a réservé le livre.
- **Réservation** : porte sur un livre (pas un exemplaire), seulement si aucun exemplaire n'est disponible. Les réservations sont servies dans l'ordre d'arrivée : au retour, l'exemplaire passe en `reserve` pour le premier lecteur en attente.

### 7.5 Autres règles

- **Suppression d'un livre** : refusée s'il a un exemplaire sorti ou réservé, des réservations en attente, ou un historique d'emprunts.
- **Codes** `EX-0001` et `AD-0001` : générés automatiquement.

---

## 8. Guide d'utilisation

Dans tous les menus, on tape le numéro de l'option puis Entrée ; `0` revient en arrière ou annule.

| Action | Chemin |
|---|---|
| Ajouter un livre par ISBN | Bibliothécaire → `1` Livres → `1` Ajouter → `1` Par ISBN, puis confirmer le résultat d'Open Library, choisir catégorie, genre, prix et nombre d'exemplaires |
| Donner un genre à un livre | Bibliothécaire → `1` Livres → `2` Modifier → répondre `O` à « Changer le genre » |
| Inscrire un adhérent | Bibliothécaire → `3` Adhérents → `1` Inscrire ; le numéro de carte s'affiche |
| Emprunter | `3` Emprunter → numéro de carte → `3` Emprunter un livre |
| Prolonger / réserver | Espace lecteur → `4` ou `5` |
| Enregistrer un retour | Bibliothécaire → `4`, code de l'exemplaire, état (`1` bon, `2` abîmé) |
| Déclarer une perte | Bibliothécaire → `5`, code de l'exemplaire |
| Encaisser une amende | Bibliothécaire → `6` Amendes → `2` Encaisser |
| Lire sur place | `2` Lire sur place → `4` Consulter un livre, puis `5` Rendre le livre consulté avec le code affiché |

---

## 9. Données et erreurs

- Chaque modification est enregistrée immédiatement dans `data/bibliotheque.db`.
- **Sauvegarder** : copier ce fichier. **Repartir de zéro** : le supprimer (programme fermé).
- **Open Library indisponible** (pas d'internet, délai de 5 s dépassé, ISBN introuvable, erreur HTTP, `requests` absent) : message `[ERREUR]` puis saisie manuelle avec l'ISBN déjà rempli.
- **Saisie invalide** : message `[ERREUR]` et nouvelle demande, sans planter.
- **Erreur de base de données** : message et retour au menu. **Ctrl+C** : fermeture propre.

---

## 10. Auteur

**Kadjo Kadjo Joël Timothée**
