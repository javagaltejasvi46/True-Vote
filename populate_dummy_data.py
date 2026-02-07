import os
import django
import random
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voting_system.settings')
django.setup()

from polls.models import Poll, Choice, Candidate, Branch, Department

def populate():
    print("Populating fake data...")

    # Create Superuser if not exists
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        print("Superuser 'admin' created with password 'admin'")

    branches = Branch.objects.all()
    departments = Department.objects.all()

    if not branches.exists() or not departments.exists():
        print("Please run initial_data.py first to seed branches and departments.")
        return

    # Create Polls
    poll_questions = [
        "Presidential Election 2026",
        "Cultural Secretary Election",
        "Sports Captain Election",
        "Technical Head Election"
    ]

    for question in poll_questions:
        # Check if poll already exists to prevent duplicates
        if not Poll.objects.filter(question=question).exists():
            dept = random.choice(departments)
            poll = Poll.objects.create(
                question=question,
                pub_date=timezone.now(),
                is_active=True,
                department=dept.department_name, # Assuming choice field stores name
                branch=None # General poll
            )
            print(f"Created Poll: {question}")

            # Create Candidates for this poll
            for i in range(3):
                username = f"candidate_{poll.id}_{i}"
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(username=username, password='password123')
                    candidate = Candidate.objects.create(
                        user=user,
                        name=f"Candidate {i+1} for {question}",
                        age=20 + i,
                        sex='M' if i % 2 == 0 else 'F',
                        branch=random.choice(branches),
                        department=dept,
                        position="Representative",
                        is_candidate=True
                    )
                    
                    Choice.objects.create(
                        poll=poll,
                        candidate=candidate,
                        votes=random.randint(0, 50) # Random initial votes
                    )
                    print(f"  Added Candidate/Choice: {candidate.name}")
        else:
            print(f"Poll '{question}' already exists.")

    print("Fake data population complete!")

if __name__ == '__main__':
    populate()
