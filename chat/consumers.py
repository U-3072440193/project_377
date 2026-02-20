# https://zentyx.ru/posts/websocket-i-django-channels/

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import ChatRoom, ChatMessage,PrivateChat, PrivateMessage
from boards.models import Board, BoardPermit
from django.db.models import Q

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.board_id = self.scope['url_route']['kwargs']['board_id']
        self.room_group_name = f'chat_board_{self.board_id}'
        
        # Проверяем авторизацию
        if self.scope["user"].is_anonymous:
            print(f"❌ Анонимный пользователь пытался подключиться к чату доски {self.board_id}")
            await self.close()
            return
            
        # Проверяем доступ к доске
        has_access = await self.check_board_access()
        if not has_access:
            print(f"❌ Пользователь {self.scope['user'].username} не имеет доступа к доске {self.board_id}")
            await self.close()
            return
        
        print(f"✅ Пользователь {self.scope['user'].username} подключился к чату доски {self.board_id}")
        
        # Присоединяемся к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Отправляем историю
        await self.send_last_messages()

    async def disconnect(self, close_code):
        print(f"🔌 Пользователь {self.scope['user'].username} отключился от чата доски {self.board_id}")
        
        # Покидаем группу
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print(f"📩 Получено сообщение: {text_data}")
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'message':
                text = data.get('text', '')
                if text:
                    await self.save_and_broadcast_message(text)
        except json.JSONDecodeError:
            print(f"❌ Ошибка парсинга JSON: {text_data}")

    @database_sync_to_async
    def check_board_access(self):
        try:
            board = Board.objects.get(id=self.board_id)
            user = self.scope["user"]
            
            if board.owner == user:
                return True
                
            if board.members.filter(id=user.id).exists():
                return True
                
            if BoardPermit.objects.filter(board=board, user=user).exists():
                return True
                
            return False
        except Board.DoesNotExist:
            return False
        except Exception as e:
            print(f"❌ Ошибка проверки доступа: {e}")
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
        
        # ИСПРАВЛЕНО: убрал лишнюю вложенность, добавил нужные поля
        return {
            'type': 'chat_message',
            'id': message.id,
            'text': message.text,
            'author': user.username,
            'author_id': user.id,
            'author_username': user.username,  # добавил для совместимости
            'created': message.created.isoformat(),
            'created_display': message.created.strftime('%d.%m.%Y %H:%M'),  # добавил
        }

    async def chat_message(self, event):
        # ИСПРАВЛЕНО: отправляем event целиком, а не event['message']
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_last_messages(self):
        room = ChatRoom.objects.filter(board_id=self.board_id).first()
        if not room:
            return []
        
        messages = ChatMessage.objects.filter(
            room=room
        ).select_related('author').order_by('-created')[:50]
        
        result = []
        for msg in reversed(messages):
            result.append({
                'id': msg.id,
                'text': msg.text,
                'author': msg.author.username,
                'author_id': msg.author.id,
                'author_username': msg.author.username,
                'created': msg.created.isoformat(),
                'created_display': msg.created.strftime('%d.%m.%Y %H:%M'),
            })
        
        return result

    async def send_last_messages(self):
        messages = await self.get_last_messages()
        await self.send(text_data=json.dumps({
            'type': 'history',
            'messages': messages,
        }))
        
            
class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Группа для конкретного пользователя
        self.user_group_name = f'private_user_{self.user.id}'
        
        # Добавляем пользователя в его личную группу
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        print(f"Private: {self.user.username} connected")

    async def disconnect(self, close_code):
        # Удаляем пользователя из группы
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
        print(f"Private: {self.user.username} disconnected")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'private_message':
            await self.handle_private_message(data)

    async def handle_private_message(self, data):
        """Обработка личного сообщения"""
        recipient_id = data['recipient_id']
        text = data['text']
        
        # Сохраняем сообщение в БД
        message_data = await self.save_private_message(recipient_id, text)
        
        # Отправляем получателю
        await self.channel_layer.group_send(
            f'private_user_{recipient_id}',
            {
                'type': 'private_chat_message',
                'message': message_data
            }
        )
        
        # Отправляем подтверждение отправителю
        await self.send(text_data=json.dumps({
            'type': 'message_sent',
            'message': message_data
        }))

    @database_sync_to_async
    def save_private_message(self, recipient_id, text):
        from .models import PrivateChat, PrivateMessage
        from django.db.models import Q
        
        # Находим или создаем чат
        chat = PrivateChat.objects.filter(
            (Q(user1=self.user) & Q(user2=recipient_id)) |
            (Q(user1=recipient_id) & Q(user2=self.user))
        ).first()
        
        if not chat:
            chat = PrivateChat.objects.create(
                user1=self.user,
                user2_id=recipient_id
            )
        
        # Создаем сообщение
        message = PrivateMessage.objects.create(
            chat=chat,
            sender=self.user,
            text=text
        )
        
        return {
            'id': message.id,
            'text': message.text,
            'sender_id': self.user.id,
            'sender_name': self.user.username,
            'created': str(message.created),
            'created_display': message.created.strftime('%d.%m.%Y %H:%M'),
            'chat_id': chat.id,
            'is_read': message.is_read
        }

    async def private_chat_message(self, event):
        """Отправка сообщения клиенту"""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message']
        }))