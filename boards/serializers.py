from rest_framework import serializers
from .models import *


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = '__all__'


class ColumnSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Column
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']  # avatar теперь виртуальное поле

    def get_avatar(self, obj):
        # проверяем, есть ли профиль
        if hasattr(obj, 'profile') and obj.profile.avatar:
            request = self.context.get('request')
            avatar_url = obj.profile.avatar.url
            # если нужно абсолютный URL для фронта:
            if request is not None:
                return request.build_absolute_uri(avatar_url)
            return avatar_url
        return None


class BoardSerializer(serializers.ModelSerializer):
    columns = ColumnSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Board
        fields = '__all__'
