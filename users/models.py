from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default/user.png')
    bio = models.TextField(blank=True)
    email = models.EmailField(max_length=100, blank=True)
    social_media_link = models.URLField(max_length=200, blank=True)
    social_media_link2 = models.URLField(max_length=200, blank=True)
    social_media_link3 = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return self.user


class Message(models.Model): #отправить пользователю сообщение
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    recipient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    file = models.FileField(upload_to='uploads/', blank=True, null=True)
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(max_length=200, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

    class Meta:
        ordering = ['is_read', '-created'] #по прочитанным+дата созд.
