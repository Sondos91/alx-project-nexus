"""
URL configuration for polls app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Poll management
    path('polls/', views.PollListView.as_view(), name='poll-list'),
    path('polls/<uuid:poll_id>/', views.PollDetailView.as_view(), name='poll-detail'),
    
    # Voting
    path('polls/<uuid:poll_id>/vote/', views.cast_vote, name='cast-vote'),
    path('polls/<uuid:poll_id>/results/', views.poll_results, name='poll-results'),
    
    # User-specific endpoints
    path('user/polls/', views.user_polls, name='user-polls'),
    path('user/votes/', views.user_votes, name='user-votes'),
    path('user/profile/', views.user_profile, name='user-profile'),
]
