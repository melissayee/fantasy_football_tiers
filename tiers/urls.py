from django.urls import path, include
from . import views

urlpatterns = [
    path('tiers/<str:scoring>/<str:position>', views.view_tiers, name='tiers'),
    path('<str:scoring>/<int:league_id>/', views.all_players, name='all_players'),
    path('<int:league_id>/<int:team_id>', views.view_team, name='team'),
]
