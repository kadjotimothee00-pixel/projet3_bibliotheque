# Gestion de bibliothèque

Application console de gestion de bibliothèque écrite en Python 3, avec une base de données SQLite et une architecture MVC (Modèle, Vue, Contrôleur).

---

## 1. Présentation du projet

Ce programme permet de gérer une petite bibliothèque depuis un terminal :

- le **bibliothécaire** gère le catalogue (livres et exemplaires), les adhérents, les retours, les pertes, les amendes, les réservations et les paramètres ;
- n'importe quel visiteur peut **lire sur place** sans s'identifier ;
- un **adhérent** inscrit peut emprunter, prolonger, réserver et consulter son compte avec son numéro de carte.

Toutes les données sont enregistrées dans un fichier SQLite : quand on quitte et qu'on relance le programme, rien n'est perdu.

Les livres peuvent être ajoutés automatiquement à partir de leur ISBN grâce à l'API Open Library (gratuite, sans clé).

---

## 2. Fonctionnalités

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

### 2.1 Espace Bibliothécaire (identifiant + mot de passe)

| N° | Menu | Contenu |
|---|---|---|
| 1 | Gestion des livres | Ajouter (par ISBN avec Open Library ou saisie manuelle), modifier, supprimer, rechercher (titre, auteur, catégorie, ISBN), lister avec le nombre d'exemplaires disponibles / total |
| 2 | Gestion des exemplaires | Ajouter des exemplaires à un livre, changer l'état d'un exemplaire, lister les exemplaires d'un livre |
| 3 | Gestion des adhérents | Inscrire, modifier, rechercher (numéro de carte ou nom), lister, bloquer / débloquer |
| 4 | Enregistrer un retour | Saisie du code exemplaire, état constaté, calcul automatique des amendes |
| 5 | Déclarer un livre perdu | Amende de perte (+ retard éventuel) |
| 6 | Amendes | Lister les impayées, encaisser, historique d'un adhérent |
| 7 | Emprunts en retard | Liste avec le nombre de jours et l'amende qui serait due aujourd'hui |
| 8 | Réservations | Lister les réservations actives, annuler une réservation |
| 9 | Statistiques | Livres, exemplaires par statut, adhérents, emprunts, amendes, top 5, répartition par catégorie |
| 10 | Paramètres | Afficher, modifier une valeur, changer le mot de passe, changer l'identifiant |

Après 3 tentatives de connexion échouées, le programme revient au menu principal.

### 2.2 Lire sur place (aucune identification)

1. Afficher les livres disponibles (livres ayant au moins un exemplaire disponible)
2. Rechercher un livre (titre, auteur, catégorie)
3. Voir la disponibilité d'un livre (liste des exemplaires et de leur statut)
4. Consulter un livre : un exemplaire disponible est attribué, il passe en `en_consultation` et son code est affiché
5. Rendre le livre consulté : saisie du code, l'exemplaire redevient `disponible`

La lecture sur place n'est pas limitée par `max_livres` et aucun registre des visites n'est tenu.

### 2.3 Emprunter (identification par numéro de carte)

Le lecteur saisit son numéro de carte (`AD-0001`, ou simplement `1`). S'il n'existe pas, le programme lui demande de s'inscrire auprès du bibliothécaire.

