# https://zentyx.ru/posts/websocket-i-django-channels/

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import ChatRoom, ChatMessage
from boards.models import Board, BoardPermit

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.board_id = self.scope['url_route']['kwargs']['board_id']
        self.room_group_name = f'chat_board_{self.board_id}'
        
        # Проверяем авторизацию
        if self.scope["user"].is_anonymous:
            await self.close()
            return
            
        # Проверяем доступ к доске
        if not await self.check_board_access():
            await self.close()
            return
        
        # Присоединяемся к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Отправляем историю
        await self.send_last_messages()

    async def disconnect(self, close_code):
        # Покидаем группу
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            text = data.get('text', '')
            await self.save_and_broadcast_message(text)

    @database_sync_to_async
    def check_board_access(self):
        try:
            board = Board.objects.get(id=self.board_id)
            user = self.scope["user"]
            
            if board.owner == user:
                return True
                
            # Проверяем через members
            if board.members.filter(id=user.id).exists():
                return True
                
            # Или через BoardPermit
            if BoardPermit.objects.filter(board=board, user=user).exists():
                return True
                
            return False
        except:
            return False

    @database_sync_to_async
    def save_and_broadcast_message(self, text):
        user = self.scope["user"]
        
        # Получаем или создаем комнату
        room, created = ChatRoom.objects.get_or_create(board_id=self.board_id)
        
        # Создаем сообщение
        message = ChatMessage.objects.create(
            room=room,
            author=user,
            text=text
        )
        
        # Возвращаем данные для рассылки
        return {
            'type': 'chat_message',
            'message': {
                'id': message.id,
                'text': message.text,
                'author': user.username,
                'author_id': user.id,
                'created': message.created.isoformat(),
            }
        }

    async def chat_message(self, event):
        # Отправляем сообщение всем в группе
        await self.send(text_data=json.dumps(event['message']))

    @database_sync_to_async
    def get_last_messages(self):
        room = ChatRoom.objects.filter(board_id=self.board_id).first()
        if not room:
            return []
        
        messages = ChatMessage.objects.filter(
            room=room
        ).select_related('author').order_by('-created')[:20]
        
        return [{
            'id': msg.id,
            'text': msg.text,
            'author': msg.author.username,
            'author_id': msg.author.id,
            'created': msg.created.isoformat(),
        } for msg in reversed(messages)]

    async def send_last_messages(self):
        messages = await self.get_last_messages()
        await self.send(text_data=json.dumps({
            'type': 'history',
            'messages': messages,
        }))