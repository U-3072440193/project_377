from django.urls import path
from .views import ColumnCreateAPIView, ColumnDeleteAPIView, TaskPriorityUpdateAPIView

from django.urls import path
from . import views

urlpatterns = [
    path('boards/<int:pk>/', views.boards_page, name='boards-page'),
    path('new-board', views.new_board, name='new-board'),
    path('boards/<int:pk>/delete/', views.delete_board, name='delete_board'),
    path('my-boards/', views.my_boards, name='my-boards'),
    path('search-users-for-board/', views.search_users_for_board, name='search-users-for-board'),
    path('boards/<int:board_id>/add-member/', views.add_board_member, name='add-board-member'),
    path('board/<int:board_id>/exit/', views.exit_board, name='exit_board'),
    path('archive/', views.archived_boards, name='archive'),
    path('board/<int:board_id>/archive/', views.archive_board, name='archive_board'),
    path('archive/board/<int:board_id>/', views.archive_board_view, name='archive-view'),

]
