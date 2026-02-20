from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Max
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import PrivateChat, PrivateMessage

class MyDialogsView(APIView):
    """Список диалогов текущего пользователя"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Находим все чаты где участвует пользователь
        chats = PrivateChat.objects.filter(
            Q(user1=request.user) | Q(user2=request.user)
        )
        
        result = []
        for chat in chats:
            other_user = chat.get_other_user(request.user)
            last_message = chat.messages.last()
            
            result.append({
                'id': chat.id,
                'other_user': {
                    'id': other_user.id,
                    'username': other_user.username,
                },
                'last_message': last_message.text[:50] if last_message else '',
                'last_message_time': last_message.created if last_message else None,
                'unread_count': chat.messages.filter(~Q(sender=request.user), is_read=False).count()
            })
        
        return Response(result)

class DialogMessagesView(APIView):
    """Сообщения конкретного диалога"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, chat_id):
        chat = get_object_or_404(PrivateChat, id=chat_id)
        
        # Проверяем доступ
        if request.user not in [chat.user1, chat.user2]:
            return Response({'error': 'Нет доступа'}, status=403)
        
        # Помечаем как прочитанные
        chat.messages.filter(~Q(sender=request.user), is_read=False).update(is_read=True)
        
        messages = chat.messages.all().order_by('-created')[:50]
        
        result = [{
            'id': msg.id,
            'text': msg.text,
            'sender_id': msg.sender.id,
            'sender_name': msg.sender.username,
            'created': msg.created,
            'is_read': msg.is_read
        } for msg in messages]
        
        return Response(result[::-1])  # от старых к новым

class SendPrivateMessageView(APIView):
    """Отправка сообщения"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, chat_id):
        chat = get_object_or_404(PrivateChat, id=chat_id)
        
        if request.user not in [chat.user1, chat.user2]:
            return Response({'error': 'Нет доступа'}, status=403)
        
        text = request.data.get('text', '').strip()
        if not text:
            return Response({'error': 'Пустое сообщение'}, status=400)
        
        message = PrivateMessage.objects.create(
            chat=chat,
            sender=request.user,
            text=text
        )
        
        return Response({
            'id': message.id,
            'text': message.text,
            'sender_id': message.sender.id,
            'sender_name': message.sender.username,
            'created': message.created,
            'is_read': message.is_read
        }, status=201)

class SearchUsersView(APIView):
    """Поиск пользователей для нового чата"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.GET.get('q', '')
        if len(query) < 2:
            return Response([])
        
        users = User.objects.filter(
            username__icontains=query
        ).exclude(id=request.user.id)[:10]
        
        result = [{
            'id': user.id,
            'username': user.username,
        } for user in users]
        
        return Response(result)

class CreatePrivateChatView(APIView):
    """Создать новый диалог"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        other_user_id = request.data.get('user_id')
        other_user = get_object_or_404(User, id=other_user_id)
        
        # Проверяем, может уже есть чат
        chat = PrivateChat.objects.filter(
            (Q(user1=request.user) & Q(user2=other_user)) |
            (Q(user1=other_user) & Q(user2=request.user))
        ).first()
        
        if not chat:
            chat = PrivateChat.objects.create(
                user1=request.user,
                user2=other_user
            )
        
        return Response({'chat_id': chat.id})