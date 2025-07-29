from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # Main Pages
    path('', views.HomeView.as_view(), name='home'),
    path('events/', views.EventsView.as_view(), name='events'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # Event URLs
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='detail'),
    path('event/add/', views.EventCreateView.as_view(), name='add'),
    path('event/<int:pk>/edit/', views.EventUpdateView.as_view(), name='edit'),
    path('event/<int:pk>/delete/', views.EventDeleteView.as_view(), name='delete'),

    # Participant URLs
    path('participant/add/', views.ParticipantCreateView.as_view(), name='participant_add'),
    path('participant/<int:pk>/edit/', views.ParticipantUpdateView.as_view(), name='participant_edit'),
    path('participant/<int:pk>/delete/', views.ParticipantDeleteView.as_view(), name='participant_delete'),

    # Category URLs
    path('category/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('category/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('category/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
] 