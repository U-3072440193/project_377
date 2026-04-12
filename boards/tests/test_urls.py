import pytest
from django.urls import reverse, resolve
from boards import views
from boards.models import Board, Column, Task
from boards.api_urls import BoardListAPIView, ColumnCreateAPIView, TaskCreateAPIView, UserAPIView

class TestBoardUrls:
    """Тесты для URL досок."""
    
    def test_board_detail_url(self):
        url = reverse('boards-page', kwargs={'pk': 1})
        assert url == '/boards/boards/1/'   
    
    def test_new_board_url(self):
        url = reverse('new-board')
        assert url == '/boards/new-board'   
    
    def test_delete_board_url(self):
        url = reverse('delete_board', kwargs={'pk': 1})
        assert url == '/boards/boards/1/delete/'   
    
    def test_add_member_url(self):
        url = reverse('add-board-member', kwargs={'board_id': 1})
        assert url == '/boards/boards/1/add-member/'  
    
    def test_archive_list_url(self):
        url = reverse('archive')
        assert url == '/boards/archive/'   
    
    def test_archive_board_url(self):
        url = reverse('archive_board', kwargs={'board_id': 1})
        assert url == '/boards/board/1/archive/'  
    
    def test_archive_view_url(self):
        url = reverse('archive-view', kwargs={'board_id': 1})
        assert url == '/boards/archive/board/1/'   
    
    def test_move_board_up_url(self):
        url = reverse('move_board_up', kwargs={'board_id': 1})
        assert url == '/boards/1/move-up/'  
    
    def test_move_board_down_url(self):
        url = reverse('move_board_down', kwargs={'board_id': 1})
        assert url == '/boards/1/move-down/'  
    
    def test_my_boards_url(self):
        url = reverse('my-boards')
        assert url == '/boards/my-boards/'   
        
class TestBoardAPIUrls:
    """Тесты для API URL."""
    
    def test_board_list_api_url(self):
        """URL для списка досок (без параметров) - такого нет!"""
               
        # Проверим, что URL с параметром работает
        url = reverse('board-list', kwargs={'pk': 1})
        assert url == '/api/boards/1/'
        
        resolver = resolve('/api/boards/1/')
        assert resolver.func.view_class == BoardListAPIView
    
    def test_board_detail_api_url(self):
        """Детальный просмотр доски (тот же URL что и выше)."""
        url = reverse('board-list', kwargs={'pk': 1})  # используется то же имя!
        assert url == '/api/boards/1/'
        
        resolver = resolve('/api/boards/1/')
        assert resolver.func.view_class == BoardListAPIView
    
    def test_create_column_api_url(self):
        url = reverse('column-create', kwargs={'board_id': 1})
        assert url == '/api/boards/1/columns/'
        
        resolver = resolve('/api/boards/1/columns/')
        assert resolver.func.view_class == ColumnCreateAPIView
    
    def test_create_task_api_url(self):
        url = reverse('task-create', kwargs={'column_id': 1})
        assert url == '/api/columns/1/tasks/'
        
        resolver = resolve('/api/columns/1/tasks/')
        assert resolver.func.view_class == TaskCreateAPIView
    
    def test_user_api_url(self):
        """Тест для URL пользователя."""
        
        url = reverse('user-api')  
        assert url == '/api/user/'
        
        resolver = resolve('/api/user/')
        assert resolver.func.view_class == UserAPIView
        
@pytest.mark.django_db
class TestBoardAPI:
    """Тесты для API досок."""
    
    def test_get_board_unauthorized(self, api_client, board):
        """Неавторизованный пользователь получает 403 (доступ запрещён)."""
        url = reverse('board-list', kwargs={'pk': board.id})
        response = api_client.get(url)
        assert response.status_code == 403
    
    def test_get_board_authorized(self, authenticated_client, board):
        url = reverse('board-list', kwargs={'pk': board.id})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert response.data['title'] == board.title
    
    def test_get_nonexistent_board(self, authenticated_client):
        url = reverse('board-list', kwargs={'pk': 99999})
        response = authenticated_client.get(url)
        assert response.status_code == 404

@pytest.mark.django_db
class TestColumnAPI:
    """Тесты для API колонок."""
    
    def test_create_column(self, authenticated_client, board):
        url = reverse('column-create', kwargs={'board_id': board.id})
        response = authenticated_client.post(url, {'title': 'New Column'})
        assert response.status_code == 201
        assert Column.objects.filter(title='New Column', board=board).exists()
    
    def test_create_column_invalid_data(self, authenticated_client, board):
        url = reverse('column-create', kwargs={'board_id': board.id})
        response = authenticated_client.post(url, {'title': ''})
        assert response.status_code == 400

@pytest.mark.django_db
class TestTaskAPI:
    """Тесты для API задач."""
    
    def test_create_task(self, authenticated_client, column):
        url = reverse('task-create', kwargs={'column_id': column.id})
        response = authenticated_client.post(url, {'title': 'New Task'})
        assert response.status_code == 201
        assert Task.objects.filter(title='New Task', column=column).exists()
    
    def test_rename_task(self, authenticated_client, task):
        url = reverse('task-rename', kwargs={'pk': task.id})
        response = authenticated_client.patch(url, {'title': 'Updated'})
        assert response.status_code == 200
        task.refresh_from_db()
        assert task.title == 'Updated'
    
    def test_delete_task(self, authenticated_client, task):
        url = reverse('task-delete', kwargs={'pk': task.id})
        response = authenticated_client.delete(url)
        assert response.status_code == 204
        assert not Task.objects.filter(id=task.id).exists()