from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import os
import json
from django.contrib import messages
from ..forms import BoardForm
from ..models import Board, BoardPermit, User
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.db.models import Q

# -------------------Для BoardListAPIView---------------
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Board
from ..serializers import BoardSerializer
from .utils import UNIVERSAL_FOR_AUTHENTICATION, UNIVERSAL_FOR_PERMISSION_CLASSES


# ------------------Доска------------------
def board_detail(request, board_id):  # передача номера доски! удалить если передача будет не через переменную window
    board = get_object_or_404(Board, id=board_id)
    return render(request, 'index.html', {'board': board})


# def boards_page(request, pk):
#     board = get_object_or_404(Board, id=pk)
#     user_data = {
#         "user_id": request.user.id,
#         "username": request.user.username,
#     }
#     return render(request, "boards/board.html", {
#         "board": board,
#         "user_data": user_data,
#     })


# def boards_page(request, pk):
#     board = get_object_or_404(Board, id=pk)
#     user_data = {
#         "user_id": request.user.id,
#         "username": request.user.username,
#     }
#     index_path = os.path.join(settings.BASE_DIR, 'boards', 'frontend', 'build', 'index.html')
#     return FileResponse(open(index_path,
#                              'rb'))  # открывает файл в бинарном режиме для чтения, для отдачи файлов как HTTP-ответ с помощью FileResponse и Django автоматически ставит заголовки


def react_app_view(request, pk):  # ← добавить параметр pk
    # Можно получить доску для контекста
    board = get_object_or_404(Board, id=pk)

    # Передать данные в React через контекст
    context = {
        'board_id': board.id,
        'board_title': board.title,
        # Можно передать пользовательские данные
        'user_data': {
            'user_id': request.user.id,
            'username': request.user.username,
        }
    }

    return render(request, 'boards/react.html', context)


# -----------------------Действия с бордами-------------------------------


@login_required(login_url='login')
def new_board(request):
    if request.method == 'POST':
        form = BoardForm(request.POST)  # создаём форму из POST-данных
        if form.is_valid():
            board = form.save(commit=False)  # сохранение без копирования в бд
            board.owner = request.user
            board.save()
            # Автоматически добавляем владельца
            BoardPermit.objects.get_or_create(
                board=board,
                user=request.user,
                defaults={'role': 'owner'}
            )
            return redirect('boards-page', pk=board.id)
    else:
        form = BoardForm()

    context = {
        'form': form
    }
    return render(request, 'boards/new-board-form.html', context)


@login_required(login_url='login')
def delete_board(request, pk):
    board = get_object_or_404(Board, id=pk, owner=request.user)
    board.delete()
    return redirect('profile')


@login_required(login_url='login')
def my_boards(request):
    user = request.user

    owned_boards = Board.objects.filter(owner=user)
    permitted_boards = Board.objects.filter(
        boardpermit__user=user
    ).exclude(owner=user)

    boards = (owned_boards | permitted_boards).order_by('-created').distinct()
    

    context = {
        'boards': boards.distinct().filter(is_archived=False),
        'archived_boards': boards.distinct().filter(is_archived=True),
    }

    return render(request, 'boards/my-boards.html', context)


@login_required
def search_users_for_board(request):
    query = request.GET.get('search', '').strip()
    users = User.objects.filter(username__icontains=query)[:10]
    data = [{'id': u.id, 'username': u.username} for u in users]
    return JsonResponse(data, safe=False)


@login_required
def add_board_member(request, board_id):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    board = get_object_or_404(Board, id=board_id)

    #  ТОЛЬКО ВЛАДЕЛЕЦ
    if request.user != board.owner:
        return HttpResponseForbidden("You are not the board owner")

    user_id = request.POST.get('recipient_id')
    role = request.POST.get('role')

    if not user_id or not role:
        return HttpResponseBadRequest("Missing data")

    # допустимые роли
    # ALLOWED_ROLES = {'member', 'viewer'}

    # if role not in ALLOWED_ROLES:
    #     return HttpResponseBadRequest("Invalid role")

    user = get_object_or_404(User, id=user_id)

    #  нельзя добавить owner
    # if user == board.owner:
    #     return HttpResponseBadRequest("Owner already exists")

    BoardPermit.objects.get_or_create(
        board=board,
        user=user,
        defaults={'role': role}
    )

    return redirect('my-boards')


# Передача мемберов в реакт
def board_members_api(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    permits = BoardPermit.objects.filter(board=board)
    data = []

    for permit in permits:
        user = permit.user
        # безопасно получаем аватар из профиля
        avatar_url = getattr(getattr(user, 'profile', None), 'avatar', None)
        avatar_url = avatar_url.url if avatar_url else '/media/avatars/default/user.png'

        data.append({
            "id": user.id,
            "username": user.username,
            "role": permit.role,
            "avatar": avatar_url,
        })

    return JsonResponse(data, safe=False)


@login_required
@csrf_exempt
def remove_board_member(request, board_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'user_id required'}, status=400)

        board = get_object_or_404(Board, id=board_id)
        # проверяем, что текущий юзер – владелец или админ
        if board.owner != request.user:
            return JsonResponse({'error': 'Нет прав'}, status=403)

        permit = get_object_or_404(BoardPermit, board=board, user_id=user_id)
        permit.delete()
        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def exit_board(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    # Проверяем, что пользователь не владелец
    if request.user == board.owner:
        messages.error(request, "Владелец доски не может выйти из нее. Удалите доску или передайте права владения.")
        return redirect('my-boards')
    
    # Проверяем, есть ли у пользователя разрешение на эту доску
    try:
        user_permit = BoardPermit.objects.get(board=board, user=request.user)
        user_permit.delete()
        messages.success(request, f"Вы вышли из доски '{board.title}'")
    except BoardPermit.DoesNotExist:
        messages.error(request, "Вы не являетесь участником этой доски")
    
    return redirect('my-boards')


# Передача доски в реакт
class BoardListAPIView(APIView):  # отправка json в реакт
    # authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    # permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES

    def get(self, request, pk):
        board = get_object_or_404(Board, id=pk)
        serializer = BoardSerializer(board)
        return Response(serializer.data)


#------------Архив------------
@login_required
def archive_board(request,board_id):
    board = get_object_or_404(Board, id=board_id)
    
    # Проверяем, что пользователь - владелец
    if request.user != board.owner:
        messages.error(request, "Только владелец может архивировать доску")
        return redirect('my-boards')
    
    # Переключаем состояние архивации
    board.is_archived = not board.is_archived
    board.save()
    
    if board.is_archived:
        messages.success(request, f'Доска "{board.title}" перемещена в архив')
    else:
        messages.success(request, f'Доска "{board.title}" восстановлена из архива')
    
    return redirect('my-boards')

@login_required
def archived_boards(request):
    archived_boards = Board.objects.filter(
        Q(owner=request.user) | Q(members=request.user),
        is_archived=True
    ).distinct()
    
    return render(request, 'boards/archived-boards.html', {
        'archived_boards': archived_boards
    })

@login_required
def archive_board_view(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    
    # Проверяем доступ
    if not (board.owner == request.user or 
            board.boardpermit_set.filter(user=request.user).exists()):
        return HttpResponseForbidden("Нет доступа к этой доске")
    
    # Проверяем, что доска действительно в архиве
    if not board.is_archived:
        messages.info(request, "Эта доска не находится в архиве")
        return redirect('boards-page', pk=board.id)
    
    user_data = {
        "user_id": request.user.id,
        "username": request.user.username,
    }
    
    return render(request, "boards/board.html", {
        "board": board,
        "user_data": user_data,
        "is_archive_view": True,
    })