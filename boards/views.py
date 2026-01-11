import os
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session

from rest_framework.views import APIView
from rest_framework.response import Response

# местные импорты
from .forms import BoardForm
from .models import Board, BoardPermit, User
from .serializers import BoardSerializer, UserSerializer
# компоненты view
from .view_parts.utils import json_login_required
from .view_parts.auth import *
from .view_parts.debug import *
from .view_parts.boards import *
from .view_parts.tasks import *
from .view_parts.columns import *
from .view_parts.comments import *


class UserAPIView(APIView):  # отправка json в реакт
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"isAuthenticated": False}, status=401)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    # def get(self, request, pk):
    #     # Только владелец или участники могут видеть доску
    #     board = get_object_or_404(Board, id=pk)
    #     if board.owner != request.user and request.user not in board.members.all():
    #         return Response({"detail": "Нет доступа"}, status=403)
    #     serializer = BoardSerializer(board)
    #     return Response(serializer.data)
