from django.db.models.signals import post_save, post_delete
from .models import Profile
from django.contrib.auth.models import User


# Создание профиля при создании User
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            username=instance.username,
            email=instance.email,
            first_name=instance.first_name
        )


# Обновление User при изменении профиля
def update_profile(sender, instance, created, **kwargs):
    profile = instance
    user = profile.user
    if not created:
        user.first_name = profile.first_name
        user.username = profile.username
        user.email = profile.email
        user.save()


# Удаление User при удалении профиля
def delete_user(sender, instance, **kwargs):
    user = instance.user
    user.delete()


post_save.connect(create_profile, sender=User)
post_save.connect(update_profile, sender=Profile)
post_delete.connect(delete_user, sender=Profile)
