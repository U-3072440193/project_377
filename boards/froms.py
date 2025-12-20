from .models import Board, Column
from django.forms import ModelForm


class BoardForm(ModelForm):
    class Meta:
        model = Board
        fields = [
            'title',
        ]

        labels = {
            'title': 'Название',
        }


class ColumnForm(ModelForm):
    class Meta:
        model = Column
        fields = [
            'title',
        ]

        labels = {
            'title': 'Название колонки',
        }
