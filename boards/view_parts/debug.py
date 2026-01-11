from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from ..models import Task, BoardPermit


# ------------------отладка--------------------
@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def debug_task_auth(request, task_id):
    """Проверка прав для конкретной задачи"""
    task = get_object_or_404(Task, id=task_id)
    board = task.column.board

    # Проверяем разные условия
    is_owner = board.owner == request.user
    has_permit = BoardPermit.objects.filter(board=board, user=request.user).exists()
    user_is_creator = task.creator == request.user

    return Response({
        'task_id': task.id,
        'task_title': task.title,
        'board_id': board.id,
        'board_title': board.title,
        'current_user': {
            'id': request.user.id,
            'username': request.user.username,
        },
        'board_owner': {
            'id': board.owner.id,
            'username': board.owner.username,
        },
        'task_creator': {
            'id': task.creator.id if task.creator else None,
            'username': task.creator.username if task.creator else None,
        },
        'auth_checks': {
            'is_authenticated': request.user.is_authenticated,
            'is_board_owner': is_owner,
            'has_board_permit': has_permit,
            'is_task_creator': user_is_creator,
            'can_access': is_owner or has_permit,
        }
    })


@api_view(['GET'])
def test_auth(request):
    """Простейший тест аутентификации"""
    return Response({
        'is_authenticated': request.user.is_authenticated,
        'user': request.user.username if request.user.is_authenticated else 'anonymous',
        'session_key': request.session.session_key if hasattr(request, 'session') else 'no session',
    })


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def debug_task_check(request, task_id):
    """Проверка конкретной задачи и прав"""
    task = get_object_or_404(Task, id=task_id)
    board = task.column.board

    # Полная проверка
    is_owner = board.owner == request.user
    has_permit = BoardPermit.objects.filter(board=board, user=request.user).exists()

    print("=" * 50)
    print(f"DEBUG: User: {request.user.username} (id: {request.user.id})")
    print(f"DEBUG: Task: {task.title} (id: {task.id})")
    print(f"DEBUG: Board: {board.title} (id: {board.id})")
    print(f"DEBUG: Board owner: {board.owner.username} (id: {board.owner.id})")
    print(f"DEBUG: Is owner: {is_owner}")
    print(f"DEBUG: Has permit: {has_permit}")
    print(f"DEBUG: Can access: {is_owner or has_permit}")
    print("=" * 50)

    return Response({
        'task': {
            'id': task.id,
            'title': task.title,
            'creator': task.creator.username if task.creator else None,
        },
        'board': {
            'id': board.id,
            'title': board.title,
            'owner': board.owner.username,
        },
        'user': {
            'id': request.user.id,
            'username': request.user.username,
        },
        'checks': {
            'is_owner': is_owner,
            'has_permit': has_permit,
            'can_access': is_owner or has_permit,
        }
    })
