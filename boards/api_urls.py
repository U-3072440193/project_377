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
)

urlpatterns = [
    path('boards/<int:pk>/', BoardListAPIView.as_view()),
    path('boards/<int:board_id>/columns/', ColumnCreateAPIView.as_view()),
    path('columns/<int:pk>/', ColumnDeleteAPIView.as_view()),
    path('columns/<int:column_id>/tasks/', TaskCreateAPIView.as_view()),
    path('tasks/<int:pk>/', TaskDeleteAPIView.as_view()),

    path('csrf/', get_csrf),
    path('session/', session_view),
    path('login/', login_view),
    path('logout/', logout_view),


]
