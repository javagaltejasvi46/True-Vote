from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'polls'
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='polls/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='polls/logout.html'), name='logout'),
    path('logout/confirm/', views.logout_confirm, name='logout_confirm'),
    path('register/', views.register, name='register'),
    path('candidate/add/', views.add_candidate, name='add_candidate'),
    path('', views.IndexView.as_view(), name='index'),
    path('past-elections/', views.PastElectionsView.as_view(), name='past_elections'),
    path('create/', views.create_poll, name='create'),
    path('stats/', views.election_stats, name='stats'),
    path('<int:poll_id>/stats/', views.poll_stats, name='poll_stats'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:poll_id>/vote/', views.vote, name='vote'),
    path('<int:poll_id>/delete/', views.delete_poll, name='delete_poll'),
] 