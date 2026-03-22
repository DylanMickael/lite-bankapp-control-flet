# BankApp Control - Supervision 🏦

Application de supervision bancaire moderne construite avec **Flet** (Python) et **SQLAlchemy** (Postgres). 
L'application permet la gestion des clients, des virements et l'audit complet des opérations avec des déclencheurs de base de données (Triggers).

## ✨ Fonctionnalités
- **Tableau de bord unifié** : Statistiques en temps réel (KPIs).
- **Gestion des Clients** : CRUD complet (Ajout, Modification, Suppression).
- **Gestion des Virements** : Suivi des transactions et modification d'historique.
- **Audit Système** : Traces détaillées des ajouts, modifications et suppressions avec capture du solde avant/après et de l'utilisateur.
- **Contrôle d'accès** : Rôles `admin` (accès total) et `user` (accès limité sans audit).
- **Design Premium** : Interface épurée en Light Mode avec Glassmorphism et micro-animations.

## �️ Installation

### 1. Prérequis
- Python 3.9+
- PostgreSQL installé et configuré.

### 2. Configuration de l'environnement
Clonez le projet et créez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Base de données
Créez un fichier `.env` à la racine du projet :
```env
DB_URL=postgresql://postgres:VOTRE_MOT_DE_PASSE@localhost:5432/VOTRE_NOM_DE_BDD
```

Initialisez la structure de la base de données et les triggers :
```bash
python -m app.db.setup
```

## 🚀 Lancement
Pour démarrer l'application :
```bash
python main.py
```

## 👤 Identifiants par défaut (Seeding)
| Rôle  | Utilisateur | Mot de passe |
|-------|-------------|--------------|
| Admin | `admin`     | `admin123`   |
| Staff | `dylan`     | `password123`|

## 🏗️ Architecture
- `app/components/`: Composants UI réutilisables (Cards, Modals, Tables).
- `app/controller/`: Logique métier et interactions Database.
- `app/db/`: Modèles SQLAlchemy et scripts d'initialisation.
- `app/ui/`: Pages principales (Auth, Dashboard).
- `main.py`: Point d'entrée et gestion des routes.
