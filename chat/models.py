from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from boards.models import Board


class ChatRoom(models.Model):
    board = models.OneToOneField(
        Board,
        on_delete=models.CASCADE,
        related_name='chat_room', 
        db_index=True
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"Чат доски: {self.board.title}"
    
    def get_absolute_url(self):
        # Для удобства в админке/API
        return f"/chat/{self.id}/"


def chat_file_path(instance, filename):
    """
    Структура: chat_files/user_id/board_id/filename
    """
   
    return f"chat_files/{instance.uploaded_by.id}/{instance.room.board.id}/{filename}"


class ChatMessage(models.Model):
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        db_index=True
    )
    text = models.TextField(
        max_length=2000,  
        blank=True,  
        validators=[MaxLengthValidator(2000)]
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    
    # Связь с файлом (ОДИН файл на сообщение)
    attachment = models.ForeignKey(
        'ChatFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='message_attachment'
    )

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['room', 'created']),  # Для быстрой загрузки истории
        ]

    def __str__(self):
        if self.attachment:
            return f"{self.author.username}: [файл] {self.text[:20]}"
        return f"{self.author.username}: {self.text[:50]}"
    
    def save(self, *args, **kwargs):
        # Помечаем сообщение как отредактированное при изменении
        if self.pk:
            self.is_edited = True
        super().save(*args, **kwargs)


class ChatFile(models.Model):
    """Отдельная модель для файлов в чате"""
    room = models.ForeignKey(  
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="files"
    )
    file = models.FileField(upload_to=chat_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True
    )
    # Дополнительные поля для удобства
    original_filename = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(default=0)  # в байтах
    mime_type = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.original_filename or self.file.name} ({self.uploaded_by.username})"
    
    def save(self, *args, **kwargs):
        # Сохраняем оригинальное имя файла при первом сохранении
        if not self.pk and self.file:
            self.original_filename = self.file.name
            self.file_size = self.file.size
            # Можно определить MIME-тип (нужна дополнительная библиотека)
        super().save(*args, **kwargs)
        
        
class PrivateChat(models.Model):
    """Личный чат между двумя пользователями"""
    user1 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='private_chats_as_user1'
    )
    user2 = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='private_chats_as_user2'
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user1', 'user2']  # чтобы не создать дубликат
    
    def __str__(self):
        return f"Чат между {self.user1.username} и {self.user2.username}"
    
    def get_other_user(self, user):
        """Возвращает собеседника"""
        return self.user2 if user == self.user1 else self.user1

class PrivateMessage(models.Model):
    """Сообщение в личном чате"""
    chat = models.ForeignKey(
        PrivateChat, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_private_messages'
    )
    text = models.TextField(max_length=2000)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created']