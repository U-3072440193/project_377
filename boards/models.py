from django.db import models
from django.contrib.auth.models import User


class Board(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    hidden = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # проверяем, новая ли это доска
        super().save(*args, **kwargs)

        # Автоматически добавляем владельца как участника
        if is_new:
            BoardPermit.objects.get_or_create(
                board=self,
                user=self.owner,
                defaults={'role': 'owner'}
            )


class BoardPermit(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['board', 'user'], name='unique_board_user')
        ]  # добавление юзера 1 раз, если у него нет доступа

    ROLE_CHOICES = [
        ('owner', 'owner'),
        ('member', 'member'),
        ('viewer', 'viewer'),
    ]

    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')

    def __str__(self):
        return f"{self.user.username} — {self.role} на {self.board.title}"


class Column(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='columns')
    title = models.CharField(max_length=255)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position']

    def save(self, *args, **kwargs):
        if self.position == 0 or self.position is None:
            last_column = Column.objects.filter(board=self.board).order_by('-position').first()
            self.position = last_column.position + 1 if last_column else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.position})"


class Task(models.Model):
    PRIORITY = [
        ('low', 'low'),
        ('average', 'average'),
        ('high', 'high'),
        ('maximal', 'maximal'),
    ]
    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    position = models.PositiveIntegerField(default=0)
    priority = models.CharField(max_length=10, choices=PRIORITY, default='low')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.position == 0 or self.position is None:
            last_task = Task.objects.filter(column=self.column).order_by('-position').first()
            self.position = last_task.position + 1 if last_task else 1
        super().save(*args, **kwargs)


def task_file_path(instance, filename):
    """
    Структура: task_files/user_id/board_id/task_id/filename
    """
    # Используем uploaded_by.id вместо task.creator.id
    # потому что файл может загружать не создатель задачи
    return f"task_files/{instance.uploaded_by.id}/{instance.task.column.board.id}/{instance.task.id}/{filename}"


class TaskFile(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="files"
    )
    file = models.FileField(upload_to=task_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.file.name}"


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.PROTECT, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"{self.user.username} — {self.task.title}"
