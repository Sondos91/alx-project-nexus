"""
Tests for the Online Poll System.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from .models import Poll, PollOption, Vote


class PollModelTest(TestCase):
    """Test cases for Poll model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.poll = Poll.objects.create(
            title='Test Poll',
            description='A test poll',
            creator=self.user
        )
    
    def test_poll_creation(self):
        """Test poll creation."""
        self.assertEqual(self.poll.title, 'Test Poll')
        self.assertEqual(self.poll.creator, self.user)
        self.assertTrue(self.poll.is_active)
        self.assertFalse(self.poll.is_expired)
    
    def test_poll_expiration(self):
        """Test poll expiration logic."""
        # Test with future expiration
        future_time = timezone.now() + timedelta(days=1)
        self.poll.expires_at = future_time
        self.poll.save()
        self.assertFalse(self.poll.is_expired)
        
        # Test with past expiration
        past_time = timezone.now() - timedelta(days=1)
        self.poll.expires_at = past_time
        self.poll.save()
        self.assertTrue(self.poll.is_expired)
    
    def test_can_vote(self):
        """Test voting eligibility."""
        # Active poll should allow voting
        self.assertTrue(self.poll.can_vote)
        
        # Inactive poll should not allow voting
        self.poll.is_active = False
        self.poll.save()
        self.assertFalse(self.poll.can_vote)
        
        # Expired poll should not allow voting
        self.poll.is_active = True
        self.poll.expires_at = timezone.now() - timedelta(days=1)
        self.poll.save()
        self.assertFalse(self.poll.can_vote)


class PollOptionModelTest(TestCase):
    """Test cases for PollOption model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.poll = Poll.objects.create(
            title='Test Poll',
            creator=self.user
        )
        self.option = PollOption.objects.create(
            poll=self.poll,
            text='Option 1',
            order=1
        )
    
    def test_option_creation(self):
        """Test poll option creation."""
        self.assertEqual(self.option.text, 'Option 1')
        self.assertEqual(self.option.poll, self.poll)
        self.assertEqual(self.option.vote_count, 0)
    
    def test_vote_count_update(self):
        """Test vote count update."""
        # Create a vote
        Vote.objects.create(
            poll=self.poll,
            option=self.option,
            voter=self.user
        )
        
        # Update vote count
        self.option.update_vote_count()
        self.assertEqual(self.option.vote_count, 1)


class VoteModelTest(TestCase):
    """Test cases for Vote model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.poll = Poll.objects.create(
            title='Test Poll',
            creator=self.user
        )
        self.option = PollOption.objects.create(
            poll=self.poll,
            text='Option 1'
        )
    
    def test_vote_creation(self):
        """Test vote creation."""
        vote = Vote.objects.create(
            poll=self.poll,
            option=self.option,
            voter=self.user
        )
        
        self.assertEqual(vote.poll, self.poll)
        self.assertEqual(vote.option, self.option)
        self.assertEqual(vote.voter, self.user)
    
    def test_vote_save_updates_counts(self):
        """Test that saving a vote updates cached counts."""
        initial_poll_votes = self.poll.total_votes
        initial_option_votes = self.option.vote_count
        
        Vote.objects.create(
            poll=self.poll,
            option=self.option,
            voter=self.user
        )
        
        # Refresh from database
        self.poll.refresh_from_db()
        self.option.refresh_from_db()
        
        self.assertEqual(self.poll.total_votes, initial_poll_votes + 1)
        self.assertEqual(self.option.vote_count, initial_option_votes + 1)


class PollAPITest(APITestCase):
    """Test cases for Poll API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.poll_data = {
            'title': 'API Test Poll',
            'description': 'A poll for testing API',
            'options': [
                {'text': 'Option 1', 'order': 1},
                {'text': 'Option 2', 'order': 2}
            ]
        }
    
    def test_create_poll_authenticated(self):
        """Test creating a poll while authenticated."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/polls/', self.poll_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Poll.objects.count(), 1)
        
        poll = Poll.objects.first()
        self.assertEqual(poll.title, 'API Test Poll')
        self.assertEqual(poll.creator, self.user)
        self.assertEqual(poll.options.count(), 2)
    
    def test_create_poll_unauthenticated(self):
        """Test creating a poll while unauthenticated."""
        response = self.client.post('/api/polls/', self.poll_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_polls(self):
        """Test listing polls."""
        # Create a poll
        poll = Poll.objects.create(
            title='Test Poll',
            creator=self.user
        )
        
        response = self.client.get('/api/polls/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_poll_detail(self):
        """Test getting poll details."""
        poll = Poll.objects.create(
            title='Test Poll',
            creator=self.user
        )
        PollOption.objects.create(poll=poll, text='Option 1')
        
        response = self.client.get(f'/api/polls/{poll.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Poll')
        self.assertEqual(len(response.data['options']), 1)


class VoteAPITest(APITestCase):
    """Test cases for Vote API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.poll = Poll.objects.create(
            title='Vote Test Poll',
            creator=self.user
        )
        self.option = PollOption.objects.create(
            poll=self.poll,
            text='Test Option'
        )
    
    def test_cast_vote_authenticated(self):
        """Test casting a vote while authenticated."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/polls/{self.poll.id}/vote/',
            {'option_text': 'Test Option'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vote.objects.count(), 1)
        
        vote = Vote.objects.first()
        self.assertEqual(vote.poll, self.poll)
        self.assertEqual(vote.option, self.option)
        self.assertEqual(vote.voter, self.user)
    
    def test_cast_vote_anonymous(self):
        """Test casting a vote anonymously."""
        response = self.client.post(
            f'/api/polls/{self.poll.id}/vote/',
            {'option_text': 'Test Option'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vote.objects.count(), 1)
        
        vote = Vote.objects.first()
        self.assertEqual(vote.poll, self.poll)
        self.assertEqual(vote.option, self.option)
        self.assertIsNone(vote.voter)
        self.assertIsNotNone(vote.voter_ip)
    
    def test_duplicate_vote_prevention(self):
        """Test prevention of duplicate votes."""
        self.client.force_authenticate(user=self.user)
        
        # First vote
        response1 = self.client.post(
            f'/api/polls/{self.poll.id}/vote/',
            {'option_text': 'Test Option'},
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second vote (should fail)
        response2 = self.client.post(
            f'/api/polls/{self.poll.id}/vote/',
            {'option_text': 'Test Option'},
            format='json'
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already voted', str(response2.data))
    
    def test_get_poll_results(self):
        """Test getting poll results."""
        # Create a vote
        Vote.objects.create(
            poll=self.poll,
            option=self.option,
            voter=self.user
        )
        
        response = self.client.get(f'/api/polls/{self.poll.id}/results/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['total_votes'], 1)
        self.assertEqual(len(data['options']), 1)
        self.assertEqual(data['options'][0]['vote_count'], 1)
        self.assertEqual(data['options'][0]['percentage'], 100.0)
