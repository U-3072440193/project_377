import pytest
from django.contrib.auth import get_user_model
from boards.models import Board, Column, Task, TaskFile, Comment
from django.core.files.uploadedfile import SimpleUploadedFile
import os

User = get_user_model()

@pytest.mark.django_db
class TestBoardModel:
    """Тесты для модели Board."""
    
    def test_create_board(self, user):
        """Проверка создания доски с минимальными полями."""
        board = Board.objects.create(
            title='Моя доска',
            owner=user
        )
        assert board.title == 'Моя доска'
        assert board.owner == user
        assert board.is_archived is False
        assert board.created is not None  # auto_now_add
        assert str(board) == 'Моя доска'
    
    def test_board_unique_title_per_owner(self, user):
        """Проверка уникальности названия доски у одного владельца."""
        Board.objects.create(title='Доска', owner=user)
        
        with pytest.raises(Exception):  # Если unique вместе с owner
            Board.objects.create(title='Доска', owner=user)
    
    def test_board_archive(self, user):
        """Проверка архивации доски."""
        board = Board.objects.create(title='Доска', owner=user)
        assert board.is_archived is False
        
        board.is_archived = True
        board.save()
        
        board.refresh_from_db()
        assert board.is_archived is True
    
    def test_board_creates_permit_for_owner(self, user):
        """Проверка, что при создании доски создаётся BoardPermit для владельца."""
        board = Board.objects.create(title='Доска', owner=user)
        
        # Проверяем, что permit создался
        from boards.models import BoardPermit
        permit = BoardPermit.objects.get(board=board, user=user)
        assert permit.role == 'owner'


@pytest.mark.django_db
class TestColumnModel:
    
    def test_create_column(self, board):
        """Проверка создания колонки."""
        column = Column.objects.create(
            title='To Do',
            board=board,
            position=1
        )
        assert column.title == 'To Do'
        assert column.board == board
        assert column.position == 1
        assert str(column) == f"{column.title} ({column.position})"
    
    def test_column_position_unique_in_board(self, board):
        """Проверка уникальности позиции в пределах доски."""
        Column.objects.create(title='Колонка 1', board=board, position=1)
        
        with pytest.raises(Exception):  # unique_together вероятно
            Column.objects.create(title='Колонка 2', board=board, position=1)
    
    def test_column_position_can_duplicate_in_different_boards(self, board, user):
        """Позиции могут совпадать в разных досках."""
        board2 = Board.objects.create(title='Доска 2', owner=user)
        
        Column.objects.create(title='Колонка 1', board=board, position=1)
        column2 = Column.objects.create(title='Колонка 1', board=board2, position=1)
        assert column2.position == 1


@pytest.mark.django_db
class TestTaskModel:
    
    def test_create_task(self, column, user):
        """Проверка создания задачи."""
        task = Task.objects.create(
            title='Сделать тесты',
            column=column,
            position=1,
            creator=user  
        )
        assert task.title == 'Сделать тесты'
        assert task.column == column
        assert task.position == 1
        assert task.creator == user  # проверяем creator
        assert task.created is not None  # auto_now_add
        assert task.priority == 'low'  # значение по умолчанию
    
    def test_task_position_unique_in_column(self, column, user):
        """Проверка уникальности позиции в пределах колонки."""
        Task.objects.create(
            title='Задача 1',
            column=column,
            position=1,
            creator=user
        )
        
        with pytest.raises(Exception):  # если есть unique_together
            Task.objects.create(
                title='Задача 2',
                column=column,
                position=1,
                creator=user
            )
    
    def test_task_can_move_to_another_column(self, board, column, user):
        """Проверка перемещения задачи между колонками."""
        column2 = Column.objects.create(title='Done', board=board, position=2)
        task = Task.objects.create(
            title='Задача',
            column=column,
            position=1,
            creator=user
        )
        
        task.column = column2
        task.save()
        
        task.refresh_from_db()
        assert task.column == column2
    
    def test_task_deadline_overdue(self, user, column):
        """Проверка метода is_overdue."""
        from django.utils import timezone
        from datetime import timedelta
        
        task = Task.objects.create(
            title='Задача',
            column=column,
            creator=user,
            deadline=timezone.now() - timedelta(days=1)  # вчера
        )
        assert task.is_overdue() is True
        
        task.deadline = timezone.now() + timedelta(days=1)  # завтра
        task.save()
        assert task.is_overdue() is False
        
        task.deadline = None
        assert task.is_overdue() is False
        
        
@pytest.mark.django_db
class TestTaskFileModel:
    """Тесты для модели TaskFile (загрузка файлов в задачу)."""
    
    def test_create_task_file(self, task, user):
        """Проверка создания файла, прикреплённого к задаче."""
        # Создаём тестовый файл в памяти
        test_file = SimpleUploadedFile(
        "test_file.txt",
        b"Test file content",  # используем английский текст для простоты
        content_type="text/plain"
    )
        
        task_file = TaskFile.objects.create(
            task=task,
            file=test_file,
            uploaded_by=user
        )
        
        assert task_file.task == task
        assert task_file.uploaded_by == user
        assert task_file.uploaded_at is not None
        assert task_file.file.name.endswith("test_file.txt")
        assert str(task_file) == task_file.file.name
        
        # Проверяем, что файл был сохранён
        assert task_file.file.size > 0
        
        # Очистка: удаляем файл после теста
        if task_file.file:
            task_file.file.delete()
    
    def test_task_file_relation(self, task, user):
        """Проверка связи Task -> TaskFile (один ко многим)."""
        # Создаём два файла для одной задачи
        file1 = SimpleUploadedFile("file1.txt", b"content1", content_type="text/plain")
        file2 = SimpleUploadedFile("file2.txt", b"content2", content_type="text/plain")
        
        task_file1 = TaskFile.objects.create(task=task, file=file1, uploaded_by=user)
        task_file2 = TaskFile.objects.create(task=task, file=file2, uploaded_by=user)
        
        # Проверяем, что related_name работает
        assert task.files.count() == 2
        assert task_file1 in task.files.all()
        assert task_file2 in task.files.all()
        
        # Очистка
        for tf in [task_file1, task_file2]:
            if tf.file:
                tf.file.delete()
    
    def test_task_file_path_generation(self, task, user):
        """Проверка, что путь к файлу генерируется правильно."""
        test_file = SimpleUploadedFile("document.pdf", b"pdf content", content_type="application/pdf")
        
        task_file = TaskFile.objects.create(
            task=task,
            file=test_file,
            uploaded_by=user
        )
        
        # Ожидаемый путь: task_files/user_id/board_id/task_id/document.pdf
        expected_parts = [
            f"task_files/{user.id}",
            f"{task.column.board.id}",
            f"{task.id}",
            "document.pdf"
        ]
        
        # Проверяем, что все части пути присутствуют
        file_path = task_file.file.name
        for part in expected_parts:
            assert part in file_path
        
        # Очистка
        task_file.file.delete()
        
@pytest.mark.django_db
class TestCommentModel:
    """Тесты для модели TaskFile (загрузка файлов в задачу)."""
    def test_create_comment(self, task, user):
        """Проверка создания задачи."""
        comment = Comment.objects.create(
            text='Сделать тесты',
            task=task,
            user=user  
        )
        assert comment.text == 'Сделать тесты'
        assert comment.task == task
        assert comment.user == user  # проверяем creator
        assert comment.created is not None  # auto_now_add
        