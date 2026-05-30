import os
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stageflow.settings')
django.setup()

from stages.models import Utilisateur, Etudiant, Enseignant, PropositionStage, Notification, DemandeStage

def seed():
    print("Début du peuplement de la base de données...")

    # Nettoyage des anciennes données dans le bon ordre des clés étrangères (RESTRICT)
    Notification.objects.all().delete()
    DemandeStage.objects.all().delete()
    PropositionStage.objects.all().delete()
    Utilisateur.objects.all().delete()
    print("Anciennes donnees supprimees.")

    # 1. Création de l'enseignant (Ahmed Benali)
    enseignant = Enseignant.objects.create(
        nom="Benali",
        prenom="Ahmed",
        email="a.benali@estin.dz",
        role="enseignant",
        grade="Maître de Conférences (MCA)",
        departement="Informatique"
    )
    print(f"Enseignant créé : {enseignant}")

    # 2. Création de l'étudiante (Amina Ouali)
    etudiant = Etudiant.objects.create(
        nom="Ouali",
        prenom="Amina",
        email="a.ouali@estin.dz",
        role="etudiant",
        matricule="20220345",
        specialite="Cybersécurité",
        niveau="L3",
        departement="Informatique"
    )
    print(f"Étudiante créée : {etudiant}")

    # 3. Création de l'administrateur (DPGR)
    admin = Utilisateur.objects.create(
        nom="Admin",
        prenom="DPGR",
        email="admin@estin.dz",
        role="admin"
    )
    print(f"Administrateur créé : {admin}")

    # 4. Création des propositions de stages (liées à l'enseignant Ahmed Benali)
    propositions = [
        {
            "titre": "Application de gestion des ressources humaines",
            "description": "Conception et développement d'une application web full-stack moderne avec React et Node.js pour automatiser le suivi des effectifs.",
            "technologies": "React, Node.js, MongoDB",
            "entreprise": "Sonatrach",
            "statut": "Ouvert"
        },
        {
            "titre": "Analyse prédictive des données médicales",
            "description": "Étude et modélisation prédictive sur des jeux de données de patients réels pour l'aide au diagnostic précoce.",
            "technologies": "Python, Pandas, scikit-learn",
            "entreprise": "CHU Béjaïa",
            "statut": "Ouvert"
        },
        {
            "titre": "Audit de sécurité et tests d'intrusion",
            "description": "Réaliser un audit de vulnérabilité complet et des tests d'intrusion simulés sur les serveurs internes de la banque.",
            "technologies": "Kali Linux, Metasploit, Nmap",
            "entreprise": "BNA Banque",
            "statut": "Ouvert"
        },
        {
            "titre": "Chatbot NLP pour service client automatisé",
            "description": "Conception d'un agent conversationnel intelligent à base de Transformers pour répondre en temps réel aux requêtes clients.",
            "technologies": "Python, HuggingFace, LangChain",
            "entreprise": "Djezzy",
            "statut": "Ouvert"
        }
    ]

    created_props = []
    for p in propositions:
        prop = PropositionStage.objects.create(
            titre=p["titre"],
            description=p["description"],
            technologies=p["technologies"],
            entreprise=p["entreprise"],
            statut=p["statut"],
            enseignant=enseignant
        )
        created_props.append(prop)
        print(f"Proposition créée : {prop}")

    # 5. Création d'une demande de stage fictive (Amina postule au stage d'Audit de Sécurité de la BNA)
    demande = DemandeStage.objects.create(
        etudiant=etudiant,
        proposition=created_props[2], # Audit de sécurité BNA
        lettre_motivation="Je suis vivement intéressée par cette offre de stage pratique au sein de votre prestigieuse institution financière. Ma spécialité en Cybersécurité correspond parfaitement aux prérequis.",
        cv="cvs/2026/05/cv_amina_ouali.pdf",
        statut="En attente"
    )
    print("Demande de stage creee.")

    # 6. Création de notifications d'accueil
    Notification.objects.create(
        utilisateur=etudiant,
        message="Bienvenue sur StageFlow ! Complétez vos candidatures pour les stages ouverts."
    )
    Notification.objects.create(
        utilisateur=enseignant,
        message="Bienvenue sur StageFlow ! Vous pouvez désormais publier de nouveaux sujets de stages."
    )
    print("Notifications de bienvenue creees.")

    print("Peuplement terminé avec succès !")

if __name__ == "__main__":
    seed()
