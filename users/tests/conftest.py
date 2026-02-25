import pytest
from django.contrib.auth import get_user_model
from users.models import Profile,Message

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='12345')

@pytest.fixture
def user2():
    return User.objects.create_user(username='testuser2', password='123456789')

#@pytest.fixture
#def profile(user):
#    return Profile.objects.create(
#        user=user,
#        username=user.username,
#        first_name="Tester",
#        last_name="Testerson",
#        bio="Test bio",
#        email="test@email.ru",
#        email_notifications=False
#    )

@pytest.fixture
def message(user, user2):
    return Message.objects.create(
        sender=user,
        recipient=user2,
        name=user.username,
        email="user2@test.ru",
        subject="Test subject",
        body="Test body",
        is_read=False
    )