from django.contrib import admin
from .models import ChatRoom, ChatMessage, ChatFile

admin.site.register(ChatRoom)
admin.site.register(ChatFile)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('author', 'room', 'text_short', 'created', 'is_edited')
    list_filter = ('room', 'created', 'is_edited')
    search_fields = ('text', 'author__username')
    
    def text_short(self, obj):
        return obj.text[:50] if obj.text else '[файл]'