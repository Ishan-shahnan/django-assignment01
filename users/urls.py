from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile-edit'),
    path('profile/change-password/', views.change_password, name='change-password'),
]
