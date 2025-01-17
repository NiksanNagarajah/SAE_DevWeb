# SAE_DevWeb

## Groupe

- Romain LIMA

- Mohamed-Amine YAHYAOUI

- Niksan NAGARAJAH

## Installation

Afin de lancer le projet, il est nécessaire d'installer les dépendances du projet. Pour cela, il suffit de lancer la commande suivante dans le répertoire courant du projet (là où se trouve le `README.md`) :

```bash
./install.sh
```

## Lancement

Pour lancer le projet, il suffit d'activer l'environnement virtuel avec la commande suivante :

```bash
source venv/bin/activate
```
Puis, se déplacer dans le répertoire `app` avec la commande suivante :

```bash
cd app
```

Enfin, il suffit de lancer le serveur avec la commande suivante :

```bash
flask run
```

Et d'accéder au site à l'aide de l'adresse suivante : `http://127.0.0.1:5000` en utilisant un navigateur web ou en cliquant sur le lien afficher sur le terminal. 

## Fonctionnalités 

### Gestion des utilisateurs :

- Inscription d'utilisateurs avec validation des données (email, mot de passe, numéro de téléphone, etc.).

- Connexion/déconnexion des utilisateurs.

### Rôles utilisateur : Adhérent, Moniteur, Administrateur, avec des permissions spécifiques.

- Gestion de profils (accès aux informations de l'utilisateur connecté).

### Gestion des cours :

- Création, modification et suppression de cours (par les administrateurs).

- Affichage du calendrier des cours.

- Restrictions sur le nombre maximum de participants par cours.

- Validation des horaires pour éviter des chevauchements pour les poneys, adhérent et moniteurs.

### Gestion des réservations :

- Réservation de cours par les adhérents en fonction des poneys et des disponibilités.

- Validation de contraintes avant réservation comme le respect du poids supportable des poneys. 

- Disponibilité des poneys et des moniteurs. 

- Restriction des moniteurs pour effectuer des réservations. 

### Gestion des poneys :

- Ajout, modification, suppression et récupération des données des poneys.
Validation pour vérifier si les poneys respectent des périodes de repos entre les cours.

### Système de tarifs :

- Association des utilisateurs à des tarifs spécifiques basés sur leur tranche d'âge.

### Système de rôles et permissions :

- Restriction de certaines actions aux administrateurs ou moniteurs.

- Gestion des rôles des utilisateurs (promotion/déclassement entre rôles).

### Sécurisation et gestion des données :

- Hashage des mots de passe pour la sécurité.

## Ressources

### Lien MCD Draw.io 

https://drive.google.com/file/d/1Nbkrg4mVENq1PF-XBymrhXGbfDvFaqIk/view?usp=sharing 

### Lien Maquette Figma

https://www.figma.com/design/qutRu8s9elGK87EjxNMC4H/Untitled?node-id=0-1&m=dev&t=uJ1Obn86xRshk2Je-1
