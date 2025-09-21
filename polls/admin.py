"""
Admin configuration for the Online Poll System.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Poll, PollOption, Vote, PollResult


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'creator', 'is_active', 'total_votes', 
        'created_at', 'expires_at', 'is_expired_display'
    ]
    list_filter = ['is_active', 'created_at', 'expires_at', 'creator']
    search_fields = ['title', 'description', 'creator__username']
    readonly_fields = ['id', 'total_votes', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'description', 'creator')
        }),
        ('Settings', {
            'fields': ('is_active', 'allow_multiple_votes', 'expires_at')
        }),
        ('Statistics', {
            'fields': ('total_votes', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_expired_display(self, obj):
        """Display expiration status with color coding."""
        if obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        elif obj.expires_at:
            return format_html('<span style="color: orange;">Active (Expires: {})</span>', obj.expires_at)
        else:
            return format_html('<span style="color: green;">Active (No expiration)</span>')
    
    is_expired_display.short_description = 'Status'


@admin.register(PollOption)
class PollOptionAdmin(admin.ModelAdmin):
    list_display = ['text', 'poll', 'vote_count', 'order']
    list_filter = ['poll']
    search_fields = ['text', 'poll__title']
    readonly_fields = ['id', 'vote_count']
    ordering = ['poll', 'order']
    
    fieldsets = (
        ('Option Information', {
            'fields': ('id', 'poll', 'text', 'order')
        }),
        ('Statistics', {
            'fields': ('vote_count',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = [
        'voter_display', 'poll', 'option', 'created_at', 'voter_type'
    ]
    list_filter = ['created_at', 'poll', 'voter']
    search_fields = [
        'poll__title', 'option__text', 'voter__username', 
        'voter_ip', 'voter_session'
    ]
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Vote Information', {
            'fields': ('id', 'poll', 'option', 'created_at')
        }),
        ('Voter Information', {
            'fields': ('voter', 'voter_ip', 'voter_session'),
            'classes': ('collapse',)
        }),
    )
    
    def voter_display(self, obj):
        """Display voter information."""
        if obj.voter:
            return f"{obj.voter.username} (User)"
        elif obj.voter_ip:
            return f"{obj.voter_ip} (IP)"
        elif obj.voter_session:
            return f"{obj.voter_session[:8]}... (Session)"
        return "Unknown"
    
    def voter_type(self, obj):
        """Display voter type with color coding."""
        if obj.voter:
            return format_html('<span style="color: blue;">Authenticated</span>')
        else:
            return format_html('<span style="color: gray;">Anonymous</span>')
    
    voter_display.short_description = 'Voter'
    voter_type.short_description = 'Type'


@admin.register(PollResult)
class PollResultAdmin(admin.ModelAdmin):
    list_display = ['poll', 'total_votes', 'last_updated']
    list_filter = ['last_updated', 'poll__creator']
    search_fields = ['poll__title']
    readonly_fields = ['poll', 'results_data', 'last_updated', 'total_votes']
    
    fieldsets = (
        ('Result Information', {
            'fields': ('poll', 'total_votes', 'last_updated')
        }),
        ('Results Data', {
            'fields': ('results_data',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent manual creation of results."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent manual editing of results."""
        return False
