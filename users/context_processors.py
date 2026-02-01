from .models import Message

def unread_messages_count(request):
    if request.user.is_authenticated:
        unread_count = Message.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return {'unread': unread_count}
    return {'unread': 0}