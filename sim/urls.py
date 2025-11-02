from django.urls import path
from . import views

urlpatterns = [
    path('lobby/', views.lobby, name='lobby'),
    path('', views.chat, name='chat'),
    path('create-message/', views.create_message, name='create-message')
]
