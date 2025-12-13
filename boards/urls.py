from django.urls import path
from . import views

urlpatterns = [
    path('board/', views.BoardListAPIView.as_view(), name='board'),
]
