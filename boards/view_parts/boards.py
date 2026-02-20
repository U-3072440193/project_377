from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import os
import json
from django.contrib import messages
from ..forms import BoardForm
from ..models import Board, BoardPermit, User, UserBoardOrder
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.db.models import Q
from django.db import models, transaction


# -------------------Для BoardListAPIView---------------
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Board
from ..serializers import BoardSerializer
from .utils import UNIVERSAL_FOR_AUTHENTICATION, UNIVERSAL_FOR_PERMISSION_CLASSES, get_react_js_filename, \
    get_react_css_filename
from rest_framework import status
from django.views.decorators.http import require_POST


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

    # Получаем имена файлов
    react_js = get_react_js_filename()  # например: main.23c0e5d0.js
    react_css = get_react_css_filename()  # например: main.23c0e5d0.css
    # Передать данные в React через контекст
    context = {
        'board_id': board.id,
        'board_title': board.title,
        # Можно передать пользовательские данные
        'user_data': {
            'user_id': request.user.id,
            'username': request.user.username,
            'react_js': react_js,
            'react_css': react_css,
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

            # Находим максимальную позицию у пользователя и ставим +1 (СВЕРХУ)
            max_position = Board.objects.filter(
                owner=request.user,
                is_archived=False
            ).aggregate(models.Max('position'))['position__max'] or 0

            # Устанавливаем позицию на 1 больше максимальной (новые сверху)
            board.position = max_position + 1
            board.save()

            # Автоматически добавляем владельца
            BoardPermit.objects.get_or_create(
                board=board,
                user=request.user,
                defaults={'role': 'owner'}
            )

            # Также создаем запись в UserBoardOrder
            UserBoardOrder.objects.create(
                user=request.user,
                board=board,
                position=1  # Новая доска всегда сверху
            )

            # Обновляем позиции остальных досок пользователя
            # Смещаем все существующие доски вниз на 1
            UserBoardOrder.objects.filter(
                user=request.user
            ).exclude(board=board).update(position=models.F('position') + 1)

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

    # Получаем доски с учетом порядка
    boards = get_user_boards_with_order(user)

    context = {
        'boards': boards,
        'archived_boards': Board.objects.filter(
            Q(owner=user) | Q(boardpermit__user=user),
            is_archived=True
        ).distinct(),
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


# ------------Архив------------
@login_required
def archive_board(request, board_id):
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


class BoardRenameAPIView(APIView):
    authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES

    def patch(self, request, pk):
        board = get_object_or_404(Board, pk=pk)

        # Проверка прав: только владелец может переименовать доску
        if board.owner != request.user:
            return Response(
                {"error": "Нет прав на редактирование доски"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Проверка, что доска не в архиве
        if board.is_archived:
            return Response(
                {"error": "Невозможно переименовать доску в архиве"},
                status=status.HTTP_400_BAD_REQUEST
            )

        title = request.data.get("title")
        if not title or not title.strip():
            return Response(
                {"error": "Название обязательно и не может быть пустым"},
                status=status.HTTP_400_BAD_REQUEST
            )

        title = title.strip()
        if len(title) > 200:  # Проверка максимальной длины
            return Response(
                {"error": "Название слишком длинное (максимум 200 символов)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем, изменилось ли название
        if board.title == title:
            return Response(
                {"message": "Название не изменилось"},
                status=status.HTTP_200_OK
            )

        board.title = title
        board.save()

        serializer = BoardSerializer(board)
        return Response(serializer.data, status=status.HTTP_200_OK)


@login_required
@require_POST
def move_board_up(request, board_id):
    """Переместить доску вверх в пользовательском порядке"""
    try:
        board = get_object_or_404(Board, id=board_id)
        user = request.user

        # Получаем текущий порядок пользователя
        user_orders = UserBoardOrder.objects.filter(
            user=user
        ).order_by('position')

        # Преобразуем в список ID досок
        board_ids = [order.board_id for order in user_orders]

        # Находим индекс текущей доски
        try:
            current_index = board_ids.index(board.id)
        except ValueError:
            # Доски нет в порядке пользователя - добавляем в конец
            UserBoardOrder.objects.create(
                user=user,
                board=board,
                position=len(board_ids) + 1
            )
            return JsonResponse({
                'success': True,
                'message': f'Доска "{board.title}" добавлена в список'
            })

        if current_index > 0:
            # Меняем местами с предыдущей доской
            board_ids[current_index], board_ids[current_index - 1] = \
                board_ids[current_index - 1], board_ids[current_index]

            # Обновляем позиции в БД
            update_board_positions(user, board_ids)

            return JsonResponse({
                'success': True,
                'message': f'Доска "{board.title}" перемещена выше'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Доска уже на первой позиции'
            })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def move_board_down(request, board_id):
    """Переместить доску вниз в пользовательском порядке"""
    try:
        board = get_object_or_404(Board, id=board_id)
        user = request.user

        # Получаем текущий порядок пользователя
        user_orders = UserBoardOrder.objects.filter(
            user=user
        ).order_by('position')

        # Преобразуем в список ID досок
        board_ids = [order.board_id for order in user_orders]

        # Находим индекс текущей доски
        try:
            current_index = board_ids.index(board.id)
        except ValueError:
            # Доски нет в порядке пользователя - добавляем в конец
            UserBoardOrder.objects.create(
                user=user,
                board=board,
                position=len(board_ids) + 1
            )
            return JsonResponse({
                'success': True,
                'message': f'Доска "{board.title}" добавлена в список'
            })

        if current_index < len(board_ids) - 1:
            # Меняем местами со следующей доской
            board_ids[current_index], board_ids[current_index + 1] = \
                board_ids[current_index + 1], board_ids[current_index]

            # Обновляем позиции в БД
            update_board_positions(user, board_ids)

            return JsonResponse({
                'success': True,
                'message': f'Доска "{board.title}" перемещена ниже'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Доска уже на последней позиции'
            })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def get_user_boards_with_order(user):
    """Получить доски пользователя с учетом его порядка"""
    # Все доступные доски
    owned_boards = Board.objects.filter(owner=user, is_archived=False)
    permitted_boards = Board.objects.filter(
        boardpermit__user=user,
        is_archived=False
    ).exclude(owner=user)

    all_boards = (owned_boards | permitted_boards).distinct()

    # Получаем пользовательский порядок
    user_orders = UserBoardOrder.objects.filter(
        user=user,
        board__in=all_boards
    ).select_related('board')

    # Создаем словарь позиций
    position_dict = {order.board_id: order.position for order in user_orders}

    # Инициализируем порядок для досок без записи
    for board in all_boards:
        if board.id not in position_dict:
            # Создаем запись с дефолтной позицией
            UserBoardOrder.objects.create(
                user=user,
                board=board,
                position=len(position_dict) + 1
            )
            position_dict[board.id] = len(position_dict) + 1

    # Сортируем доски по позиции
    sorted_boards = sorted(
        all_boards,
        key=lambda b: position_dict.get(b.id, 999999)
    )

    return sorted_boards



def update_board_positions(user, board_ids_in_order):
    """Обновить позиции досок для пользователя без удаления записей"""
    with transaction.atomic():
        for position, board_id in enumerate(board_ids_in_order, start=1):
            UserBoardOrder.objects.filter(
                user=user,
                board_id=board_id
            ).update(position=position)