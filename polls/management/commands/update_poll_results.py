"""
Django management command to update poll results.
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from polls.models import Poll, PollResult
from polls.views import generate_poll_results


class Command(BaseCommand):
    help = 'Update cached poll results for all active polls'

    def add_arguments(self, parser):
        parser.add_argument(
            '--poll-id',
            type=str,
            help='Update results for a specific poll ID',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if results are recent',
        )

    def handle(self, *args, **options):
        poll_id = options.get('poll_id')
        force = options.get('force', False)
        
        if poll_id:
            try:
                poll = Poll.objects.get(id=poll_id)
                self.update_poll_results(poll, force)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated results for poll: {poll.title}')
                )
            except Poll.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Poll with ID {poll_id} not found')
                )
        else:
            # Update all active polls
            polls = Poll.objects.filter(is_active=True)
            updated_count = 0
            
            for poll in polls:
                if self.update_poll_results(poll, force):
                    updated_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {updated_count} polls')
            )

    def update_poll_results(self, poll, force=False):
        """Update results for a specific poll."""
        try:
            # Check if we need to update
            if not force:
                poll_result = PollResult.objects.filter(poll=poll).first()
                if poll_result and poll_result.total_votes == poll.total_votes:
                    return False
            
            # Generate new results
            results = generate_poll_results(poll)
            
            # Update cache
            cache_key = f"poll_results_{poll.id}"
            cache.set(cache_key, results, timeout=300)
            
            # Update or create PollResult record
            poll_result, created = PollResult.objects.get_or_create(poll=poll)
            poll_result.update_results()
            
            return True
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating poll {poll.id}: {str(e)}')
            )
            return False
