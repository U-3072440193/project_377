import pytest
from django.contrib.auth import get_user_model
from boards.models import Board, Column, Task, Comment
from rest_framework.test import APIClient

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
    
@pytest.fixture
def api_client():
    """Клиент для API запросов."""
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, user):
    """Клиент с авторизацией."""
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def task_file(task, user):
    """Создает тестовый файл для задачи."""
    from django.core.files.uploadedfile import SimpleUploadedFile
    from boards.models import TaskFile
    
    test_file = SimpleUploadedFile(
        "test.txt",
        b"test content",
        content_type="text/plain"
    )
    
    task_file = TaskFile.objects.create(
        task=task,
        file=test_file,
        uploaded_by=user
    )
    yield task_file
    # очистка после теста
    if task_file.file:
        task_file.file.delete()
        
@pytest.fixture
def user2():
    """Создает второго тестового пользователя."""
    return User.objects.create_user(username='testuser2', password='12345')