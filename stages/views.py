import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404
from .models import (
    Utilisateur, Etudiant, Enseignant,
    PropositionStage, DemandeStage, Refus,
    Attestation, Notification, Archive
)

# ─────────────────────────────────────────────────────────────────────────────
# UTILS
# ─────────────────────────────────────────────────────────────────────────────

def get_json_payload(request):
    try:
        return json.loads(request.body)
    except Exception:
        return {}

# ─────────────────────────────────────────────────────────────────────────────
# 1. AUTHENTICATION & SESSION
# ─────────────────────────────────────────────────────────────────────────────

@csrf_exempt
def api_login(request):
    """
    Simulation de connexion via Email SSO @estin.dz.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode POST uniquement.'}, status=405)

    data = get_json_payload(request)
    email = data.get('email')

    if not email:
        return JsonResponse({'error': 'Email requis.'}, status=400)

    try:
        user = Utilisateur.objects.get(email=email)
        user_data = {
            'id': user.id,
            'nom': user.nom,
            'prenom': user.prenom,
            'email': user.email,
            'role': user.role,
        }
        return JsonResponse({'success': True, 'user': user_data})
    except Utilisateur.DoesNotExist:
        return JsonResponse({'error': 'Utilisateur introuvable.'}, status=404)

# ─────────────────────────────────────────────────────────────────────────────
# 2. PROPOSITIONS DE STAGE
# ─────────────────────────────────────────────────────────────────────────────

class PropositionListView(View):
    """
    GET: Liste toutes les propositions de stage ouvertes.
    POST: Permet à un enseignant de publier une nouvelle proposition.
    """
    def get(self, request):
        propositions = PropositionStage.objects.all().order_by('-date_publication')
        data = []
        for prop in propositions:
            data.append({
                'id': prop.id,
                'titre': prop.titre,
                'description': prop.description,
                'technologies': prop.technologies,
                'entreprise': prop.entreprise,
                'statut': prop.statut,
                'date_publication': prop.date_publication.isoformat(),
                'enseignant': {
                    'id': prop.enseignant.id,
                    'nom': prop.enseignant.nom,
                    'prenom': prop.enseignant.prenom,
                }
            })
        return JsonResponse({'propositions': data})

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        data = get_json_payload(request)
        id_enseignant = data.get('id_enseignant')
        titre = data.get('titre')
        description = data.get('description')
        technologies = data.get('technologies', '')
        entreprise = data.get('entreprise')

        if not all([id_enseignant, titre, description, entreprise]):
            return JsonResponse({'error': 'Données incomplètes (id_enseignant, titre, description, entreprise requis).'}, status=400)

        try:
            enseignant = Enseignant.objects.get(id_user=id_enseignant)
        except Enseignant.DoesNotExist:
            return JsonResponse({'error': 'Enseignant introuvable.'}, status=404)

        prop = PropositionStage.objects.create(
            titre=titre,
            description=description,
            technologies=technologies,
            entreprise=entreprise,
            enseignant=enseignant
        )

        return JsonResponse({
            'success': True,
            'id_proposition': prop.id,
            'message': 'Proposition créée avec succès.'
        }, status=201)

# ─────────────────────────────────────────────────────────────────────────────
# 3. DEMANDES DE STAGE
# ─────────────────────────────────────────────────────────────────────────────

class DemandeListView(View):
    """
    GET: Liste les demandes. Filtrable par id_etudiant ou id_enseignant.
    POST: Un étudiant postule à une offre de stage (avec simulation d'upload).
    """
    def get(self, request):
        id_etudiant = request.GET.get('id_etudiant')
        id_enseignant = request.GET.get('id_enseignant')
        
        demandes = DemandeStage.objects.all()
        if id_etudiant:
            demandes = demandes.filter(etudiant_id=id_etudiant)
        elif id_enseignant:
            demandes = demandes.filter(proposition__enseignant_id=id_enseignant)

        data = []
        for dem in demandes.order_by('-date_demande'):
            # Check for refus/attestation
            refus_motif = getattr(dem, 'details_refus', None)
            attestation_num = getattr(dem, 'attestation', None)
            
            data.append({
                'id': dem.id,
                'date_demande': dem.date_demande.isoformat(),
                'statut': dem.statut,
                'cv_url': dem.cv.name if dem.cv else '',
                'lettre_motivation': dem.lettre_motivation,
                'etudiant': {
                    'id': dem.etudiant.id,
                    'nom': dem.etudiant.nom,
                    'prenom': dem.etudiant.prenom,
                    'matricule': dem.etudiant.matricule,
                    'specialite': dem.etudiant.specialite
                },
                'proposition': {
                    'id': dem.proposition.id,
                    'titre': dem.proposition.titre,
                    'entreprise': dem.proposition.entreprise
                },
                'motif_refus': refus_motif.motif if refus_motif else None,
                'attestation_numero': attestation_num.numero if attestation_num else None
            })
        return JsonResponse({'demandes': data})

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        # On accepte du JSON ou du Multipart (si upload réel de fichier)
        if request.content_type.startswith('multipart/form-data'):
            id_etudiant = request.POST.get('id_etudiant')
            id_proposition = request.POST.get('id_proposition')
            lettre_motivation = request.POST.get('lettre_motivation', '')
            cv_file = request.FILES.get('cv')
        else:
            data = get_json_payload(request)
            id_etudiant = data.get('id_etudiant')
            id_proposition = data.get('id_proposition')
            lettre_motivation = data.get('lettre_motivation', '')
            cv_file = 'dummy_path_to_cv.pdf' # simulation

        if not id_etudiant or not id_proposition:
            return JsonResponse({'error': 'id_etudiant et id_proposition requis.'}, status=400)

        try:
            etudiant = Etudiant.objects.get(id_user=id_etudiant)
        except Etudiant.DoesNotExist:
            return JsonResponse({'error': 'Étudiant introuvable.'}, status=404)

        try:
            proposition = PropositionStage.objects.get(id=id_proposition)
        except PropositionStage.DoesNotExist:
            return JsonResponse({'error': 'Proposition de stage introuvable.'}, status=404)

        demande = DemandeStage.objects.create(
            etudiant=etudiant,
            proposition=proposition,
            lettre_motivation=lettre_motivation,
            cv=cv_file
        )

        # Envoyer une notification à l'enseignant
        Notification.objects.create(
            utilisateur=proposition.enseignant,
            message=f"Nouvelle demande de stage reçue pour '{proposition.titre}' de la part de {etudiant.prenom} {etudiant.nom}."
        )

        return JsonResponse({
            'success': True,
            'id_demande': demande.id,
            'message': 'Candidature déposée avec succès.'
        }, status=201)

# ─────────────────────────────────────────────────────────────────────────────
# 4. GESTION DES STATUTS (Acceptation, Refus, Validation, Archivage)
# ─────────────────────────────────────────────────────────────────────────────

@csrf_exempt
def api_traitement_demande(request, id_demande):
    """
    Traite le statut d'une candidature de stage.
    Payload: { "statut": "Acceptée" | "Refusée" | "Validée" | "Archivée", "motif": "...", "appreciation": "..." }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST uniquement.'}, status=405)

    demande = get_object_or_404(DemandeStage, pk=id_demande)
    data = get_json_payload(request)
    statut = data.get('statut')

    if not statut:
        return JsonResponse({'error': 'Nouveau statut requis.'}, status=400)

    # 1. Gestion du Refus
    if statut == 'Refusée':
        motif = data.get('motif', 'Aucun motif renseigné.')
        demande.statut = 'Refusée'
        demande.save()
        
        # Enregistrer ou mettre à jour le motif de refus
        Refus.objects.update_or_create(demande=demande, defaults={'motif': motif})
        
        # Supprimer l'attestation si elle existait auparavant
        Attestation.objects.filter(demande=demande).delete()
        
        # Notifier l'étudiant
        Notification.objects.create(
            utilisateur=demande.etudiant,
            message=f"Votre demande de stage pour '{demande.proposition.titre}' a été refusée. Motif : {motif}."
        )

    # 2. Gestion de l'Acceptation
    elif statut == 'Acceptée':
        demande.statut = 'Acceptée'
        demande.save()
        # Supprimer le refus si présent
        Refus.objects.filter(demande=demande).delete()
        
        Notification.objects.create(
            utilisateur=demande.etudiant,
            message=f"Félicitations, votre demande de stage pour '{demande.proposition.titre}' a été acceptée par l'enseignant."
        )

    # 3. Gestion de la Validation finale et Génération de l'Attestation
    elif statut == 'Validée':
        demande.statut = 'Validée'
        demande.save()
        
        # Simulation de génération d'attestation
        import uuid
        num_attestation = f"ATT-{uuid.uuid4().hex[:8].upper()}"
        appreciation = data.get('appreciation', 'Très bon stage.')
        mention = data.get('mention', 'Bien')
        
        Attestation.objects.update_or_create(
            demande=demande,
            defaults={
                'numero': num_attestation,
                'fichier_pdf': f"attestations/attestation_{demande.id}.pdf",
                'appreciation': appreciation,
                'mention': mention
            }
        )

        Notification.objects.create(
            utilisateur=demande.etudiant,
            message=f"Votre stage pour '{demande.proposition.titre}' a été validé ! Votre attestation N° {num_attestation} est disponible."
        )

    # 4. Archivage
    elif statut == 'Archivée':
        demande.statut = 'Archivée'
        demande.save()
        
        Archive.objects.get_or_create(demande=demande)
        
        Notification.objects.create(
            utilisateur=demande.etudiant,
            message=f"Le dossier de votre stage pour '{demande.proposition.titre}' a été archivé."
        )

    else:
        return JsonResponse({'error': 'Statut invalide.'}, status=400)

    return JsonResponse({
        'success': True,
        'nouveau_statut': demande.statut,
        'message': f"Candidature mise à jour vers '{demande.statut}'."
    })

# ─────────────────────────────────────────────────────────────────────────────
# 5. NOTIFICATIONS
# ─────────────────────────────────────────────────────────────────────────────

class NotificationListView(View):
    """
    GET: Récupère les notifications d'un utilisateur.
    POST: Marque les notifications comme lues.
    """
    def get(self, request):
        id_user = request.GET.get('id_user')
        if not id_user:
            return JsonResponse({'error': 'id_user requis.'}, status=400)
            
        notifications = Notification.objects.filter(utilisateur_id=id_user).order_by('-date_envoi')
        data = []
        for notif in notifications:
            data.append({
                'id': notif.id,
                'message': notif.message,
                'lu': notif.lu,
                'date_envoi': notif.date_envoi.isoformat()
            })
        return JsonResponse({'notifications': data})

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        data = get_json_payload(request)
        id_user = data.get('id_user')
        if not id_user:
            return JsonResponse({'error': 'id_user requis.'}, status=400)

        # Marque toutes les notifications de l'utilisateur comme lues
        Notification.objects.filter(utilisateur_id=id_user, lu=False).update(lu=True)
        return JsonResponse({'success': True, 'message': 'Toutes les notifications ont été marquées comme lues.'})
