from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Branch(models.Model):
    branch_name = models.CharField(max_length=100)
    branch_code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.branch_name} ({self.branch_code})"

class Department(models.Model):
    department_name = models.CharField(max_length=100)
    dept_id = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.department_name} ({self.dept_id})"

class Voter(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    srn = models.CharField(max_length=20, unique=True, null=True, blank=True)
    sex = models.CharField(max_length=1, choices=GENDER_CHOICES)
    is_voter = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Candidate(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    sex = models.CharField(max_length=1, choices=GENDER_CHOICES)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    position = models.CharField(max_length=100, default='Candidate')
    is_candidate = models.BooleanField(default=True)

    def __str__(self):
        position_str = f" - {self.position}" if self.position else ""
        return f"{self.name}{position_str}"

class Poll(models.Model):
    DEPARTMENT_CHOICES = [
        ('Cultural', 'Cultural'),
        ('Technical', 'Technical'),
        ('President', 'President'),
        ('Vice President', 'Vice President'),
        ('Social', 'Social'),
    ]
    question = models.CharField(max_length=200, null=True, blank=True)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    is_active = models.BooleanField(default=True)
    department = models.CharField(max_length=32, choices=DEPARTMENT_CHOICES, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        date_str = self.pub_date.strftime("%d %b %Y")
        return f"{self.department or 'Election'} - {date_str}"

    def is_currently_active(self):
        # Check if election is active and if today's date matches the election date
        now = timezone.now().date()
        election_date = self.pub_date.date()
        
        # Check if the election is today
        date_match = (now == election_date)
        
        # Return true if the election is active and today's date matches the election date
        return self.is_active and date_match

    def is_past_election(self):
        # Check if the election date has passed
        now = timezone.now().date()
        election_date = self.pub_date.date()
        
        # Return true if today's date is after the election date
        return now > election_date

    def title(self):
        if self.question:
            return self.question
        date_str = self.pub_date.strftime("%d %b %Y")
        return f"{self.department or 'Election'} - {date_str}"

class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='choices')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True, blank=True)
    votes = models.IntegerField(default=0)

    def __str__(self):
        if self.candidate:
            return f"{self.candidate.name} - {self.poll}"
        return f"Choice for {self.poll}"

    def percentage(self):
        total_votes = sum(choice.votes for choice in self.poll.choices.all())
        if total_votes == 0:
            return 0
        return (self.votes / total_votes) * 100

class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter', 'poll')
