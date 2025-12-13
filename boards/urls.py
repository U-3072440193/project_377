from django.urls import path
from . import views


urlpatterns = [

    path('boards/', views.boards_page, name='boards-page'), # HTML-страница
    path('api/boards/', views.BoardListAPIView.as_view(), name='boards-api'), # API
]
