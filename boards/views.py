from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework.permissions import AllowAny #разрешен доступ всем, только для разработки!! удалить после финишной отладке
from .forms import BoardForm, ColumnForm
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, FileResponse
from django.contrib.sessions.models import Session
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
import os
from django.conf import settings
from django.db import IntegrityError
from django.db.models import F, Q
from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from rest_framework.parsers import MultiPartParser, FormParser


def board_detail(request, board_id):  # передача номера доски! удалить если передача будет не через переменную window
    board = get_object_or_404(Board, id=board_id)
    return render(request, 'index.html', {'board': board})


def json_login_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Вы не авторизованы'}, status=401)
        return view_func(request, *args, **kwargs)

    return wrapped_view


class BoardListAPIView(APIView):  # отправка json в реакт

    def get(self, request, pk):
        board = get_object_or_404(Board, id=pk)
        serializer = BoardSerializer(board)
        return Response(serializer.data)


class UserAPIView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"isAuthenticated": False}, status=401)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    # def get(self, request, pk):
    #     # Только владелец или участники могут видеть доску
    #     board = get_object_or_404(Board, id=pk)
    #     if board.owner != request.user and request.user not in board.members.all():
    #         return Response({"detail": "Нет доступа"}, status=403)
    #     serializer = BoardSerializer(board)
    #     return Response(serializer.data)


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
def boards_page(request, pk):
    board = get_object_or_404(Board, id=pk)
    user_data = {
        "user_id": request.user.id,
        "username": request.user.username,
    }
    index_path = os.path.join(settings.BASE_DIR, 'boards', 'frontend', 'build', 'index.html')
    return FileResponse(open(index_path,
                             'rb'))  # открывает файл в бинарном режиме для чтения, для отдачи файлов как HTTP-ответ с помощью FileResponse и Django автоматически ставит заголовки


# ----------------------------Колонки---------------------------------
class ColumnCreateAPIView(APIView):
    def post(self, request, board_id):
        board = get_object_or_404(Board, id=board_id)
        title = request.data.get('title')
        if not title:
            return Response({'error': 'Title is required'}, status=status.HTTP_400_BAD_REQUEST)

        column = Column.objects.create(board=board, title=title, position=board.columns.count() + 1)
        serializer = ColumnSerializer(column)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ColumnDeleteAPIView(APIView):
    authentication_classes = [
        BasicAuthentication]  # !!!!токен отсутствует или request не правильный, Django возвращает 403 Forbidden. Защита нарушена!!!Требуется проработка корректного приема CSRF от реакта
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        column = get_object_or_404(Column, id=pk)
        column.delete()
        return Response(status=204)


# -----------------------Действия с бордами-------------------------------


@login_required(login_url='login')
def new_board(request):
    if request.method == 'POST':
        form = BoardForm(request.POST)  # создаём форму из POST-данных
        if form.is_valid():
            board = form.save(commit=False)  # сохранение без копирования в бд
            board.owner = request.user
            board.save()
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


# -----------------таски----------------------
class TaskCreateAPIView(APIView):
    authentication_classes = [
        BasicAuthentication]  # !!!!токен отсутствует или request не правильный, Django возвращает 403 Forbidden. Защита нарушена!!!Требуется проработка корректного приема CSRF от реакта
    permission_classes = [IsAuthenticated]

    def post(self, request, column_id):
        column = get_object_or_404(Column, id=column_id)
        title = request.data.get("title")
        if not title:
            return Response({"error": "Title is required"}, status=400)

        task = Task.objects.create(
            column=column,
            title=title,
            position=column.tasks.count() + 1,
            creator=request.user
        )
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=201)


