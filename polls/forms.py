from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Voter, Candidate, Branch, Department

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class VoterProfileForm(forms.ModelForm):
    class Meta:
        model = Voter
        fields = ('age', 'sex', 'srn')
        widgets = {
            'sex': forms.Select(attrs={'class': 'form-control'}),
        }

class CandidateRegistrationForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ('name', 'age', 'sex', 'position')
        widgets = {
            'sex': forms.Select(attrs={'class': 'form-control'}),
        } 