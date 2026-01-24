#  (ВРЕМЕННАЯ ВЕРСИЯ)
from django.urls import path
from . import views

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
    
    # Остальные пути:
    # path('rooms/<int:room_id>/', 
    #      views.ChatRoomDetailAPIView.as_view(), 
    #      name='chat-api-room-detail'),
    # 
    # path('boards/<int:board_id>/search/', 
    #      views.ChatSearchAPIView.as_view(), 
    #      name='chat-api-search'),
]