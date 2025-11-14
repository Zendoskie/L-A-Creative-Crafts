from django.urls import path
from . import views

app_name = 'chatbot_app'

urlpatterns = [
    path('', views.intro_view, name='intro'),
    path('chat/', views.chat_view, name='chat'),
    path('api/chat/', views.chat_api, name='chat_api'),
]

