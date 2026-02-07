from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.db import models, transaction
import json
from .models import Poll, Choice, Vote, Voter, Candidate, Branch, Department
from .forms import UserRegistrationForm, VoterProfileForm, CandidateRegistrationForm

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = VoterProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Create user account
            user = user_form.save()
            
            # Create voter profile
            voter = profile_form.save(commit=False)
            voter.user = user
            voter.name = f"{user.first_name} {user.last_name}".strip() or user.username
            voter.save()
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful! You can now vote in elections.')
            return redirect('polls:index')
    else:
        user_form = UserRegistrationForm()
        profile_form = VoterProfileForm()
    
    return render(request, 'polls/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def register_voter(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = VoterProfileForm(request.POST)
        if form.is_valid():
            voter = form.save(commit=False)
            voter.user = user
            voter.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('polls:index')
    else:
        form = VoterProfileForm()
    
    return render(request, 'polls/register_voter.html', {'form': form})

def register_candidate(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = CandidateRegistrationForm(request.POST)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.user = user
            candidate.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('polls:index')
    else:
        form = CandidateRegistrationForm()
    
    return render(request, 'polls/register_candidate.html', {'form': form})

class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_poll_list'

    def get_queryset(self):
        # Auto-archive: Mark past elections as inactive efficiently
        today = timezone.now().date()
        
        # Use bulk update to avoid N+1 queries
        Poll.objects.filter(
            pub_date__date__lt=today,
            is_active=True
        ).update(is_active=False)
            
        # Get active polls excluding past elections
        return Poll.objects.filter(
            is_active=True,
            pub_date__date__gte=today
        ).order_by('pub_date')

class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Poll
    template_name = 'polls/detail.html'

    def get_queryset(self):
        # Return all polls without filtering by pub_date
        return Poll.objects.all()
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Provide timezone-aware datetime with timestamp for template
        context['now'] = timezone.now()
        return context

class ResultsView(LoginRequiredMixin, generic.DetailView):
    model = Poll
    template_name = 'polls/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

@login_required
def vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    
    # Make sure the poll is active and today is the election date
    if not poll.is_currently_active():
        messages.error(request, 'This election is not active for today. Voting is only allowed on the scheduled election date.')
        return redirect('polls:index')
    
    # Check if the user has already voted
    user = request.user
    if Vote.objects.filter(poll=poll, voter__user=user).exists():
        messages.error(request, 'You have already voted in this election.')
        return redirect('polls:results', pk=poll.id)
    
    # Check if user is a voter
    if not hasattr(user, 'voter'):
        messages.error(request, 'You need to complete your voter registration profile before voting.')
        return redirect('polls:register_voter', user_id=user.id)
    
    voter = user.voter
    
    if request.method == 'POST':
        try:
            # Make sure a choice was selected
            if 'choice' not in request.POST:
                return render(request, 'polls/detail.html', {
                    'poll': poll,
                    'error_message': "You didn't select a choice.",
                })
            
            # Ensure the choice exists
            choice_id = request.POST['choice']
            selected_choice = poll.choices.get(pk=choice_id)
            
            # Use database transaction to ensure atomicity
            with transaction.atomic():
                # Re-check vote status inside transaction to be safe
                if Vote.objects.filter(poll=poll, voter=voter).exists():
                    messages.error(request, 'You have already voted in this election.')
                    return redirect('polls:results', pk=poll.id)

                # Increment the choice's vote count atomically using F-expression
                # This prevents race conditions under high concurrency
                selected_choice.votes = models.F('votes') + 1
                selected_choice.save()
                
                # Record the vote
                Vote.objects.create(
                    voter=voter,
                    poll=poll,
                    choice=selected_choice
                )
            
            messages.success(request, 'Your vote has been recorded!')
            return HttpResponseRedirect(reverse('polls:results', args=(poll.id,)))
            
        except Choice.DoesNotExist:
            messages.error(request, 'The selected choice does not exist.')
            return render(request, 'polls/detail.html', {
                'poll': poll,
                'error_message': "The selected choice does not exist.",
            })
        except Exception as e:
            messages.error(request, f'Error recording vote: {str(e)}')
            return render(request, 'polls/detail.html', {
                'poll': poll,
                'error_message': f"Error recording vote: {str(e)}",
            })
    
    return render(request, 'polls/detail.html', {'poll': poll})

@login_required
def create_poll(request):
    if not request.user.is_staff:
        messages.error(request, 'Only admins can create elections.')
        return redirect('polls:index')
        
    if request.method == 'POST':
        department = request.POST.get('department')
        question = request.POST.get('question')
        start_date = request.POST.get('start_date')
        selected_candidates = request.POST.getlist('candidates')
        
        if not selected_candidates:
            messages.error(request, 'Please select at least one candidate for the election.')
            candidates = Candidate.objects.all()
            return render(request, 'polls/create.html', {'candidates': candidates})
        
        # Parse date if provided
        pub_date = timezone.now()
        if start_date:
            naive_datetime = timezone.datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
            pub_date = timezone.make_aware(naive_datetime)
        
        # Create the poll with the active flag set to true
        poll = Poll.objects.create(
            department=department,
            question=question,
            pub_date=pub_date,
            is_active=True
        )
        
        # Add only selected candidates as choices
        for candidate_id in selected_candidates:
            try:
                candidate = Candidate.objects.get(id=candidate_id)
                Choice.objects.create(
                    poll=poll,
                    candidate=candidate
                )
            except Candidate.DoesNotExist:
                continue
        
        messages.success(request, f'Election created successfully with {len(selected_candidates)} candidates!')
        return HttpResponseRedirect(reverse('polls:detail', args=(poll.id,)))
    
    # Get all candidates to display in the form
    candidates = Candidate.objects.all()
    return render(request, 'polls/create.html', {'candidates': candidates})

def logout_confirm(request):
    return render(request, 'polls/logout_confirm.html')

@login_required
def add_candidate(request):
    if not request.user.is_staff:
        messages.error(request, 'Only admins can add candidates.')
        return redirect('polls:index')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        age_str = request.POST.get('age')
        sex = request.POST.get('sex')
        position = request.POST.get('position')
        
        if name and age_str and sex and position:
            try:
                age = int(age_str)
            except ValueError:
                messages.error(request, 'Age must be a valid number.')
                return redirect('polls:create')

            # Create a new user for the candidate
            username = name.lower().replace(' ', '_')
            
            # Robust username generation to prevent collision race conditions
            import random
            import string
            from django.db import IntegrityError

            while True:
                # Create random password
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                try:
                    with transaction.atomic():
                        user = User.objects.create_user(
                            username=username,
                            password=password,
                            email=f"{username}@example.com"
                        )
                        # Create the candidate profile
                        Candidate.objects.create(
                            user=user,
                            name=name,
                            age=age,
                            sex=sex,
                            position=position,
                            is_candidate=True
                        )
                    break # Success, exit loop
                except IntegrityError:
                    # Username taken, append random suffix and retry
                    suffix = ''.join(random.choices(string.digits, k=4))
                    username = f"{name.lower().replace(' ', '_')}_{suffix}"
            
            messages.success(request, f'Candidate {name} added successfully! Username: {username}, Password: {password}')
            return redirect('polls:create')
        else:
            messages.error(request, 'Please fill all the required fields.')
            
    return redirect('polls:create')

@login_required
def delete_poll(request, poll_id):
    # Check if user is admin
    if not request.user.is_staff:
        messages.error(request, 'Only admins can delete elections.')
        return redirect('polls:index')
    
    poll = get_object_or_404(Poll, pk=poll_id)
    
    if request.method == 'POST':
        # Delete the poll and redirect to index
        poll_name = poll.title()
        poll.delete()
        messages.success(request, f'Election "{poll_name}" has been deleted successfully.')
        return redirect('polls:index')
    
    # Show confirmation page
    return render(request, 'polls/delete_confirm.html', {'poll': poll})

@login_required
def poll_stats(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    choices = Choice.objects.filter(poll=poll)
    
    # Skip polls with no choices
    if not choices.exists():
        messages.warning(request, 'This election has no candidates to display stats for.')
        return redirect('polls:detail', pk=poll_id)
    
    total_poll_votes = sum(choice.votes for choice in choices)
    
    # Prepare chart data
    labels = []
    votes = []
    percentages = []
    
    for choice in choices:
        candidate_name = choice.candidate.name if choice.candidate else "Unknown"
        labels.append(candidate_name)
        votes.append(choice.votes)
        percentage = 0
        if total_poll_votes > 0:
            percentage = round((choice.votes / total_poll_votes) * 100, 1)
        percentages.append(percentage)
    
    # Add poll with chart data
    chart_data = {
        'labels': labels,
        'votes': votes,
        'percentages': percentages
    }
    
    # Convert chart data to JSON for template
    chart_data_json = json.dumps(chart_data)
    
    # Get voter information
    total_voters = Voter.objects.count()
    participation_rate = 0
    if total_voters > 0:
        participation_rate = round((total_poll_votes / total_voters) * 100, 1)
    
    # Initialize context with common data
    context = {
        'poll': poll,
        'total_votes': total_poll_votes,
        'chart_data': chart_data_json,
        'participation_rate': participation_rate,
    }
    
    # Only include vote timeline for admin users
    if request.user.is_staff:
        vote_timeline = Vote.objects.filter(poll=poll).order_by('-voted_at')[:50]
        context['vote_timeline'] = vote_timeline
    
    return render(request, 'polls/poll_stats.html', context)

@login_required
def election_stats(request):
    # Get all departments from the DEPARTMENT_CHOICES in Poll model
    departments = [dept[0] for dept in Poll.DEPARTMENT_CHOICES]
    
    # Get total elections, votes, and candidates
    total_elections = Poll.objects.count()
    total_votes = Vote.objects.count()
    total_candidates = Candidate.objects.count()
    
    # Organize polls by department
    dept_polls = {}
    for dept in departments:
        polls = Poll.objects.filter(department=dept)
        
        # Skip if no polls for this department
        if not polls.exists():
            continue
            
        dept_polls[dept] = []
        
        # Process each poll for chart data
        for poll in polls:
            choices = Choice.objects.filter(poll=poll)
            
            # Skip polls with no choices
            if not choices.exists():
                continue
                
            total_poll_votes = sum(choice.votes for choice in choices)
            
            # Prepare chart data
            labels = []
            votes = []
            percentages = []
            
            for choice in choices:
                candidate_name = choice.candidate.name if choice.candidate else "Unknown"
                labels.append(candidate_name)
                votes.append(choice.votes)
                percentage = 0
                if total_poll_votes > 0:
                    percentage = round((choice.votes / total_poll_votes) * 100, 1)
                percentages.append(percentage)
            
            # Add poll with chart data to department
            poll_data = {
                'id': poll.id,
                'title': poll.title(),
                'pub_date': poll.pub_date,
                'chart_data': {
                    'labels': labels,
                    'votes': votes,
                    'percentages': percentages
                }
            }
            
            dept_polls[dept].append(poll_data)
    
    # Calculate REAL participation data
    participation_data = {
        'departments': departments,
        'participation': []
    }
    
    total_registered_voters = Voter.objects.count()
    
    for dept in departments:
        if dept in dept_polls and total_registered_voters > 0:
            # Aggregate total votes for all polls in this department
            # Note: This is an approximation since voters aren't strictly linked to departments
            # A more accurate metric would be (Unique Voters in Dept Polls / Total Voters)
            dept_vote_count = 0
            for poll_data in dept_polls[dept]:
                # Sum the votes from the chart data we already prepared
                dept_vote_count += sum(poll_data['chart_data']['votes'])
            
            # Use max participation to avoid >100% if voters vote in multiple polls
            # ideally we'd query distinct voters, but this is a solid improvement over random
            participation_rate = round((dept_vote_count / (total_registered_voters * len(dept_polls[dept]) or 1)) * 100, 1)
            participation_data['participation'].append(min(participation_rate, 100))
        else:
            participation_data['participation'].append(0)
    
    # Handle empty departments
    for dept in list(dept_polls.keys()):
        if not dept_polls[dept]:
            del dept_polls[dept]
    
    # Convert chart data to JSON for template
    for dept, polls in dept_polls.items():
        for poll in polls:
            poll['chart_data'] = json.dumps(poll['chart_data'])
    
    participation_data = json.dumps(participation_data)
    
    context = {
        'departments': departments,
        'total_elections': total_elections,
        'total_votes': total_votes,
        'total_candidates': total_candidates,
        'dept_polls': dept_polls,
        'participation_data': participation_data
    }
    
    return render(request, 'polls/stats.html', context)

class PastElectionsView(LoginRequiredMixin, generic.ListView):
    template_name = 'polls/past_elections.html'
    context_object_name = 'past_poll_list'
    
    def get_queryset(self):
        # Get all past elections (either by date or because they were archived)
        today = timezone.now().date()
        return Poll.objects.filter(
            # Either past date OR manually archived (is_active=False)
            Q(pub_date__date__lt=today) | Q(is_active=False)
        ).order_by('-pub_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_past_elections'] = self.get_queryset().count()
        return context
