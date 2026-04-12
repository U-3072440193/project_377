import pytest
from django.urls import reverse, resolve
from chat.views import ChatHistoryAPIView, ChatSendMessageAPIView, ChatUploadFileAPIView, ChatMarkReadAPIView
from chat.private_api import MyDialogsView, DialogMessagesView, SendPrivateMessageView, SearchUsersView, CreatePrivateChatView

class TestChatAPIUrls:
    """Тесты для URL чата."""
    
    
    def test_chat_history_url(self):
        url = reverse('chat-api-history', kwargs={'board_id': 1})
        assert url == '/api/chat/boards/1/history/'
        
        resolver = resolve('/api/chat/boards/1/history/')
        assert resolver.func.view_class == ChatHistoryAPIView
    
    def test_chat_send_url(self):
        url = reverse('chat-api-send', kwargs={'board_id': 1})
        assert url == '/api/chat/boards/1/send/'
        
        resolver = resolve('/api/chat/boards/1/send/')
        assert resolver.func.view_class == ChatSendMessageAPIView
    
    def test_chat_upload_url(self):
        url = reverse('chat-api-upload', kwargs={'board_id': 1})
        assert url == '/api/chat/boards/1/upload/'
        
        resolver = resolve('/api/chat/boards/1/upload/')
        assert resolver.func.view_class == ChatUploadFileAPIView
    
    def test_chat_mark_read_url(self):
        url = reverse('chat-api-mark-read', kwargs={'board_id': 1})
        assert url == '/api/chat/boards/1/mark-read/'
        
        resolver = resolve('/api/chat/boards/1/mark-read/')
        assert resolver.func.view_class == ChatMarkReadAPIView
    
    
    def test_my_dialogs_url(self):
        url = reverse('my-dialogs')
        assert url == '/api/chat/my-dialogs/'
        
        resolver = resolve('/api/chat/my-dialogs/')
        assert resolver.func.view_class == MyDialogsView
    
    def test_dialog_messages_url(self):
        url = reverse('dialog-messages', kwargs={'chat_id': 1})
        assert url == '/api/chat/dialog/1/messages/'
        
        resolver = resolve('/api/chat/dialog/1/messages/')
        assert resolver.func.view_class == DialogMessagesView
    
    def test_send_private_url(self):
        url = reverse('send-private', kwargs={'chat_id': 1})
        assert url == '/api/chat/dialog/1/send/'
        
        resolver = resolve('/api/chat/dialog/1/send/')
        assert resolver.func.view_class == SendPrivateMessageView
    
    def test_search_users_url(self):
        url = reverse('search-users')
        assert url == '/api/chat/search-users/'
        
        resolver = resolve('/api/chat/search-users/')
        assert resolver.func.view_class == SearchUsersView
    
    def test_create_dialog_url(self):
        url = reverse('create-dialog')
        assert url == '/api/chat/create-dialog/'
        
        resolver = resolve('/api/chat/create-dialog/')
        assert resolver.func.view_class == CreatePrivateChatView