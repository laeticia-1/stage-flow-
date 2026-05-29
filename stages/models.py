"""
StageFlow — Modèles Django (models.py)
Projet : Système de Gestion des Stages Universitaires (ESTIN)
Backend : Django | Base de données : MySQL | Auth : SSO @estin.dz
"""

from django.db import models


# ─────────────────────────────────────────────────────────────────────────────
# 1. UTILISATEUR & HÉRITAGE MULTI-TABLE
# ─────────────────────────────────────────────────────────────────────────────

class Utilisateur(models.Model):
    """
    Entité parente. Tous les utilisateurs partagent ces attributs.
    L'héritage Django (multi-table) crée automatiquement une jointure
    OneToOneField vers les sous-classes Etudiant et Enseignant.
    """
    ROLE_CHOICES = [
        ('etudiant',   'Étudiant'),
        ('enseignant', 'Enseignant'),
        ('admin',      'Administrateur'),
    ]

    nom           = models.CharField(max_length=100)
    prenom        = models.CharField(max_length=100)
    email         = models.EmailField(unique=True)
    role          = models.CharField(max_length=20, choices=ROLE_CHOICES)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Utilisateur'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.prenom} {self.nom} [{self.get_role_display()}]"


class Etudiant(Utilisateur):
    """
    Sous-classe de Utilisateur (héritage 1:1).
    Django crée une colonne id_user_ptr qui est PK + FK vers Utilisateur.
    """
    matricule   = models.CharField(max_length=50, unique=True)
    specialite  = models.CharField(max_length=100)
    niveau      = models.CharField(max_length=50)
    departement = models.CharField(max_length=100)

    class Meta:
        db_table = 'Etudiant'
        verbose_name = 'Étudiant'
        verbose_name_plural = 'Étudiants'

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.matricule}"


class Enseignant(Utilisateur):
    """
    Sous-classe de Utilisateur (héritage 1:1).
    """
    grade       = models.CharField(max_length=100)
    departement = models.CharField(max_length=100)

    class Meta:
        db_table = 'Enseignant'
        verbose_name = 'Enseignant'
        verbose_name_plural = 'Enseignants'

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.grade}"


# ─────────────────────────────────────────────────────────────────────────────
# 2. PROPOSITION DE STAGE
# ─────────────────────────────────────────────────────────────────────────────

class PropositionStage(models.Model):
    """
    Offre de stage créée et gérée par un Enseignant.
    Un enseignant peut créer plusieurs propositions (0,N).
    """
    titre            = models.CharField(max_length=200)
    description      = models.TextField()
    technologies     = models.CharField(max_length=255, blank=True, null=True,
                                        help_text="Ex: Django, React, MySQL")
    entreprise       = models.CharField(max_length=150)
    date_publication = models.DateTimeField(auto_now_add=True)
    statut           = models.CharField(max_length=50, default='Ouvert')
    enseignant       = models.ForeignKey(
        Enseignant,
        on_delete=models.RESTRICT,       # Empêche la suppression si des offres existent
        related_name='propositions',
        db_column='id_enseignant'
    )

    class Meta:
        db_table = 'PropositionStage'
        verbose_name = 'Proposition de Stage'
        verbose_name_plural = 'Propositions de Stage'

    def __str__(self):
        return f"{self.titre} @ {self.entreprise}"


# ─────────────────────────────────────────────────────────────────────────────
# 3. DEMANDE DE STAGE (entité centrale du workflow)
# ─────────────────────────────────────────────────────────────────────────────

