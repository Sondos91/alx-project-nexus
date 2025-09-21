"""
API views for the Online Poll System.
Provides RESTful endpoints for poll management, voting, and results.
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import Poll, PollOption, Vote, PollResult
from .serializers import (
    PollListSerializer, PollDetailSerializer, PollCreateSerializer,
    VoteSerializer, PollResultSerializer, UserSerializer
)


class PollListView(generics.ListCreateAPIView):
    """
    List all polls or create a new poll.
    
    GET: Retrieve a paginated list of polls with basic information.
    POST: Create a new poll (requires authentication).
    """
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PollCreateSerializer
        return PollListSerializer
    
    def get_queryset(self):
        """Filter polls based on query parameters."""
        queryset = Poll.objects.select_related('creator').prefetch_related('options')
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by creator
        creator = self.request.query_params.get('creator')
        if creator:
            queryset = queryset.filter(creator__username__icontains=creator)
        
        # Filter by search term
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset.order_by('-created_at')
    
    @extend_schema(
        summary="List polls",
        description="Retrieve a paginated list of polls with filtering options.",
        parameters=[
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by active status'
            ),
            OpenApiParameter(
                name='creator',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by creator username'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search in title and description'
            ),
            OpenApiParameter(
                name='date_from',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter polls created from this date'
            ),
            OpenApiParameter(
                name='date_to',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter polls created until this date'
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create poll",
        description="Create a new poll with multiple options.",
        examples=[
            OpenApiExample(
                'Poll Creation Example',
                value={
                    "title": "What's your favorite programming language?",
                    "description": "Choose your preferred language for backend development",
                    "expires_at": "2024-12-31T23:59:59Z",
                    "allow_multiple_votes": False,
                    "options": [
                        {"text": "Python", "order": 1},
                        {"text": "JavaScript", "order": 2},
                        {"text": "Java", "order": 3},
                        {"text": "Go", "order": 4}
                    ]
                }
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PollDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a poll.
    
    GET: Retrieve detailed poll information with options and results.
    PUT/PATCH: Update poll (only by creator).
    DELETE: Delete poll (only by creator).
    """
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PollCreateSerializer
        return PollDetailSerializer
    
    def get_queryset(self):
        return Poll.objects.select_related('creator').prefetch_related('options')
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def perform_update(self, serializer):
        """Ensure only the creator can update the poll."""
        if serializer.instance.creator != self.request.user:
            raise PermissionError("You can only update polls you created.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Ensure only the creator can delete the poll."""
        if instance.creator != self.request.user:
            raise PermissionError("You can only delete polls you created.")
        instance.delete()
    
    @extend_schema(
        summary="Get poll details",
        description="Retrieve detailed information about a specific poll including options and voting status."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update poll",
        description="Update poll details (only by creator)."
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partially update poll",
        description="Partially update poll details (only by creator)."
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete poll",
        description="Delete a poll (only by creator)."
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


@extend_schema(
    summary="Cast vote",
    description="Cast a vote for a specific poll option.",
    request=VoteSerializer,
    responses={
        201: VoteSerializer,
        400: {"description": "Validation error"},
        404: {"description": "Poll not found"},
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def cast_vote(request, poll_id):
    """
    Cast a vote for a poll option.
    
    Supports both authenticated and anonymous voting.
    Prevents duplicate votes unless poll allows multiple votes.
    """
    poll = get_object_or_404(Poll, id=poll_id)
    
    serializer = VoteSerializer(
        data=request.data,
        context={'poll': poll, 'request': request}
    )
    
    if serializer.is_valid():
        vote = serializer.save()
        
        # Update cached results asynchronously
        update_poll_results_async.delay(poll_id)
        
        return Response({
            'message': 'Vote cast successfully',
            'vote_id': vote.id,
            'option_id': vote.option.id,
            'option_text': vote.option.text
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get poll results",
    description="Retrieve real-time poll results with vote counts and percentages.",
    responses={
        200: PollResultSerializer,
        404: {"description": "Poll not found"},
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def poll_results(request, poll_id):
    """
    Get real-time poll results.
    
    Returns cached results for performance, with vote counts and percentages.
    """
    poll = get_object_or_404(Poll, id=poll_id)
    
    # Try to get cached results first
    cache_key = f"poll_results_{poll_id}"
    results = cache.get(cache_key)
    
    if not results:
        # Generate results if not cached
        results = generate_poll_results(poll)
        cache.set(cache_key, results, timeout=300)  # Cache for 5 minutes
    
    return Response(results, status=status.HTTP_200_OK)


def generate_poll_results(poll):
    """Generate poll results with vote counts and percentages."""
    options_data = []
    total_votes = poll.total_votes
    
    for option in poll.options.all():
        percentage = (option.vote_count / total_votes * 100) if total_votes > 0 else 0
        options_data.append({
            'id': str(option.id),
            'text': option.text,
            'vote_count': option.vote_count,
            'percentage': round(percentage, 2)
        })
    
    return {
        'poll_id': str(poll.id),
        'poll_title': poll.title,
        'total_votes': total_votes,
        'options': options_data,
        'last_updated': timezone.now().isoformat(),
        'is_active': poll.is_active,
        'is_expired': poll.is_expired
    }


@extend_schema(
    summary="Get user polls",
    description="Retrieve polls created by the authenticated user.",
    responses={
        200: PollListSerializer(many=True),
        401: {"description": "Authentication required"},
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_polls(request):
    """Get polls created by the authenticated user."""
    polls = Poll.objects.filter(creator=request.user).select_related('creator').prefetch_related('options')
    serializer = PollListSerializer(polls, many=True, context={'request': request})
    return Response(serializer.data)


@extend_schema(
    summary="Get user votes",
    description="Retrieve votes cast by the authenticated user.",
    responses={
        200: {"description": "List of user votes"},
        401: {"description": "Authentication required"},
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_votes(request):
    """Get votes cast by the authenticated user."""
    votes = Vote.objects.filter(voter=request.user).select_related('poll', 'option')
    
    votes_data = []
    for vote in votes:
        votes_data.append({
            'id': str(vote.id),
            'poll_id': str(vote.poll.id),
            'poll_title': vote.poll.title,
            'option_text': vote.option.text,
            'created_at': vote.created_at.isoformat()
        })
    
    return Response(votes_data)


@extend_schema(
    summary="Get user profile",
    description="Retrieve authenticated user profile with statistics.",
    responses={
        200: UserSerializer,
        401: {"description": "Authentication required"},
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get authenticated user profile with poll and vote statistics."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# Celery task for async result updates
from celery import shared_task

@shared_task
def update_poll_results_async(poll_id):
    """Update poll results asynchronously."""
    try:
        poll = Poll.objects.get(id=poll_id)
        
        # Update cached results
        cache_key = f"poll_results_{poll_id}"
        results = generate_poll_results(poll)
        cache.set(cache_key, results, timeout=300)
        
        # Update or create PollResult record
        poll_result, created = PollResult.objects.get_or_create(poll=poll)
        poll_result.update_results()
        
    except Poll.DoesNotExist:
        pass
