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

)

urlpatterns = [
    path('boards/<int:pk>/', BoardListAPIView.as_view()),
    path('boards/<int:board_id>/columns/', ColumnCreateAPIView.as_view()),
    path('columns/<int:pk>/', ColumnDeleteAPIView.as_view()),
    path('columns/<int:column_id>/tasks/', TaskCreateAPIView.as_view()),
    path('tasks/<int:pk>/', TaskDeleteAPIView.as_view()),
    path('user/', UserAPIView.as_view()),

    path('csrf/', get_csrf),
    path('session/', session_view),
    path('login/', login_view),
    path('logout/', logout_view),
    path('user_info/', user_info, name='api-userInfo'),
    path('kill_all_sessions/', kill_all_sessions, name='kill-all-sessions'),

]
