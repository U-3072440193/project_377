from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from boards.models import Board, BoardPermit
from .models import ChatRoom, ChatMessage, ChatFile
from .serializers import ChatMessageSerializer, ChatFileSerializer, ChatHistorySerializer
from .views_parts.utils import (
    json_login_required, 
    UNIVERSAL_FOR_AUTHENTICATION, 
    UNIVERSAL_FOR_PERMISSION_CLASSES
)

class BaseChatAPIView(APIView):
    """Базовый класс с проверкой прав доступа к доске"""
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES
    
    def check_board_access(self, board_id, user):
        """Проверяет, есть ли у пользователя доступ к доске"""
        board = get_object_or_404(Board, id=board_id)
        
        # Владелец имеет доступ
        if board.owner == user:
            return board
        
        # Участник имеет доступ
        if board.members.filter(id=user.id).exists():
            return board
        
        # Или через BoardPermit
        if BoardPermit.objects.filter(board=board, user=user).exists():
            return board
        
        return None


class ChatHistoryAPIView(BaseChatAPIView):
    """Получение истории сообщений (REST)"""
    
    def get(self, request, board_id):
        # Проверка прав
        board = self.check_board_access(board_id, request.user)
        if not board:
            return Response(
                {"error": "Нет доступа к этой доске"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Получаем или создаем комнату
        room, created = ChatRoom.objects.get_or_create(board=board)
        
        # Параметры пагинации
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        
        # Получаем сообщения
        messages = ChatMessage.objects.filter(
            room=room
        ).select_related('author', 'attachment').order_by('-created')
        
        total = messages.count()
        messages_page = messages[offset:offset + limit]
        
        # Проверяем, есть ли еще сообщения
        has_more = (offset + limit) < total
        
        # Сериализуем
        serializer = ChatMessageSerializer(
            messages_page,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'messages': serializer.data,
            'has_more': has_more,
            'total': total,
            'room_id': room.id
        })


class ChatSendMessageAPIView(BaseChatAPIView):
    """Отправка сообщения через REST (альтернатива WebSocket)"""
    
    def post(self, request, board_id):
        # Проверка прав
        board = self.check_board_access(board_id, request.user)
        if not board:
            return Response(
                {"error": "Нет доступа к этой доске"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Получаем комнату
        room, created = ChatRoom.objects.get_or_create(board=board)
        
        # Сериализуем данные
        serializer = ChatMessageSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            # Сохраняем сообщение
            message = serializer.save(room=room)
            
            # Возвращаем созданное сообщение
            return Response(
                ChatMessageSerializer(message, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatUploadFileAPIView(BaseChatAPIView):
    """Загрузка файла в чат"""
    
    def post(self, request, board_id):
        # Проверка прав
        board = self.check_board_access(board_id, request.user)
        if not board:
            return Response(
                {"error": "Нет доступа к этой доске"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Получаем комнату
        room, created = ChatRoom.objects.get_or_create(board=board)
        
        # Проверяем файл
        if 'file' not in request.FILES:
            return Response(
                {"error": "Файл не предоставлен"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_obj = request.FILES['file']
        
        # Проверка размера (максимум 10MB)
        if file_obj.size > 10 * 1024 * 1024:
            return Response(
                {"error": "Файл слишком большой (максимум 10MB)"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создаем запись файла
        chat_file = ChatFile.objects.create(
            room=room,
            file=file_obj,
            uploaded_by=request.user
        )
        
        # Создаем сообщение о файле
        message = ChatMessage.objects.create(
            room=room,
            author=request.user,
            text=f"Файл: {file_obj.name}",
            attachment=chat_file
        )
        
        # Возвращаем данные
        return Response({
            'message': ChatMessageSerializer(message, context={'request': request}).data,
            'file': ChatFileSerializer(chat_file, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class ChatMarkReadAPIView(BaseChatAPIView):
    """Отметка сообщений как прочитанных"""
    
    def post(self, request, board_id):
        board = self.check_board_access(board_id, request.user)
        if not board:
            return Response(
                {"error": "Нет доступа к этой доске"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        room = get_object_or_404(ChatRoom, board=board)
        
        # Получаем ID сообщений для отметки
        message_ids = request.data.get('message_ids', [])
        
        if not message_ids:
            return Response({"success": True})
        
        # Здесь можно добавить логику отметки прочитанных
        # Например, через модель ChatMessageRead
        
        return Response({
            "success": True,
            "marked": len(message_ids)
        })
        
        
class GeneralChatHistoryAPIView(APIView):
    """Получение истории общего чата"""
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES
    
    def get(self, request):
        # ID служебной доски для общего чата
        GENERAL_BOARD_ID = 999999
        
        # Получаем или создаем комнату для этой доски
        room, _ = ChatRoom.objects.get_or_create(board_id=GENERAL_BOARD_ID)
        
        # Получаем сообщения
        messages = ChatMessage.objects.filter(
            room=room
        ).select_related('author').order_by('-created')[:50]
        
        # Сериализуем (можно использовать ваш существующий сериализатор)
        from chat.serializers import ChatMessageSerializer
        serializer = ChatMessageSerializer(messages, many=True, context={'request': request})
        
        return Response({
            'messages': serializer.data,
            'room_type': 'general'
        })

class GeneralChatSendAPIView(APIView):
    """Отправка сообщения в общий чат"""
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES
    
    def post(self, request):
        GENERAL_BOARD_ID = 999999
        
        room, _ = ChatRoom.objects.get_or_create(board_id=GENERAL_BOARD_ID)
        
        text = request.data.get('text', '').strip()
        if not text:
            return Response({'error': 'Текст не может быть пустым'}, status=400)
        
        message = ChatMessage.objects.create(
            room=room,
            author=request.user,
            text=text
        )
        
        from chat.serializers import ChatMessageSerializer
        serializer = ChatMessageSerializer(message, context={'request': request})
        
        return Response(serializer.data, status=201)



