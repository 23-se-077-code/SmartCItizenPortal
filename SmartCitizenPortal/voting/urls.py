from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="voting_dashboard"),
    path("verify-identity/", views.voting_verification, name="verify_identity"),
    path("vote/<int:step>/", views.vote_wizard, name="voting_wizard_step"),
    path("vote/", views.vote_wizard, {'step': 1}, name="voting_vote"),
    path("results/", views.results, name="voting_results"),
    path("update-profile/", views.update_profile, name="update_profile"),
]