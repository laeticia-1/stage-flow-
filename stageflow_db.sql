-- ============================================================
-- SCRIPT DE CREATION DE LA BASE DE DONNEES STAGEFLOW (MySQL)
-- Projet : Système de Gestion des Stages Universitaires
-- Backend : Django | BDD : MySQL | Frontend : HTML/CSS/JS
-- ============================================================

CREATE DATABASE IF NOT EXISTS stageflow_db
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE stageflow_db;

-- ─────────────────────────────────────────────────────────────
-- 1. TABLE UTILISATEUR (entité parente - héritage)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE Utilisateur (
    id_user       INT AUTO_INCREMENT PRIMARY KEY,
    nom           VARCHAR(100) NOT NULL,
    prenom        VARCHAR(100) NOT NULL,
    email         VARCHAR(150) NOT NULL UNIQUE,
    role          ENUM('etudiant', 'enseignant', 'admin') NOT NULL,
    date_creation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─────────────────────────────────────────────────────────────
-- 2. TABLE ETUDIANT (héritage 1:1 de Utilisateur)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE Etudiant (
    id_user     INT PRIMARY KEY,
    matricule   VARCHAR(50) NOT NULL UNIQUE,
    specialite  VARCHAR(100) NOT NULL,
    niveau      VARCHAR(50) NOT NULL,
    departement VARCHAR(100) NOT NULL,
    CONSTRAINT fk_etudiant_user
        FOREIGN KEY (id_user) REFERENCES Utilisateur(id_user)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─────────────────────────────────────────────────────────────
-- 3. TABLE ENSEIGNANT (héritage 1:1 de Utilisateur)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE Enseignant (
    id_user     INT PRIMARY KEY,
    grade       VARCHAR(100) NOT NULL,
    departement VARCHAR(100) NOT NULL,
    CONSTRAINT fk_enseignant_user
        FOREIGN KEY (id_user) REFERENCES Utilisateur(id_user)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─────────────────────────────────────────────────────────────
-- 4. TABLE PROPOSITIONSTAGE
-- ─────────────────────────────────────────────────────────────
CREATE TABLE PropositionStage (
    id_proposition   INT AUTO_INCREMENT PRIMARY KEY,
    titre            VARCHAR(200) NOT NULL,
    description      TEXT NOT NULL,
    technologies     VARCHAR(255),
    entreprise       VARCHAR(150) NOT NULL,
    date_publication DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    statut           VARCHAR(50) NOT NULL DEFAULT 'Ouvert',
    id_enseignant    INT NOT NULL,
    CONSTRAINT fk_proposition_enseignant
        FOREIGN KEY (id_enseignant) REFERENCES Enseignant(id_user)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─────────────────────────────────────────────────────────────
-- 5. TABLE DEMANDESTAGE (entité centrale du workflow)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE DemandeStage (
    id_demande       INT AUTO_INCREMENT PRIMARY KEY,
    date_demande     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    statut           ENUM('En attente','Acceptée','Refusée','Validée','Archivée')
                     NOT NULL DEFAULT 'En attente',
    cv               VARCHAR(255) NOT NULL COMMENT 'Chemin vers le fichier CV',
    lettre_motivation TEXT,
    id_etudiant      INT NOT NULL,
    id_proposition   INT NOT NULL,
    CONSTRAINT fk_demande_etudiant
        FOREIGN KEY (id_etudiant) REFERENCES Etudiant(id_user)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_demande_proposition
        FOREIGN KEY (id_proposition) REFERENCES PropositionStage(id_proposition)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─────────────────────────────────────────────────────────────
-- 6. TABLE REFUS (relation 1:1 optionnelle avec DemandeStage)
--    Règle métier : renseignée obligatoirement si statut = 'Refusée'
-- ─────────────────────────────────────────────────────────────
CREATE TABLE Refus (
    id_refus   INT AUTO_INCREMENT PRIMARY KEY,
    motif      TEXT NOT NULL,
    date_refus DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_demande INT NOT NULL UNIQUE,
    CONSTRAINT fk_refus_demande
        FOREIGN KEY (id_demande) REFERENCES DemandeStage(id_demande)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─────────────────────────────────────────────────────────────
-- 7. TABLE ATTESTATION (relation 1:1 avec DemandeStage)
--    Règle métier : générée uniquement après validation finale
-- ─────────────────────────────────────────────────────────────
CREATE TABLE Attestation (
    id_attestation  INT AUTO_INCREMENT PRIMARY KEY,
    numero          VARCHAR(100) NOT NULL UNIQUE,
    date_generation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fichier_pdf     VARCHAR(255) NOT NULL COMMENT 'Chemin vers le PDF généré',
    appreciation    TEXT,
    mention         VARCHAR(50),
    id_demande      INT NOT NULL UNIQUE,
    CONSTRAINT fk_attestation_demande
        FOREIGN KEY (id_demande) REFERENCES DemandeStage(id_demande)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─────────────────────────────────────────────────────────────
-- 8. TABLE NOTIFICATION
-- ─────────────────────────────────────────────────────────────
CREATE TABLE Notification (
    id_notification INT AUTO_INCREMENT PRIMARY KEY,
    message         TEXT NOT NULL,
    date_envoi      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lu              BOOLEAN NOT NULL DEFAULT FALSE,
    id_user         INT NOT NULL,
    CONSTRAINT fk_notification_user
        FOREIGN KEY (id_user) REFERENCES Utilisateur(id_user)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─────────────────────────────────────────────────────────────
-- 9. TABLE ARCHIVE (relation 1:1 avec DemandeStage)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE Archive (
    id_archive      INT AUTO_INCREMENT PRIMARY KEY,
    date_archivage  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_demande      INT NOT NULL UNIQUE,
    CONSTRAINT fk_archive_demande
        FOREIGN KEY (id_demande) REFERENCES DemandeStage(id_demande)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- FIN DU SCRIPT — 9 tables créées avec succès
-- ============================================================
