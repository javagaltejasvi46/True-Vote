from django.contrib import admin
from .models import Branch, Department, Voter, Candidate, Poll, Choice, Vote

admin.site.register(Branch)
admin.site.register(Department)
admin.site.register(Voter)
admin.site.register(Candidate)
admin.site.register(Poll)
admin.site.register(Choice)
admin.site.register(Vote)