class DemandeStage(models.Model):
    """
    Candidature d'un étudiant pour une proposition de stage.
    Cycle de vie du statut : En attente → Acceptée/Refusée → Validée → Archivée
    """
    STATUT_CHOICES = [
        ('En attente', 'En attente'),
        ('Acceptée',   'Acceptée par l\'enseignant'),
        ('Refusée',    'Refusée par l\'enseignant'),
        ('Validée',    'Validée définitivement'),
        ('Archivée',   'Archivée'),
    ]

    date_demande      = models.DateTimeField(auto_now_add=True)
    statut            = models.CharField(
                            max_length=20,
                            choices=STATUT_CHOICES,
                            default='En attente'
                        )
    cv                = models.FileField(upload_to='cvs/%Y/%m/')
    lettre_motivation = models.TextField(blank=True, null=True)
    etudiant          = models.ForeignKey(
                            Etudiant,
                            on_delete=models.CASCADE,
                            related_name='demandes',
                            db_column='id_etudiant'
                        )
    proposition       = models.ForeignKey(
                            PropositionStage,
                            on_delete=models.CASCADE,
                            related_name='demandes',
                            db_column='id_proposition'
                        )

    class Meta:
        db_table = 'DemandeStage'
        verbose_name = 'Demande de Stage'
        verbose_name_plural = 'Demandes de Stage'

    def __str__(self):
        return f"Demande #{self.pk} — {self.etudiant} → {self.proposition.titre}"


# ─────────────────────────────────────────────────────────────────────────────
# 4. REFUS (relation 1:1 optionnelle — obligatoire si statut = Refusée)
# ─────────────────────────────────────────────────────────────────────────────

class Refus(models.Model):
    """
    Enregistre le motif de refus d'une demande de stage.
    Règle métier : doit être créé si DemandeStage.statut == 'Refusée'.
    """
    motif      = models.TextField()
    date_refus = models.DateTimeField(auto_now_add=True)
    demande    = models.OneToOneField(
                     DemandeStage,
                     on_delete=models.CASCADE,
                     related_name='details_refus',
                     db_column='id_demande'
                 )

    class Meta:
        db_table = 'Refus'
        verbose_name = 'Refus'
        verbose_name_plural = 'Refus'

    def __str__(self):
        return f"Refus de la demande #{self.demande_id}"


# ─────────────────────────────────────────────────────────────────────────────
# 5. ATTESTATION (relation 1:1 — générée après validation finale)
# ─────────────────────────────────────────────────────────────────────────────

class Attestation(models.Model):
    """
    Document officiel de fin de stage.
    Règle métier : créée uniquement lorsque DemandeStage.statut == 'Validée'.
    """
    numero          = models.CharField(max_length=100, unique=True)
    date_generation = models.DateTimeField(auto_now_add=True)
    fichier_pdf     = models.FileField(upload_to='attestations/%Y/')
    appreciation    = models.TextField(blank=True, null=True)
    mention         = models.CharField(max_length=50, blank=True, null=True)
    demande         = models.OneToOneField(
                          DemandeStage,
                          on_delete=models.CASCADE,
                          related_name='attestation',
                          db_column='id_demande'
                      )

    class Meta:
        db_table = 'Attestation'
        verbose_name = 'Attestation'
        verbose_name_plural = 'Attestations'

    def __str__(self):
        return f"Attestation N° {self.numero}"


# ─────────────────────────────────────────────────────────────────────────────
# 6. NOTIFICATION
# ─────────────────────────────────────────────────────────────────────────────

class Notification(models.Model):
    """
    Notification système envoyée à un utilisateur (étudiant, enseignant ou admin).
    """
    message    = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu         = models.BooleanField(default=False)
    utilisateur = models.ForeignKey(
                      Utilisateur,
                      on_delete=models.CASCADE,
                      related_name='notifications',
                      db_column='id_user'
                  )

    class Meta:
        db_table = 'Notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-date_envoi']

    def __str__(self):
        return f"Notif → {self.utilisateur.email} | Lu: {self.lu}"


# ─────────────────────────────────────────────────────────────────────────────
# 7. ARCHIVE (relation 1:1 — dossier finalisé par l'administration)
# ─────────────────────────────────────────────────────────────────────────────

class Archive(models.Model):
    """
    Représente l'archivage définitif d'un dossier de stage.
    """
    date_archivage = models.DateTimeField(auto_now_add=True)
    demande        = models.OneToOneField(
                         DemandeStage,
                         on_delete=models.CASCADE,
                         related_name='archive',
                         db_column='id_demande'
                     )

    class Meta:
        db_table = 'Archive'
        verbose_name = 'Archive'
        verbose_name_plural = 'Archives'

    def __str__(self):
        return f"Archive du dossier #{self.demande_id} — {self.date_archivage:%d/%m/%Y}"