class TaskDeleteAPIView(APIView):
    authentication_classes = [
        BasicAuthentication]  # !!!!токен отсутствует или request не правильный, Django возвращает 403 Forbidden. Защита нарушена!!!Требуется проработка корректного приема CSRF от реакта
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        if task.creator != request.user:
            return Response(status=403)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskMoveView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        """
        Перемещает задачу в другую колонку и/или меняет её позицию.
        Пример JSON тела запроса:
        {
            "column": 2,          # ID новой колонки (обязательно)
            "position": 0         # Новая позиция в колонке (0-based, опционально)
        }
        """
        try:
            task = Task.objects.select_for_update().get(pk=pk)
            board = task.column.board

            # Проверяем права пользователя!Временно! Права будут разделегированы между мемберами
            if board.owner != request.user and not BoardPermit.objects.filter(board=board, user=request.user).exists():
                return Response(
                    {"error": "У вас нет прав для перемещения этой задачи"},
                    status=status.HTTP_403_FORBIDDEN
                )

            column_id = request.data.get('column')
            position = request.data.get('position')

            if column_id is None:
                return Response(
                    {"error": "Не указана колонка"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            new_column = get_object_or_404(Column, pk=column_id)

            # Проверяем, что новая колонка в той же доске
            if new_column.board != board:
                return Response(
                    {"error": "Колонка должна принадлежать той же доске"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Сохраняем старую колонку
            old_column = task.column

            with transaction.atomic():
                # Если задача перемещается в другую колонку
                if old_column.id != new_column.id:
                    #  Удаляем задачу из старой колонки и корректируем позиции
                    Task.objects.filter(
                        column=old_column,
                        position__gt=task.position
                    ).update(position=F('position') - 1)

                    #  Добавляем задачу в новую колонку
                    task.column = new_column
                    if position is not None:
                        # Освобождаем место для новой задачи в новой колонке
                        Task.objects.filter(
                            column=new_column,
                            position__gte=position
                        ).update(position=F('position') + 1)
                        task.position = position
                    else:
                        # Если позиция не указана, ставим в конец
                        last_position = Task.objects.filter(
                            column=new_column
                        ).aggregate(models.Max('position'))['position__max'] or 0
                        task.position = last_position + 1
                else:
                    # Перемещение внутри той же колонки
                    if position is not None and position != task.position:
                        old_position = task.position
                        if position > old_position:
                            # Перемещаем вниз
                            Task.objects.filter(
                                column=old_column,
                                position__gt=old_position,
                                position__lte=position
                            ).update(position=F('position') - 1)
                        else:
                            # Перемещаем вверх
                            Task.objects.filter(
                                column=old_column,
                                position__lt=old_position,
                                position__gte=position
                            ).update(position=F('position') + 1)
                        task.position = position

                task.save()
                serializer = TaskSerializer(task)
                return Response(serializer.data)

        except Task.DoesNotExist:
            return Response(
                {"error": "Задача не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TaskUpdateAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk)

        board = task.column.board

        # Проверка прав
        if board.owner != request.user and not BoardPermit.objects.filter(
                board=board,
                user=request.user
        ).exists():
            return Response(
                {"error": "Нет прав на редактирование задачи"},
                status=status.HTTP_403_FORBIDDEN
            )

        description = request.data.get("description")

        if description is None:
            return Response(
                {"error": "description is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.description = description
        task.save()

        serializer = TaskSerializer(task)
        return Response(serializer.data, status=200)


class TaskFileUploadAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        board = task.column.board

        # проверка прав
        if board.owner != request.user and not BoardPermit.objects.filter(
                board=board,
                user=request.user
        ).exists():
            return Response({"error": "Нет прав"}, status=403)

        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return Response({"error": "Файл не передан"}, status=400)

        task_file = TaskFile.objects.create(
            task=task,
            file=uploaded_file,
            uploaded_by=request.user
        )

        serializer = TaskFileSerializer(task_file)
        return Response(serializer.data, status=201)


class TaskFilesListAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Получение списка файлов для конкретной задачи"""
        task = get_object_or_404(Task, id=pk)
        board = task.column.board

        # Проверка прав на просмотр файлов
        if board.owner != request.user and not BoardPermit.objects.filter(
                board=board,
                user=request.user
        ).exists():
            return Response(
                {"error": "Нет прав на просмотр файлов"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Получаем файлы задачи с контекстом запроса для построения полных URL
        files = task.files.all()
        serializer = TaskFileSerializer(files, many=True, context={'request': request})
        return Response(serializer.data)


class TaskFileDeleteAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, file_id):
        """Удаление файла"""
        task_file = get_object_or_404(TaskFile, id=file_id)
        board = task_file.task.column.board

        # Проверка прав
        if board.owner != request.user and not BoardPermit.objects.filter(
                board=board,
                user=request.user
        ).exists():
            return Response(
                {"error": "Нет прав на удаление файла"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Удаляем файл
        task_file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------
# -------------------Комменты--------------------
class AddCommentAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        text = request.data.get("text")

        if not text:
            return Response({"error": "Text is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем комментарий с полем user
        comment = Comment.objects.create(
            task=task,
            user=request.user,  # ИЗМЕНЕНИЕ: user вместо creator
            text=text,
        )

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@login_required(login_url='login')
def my_boards(request):
    user = request.user

    owned_boards = Board.objects.filter(owner=user)
    permitted_boards = Board.objects.filter(
        boardpermit__user=user
    ).exclude(owner=user)

    boards = (owned_boards | permitted_boards).order_by('-created').distinct()

    context = {
        'boards': boards.distinct()
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
    ALLOWED_ROLES = {'member', 'viewer'}

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
@csrf_exempt  # если используешь fetch с CSRF, можно убрать csrf_exempt
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


# -----------------сессии и передача в реакт токенов----------------------  https://habr.com/ru/articles/804615/

# Создаёт уникальный CSRF-токен и вставляет в cookie браузеру
# @ensure_csrf_cookie
# def get_csrf(request):
#     return JsonResponse({"detail": "CSRF cookie set"})
#
#
# @ensure_csrf_cookie  # <- Принудительная отправка CSRF cookie
# def session_view(request):
#     if not request.user.is_authenticated:
#         return JsonResponse({'isAuthenticated': False})
#
#     return JsonResponse({'isAuthenticated': True, 'username': request.user.username, 'user_id': request.user.id})
#
#
# def user_info(request):
#     return JsonResponse({'username': request.user.username})
#
#
# # Проверка сессии
# # @ensure_csrf_cookie
# # def session_view(request):
# #     if not request.user.is_authenticated:
# #         return JsonResponse({"isAuthenticated": False})
# #     return JsonResponse({
# #         "isAuthenticated": True,
# #         "username": request.user.username,
# #         "user_id": request.user.id,
# #     })
#
#
# # Вход
# @require_POST
# def login_view(request):
#     data = json.loads(request.body)
#     username = data.get('username')
#     password = data.get('password')
#     if not username or not password:
#         return JsonResponse({'detail': 'Введите логин и пароль'}, status=400)
#
#     user = authenticate(username=username, password=password)
#     if user is None:
#         return JsonResponse({'detail': 'Неверные данные'}, status=400)
#
#     login(request, user)  # создаётся сессия
#     return JsonResponse({'detail': 'Успешно авторизованы'})
#
#
# # Выход
# def logout_view(request):
#     logout(request)
#     return JsonResponse({'detail': 'Вы вышли'})

# Создаёт уникальный CSRF-токен и вставляет в cookie браузеру
def get_csrf(request):
    response = JsonResponse({'detail': 'CSRF cookie set'})
    response['X-CSRFToken'] = get_token(request)
    return response


@require_POST
def login_view(request):
    # Получаем авторизационные данные
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')

    # Валидация
    if username is None or password is None:
        return JsonResponse({'detail': 'Пожалуйста предоставьте логин и пароль'}, status=400)

    # Аутентификация пользоваля
    user = authenticate(username=username, password=password)

    if user is None:
        return JsonResponse({'detail': 'Неверные данные'}, status=400)

    # Создаётся сессия. session_id отправляется в куки
    login(request, user)
    return JsonResponse({'detail': 'Успешная авторизация'})


# Сессия удаляется из БД и session_id на клиенте более недействителен
@json_login_required
def logout_view(request):
    logout(request)
    return JsonResponse({'detail': 'Вы успешно вышли'})


# Узнать авторизован ли пользователь и получить его данные
@ensure_csrf_cookie  # <- Принудительная отправка CSRF cookie
def session_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})

    return JsonResponse({'isAuthenticated': True, 'username': request.user.username, 'user_id': request.user.id})


# Получение информации о пользователе
@json_login_required
def user_info(request):
    return JsonResponse({'username': request.user.username})


# Удаление всех сессий из БД
# Вы можете переделать так, чтобы отзывать сессию у определённого пользователя
@json_login_required
def kill_all_sessions(request):
    sessions = Session.objects.all()
    sessions.delete()

    return JsonResponse({'detail': 'Сессии успешно завершены'})
