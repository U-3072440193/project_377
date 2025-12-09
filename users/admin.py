from django.contrib import admin
from .models import Profile, Message


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'username', 'email', 'first_name', 'last_name', 'created', 'updated')
    list_filter = ('created', 'updated')
    search_fields = ('user__username', 'username', 'email', 'first_name', 'last_name')
    list_display_links = ('id', 'user', 'username',)


class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'recipient', 'subject', 'created')
    list_filter = ('created',)
    search_fields = ('subject', 'body', 'sender__username', 'recipient__username')


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Message, MessageAdmin)
