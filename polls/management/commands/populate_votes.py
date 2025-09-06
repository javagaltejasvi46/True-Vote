import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from polls.models import Poll, Choice, Vote, Voter, Candidate

class Command(BaseCommand):
    help = 'Populates the database with fake votes for testing'

    def add_arguments(self, parser):
        parser.add_argument('--votes', type=int, default=100, help='Number of votes to generate')
        parser.add_argument('--clear', action='store_true', help='Clear existing votes before adding new ones')

    def handle(self, *args, **options):
        num_votes = options['votes']
        clear_votes = options['clear']
        
        # Get active polls (elections)
        active_polls = Poll.objects.filter(is_active=True)
        
        if not active_polls.exists():
            self.stdout.write(self.style.ERROR('No active elections found. Please create an active election first.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Found {active_polls.count()} active elections'))
        
        # Clear existing votes if requested
        if clear_votes:
            Vote.objects.all().delete()
            # Reset vote counts for all choices
            Choice.objects.all().update(votes=0)
            self.stdout.write(self.style.SUCCESS('Cleared existing votes'))
        
        # Get or create voters
        voters = self.ensure_voters_exist(num_votes)
        
        # Generate votes
        created_votes = 0
        skipped_votes = 0
        
        for poll in active_polls:
            choices = Choice.objects.filter(poll=poll)
            
            if not choices.exists():
                self.stdout.write(self.style.WARNING(f'No choices found for election: {poll.title()}. Skipping.'))
                continue
                
            self.stdout.write(self.style.SUCCESS(f'Generating votes for election: {poll.title()}'))
            
            # Distribute votes somewhat realistically
            # Create a weighted distribution for choices
            weights = self.generate_realistic_weights(choices.count())
            
            # Assign each voter to a choice based on weighted distribution
            for voter in voters:
                # Skip if voter already voted in this poll
                if Vote.objects.filter(voter=voter, poll=poll).exists():
                    skipped_votes += 1
                    continue
                
                # Select a choice based on weights
                selected_choice = random.choices(
                    population=list(choices),
                    weights=weights,
                    k=1
                )[0]
                
                # Create vote
                Vote.objects.create(
                    voter=voter,
                    poll=poll,
                    choice=selected_choice
                )
                
                # Update vote count
                selected_choice.votes += 1
                selected_choice.save()
                
                created_votes += 1
                
                # Add some randomness to stop after a certain number of votes
                if created_votes >= num_votes:
                    break
            
            if created_votes >= num_votes:
                break
        
        self.stdout.write(self.style.SUCCESS(f'Created {created_votes} votes'))
        if skipped_votes > 0:
            self.stdout.write(self.style.WARNING(f'Skipped {skipped_votes} voters who had already voted'))
    
    def ensure_voters_exist(self, num_needed):
        """Make sure we have enough voters in the database"""
        existing_voters = Voter.objects.all()
        num_existing = existing_voters.count()
        
        if num_existing >= num_needed:
            self.stdout.write(self.style.SUCCESS(f'Using {num_needed} of {num_existing} existing voters'))
            return list(existing_voters[:num_needed])
        
        # We need to create additional voters
        self.stdout.write(self.style.SUCCESS(f'Creating {num_needed - num_existing} additional voters'))
        
        voters = list(existing_voters)
        
        # Create fake users and voters
        for i in range(num_existing, num_needed):
            # Create user
            username = f'testvoter{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': f'Voter {i+1}',
                    'email': f'voter{i+1}@example.com',
                    'password': 'pbkdf2_sha256$600000$testpassword123'  # Hashed password
                }
            )
            
            # Create voter
            voter, created = Voter.objects.get_or_create(
                user=user,
                defaults={
                    'name': f'Voter {i+1}',
                    'age': random.randint(18, 70),
                    'srn': f'SRN-{i+1:05d}',
                    'sex': random.choice(['M', 'F', 'O']),
                    'is_voter': True
                }
            )
            
            voters.append(voter)
        
        return voters
    
    def generate_realistic_weights(self, num_choices):
        """Generate realistic weights for vote distribution"""
        if num_choices <= 1:
            return [1]
            
        # Create a base weight with some randomness
        base_weight = 100 / num_choices
        
        # Add some preference for the first few choices (simulating popular candidates)
        weights = []
        remaining_weight = 100
        
        # First choice gets more votes (simulate a leading candidate)
        first_weight = base_weight * random.uniform(1.5, 2.5)
        weights.append(first_weight)
        remaining_weight -= first_weight
        
        # Last choice gets fewer votes (simulate a trailing candidate)
        if num_choices > 1:
            last_weight = base_weight * random.uniform(0.5, 0.8)
            remaining_weight -= last_weight
            
            # Middle choices share the remaining weight with some randomness
            middle_weights = []
            for i in range(num_choices - 2):
                if i == num_choices - 3:  # Last middle choice
                    weight = remaining_weight
                else:
                    weight = remaining_weight * random.uniform(0.3, 0.7) / (num_choices - 2)
                    remaining_weight -= weight
                middle_weights.append(weight)
                
            weights.extend(middle_weights)
            weights.append(last_weight)
        
        return weights 