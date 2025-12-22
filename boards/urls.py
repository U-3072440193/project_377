from django.urls import path
from . import views
from .views import ColumnCreateAPIView, ColumnDeleteAPIView
from .views import TaskCreateAPIView, TaskDeleteAPIView

from django.urls import path
from . import views

urlpatterns = [
    path('boards/<int:pk>/', views.boards_page, name='boards-page'),
    path('new-board', views.new_board, name='new-board'),
    path('boards/<int:pk>/delete/', views.delete_board, name='delete_board'),
]
