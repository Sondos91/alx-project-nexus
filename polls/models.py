"""
Database models for the Online Poll System.
Optimized for real-time voting and result computation.
"""
from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone
from django.contrib.auth.models import User
import uuid


class Poll(models.Model):
    """
    Represents a poll with multiple voting options.
    Optimized for frequent read operations and real-time results.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(5), MaxLengthValidator(200)],
        help_text="Poll title (5-200 characters)"
    )
    description = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Optional poll description (max 1000 characters)"
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_polls',
        help_text="User who created this poll"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Optional expiration date for the poll"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether the poll is currently accepting votes"
    )
    allow_multiple_votes = models.BooleanField(
        default=False,
        help_text="Whether users can vote multiple times"
    )
    total_votes = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Cached total vote count for performance"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'expires_at']),
            models.Index(fields=['creator', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} (ID: {self.id})"
    
    @property
    def is_expired(self):
        """Check if the poll has expired."""
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at
    
    @property
    def can_vote(self):
        """Check if the poll is currently accepting votes."""
        return self.is_active and not self.is_expired
    
    def update_total_votes(self):
        """Update the cached total vote count."""
        self.total_votes = self.votes.count()
        self.save(update_fields=['total_votes'])


class PollOption(models.Model):
    """
    Represents a voting option within a poll.
    Optimized for frequent vote counting operations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='options',
        db_index=True
    )
    text = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(1), MaxLengthValidator(200)],
        help_text="Option text (1-200 characters)"
    )
    vote_count = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Cached vote count for this option"
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Display order of the option"
    )
    
    class Meta:
        ordering = ['order', 'text']
        unique_together = ['poll', 'text']
        indexes = [
            models.Index(fields=['poll', 'vote_count']),
        ]
    
    def __str__(self):
        return f"{self.text} ({self.vote_count} votes)"
    
    def update_vote_count(self):
        """Update the cached vote count for this option."""
        self.vote_count = self.votes.count()
        self.save(update_fields=['vote_count'])


class Vote(models.Model):
    """
    Represents a single vote cast by a user.
    Optimized for duplicate vote prevention and result computation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='votes',
        db_index=True
    )
    option = models.ForeignKey(
        PollOption,
        on_delete=models.CASCADE,
        related_name='votes',
        db_index=True
    )
    voter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='votes',
        null=True,
        blank=True,
        db_index=True,
        help_text="User who cast the vote (null for anonymous votes)"
    )
    voter_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the voter (for anonymous vote tracking)"
    )
    voter_session = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Session ID for anonymous vote tracking"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['poll', 'voter']),
            models.Index(fields=['poll', 'voter_ip']),
            models.Index(fields=['poll', 'voter_session']),
            models.Index(fields=['option', 'created_at']),
        ]
    
    def __str__(self):
        voter_info = self.voter.username if self.voter else f"IP: {self.voter_ip}"
        return f"{voter_info} voted for '{self.option.text}' in '{self.poll.title}'"
    
    def save(self, *args, **kwargs):
        """Override save to update cached vote counts."""
        super().save(*args, **kwargs)
        # Update cached counts
        self.option.update_vote_count()
        self.poll.update_total_votes()
    
    def delete(self, *args, **kwargs):
        """Override delete to update cached vote counts."""
        super().delete(*args, **kwargs)
        # Update cached counts
        self.option.update_vote_count()
        self.poll.update_total_votes()


class PollResult(models.Model):
    """
    Cached poll results for performance optimization.
    Updated asynchronously to avoid blocking vote operations.
    """
    poll = models.OneToOneField(
        Poll,
        on_delete=models.CASCADE,
        related_name='result',
        primary_key=True
    )
    results_data = models.JSONField(
        help_text="Cached poll results in JSON format"
    )
    last_updated = models.DateTimeField(auto_now=True)
    total_votes = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Results for {self.poll.title} (Updated: {self.last_updated})"
    
    def update_results(self):
        """Update the cached results data."""
        options_data = []
        for option in self.poll.options.all():
            percentage = (option.vote_count / self.poll.total_votes * 100) if self.poll.total_votes > 0 else 0
            options_data.append({
                'id': str(option.id),
                'text': option.text,
                'vote_count': option.vote_count,
                'percentage': round(percentage, 2)
            })
        
        self.results_data = {
            'poll_id': str(self.poll.id),
            'poll_title': self.poll.title,
            'total_votes': self.poll.total_votes,
            'options': options_data,
            'last_updated': self.last_updated.isoformat()
        }
        self.total_votes = self.poll.total_votes
        self.save()
