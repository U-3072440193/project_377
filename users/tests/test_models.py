import pytest
from django.contrib.auth import get_user_model
from users.models import Profile, Message
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.utils import timezone  
from datetime import timedelta 
from django.db import IntegrityError

User = get_user_model()

@pytest.mark.django_db
class TestProfileModel:
    """Тесты для модели Profile."""
    
    def test_profile_auto_created_on_user_creation(self, user):
        """Проверка, что профиль автоматически создаётся при создании пользователя."""
        profile = Profile.objects.get(user=user)
        
        assert profile.user == user
        assert profile.username == user.username
        assert profile.email == user.email
        assert profile.first_name == user.first_name
        assert profile.created is not None
        assert profile.updated is not None
        assert str(profile) == user.username
    
    def test_update_profile_updates_user(self, user):
        """Проверка, что при обновлении профиля обновляется пользователь."""
        profile = Profile.objects.get(user=user)
        
        # Обновляем профиль
        profile.first_name = "НовоеИмя"
        profile.username = "newusername"
        profile.email = "new@email.com"
        profile.save()
        
        # Проверяем, что пользователь обновился
        user.refresh_from_db()
        assert user.first_name == "НовоеИмя"
        assert user.username == "newusername"
        assert user.email == "new@email.com"
    
    def test_profile_one_to_one_constraint(self, user):
        """Проверка, что нельзя создать второй профиль."""
        with pytest.raises(IntegrityError):
            Profile.objects.create(user=user, username=user.username)
    
    def test_delete_profile_deletes_user(self, user):
        """Проверка, что при удалении профиля удаляется пользователь."""
        profile = Profile.objects.get(user=user)
        user_id = user.id
        
        profile.delete()
        
        with pytest.raises(User.DoesNotExist):
            User.objects.get(id=user_id)
            
@pytest.mark.django_db
class TestMessageModel:
    """Тесты для модели Message."""
    
    def test_create_message(self, user, user2):
        """Проверка создания сообщения."""
        message = Message.objects.create(
            sender=user,
            recipient=user2,
            name=user.username,
            email=user.email or "sender@test.com",
            subject="Тестовая тема",
            body="Тестовое сообщение",
            is_read=False
        )
        
        assert message.sender == user
        assert message.recipient == user2
        assert message.subject == "Тестовая тема"
        assert message.body == "Тестовое сообщение"
        assert message.is_read is False
        assert message.created is not None
        assert str(message) == "Тестовая тема"
    
    def test_message_ordering(self, user, user2):
        """Проверка сортировки сообщений."""
        msg1 = Message.objects.create(
            sender=user,
            recipient=user2,
            subject="Непрочитанное",
            body="Body",
            is_read=False,
            created=timezone.now()
        )
        msg2 = Message.objects.create(
            sender=user,
            recipient=user2,
            subject="Прочитанное старое",
            body="Body",
            is_read=True,
            created=timezone.now() - timedelta(days=1)
        )
        
        messages = Message.objects.all()
        # Сначала непрочитанные, потом по дате
        assert messages[0] == msg1  # непрочитанное первым
        assert messages[1] == msg2  # потом прочитанное