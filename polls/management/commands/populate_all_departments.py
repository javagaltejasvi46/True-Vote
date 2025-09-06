import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from polls.models import Poll, Choice, Vote, Voter, Candidate

class Command(BaseCommand):
    help = 'Populates the database with elections for each department and adds fake votes'

    def add_arguments(self, parser):
        parser.add_argument('--votes-per-dept', type=int, default=30, 
                           help='Number of votes to generate per department')
        parser.add_argument('--candidates-per-dept', type=int, default=4, 
                           help='Number of candidates to generate per department')
        parser.add_argument('--clear', action='store_true', 
                           help='Clear existing department polls before adding new ones')

    def handle(self, *args, **options):
        votes_per_dept = options['votes_per_dept']
        candidates_per_dept = options['candidates_per_dept']
        clear_existing = options['clear']
        
        # Get the department choices from the Poll model
        departments = [dept[0] for dept in Poll.DEPARTMENT_CHOICES]
        
        # Clear existing department polls if requested
        if clear_existing:
            self.stdout.write(self.style.WARNING('Clearing existing department polls...'))
            for dept in departments:
                polls = Poll.objects.filter(department=dept)
                for poll in polls:
                    # Delete related choices and votes
                    Choice.objects.filter(poll=poll).delete()
                    Vote.objects.filter(poll=poll).delete()
                # Delete the polls
                polls.delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing department polls'))
        
        # Make sure we have enough candidates and voters
        candidates = self.ensure_candidates_exist(len(departments) * candidates_per_dept)
        voters = self.ensure_voters_exist(len(departments) * votes_per_dept)
        
        department_polls = []
        
        # Create a poll for each department
        for dept in departments:
            # Skip if a poll for this department already exists
            if Poll.objects.filter(department=dept).exists() and not clear_existing:
                self.stdout.write(self.style.WARNING(f'Poll for {dept} department already exists. Skipping...'))
                continue
                
            # Create a new poll for this department
            poll = Poll.objects.create(
                question=f'{dept} Department Election',
                department=dept,
                pub_date=timezone.now(),
                is_active=True
            )
            
            self.stdout.write(self.style.SUCCESS(f'Created election for {dept} department'))
            department_polls.append(poll)
            
            # Assign candidates to this poll
            dept_candidates = random.sample(candidates, min(candidates_per_dept, len(candidates)))
            
            for candidate in dept_candidates:
                Choice.objects.create(
                    poll=poll,
                    candidate=candidate
                )
            
            self.stdout.write(self.style.SUCCESS(f'Added {len(dept_candidates)} candidates to {dept} department'))
            
            # Generate votes for this poll
            choices = Choice.objects.filter(poll=poll)
            weights = self.generate_realistic_weights(choices.count())
            
            created_votes = 0
            for i in range(votes_per_dept):
                if i >= len(voters):
                    break
                    
                voter = voters[i]
                
                # Skip if voter already voted in this poll
                if Vote.objects.filter(voter=voter, poll=poll).exists():
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
            
            self.stdout.write(self.style.SUCCESS(f'Added {created_votes} votes to {dept} department'))
        
        self.stdout.write(self.style.SUCCESS(f'Created elections for {len(department_polls)} departments'))
    
    def ensure_candidates_exist(self, num_needed):
        """Make sure we have enough candidates in the database"""
        existing_candidates = Candidate.objects.all()
        num_existing = existing_candidates.count()
        
        if num_existing >= num_needed:
            self.stdout.write(self.style.SUCCESS(f'Using {num_needed} of {num_existing} existing candidates'))
            return list(existing_candidates[:num_needed])
        
        # We need to create additional candidates
        self.stdout.write(self.style.SUCCESS(f'Creating {num_needed - num_existing} additional candidates'))
        
        candidates = list(existing_candidates)
        
        positions = ['President', 'Vice President', 'Secretary', 'Treasurer', 'Member']
        
        # Create fake users and candidates
        for i in range(num_existing, num_needed):
            # Create user
            username = f'testcandidate{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': f'Candidate {i+1}',
                    'email': f'candidate{i+1}@example.com',
                    'password': 'pbkdf2_sha256$600000$testpassword123'  # Hashed password
                }
            )
            
            # Create candidate
            candidate, created = Candidate.objects.get_or_create(
                user=user,
                defaults={
                    'name': f'Candidate {i+1}',
                    'age': random.randint(21, 60),
                    'sex': random.choice(['M', 'F', 'O']),
                    'position': random.choice(positions),
                    'is_candidate': True
                }
            )
            
            candidates.append(candidate)
        
        return candidates
    
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