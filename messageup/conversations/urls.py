from django.urls import path
from .views import conversations_view, create_conversation

urlpatterns = [
	path('', conversations_view, name='conversations'),
	path('conversations/create/', create_conversation, name='create_conversation'),
]
