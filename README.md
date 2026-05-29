# StageFlow 🎓 — Conception Base de Données

Ce dépôt contient la modélisation et la conception de la base de données pour la plateforme **StageFlow** (Gestion des stages universitaires pour l'ESTIN).

## 🚀 Contenu du dépôt

*   **`schema_viewer.html`** : Une interface interactive pour consulter le modèle relationnel, le MCD Merise, le code DDL MySQL et les modèles Django.
*   **`stageflow_db.sql`** : Le script MySQL complet pour créer la base de données et les tables avec leurs contraintes d'intégrité.
*   **`models.py`** : La traduction des tables en modèles Django, prête à être intégrée dans votre application.
*   **`README.md`** : Ce document.

## 📊 Structure de la Base de Données (9 tables)

Le schéma s'articule autour des entités suivantes :
*   `Utilisateur` (avec héritage exclusif et total vers `Etudiant` et `Enseignant`).
*   `PropositionStage` (créée par les enseignants).
*   `DemandeStage` (déposée par les étudiants pour un stage).
*   `Refus`, `Attestation`, `Archive` (tables de gestion du cycle de vie de la demande).
*   `Notification` (pour l'historique des alertes).

## 💻 Comment visualiser le schéma interactif

1. Clonez ce dépôt.
2. Ouvrez un terminal dans le dossier du projet.
3. Lancez un serveur local rapide (nécessite Node.js) :
   ```bash
   npx http-server -p 8080 --cors
   ```
4. Ouvrez votre navigateur à l'adresse : [http://127.0.0.1:8080/schema_viewer.html](http://127.0.0.1:8080/schema_viewer.html)

---
*Projet développé dans le cadre de la gestion des stages universitaires.*
