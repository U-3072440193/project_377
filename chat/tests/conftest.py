import pytest
from django.contrib.auth import get_user_model
from chat.models import Board, ChatRoom, ChatMessage, ChatFile, PrivateChat, PrivateMessage

User = get_user_model()

@pytest.fixture
def user():
    """Создает тестового пользователя."""
    return User.objects.create_user(username='testuser', password='12345')

@pytest.fixture
def board(user):
    """Создает тестовую доску."""
    return Board.objects.create(title='Тестовая доска', owner=user)