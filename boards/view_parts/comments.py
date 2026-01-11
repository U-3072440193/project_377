from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..models import *
from ..serializers import *
from .utils import UNIVERSAL_FOR_AUTHENTICATION, UNIVERSAL_FOR_PERMISSION_CLASSES


class AddCommentAPIView(APIView):
    authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES

    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        text = request.data.get("text")

        if not text:
            return Response({"error": "Text is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем комментарий с полем user
        comment = Comment.objects.create(
            task=task,
            user=request.user,
            text=text,
        )

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)