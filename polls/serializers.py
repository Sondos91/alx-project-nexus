"""
Serializers for the Online Poll System API.
Provides data validation and serialization for all API endpoints.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Poll, PollOption, Vote, PollResult


class PollOptionSerializer(serializers.ModelSerializer):
    """Serializer for poll options."""
    vote_count = serializers.ReadOnlyField()
    
    class Meta:
        model = PollOption
        fields = ['id', 'text', 'vote_count', 'order']
        read_only_fields = ['id', 'vote_count']


class PollOptionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating poll options."""
    
    class Meta:
        model = PollOption
        fields = ['text', 'order']


class PollListSerializer(serializers.ModelSerializer):
    """Serializer for poll list view (minimal data)."""
    creator_username = serializers.CharField(source='creator.username', read_only=True)
    option_count = serializers.SerializerMethodField()
    is_expired = serializers.ReadOnlyField()
    can_vote = serializers.ReadOnlyField()
    
    class Meta:
        model = Poll
        fields = [
            'id', 'title', 'description', 'creator_username', 'created_at',
            'expires_at', 'is_active', 'total_votes', 'option_count',
            'is_expired', 'can_vote'
        ]
    
    def get_option_count(self, obj):
        return obj.options.count()


class PollDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed poll view with options."""
    creator_username = serializers.CharField(source='creator.username', read_only=True)
    options = PollOptionSerializer(many=True, read_only=True)
    is_expired = serializers.ReadOnlyField()
    can_vote = serializers.ReadOnlyField()
    user_has_voted = serializers.SerializerMethodField()
    
    class Meta:
        model = Poll
        fields = [
            'id', 'title', 'description', 'creator_username', 'created_at',
            'expires_at', 'is_active', 'allow_multiple_votes', 'total_votes',
            'options', 'is_expired', 'can_vote', 'user_has_voted'
        ]
    
    def get_user_has_voted(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        return obj.votes.filter(voter=request.user).exists()


class PollCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new polls."""
    options = PollOptionCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = Poll
        fields = [
            'title', 'description', 'expires_at', 'allow_multiple_votes',
            'options'
        ]
    
    def validate_title(self, value):
        """Validate poll title."""
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long.")
        return value.strip()
    
    def validate_options(self, value):
        """Validate poll options."""
        if len(value) < 2:
            raise serializers.ValidationError("Poll must have at least 2 options.")
        
        if len(value) > 10:
            raise serializers.ValidationError("Poll cannot have more than 10 options.")
        
        # Check for duplicate option texts
        option_texts = [option['text'].strip() for option in value]
        if len(option_texts) != len(set(option_texts)):
            raise serializers.ValidationError("Poll options must be unique.")
        
        return value
    
    def validate_expires_at(self, value):
        """Validate expiration date."""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Expiration date must be in the future.")
        return value
    
    def create(self, validated_data):
        """Create poll with options."""
        options_data = validated_data.pop('options')
        validated_data['creator'] = self.context['request'].user
        poll = Poll.objects.create(**validated_data)
        
        # Create poll options
        for i, option_data in enumerate(options_data):
            PollOption.objects.create(
                poll=poll,
                text=option_data['text'].strip(),
                order=option_data.get('order', i)
            )
        
        return poll


class VoteSerializer(serializers.ModelSerializer):
    """Serializer for casting votes."""
    option_text = serializers.CharField(write_only=True)
    option_id = serializers.UUIDField(read_only=True)
    
    class Meta:
        model = Vote
        fields = ['option_text', 'option_id']
        read_only_fields = ['option_id']
    
    def validate_option_text(self, value):
        """Validate that the option exists for this poll."""
        poll = self.context['poll']
        try:
            option = poll.options.get(text__iexact=value.strip())
            return option
        except PollOption.DoesNotExist:
            available_options = [opt.text for opt in poll.options.all()]
            raise serializers.ValidationError(
                f"Invalid option. Available options: {', '.join(available_options)}"
            )
    
    def validate(self, attrs):
        """Validate vote constraints."""
        poll = self.context['poll']
        request = self.context['request']
        option = attrs['option_text']
        
        # Check if poll is active and not expired
        if not poll.can_vote:
            if poll.is_expired:
                raise serializers.ValidationError("This poll has expired.")
            else:
                raise serializers.ValidationError("This poll is not currently active.")
        
        # Check for duplicate votes
        if not poll.allow_multiple_votes:
            if request.user.is_authenticated:
                if poll.votes.filter(voter=request.user).exists():
                    raise serializers.ValidationError("You have already voted in this poll.")
            else:
                # For anonymous users, check by IP and session
                voter_ip = self.get_client_ip(request)
                voter_session = request.session.session_key
                
                if voter_ip and poll.votes.filter(voter_ip=voter_ip).exists():
                    raise serializers.ValidationError("You have already voted in this poll.")
                
                if voter_session and poll.votes.filter(voter_session=voter_session).exists():
                    raise serializers.ValidationError("You have already voted in this poll.")
        
        return attrs
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def create(self, validated_data):
        """Create vote."""
        poll = self.context['poll']
        request = self.context['request']
        option = validated_data['option_text']
        
        vote_data = {
            'poll': poll,
            'option': option,
        }
        
        if request.user.is_authenticated:
            vote_data['voter'] = request.user
        else:
            vote_data['voter_ip'] = self.get_client_ip(request)
            vote_data['voter_session'] = request.session.session_key
        
        vote = Vote.objects.create(**vote_data)
        return vote


class PollResultSerializer(serializers.ModelSerializer):
    """Serializer for poll results."""
    results_data = serializers.JSONField(read_only=True)
    last_updated = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = PollResult
        fields = ['results_data', 'last_updated', 'total_votes']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user information."""
    created_polls_count = serializers.SerializerMethodField()
    votes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'date_joined', 'created_polls_count', 'votes_count']
        read_only_fields = ['id', 'date_joined']
    
    def get_created_polls_count(self, obj):
        return obj.created_polls.count()
    
    def get_votes_count(self, obj):
        return obj.votes.count()
