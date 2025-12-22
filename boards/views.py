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
from rest_framework.permissions import IsAuthenticated

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse


class BoardListAPIView(APIView):  # отправка json в реакт

    def get(self, request, pk):
        board = get_object_or_404(Board, id=pk)
        serializer = BoardSerializer(board)
        return Response(serializer.data)

    # def get(self, request, pk):
    #     # Только владелец или участники могут видеть доску
    #     board = get_object_or_404(Board, id=pk)
    #     if board.owner != request.user and request.user not in board.members.all():
    #         return Response({"detail": "Нет доступа"}, status=403)
    #     serializer = BoardSerializer(board)
    #     return Response(serializer.data)


def boards_page(request, pk):
    board = get_object_or_404(Board, id=pk)
    return render(request, 'boards/board.html', {
        'board_id': board.id,
        'user_id': request.user.id,
        'username': request.user.username,
    })


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
    def delete(self, request, pk):
        column = get_object_or_404(Column, id=pk)
        if column.board.owner != request.user:
            return Response({"detail": "Forbidden"}, status=403)
        column.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        if task.creator != request.user:
            return Response(status=403)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------сессии и передача в реакт токенов----------------------

# Получение CSRF
@ensure_csrf_cookie
def get_csrf(request):
    response = JsonResponse({"detail": "CSRF cookie set"})
    response["Access-Control-Allow-Credentials"] = "true"
    return response


# Проверка сессии
@ensure_csrf_cookie
def session_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"isAuthenticated": False})
    return JsonResponse({
        "isAuthenticated": True,
        "username": request.user.username,
        "user_id": request.user.id,
    })


# Вход
@require_POST
def login_view(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return JsonResponse({'detail': 'Введите логин и пароль'}, status=400)

    user = authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({'detail': 'Неверные данные'}, status=400)

    login(request, user)  # создаётся сессия
    return JsonResponse({'detail': 'Успешно авторизованы'})


# Выход
def logout_view(request):
    logout(request)
    return JsonResponse({'detail': 'Вы вышли'})
