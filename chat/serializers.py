from rest_framework import serializers
from .models import Board, ChatRoom,ChatMessage,ChatFile
from django.contrib.auth.models import User


# Для информации об авторе (можно импортировать из boards)
class ChatUserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar']
    
    def get_avatar(self, obj):
        if hasattr(obj, 'profile') and obj.profile.avatar:
            return obj.profile.avatar.url
        return '/media/avatars/default/user.png'


# Сериализатор для вложений
class ChatFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    uploaded_by = ChatUserSerializer(read_only=True)
    
    class Meta:
        model = ChatFile
        fields = ['id', 'file', 'file_url', 'file_name', 'uploaded_at', 'uploaded_by']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_url(obj.file.url)
            return obj.file.url
        return None
    
    def get_file_name(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]
        return ""


# Основной сериализатор сообщений
class ChatMessageSerializer(serializers.ModelSerializer):
    author = ChatUserSerializer(read_only=True)
    attachment = ChatFileSerializer(read_only=True)

    created_display = serializers.SerializerMethodField()
    is_own = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            'id',
            'author',
            'text',
            'attachment',
            'created',
            'created_display',
            'updated',
            'is_edited',
            'is_own',
        ]
        read_only_fields = [
            'id',
            'author',
            'created',
            'updated',
            'is_edited',
            'attachment',
        ]

    def get_created_display(self, obj):
        from django.utils.timesince import timesince
        import datetime

        now = datetime.datetime.now(datetime.timezone.utc)

        if (now - obj.created).days == 0:
            return obj.created.strftime('%H:%M')
        elif (now - obj.created).days == 1:
            return f"Вчера {obj.created.strftime('%H:%M')}"
        elif (now - obj.created).days < 7:
            return f"{obj.created.strftime('%A')} {obj.created.strftime('%H:%M')}"
        else:
            return obj.created.strftime('%d.%m.%Y %H:%M')

    def get_is_own(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author_id == request.user.id
        return False

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Сообщение не может быть пустым"
            )
        if len(value) > 2000:
            raise serializers.ValidationError(
                "Сообщение слишком длинное (максимум 2000 символов)"
            )
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Пользователь не авторизован")

        validated_data['author'] = request.user
        return super().create(validated_data)



# Сериализатор комнаты (для списка комнат)
class ChatRoomSerializer(serializers.ModelSerializer):
    board_title = serializers.CharField(source='board.title', read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'board', 'board_title', 'created', 'last_message', 'unread_count']
    
    def get_last_message(self, obj):
        """Последнее сообщение в комнате"""
        last_msg = obj.messages.order_by('-created').first()
        if last_msg:
            return {
                'text': last_msg.text[:50] + '...' if len(last_msg.text) > 50 else last_msg.text,
                'author': last_msg.author.username,
                'created': last_msg.created
            }
        return None
    
    def get_unread_count(self, obj):
        """Количество непрочитанных сообщений"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Здесь можно реализовать логику непрочитанных
            # Например, через модель ChatMessageRead
            return 0  # Заглушка
        return 0


# Для массовой отправки сообщений (история)
class ChatHistorySerializer(serializers.Serializer):
    # Не модель, а кастомный сериализатор
    messages = ChatMessageSerializer(many=True)
    has_more = serializers.BooleanField()
    total = serializers.IntegerField()
    
    def to_representation(self, instance):
        return {
            'messages': ChatMessageSerializer(instance['messages'], many=True).data,
            'has_more': instance['has_more'],
            'total': instance['total']
        }