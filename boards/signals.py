from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BoardPermit
from django.db import models


@receiver(post_save, sender=BoardPermit)
def create_user_board_order(sender, instance, created, **kwargs):
    """При добавлении пользователя в доску создаем запись порядка"""
    if created:
        from .models import UserBoardOrder

        # Проверяем, есть ли уже запись
        if not UserBoardOrder.objects.filter(
                user=instance.user,
                board=instance.board
        ).exists():
            # Находим максимальную позицию пользователя
            max_position = UserBoardOrder.objects.filter(
                user=instance.user
            ).aggregate(models.Max('position'))['position__max'] or 0

            # Создаем новую запись
            UserBoardOrder.objects.create(
                user=instance.user,
                board=instance.board,
                position=max_position + 1
            )
