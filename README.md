# 🎓 StageFlow — Plateforme de gestion intelligente des stages

> Développé pour l'**ESTIN (École supérieure en Sciences et Technologies de l'Informatique et du Numérique)** — DPGR Béjaïa.

---

## 📋 Description

**StageFlow** est une plateforme web full-stack dédiée à la gestion des stages académiques. Elle centralise toutes les étapes du workflow, de la publication d'une offre de stage par un enseignant jusqu'à la génération de l'attestation finale, en passant par la candidature de l'étudiant et la validation administrative.

---

## 🏗️ Architecture du Projet

```
StageFlow/
├── 📄 index.html               # Point d'entrée (redirige vers acceuil)
├── 📄 acceuil.html             # Page d'accueil publique
├── 📄 connexion.html           # Page de connexion
├── 📄 etudiant.html            # Dashboard étudiant
├── 📄 enseignant.html          # Dashboard enseignant
├── 📄 admin.html               # Dashboard administration
├── 📄 schema_viewer.html       # Visualiseur interactif du schéma BDD
│
├── 📁 js/
│   └── api.js                  # Client JavaScript centralisé (fetch vers Django)
│
├── 📁 stageflow/               # ⚙️ Configuration Django
│   ├── settings.py             # Paramètres (MySQL, Apps, Media)
│   ├── urls.py                 # Routage global (admin + /api/)
│   ├── wsgi.py / asgi.py       # Points d'entrée serveur
│   └── __init__.py
│
├── 📁 stages/                  # 🏛️ Application Django principale
│   ├── models.py               # Modèles de données (9 tables)
│   ├── admin.py                # Interface admin Django customisée
│   ├── views.py                # Endpoints API JSON
│   ├── urls.py                 # Routage des endpoints
│   ├── apps.py                 # Configuration de l'app
│   └── migrations/
│
├── 📄 manage.py                # CLI Django
├── 📄 requirements.txt         # Dépendances Python
└── 📄 stageflow_db.sql         # Script SQL de création de la base MySQL
```

---

## 🗄️ Schéma de la Base de Données

9 tables relationnelles conçues pour MySQL :

| Table | Description |
|-------|-------------|
| `utilisateur` | Table parent de tous les profils |
| `etudiant` | Héritage de `utilisateur` — profil étudiant |
| `enseignant` | Héritage de `utilisateur` — profil enseignant |
| `proposition_stage` | Offres de stage publiées par les enseignants |
| `demande_stage` | Candidatures des étudiants (workflow central) |
| `refus` | Motif de refus associé à une demande |
| `attestation` | Attestation générée après validation |
| `notification` | Alertes en temps réel pour chaque acteur |
| `archive` | Dossiers archivés en fin de cycle |

---

## 🔌 API Backend (Django REST JSON)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/login/` | Connexion par email institutionnel |
| `GET` | `/api/propositions/` | Liste des propositions de stage |
| `POST` | `/api/propositions/` | Créer une proposition (enseignant) |
| `GET` | `/api/demandes/` | Liste des candidatures (filtrable) |
| `POST` | `/api/demandes/` | Soumettre une candidature (étudiant) |
| `POST` | `/api/demandes/<id>/traitement/` | Accepter / Refuser / Valider / Archiver |
| `GET` | `/api/notifications/` | Récupérer les notifications d'un utilisateur |
| `POST` | `/api/notifications/` | Marquer toutes les notifications comme lues |

---

## 🖥️ Interface Frontend

| Page | Accès | Fonctionnalités clés |
|------|-------|----------------------|
| `acceuil.html` | Public | Présentation, liens vers les espaces |
| `connexion.html` | Public | Connexion par email @estin.dz |
| `etudiant.html` | Étudiant | Parcours, propositions, candidature, notifications |
| `enseignant.html` | Enseignant | Propositions, validation, suivi, attestations |
| `admin.html` | Admin | Vue globale, dossiers, archivage, attestations |

---

## 🚀 Installation et Démarrage

### 1. Prérequis
- **Python 3.10+** installé
- **XAMPP** (ou tout serveur MySQL) démarré
- La base de données `stageflow_db` créée dans MySQL

### 2. Créer la base de données MySQL
```sql
CREATE DATABASE stageflow_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
Puis importer le schéma :
```bash
mysql -u root stageflow_db < stageflow_db.sql
```

### 3. Installer les dépendances Python
```bash
pip install -r requirements.txt
```

### 4. Appliquer les migrations Django
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Créer un super-utilisateur (admin Django)
```bash
python manage.py createsuperuser
```

### 6. Lancer le serveur
```bash
python manage.py runserver
```

L'API backend sera disponible sur : **http://127.0.0.1:8000/api/**
L'interface admin Django : **http://127.0.0.1:8000/admin/**

---

## 🔑 Comptes de démonstration (mode offline)

Lorsque le serveur Django n'est pas actif, `js/api.js` active automatiquement un mode démo avec ces comptes :

| Email | Rôle | Dashboard |
|-------|------|-----------|
| `a.ouali@estin.dz` | Étudiant | `etudiant.html` |
| `a.benali@estin.dz` | Enseignant | `enseignant.html` |
| `admin@estin.dz` | Administration | `admin.html` |

---

## 🛠️ Technologies utilisées

- **Frontend** : HTML5, CSS3 (Vanilla), JavaScript (ES2020+), Google Fonts
- **Backend** : Python 3, Django 4.2, Django ORM
- **Base de données** : MySQL (via `mysqlclient`)
- **Versioning** : Git + GitHub

---

## 👥 Acteurs de la plateforme

```
Étudiant  →  Postule aux offres, suit ses candidatures, télécharge ses attestations
Enseignant →  Publie des offres, valide/refuse les demandes, génère les attestations
Admin      →  Supervise tous les dossiers, archive, envoie des notifications globales
```

---

*Projet académique — ESTIN Béjaïa, 2025/2026*
