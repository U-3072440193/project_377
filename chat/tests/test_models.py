import pytest
from django.contrib.auth import get_user_model
from chat.models import PrivateChat 
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.db import IntegrityError

@pytest.mark.django_db
class TestPrivateChatModel:
    
    def test_create_chat(self, user, user2):
        chat = PrivateChat.objects.create(user1=user, user2=user2)
        assert chat.user1 == user
        assert chat.user2 == user2
        assert chat.created is not None
        assert chat.updated is not None
    
    def test_unique_pair_constraint(self, user, user2):
        PrivateChat.objects.create(user1=user, user2=user2)
        
        with pytest.raises(IntegrityError):
            PrivateChat.objects.create(user1=user, user2=user2)
    
    def test_get_other_user(self, user, user2, user3):
        chat = PrivateChat.objects.create(user1=user, user2=user2)
        
        assert chat.get_other_user(user) == user2
        assert chat.get_other_user(user2) == user
        
        with pytest.raises(ValueError):
            chat.get_other_user(user3)
    
   
        
       