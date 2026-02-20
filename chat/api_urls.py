#  (ВРЕМЕННАЯ ВЕРСИЯ)
from django.urls import path
from . import views
from . import private_api

# Импортируем ТОЛЬКО то, что уже существует
from .views import (
    ChatHistoryAPIView,
    ChatSendMessageAPIView, 
    ChatUploadFileAPIView,
    ChatMarkReadAPIView,
    BaseChatAPIView  
)

urlpatterns = [
    path('boards/<int:board_id>/history/', 
         views.ChatHistoryAPIView.as_view(), 
         name='chat-api-history'),
    
    path('boards/<int:board_id>/send/', 
         views.ChatSendMessageAPIView.as_view(), 
         name='chat-api-send'),
    
    path('boards/<int:board_id>/upload/', 
         views.ChatUploadFileAPIView.as_view(), 
         name='chat-api-upload'),
    
    path('boards/<int:board_id>/mark-read/', 
         views.ChatMarkReadAPIView.as_view(), 
         name='chat-api-mark-read'),
    
    path('my-dialogs/', private_api.MyDialogsView.as_view(), name='my-dialogs'),
    path('dialog/<int:chat_id>/messages/', private_api.DialogMessagesView.as_view(), name='dialog-messages'),
    path('dialog/<int:chat_id>/send/', private_api.SendPrivateMessageView.as_view(), name='send-private'),
    path('search-users/', private_api.SearchUsersView.as_view(), name='search-users'),
    path('create-dialog/', private_api.CreatePrivateChatView.as_view(), name='create-dialog'),
]