from django.db import models
from django.contrib.auth.models import User
from boards.models import Board


class ChatRoom(models.Model):
    board = models.OneToOneField(
        Board,
        on_delete=models.CASCADE,
        related_name='chat'
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat for board: {self.board.title}"


class ChatMessage(models.Model):
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"{self.author.username}: {self.text[:30]}"