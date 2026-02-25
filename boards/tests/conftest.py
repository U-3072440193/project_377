import pytest
from django.contrib.auth import get_user_model
from boards.models import Board, Column, Task, Comment

User = get_user_model()

@pytest.fixture
def user():
    """Создает тестового пользователя."""
    return User.objects.create_user(username='testuser', password='12345')

@pytest.fixture
def board(user):
    """Создает тестовую доску."""
    return Board.objects.create(title='Тестовая доска', owner=user)

@pytest.fixture
def column(board):
    """Создает тестовую колонку."""
    return Column.objects.create(title='To Do', board=board, position=1)


@pytest.fixture
def task(column, user):
    """Создает тестовую задачу."""
    return Task.objects.create(
        title='Тестовая задача',
        column=column,
        position=1,
        creator=user
    )
    
@pytest.fixture
def comment(task, user):
    """Создает тестовую задачу."""
    return Comment.objects.create(
        text='Тестовая задача',
        task=task,
        user=user,
    )