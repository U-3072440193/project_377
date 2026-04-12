import pytest
from django.contrib.auth import get_user_model
from chat.models import ChatRoom, ChatMessage, ChatFile, PrivateChat, PrivateMessage

User = get_user_model()

@pytest.fixture
def user():
    """Создает тестового пользователя."""
    return User.objects.create_user(username='testuser', password='12345')

@pytest.fixture
def user2():
    """Создает тестового пользователя."""
    return User.objects.create_user(username='testuser2', password='123456789')

@pytest.fixture
def user3():   
    """Создает третьего тестового пользователя."""
    return User.objects.create_user(username='testuser3', password='123456789')
