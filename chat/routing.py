"""Маршрутизатор для определения номера доски для передачи в consumers
https://dzen.ru/a/aDWvrT1TDR-ITMnj
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<board_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]