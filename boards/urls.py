from django.urls import path
from . import views
from .views import ColumnCreateAPIView

urlpatterns = [

    path('boards/<int:pk>/', views.boards_page, name='boards-page'),  # HTML-страница
    path('api/boards/<int:pk>/', views.BoardListAPIView.as_view(), name='boards-api'),  # API
    path('api/boards/<int:board_id>/columns/', ColumnCreateAPIView.as_view(), name='column-create'),
    path('new-board', views.new_board, name='new-board'),
    path('boards/<int:pk>/delete/', views.delete_board, name='delete_board'),
]
