from rest_framework import serializers
from .models import Board, Column, Task, BoardPermit, TaskFile, Comment
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


# Сериализатор комментов
class CommentSerializer(serializers.ModelSerializer):
    # Добавляем поле username пользователя
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user_username', 'text', 'created']


# Сериализатор задачи
class TaskSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)  # информация о создателе задачи
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'position', 'creator', 'created', 'updated', 'files', 'comments',
                  'priority', ]


# Сериализатор подгрузки файлов к задаче
class TaskFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    uploaded_by_username = serializers.ReadOnlyField(source='uploaded_by.username')

    class Meta:
        model = TaskFile
        fields = ["id", "file", "file_url", "file_name", "uploaded_at", "uploaded_by", "uploaded_by_username"]

    def get_file_url(self, obj):
        """Возвращает полный URL файла"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def get_file_name(self, obj):
        """Возвращает только имя файла без пути"""
        if obj.file:
            return obj.file.name.split('/')[-1]  # Берем последнюю часть пути
        return ""


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
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.ImageField(source='user.profile.avatar', read_only=True)

    class Meta:
        model = BoardPermit
        fields = ['user', 'role', 'username', 'avatar']