1. Afficher les livres disponibles
2. Rechercher un livre
3. Emprunter un livre (par recherche, ou en saisissant directement un code d'exemplaire)
4. Prolonger un emprunt
5. Réserver un livre indisponible
6. Voir mes emprunts, mes réservations et mes amendes

Le lecteur ne peut pas rendre un livre lui-même : c'est le bibliothécaire qui enregistre le retour, car c'est lui qui juge l'état du livre.

---

## 3. Technologies utilisées

- **Python 3** (testé avec Python 3.14)
- **SQLite** via le module standard `sqlite3`
- **API Open Library** (https://openlibrary.org) pour remplir automatiquement les informations d'un livre
- **requests** : seule bibliothèque externe, utilisée pour appeler l'API
- Modules standard : `hashlib` et `secrets` (mot de passe), `getpass` (saisie masquée), `datetime` (dates)

---

## 4. Architecture MVC

```
bibliotheque/
├── README.md
├── main.py
├── config.py
├── .gitignore
├── requirements.txt
│
├── database/
│   ├── __init__.py
│   ├── connexion.py
│   ├── schema.py
│   └── donnees_initiales.py
│
├── models/
│   ├── __init__.py
│   ├── livre.py
│   ├── categorie.py
│   ├── exemplaire.py
│   ├── adherent.py
│   ├── emprunt.py
│   ├── reservation.py
│   ├── amende.py
│   ├── parametre.py
│   └── bibliothecaire.py
│
├── views/
│   ├── __init__.py
│   ├── affichage.py
│   ├── vue_principale.py
│   ├── vue_bibliothecaire.py
│   ├── vue_lecture.py
│   └── vue_emprunt.py
│
├── controllers/
│   ├── __init__.py
│   ├── controleur_principal.py
│   ├── controleur_auth.py
│   ├── controleur_livre.py
│   ├── controleur_adherent.py
│   ├── controleur_emprunt.py
│   ├── controleur_lecture.py
│   ├── controleur_amende.py
│   └── controleur_parametre.py
│
├── services/
│   ├── __init__.py
│   └── open_library.py
│
└── data/
    └── bibliotheque.db   (créé automatiquement)
```

### Principe

```
 Utilisateur  <-->  VUE  <-->  CONTRÔLEUR  <-->  MODÈLE  <-->  Base SQLite
                                   |
                                   +-->  SERVICE (Open Library)
```

- La **vue** affiche et lit le clavier. Elle ne contient ni SQL ni règle de gestion.
- Le **contrôleur** applique les règles (peut-on emprunter ? combien coûte l'amende ?).
- Le **modèle** contient uniquement les requêtes SQL. Il ne fait ni `print` ni `input`.

### Rôle de chaque fichier

| Fichier | Rôle |
|---|---|
| `main.py` | Point d'entrée : crée les tables, insère les données de départ si besoin, crée le compte bibliothécaire au premier lancement, puis lance le menu principal. Gère Ctrl+C. |
| `config.py` | Chemin de la base, URL de l'API Open Library, délai réseau de 5 secondes. |
| `.gitignore` | Exclut la base, les caches Python et l'environnement virtuel. |
| `requirements.txt` | Dépendance externe (`requests`). |
| `database/connexion.py` | Ouvre la connexion (clés étrangères activées, accès aux colonnes par nom) et fournit `executer`, `lire_un`, `lire_tous`. |
| `database/schema.py` | Crée les 9 tables avec `CREATE TABLE IF NOT EXISTS`. |
| `database/donnees_initiales.py` | Insère catégories, paramètres et livres de départ uniquement si les tables sont vides. |
| `models/*.py` | Une classe par table avec ses requêtes SQL (ajouter, chercher, lister, modifier, supprimer, compter). `bibliothecaire.py` gère la table du compte bibliothécaire. |
| `views/affichage.py` | Outils communs : titres encadrés, séparateurs, tableaux alignés, messages `[OK]`, `[ERREUR]`, `[INFO]`, `[ATTENTION]`, saisies validées (entier, texte obligatoire, texte optionnel, O/N, téléphone, email, mot de passe masqué), pause, format des dates et des prix. |
| `views/vue_principale.py` | Menu principal. |
| `views/vue_bibliothecaire.py` | Menus et tableaux de l'espace bibliothécaire. |
| `views/vue_lecture.py` | Menu et affichages de la lecture sur place. |
| `views/vue_emprunt.py` | Menu et affichages de l'espace lecteur. |
| `controllers/controleur_principal.py` | Menu principal, menu bibliothécaire, statistiques, interception des erreurs pour que le programme ne plante jamais. |
| `controllers/controleur_auth.py` | Création du compte, connexion (3 tentatives), changement de mot de passe et d'identifiant, hachage. |
| `controllers/controleur_livre.py` | Ajout (ISBN / manuel), modification, suppression, recherche des livres ; gestion des exemplaires ; remise en circulation d'un exemplaire (avec prise en compte des réservations). |
| `controllers/controleur_adherent.py` | Inscription, modification, recherche, liste, blocage des adhérents. |
| `controllers/controleur_emprunt.py` | Espace lecteur (emprunt, prolongation, réservation, compte) et, côté bibliothécaire, retours, pertes, retards, réservations. |
| `controllers/controleur_lecture.py` | Lecture sur place. |
| `controllers/controleur_amende.py` | Liste, encaissement et historique des amendes. |
| `controllers/controleur_parametre.py` | Lecture des paramètres au moment de chaque opération, affichage et modification. |
| `services/open_library.py` | Appel à l'API Open Library. Renvoie les informations du livre ou un message d'erreur. Ne touche ni à la base ni à l'affichage. |

---

## 5. Base de données

Fichier : `data/bibliotheque.db`. Les dates sont stockées au format `AAAA-MM-JJ` et affichées au format `JJ/MM/AAAA`. Les montants sont des entiers en FCFA.

| Table | Colonnes | Remarques |
|---|---|---|
| `categories` | id, nom | nom unique |
| `livres` | id, isbn, titre, auteur, editeur, annee, categorie_id, prix, source, date_ajout | isbn unique (peut être vide), source = `manuel` ou `api` |
| `exemplaires` | id, code, livre_id, etat, statut | code `EX-0001`, etat = `bon` / `abime` / `perdu`, statut = `disponible` / `emprunte` / `en_consultation` / `reserve` / `indisponible` |
| `adherents` | id, numero_carte, nom, prenom, telephone, email, date_inscription, statut | carte `AD-0001`, statut = `actif` / `bloque` |
| `emprunts` | id, exemplaire_id, adherent_id, date_sortie, date_retour_prevue, date_retour_reelle, nb_prolongations, statut | statut = `en_cours` / `termine` |
| `reservations` | id, livre_id, adherent_id, exemplaire_id, date_reservation, statut | porte sur un livre ; exemplaire_id rempli quand un exemplaire est mis de côté ; statut = `en_attente` / `disponible` / `terminee` / `annulee` |
| `amendes` | id, emprunt_id, type, montant, payee, date_creation, date_paiement | type = `retard` / `degat` / `perte`, payee = 0 ou 1 |
| `parametres` | nom, valeur, description | règles de gestion modifiables |
| `bibliothecaire` | id, identifiant, mot_de_passe_hash, sel | mot de passe jamais stocké en clair |

### Relations

```
categories 1 ---- n livres 1 ---- n exemplaires 1 ---- n emprunts n ---- 1 adherents
                     |                                     |
                     1                                     1
                     |                                     |
                     n reservations n ---- 1 adherents     n amendes
```

- Un livre appartient à une catégorie et possède plusieurs exemplaires.
- Un emprunt relie un exemplaire et un adhérent.
- Une amende est toujours liée à un emprunt (on retrouve ainsi l'adhérent et le livre).
- Une réservation relie un livre et un adhérent, et éventuellement l'exemplaire mis de côté.

---

## 6. Règles de gestion

### 6.1 Paramètres par défaut

| Nom | Valeur | Description |
|---|---|---|
| max_livres | 3 | nombre maximum d'emprunts en cours par adhérent |
| duree_pret | 14 | durée d'un prêt en jours |
| duree_prolongation | 2 | nombre de jours ajoutés par une prolongation |
| max_prolongations | 1 | nombre maximum de prolongations par emprunt |
| amende_par_jour | 100 | amende en FCFA par jour de retard et par livre |
| prix_defaut | 5000 | prix en FCFA utilisé si le livre n'a pas de prix saisi |
| pourcentage_degat | 50 | pourcentage du prix du livre payé pour un livre abîmé |

Ces valeurs ne sont jamais écrites en dur dans le code : elles sont relues dans la table `parametres` au moment de chaque opération. Modifier un paramètre ne change pas les emprunts déjà enregistrés (par exemple, une date de retour déjà calculée reste la même).

### 6.2 Conditions d'emprunt (vérifiées dans cet ordre)

1. L'adhérent est `actif` (pas `bloque`).
2. Il n'a aucune amende impayée.
3. Il n'a aucun emprunt en retard.
4. Il a moins de `max_livres` emprunts en cours.
5. L'exemplaire existe et n'est pas `perdu`.
6. L'exemplaire est `disponible`, ou bien il est `reserve` pour cet adhérent.

Si l'emprunt est accepté : date de retour prévue = aujourd'hui + `duree_pret`, l'exemplaire passe en `emprunte` et la réservation éventuelle passe en `terminee`.

### 6.3 Calcul des amendes (avec les paramètres par défaut)

| Situation | Calcul | Exemple |
|---|---|---|
| Retard | jours de retard x `amende_par_jour` | 5 jours de retard : 5 x 100 = **500 FCFA** |
| Livre abîmé | prix x `pourcentage_degat` / 100, arrondi | livre à 4 000 FCFA : 4 000 x 50 / 100 = **2 000 FCFA** |
| Livre perdu | 100 % du prix (+ retard éventuel) | livre à 6 000 FCFA rendu à temps : **6 000 FCFA** |

Exemple complet : *Climbié* (4 000 FCFA) rendu abîmé avec 5 jours de retard. Deux amendes sont créées : 500 FCFA (retard) + 2 000 FCFA (dégât) = **2 500 FCFA**. Tant qu'elles ne sont pas payées, l'adhérent ne peut ni emprunter ni réserver.

### 6.4 Prolongations

Une prolongation ajoute `duree_prolongation` jours à la date de retour prévue. Elle est refusée si :

- l'adhérent est bloqué ;
- l'emprunt est déjà en retard ;
- le nombre de prolongations a atteint `max_prolongations` ;
- un autre lecteur attend ce livre (réservation `en_attente`).

Exemple : retour prévu le 02/12/2026, après prolongation : 04/12/2026. Une seconde demande est refusée.

### 6.5 Réservations

- Une réservation porte sur un livre (pas sur un exemplaire précis).
- Elle n'est possible que si aucun exemplaire du livre n'est disponible.
- Elle est refusée si l'adhérent a déjà une réservation active sur ce livre, ou s'il a déjà ce livre en emprunt.
- Mêmes conditions de compte que l'emprunt : adhérent actif, sans amende impayée.
- Les réservations sont servies dans l'ordre d'arrivée (la plus ancienne d'abord).
- Au retour d'un exemplaire, s'il existe une réservation en attente, l'exemplaire passe en `reserve`, la réservation passe en `disponible`, et le programme indique au bibliothécaire pour qui le mettre de côté.
- Si une réservation `disponible` est annulée, l'exemplaire passe au lecteur suivant ou redevient disponible.

### 6.6 Autres règles

- **Suppression d'un livre** : refusée si un exemplaire est emprunté, en consultation ou réservé, si des réservations sont en attente, ou si le livre a déjà été emprunté (son historique sert au suivi des amendes).
- **Blocage** : un adhérent bloqué ne peut ni emprunter, ni prolonger, ni réserver.
- **Codes** : les codes `EX-0001` et `AD-0001` sont générés automatiquement en continuant à partir du plus grand code existant.

---

## 7. Installation

### Prérequis

- Python 3.8 ou plus récent (`python --version`)
- Une connexion internet (seulement pour l'ajout de livres par ISBN)

### Étapes

1. Se placer dans le dossier du projet :
   ```
   cd bibliotheque
   ```
2. Créer et activer un environnement virtuel :
   ```
   python -m venv venv
   venv\Scripts\activate          (Windows)
   source venv/bin/activate       (Linux / macOS)
   ```
3. Installer la dépendance :
   ```
   pip install -r requirements.txt
   ```
Aucune clé API n'est nécessaire : l'API Open Library est gratuite et ouverte.

---

## 8. Lancement

```
python main.py
```

### Au premier lancement

1. Le dossier `data/` et le fichier `bibliotheque.db` sont créés.
2. Les tables sont créées.
3. Les données de départ sont insérées : 10 catégories, 7 paramètres et 23 livres (auteurs ivoiriens, africains et classiques) avec 1 à 3 exemplaires chacun (40 exemplaires au total). Aucun adhérent n'est créé.
4. Le programme demande de créer le compte bibliothécaire : identifiant, puis mot de passe (saisie masquée, 4 caractères minimum, confirmation obligatoire).

Aux lancements suivants, rien n'est recréé ni dupliqué : le programme affiche directement le menu principal.

---

## 9. Guide d'utilisation

Dans tous les menus, on tape le numéro de l'option puis Entrée. `0` permet de revenir en arrière ou d'annuler.

### Ajouter un livre par ISBN

1. Menu principal : `1` (Bibliothécaire), identifiant et mot de passe.
2. `1` Gestion des livres, puis `1` Ajouter un livre, puis `1` Par ISBN.
3. Saisir l'ISBN (les tirets et espaces sont acceptés, ex : `978-2-07-036002-4`).
4. Si le livre existe déjà, le programme propose d'ajouter des exemplaires.
5. Sinon, le résultat d'Open Library s'affiche : confirmer avec `O`.
6. Choisir la catégorie, le prix (Entrée = 5 000 FCFA) et le nombre d'exemplaires.
7. Vérifier le récapitulatif et confirmer. Les codes des exemplaires (ex : `EX-0041`) s'affichent : les coller sur les livres.

### Inscrire un adhérent

1. Bibliothécaire, `3` Gestion des adhérents, `1` Inscrire.
2. Saisir nom, prénom, téléphone (ex : `07 01 02 03 04`) et éventuellement l'email.
3. Confirmer. Le numéro de carte (ex : `AD-0001`) s'affiche : le remettre au lecteur.

### Emprunter

1. Menu principal : `3` Emprunter, saisir le numéro de carte.
2. `3` Emprunter un livre, puis `1` Rechercher le livre.
3. Choisir le critère (titre, auteur...), taper un mot, puis l'ID du livre.
4. Confirmer : la date de retour prévue s'affiche.

### Prolonger

1. Espace lecteur, `4` Prolonger un emprunt.
2. Taper l'ID de l'emprunt : la nouvelle date de retour s'affiche (+2 jours).

### Réserver

1. Espace lecteur, `5` Réserver un livre indisponible.
2. Rechercher le livre et taper son ID. La position dans la file d'attente s'affiche.
3. Quand le livre revient, le bibliothécaire le met de côté. Le lecteur l'emprunte ensuite normalement (option `3`) : l'exemplaire réservé lui est attribué.

### Enregistrer un retour

1. Bibliothécaire, `4` Enregistrer un retour.
2. Saisir le code de l'exemplaire (ex : `EX-0001`) : l'emprunt s'affiche.
3. Indiquer l'état : `1` bon ou `2` abime, puis confirmer.
4. Le récapitulatif affiche les amendes créées. Si le livre est réservé, un message indique pour qui le mettre de côté.

### Déclarer une perte

1. Bibliothécaire, `5` Déclarer un livre perdu.
2. Saisir le code de l'exemplaire et confirmer. L'amende de perte (et de retard s'il y en a) est créée, l'exemplaire est retiré du prêt.

### Encaisser une amende

1. Bibliothécaire, `6` Amendes, `2` Encaisser une amende.
2. La liste des amendes impayées s'affiche : taper l'ID de l'amende et confirmer.

### Lire sur place

1. Menu principal : `2` Lire sur place, `4` Consulter un livre.
2. Rechercher le livre et taper son ID : le code de l'exemplaire s'affiche.
3. Après la lecture : `5` Rendre le livre consulté, puis saisir ce code.

---

## 10. Persistance des données

- Toutes les données sont dans le fichier `data/bibliotheque.db`.
- Chaque modification est enregistrée immédiatement (commit) : aucune donnée n'est gardée seulement en mémoire.
- Pour **repartir de zéro**, quitter le programme puis supprimer le fichier `data/bibliotheque.db`. Au prochain lancement, la base est recréée avec les données de départ et le compte bibliothécaire est redemandé.
- Pour **sauvegarder** la bibliothèque, il suffit de copier ce fichier.

---

## 11. Gestion des erreurs

| Situation | Comportement |
|---|---|
| Pas de connexion internet / délai de 5 secondes dépassé | Message `[ERREUR]` explicite, puis passage à la saisie manuelle avec l'ISBN déjà rempli |
| Trop de demandes envoyées (erreur 429) ou autre code d'erreur HTTP | Même chose |
| ISBN introuvable sur Open Library | Même chose |
| Réponse illisible (JSON invalide) ou autre erreur | Même chose |
| `requests` non installé | Message indiquant de lancer `pip install -r requirements.txt`, puis saisie manuelle |
| Saisie invalide (lettres à la place d'un nombre, champ obligatoire vide, choix de menu inexistant, année hors limites, email ou téléphone mal formé...) | Message `[ERREUR]` et nouvelle demande, sans planter |
| Erreur de base de données | Message `[ERREUR]`, retour au menu principal |
| Ctrl+C | Le programme se ferme proprement avec un message |

---

## 12. Améliorations possibles

- Interface graphique (Tkinter) ou interface web (Flask).
- Envoi de rappels par SMS ou email avant la date de retour.
- Plusieurs comptes bibliothécaires avec des droits différents.
- Annulation d'une réservation par le lecteur lui-même.
- Export des statistiques en fichier CSV ou PDF.
- Tests automatisés avec `unittest`.
- Recherche insensible aux accents.
- Remplacement de SHA-256 par un algorithme dédié aux mots de passe (`hashlib.pbkdf2_hmac`).

---

## 13. Auteur

**Kadjo Kadjo Joël Timothée**
