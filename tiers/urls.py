from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tiers/<str:scoring>', views.view_tiers, name='tiers'),
    path('all_players/<str:scoring>/<int:league_id>/', views.all_players, name='all_players'),
    path('roster/<str:scoring>/<int:league_id>/<int:team_id>', views.view_team, name='team'),
    path('matchup/<str:scoring>/<int:league_id>/<int:team_id>', views.view_matchup, name='matchup'),
]
