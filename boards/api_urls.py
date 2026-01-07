'''Файл предназначен для путей передачи данных от джанго в реакт и обратно, включая отладочные пути и авторизацию'''

from django.urls import path
from .views import (
    BoardListAPIView,
    ColumnCreateAPIView,
    ColumnDeleteAPIView,
    TaskCreateAPIView,
    TaskDeleteAPIView,
    session_view,
    get_csrf,
    login_view,
    logout_view,
    UserAPIView,
    user_info,
    kill_all_sessions,
    board_members_api,
    remove_board_member,
    TaskMoveView,
    TaskUpdateAPIView,
    TaskFileUploadAPIView,
    TaskFilesListAPIView,
    TaskFileDeleteAPIView,
    AddCommentAPIView,
    debug_task_auth,
    test_auth,
    debug_task_check
)

urlpatterns = [
    path('boards/<int:pk>/', BoardListAPIView.as_view()),
    path('boards/<int:board_id>/columns/', ColumnCreateAPIView.as_view()),
    path('columns/<int:pk>/', ColumnDeleteAPIView.as_view()),
    path('columns/<int:column_id>/tasks/', TaskCreateAPIView.as_view()),

    path('user/', UserAPIView.as_view()),

    path('csrf/', get_csrf),
    path('session/', session_view),
    path('login/', login_view),
    path('logout/', logout_view),
    path('user_info/', user_info, name='api-userInfo'),
    path('kill_all_sessions/', kill_all_sessions, name='kill-all-sessions'),

    path('boards/<int:board_id>/members/', board_members_api, name='board_members_api'),
    path('boards/<int:board_id>/remove-member/', remove_board_member, name='remove-board-member'),

    path('tasks/<int:pk>/', TaskDeleteAPIView.as_view()),
    path('tasks/<int:pk>/move/', TaskMoveView.as_view(), name='task-move'),
    path('tasks/<int:pk>/description/', TaskUpdateAPIView.as_view(), name='task-update-description'),
    path('tasks/<int:pk>/files/', TaskFilesListAPIView.as_view(), name='task-files-list'),  # GET список файлов
    path('tasks/<int:pk>/files/upload/', TaskFileUploadAPIView.as_view(), name='task-file-upload'),
    path('files/<int:file_id>/', TaskFileDeleteAPIView.as_view(), name='task-file-delete'),  # DELETE удаление файла
    path('tasks/<int:task_id>/comments/', AddCommentAPIView.as_view(), name='add-comment'),
    # Отладочные пути
    path('debug-task-auth/<int:task_id>/', debug_task_auth, name='debug-task-auth'),
    path('test-auth/', test_auth, name='test-auth'),
    path('debug-task-check/<int:task_id>/', debug_task_check, name='debug-task-check'),
]
