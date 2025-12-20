from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response

from .froms import BoardForm, ColumnForm
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.contrib.auth.decorators import login_required


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
    return render(request, 'boards/board.html', {
        'board_id': pk})


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
