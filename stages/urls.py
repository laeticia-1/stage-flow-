from django.urls import path
from .views import (
    api_login,
    PropositionListView,
    DemandeListView,
    api_traitement_demande,
    NotificationListView
)

urlpatterns = [
    path('login/', api_login, name='api_login'),
    path('propositions/', PropositionListView.as_view(), name='api_propositions'),
    path('demandes/', DemandeListView.as_view(), name='api_demandes'),
    path('demandes/<int:id_demande>/traitement/', api_traitement_demande, name='api_traitement_demande'),
    path('notifications/', NotificationListView.as_view(), name='api_notifications'),
]
