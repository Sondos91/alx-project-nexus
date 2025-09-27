"""
URL configuration for polls app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    
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
    path('test-auth/', views.test_auth, name='test-auth'),
    path('debug-auth/', views.debug_auth, name='debug-auth'),
]
