import pytest
from django.contrib.auth import get_user_model
from boards.forms import BoardForm, ColumnForm
from boards.models import Board, Column

User = get_user_model()

@pytest.mark.django_db
class TestBoardForm:
    """Тесты для формы создания доски."""
    
    def test_form_fields(self):
        """Проверка наличия нужных полей."""
        form = BoardForm()
        assert list(form.fields.keys()) == ['title']
    
    def test_form_labels(self):
        """Проверка меток полей."""
        form = BoardForm()
        assert form.fields['title'].label == 'Название'
    
    def test_valid_data(self):
        """Проверка валидных данных."""
        form_data = {'title': 'Моя доска'}
        form = BoardForm(data=form_data)
        assert form.is_valid() is True
    
    def test_empty_title(self):
        """Проверка пустого названия."""
        form_data = {'title': ''}
        form = BoardForm(data=form_data)
        assert form.is_valid() is False
        assert 'title' in form.errors
    
    def test_title_max_length(self):
        """Проверка максимальной длины (если есть ограничение)."""
        # Если в модели Board.title имеет max_length=200
        long_title = 'a' * 201
        form_data = {'title': long_title}
        form = BoardForm(data=form_data)
        assert form.is_valid() is False
    
    def test_save_form(self, user):
        """Проверка сохранения формы."""
        form_data = {'title': 'Сохранённая доска'}
        form = BoardForm(data=form_data)
        assert form.is_valid()
        
        board = form.save(commit=False)
        board.owner = user
        board.save()
        
        assert Board.objects.filter(title='Сохранённая доска', owner=user).exists()


@pytest.mark.django_db
class TestColumnForm:
    """Тесты для формы создания колонки."""
    
    def test_form_fields(self):
        """Проверка наличия нужных полей."""
        form = ColumnForm()
        assert list(form.fields.keys()) == ['title']
    
    def test_form_labels(self):
        """Проверка меток полей."""
        form = ColumnForm()
        assert form.fields['title'].label == 'Название колонки'
    
    def test_valid_data(self):
        """Проверка валидных данных."""
        form_data = {'title': 'To Do'}
        form = ColumnForm(data=form_data)
        assert form.is_valid() is True
    
    def test_empty_title(self):
        """Проверка пустого названия."""
        form_data = {'title': ''}
        form = ColumnForm(data=form_data)
        assert form.is_valid() is False
        assert 'title' in form.errors