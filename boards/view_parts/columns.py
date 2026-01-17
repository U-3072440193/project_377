from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..models import *
from ..serializers import *
from .utils import UNIVERSAL_FOR_AUTHENTICATION, UNIVERSAL_FOR_PERMISSION_CLASSES


class ColumnCreateAPIView(APIView):
    authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES

    def post(self, request, board_id):
                
        board = get_object_or_404(Board, id=board_id)
        
        # Проверка доступа
        is_member = board.members.filter(id=request.user.id).exists()
        is_owner = board.owner == request.user
        
        print(f"Board ID: {board_id}")
        print(f"Board owner: {board.owner.username} (id:{board.owner.id})")
        print(f"Is owner: {is_owner}, Is member: {is_member}")
        
        if not (is_member or is_owner):
            return Response({'error': 'No access to this board'}, status=status.HTTP_403_FORBIDDEN)
        
        title = request.data.get('title')
        if not title:
            return Response({'error': 'Title is required'}, status=status.HTTP_400_BAD_REQUEST)

        column = Column.objects.create(board=board, title=title, position=board.columns.count() + 1)
        serializer = ColumnSerializer(column)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ColumnDeleteAPIView(APIView):
    authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES

    def delete(self, request, pk):
        column = get_object_or_404(Column, id=pk)
        column.delete()
        return Response(status=204)
