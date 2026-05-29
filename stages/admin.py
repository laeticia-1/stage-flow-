from django.contrib import admin
from .models import (
    Utilisateur, Etudiant, Enseignant,
    PropositionStage, DemandeStage, Refus,
    Attestation, Notification, Archive
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM ADMIN CLASSES
# ─────────────────────────────────────────────────────────────────────────────

@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'prenom', 'email', 'role', 'date_creation')
    list_filter = ('role', 'date_creation')
    search_fields = ('nom', 'prenom', 'email')
    ordering = ('-date_creation',)


@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ('id_user', 'nom', 'prenom', 'matricule', 'specialite', 'niveau', 'departement')
    search_fields = ('nom', 'prenom', 'matricule', 'specialite')
    list_filter = ('specialite', 'niveau', 'departement')

    def id_user(self, obj):
        return obj.pk
    id_user.short_description = 'User ID'


@admin.register(Enseignant)
class EnseignantAdmin(admin.ModelAdmin):
    list_display = ('id_user', 'nom', 'prenom', 'grade', 'departement')
    search_fields = ('nom', 'prenom', 'grade', 'departement')
    list_filter = ('grade', 'departement')

    def id_user(self, obj):
        return obj.pk
    id_user.short_description = 'User ID'


@admin.register(PropositionStage)
class PropositionStageAdmin(admin.ModelAdmin):
    list_display = ('titre', 'entreprise', 'enseignant', 'statut', 'date_publication')
    list_filter = ('statut', 'date_publication', 'entreprise')
    search_fields = ('titre', 'description', 'technologies', 'entreprise')
    raw_id_fields = ('enseignant',)
    ordering = ('-date_publication',)


class RefusInline(admin.StackedInline):
    model = Refus
    extra = 0


class AttestationInline(admin.StackedInline):
    model = Attestation
    extra = 0


class ArchiveInline(admin.StackedInline):
    model = Archive
    extra = 0


@admin.register(DemandeStage)
class DemandeStageAdmin(admin.ModelAdmin):
    list_display = ('id', 'etudiant', 'proposition', 'statut', 'date_demande')
    list_filter = ('statut', 'date_demande')
    search_fields = ('etudiant__nom', 'etudiant__prenom', 'proposition__titre', 'proposition__entreprise')
    raw_id_fields = ('etudiant', 'proposition')
    inlines = [RefusInline, AttestationInline, ArchiveInline]
    ordering = ('-date_demande',)


@admin.register(Refus)
class RefusAdmin(admin.ModelAdmin):
    list_display = ('id', 'demande', 'motif', 'date_refus')
    search_fields = ('motif', 'demande__etudiant__nom')
    raw_id_fields = ('demande',)
    ordering = ('-date_refus',)


@admin.register(Attestation)
class AttestationAdmin(admin.ModelAdmin):
    list_display = ('numero', 'demande', 'mention', 'date_generation')
    search_fields = ('numero', 'demande__etudiant__nom')
    list_filter = ('mention', 'date_generation')
    raw_id_fields = ('demande',)
    ordering = ('-date_generation',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'message', 'lu', 'date_envoi')
    list_filter = ('lu', 'date_envoi')
    search_fields = ('message', 'utilisateur__nom', 'utilisateur__email')
    raw_id_fields = ('utilisateur',)
    ordering = ('-date_envoi',)


@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
    list_display = ('id', 'demande', 'date_archivage')
    raw_id_fields = ('demande',)
    ordering = ('-date_archivage',)
