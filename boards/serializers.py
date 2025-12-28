from rest_framework import serializers
from .models import Board, Column, Task, BoardPermit
from django.contrib.auth.models import User


# Сериализатор пользователя (для owner)
class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'avatar']

    def get_avatar(self, obj):
        # obj — это экземпляр User
        # здесь возвращаем путь к аватару или None
        if hasattr(obj, 'profile') and obj.profile.avatar:
            return obj.profile.avatar.url  # аватар из модели Profile
        return None


# Сериализатор задачи
class TaskSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)  # информация о создателе задачи

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'position', 'creator', 'created', 'updated']


# Сериализатор колонки
class ColumnSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)  # вложенные задачи

    class Meta:
        model = Column
        fields = ['id', 'title', 'position', 'tasks']


# Сериализатор доски
class BoardSerializer(serializers.ModelSerializer):
    columns = ColumnSerializer(many=True, read_only=True)  # вложенные колонки
    owner = UserSerializer(read_only=True)  # владелец доски

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'created', 'updated', 'columns']


# Сериализатор допусков
class PermitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardPermit
        fields = ['user', 'role']
