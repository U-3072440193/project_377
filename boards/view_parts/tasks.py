from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import F, Max

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from ..models import *
from ..serializers import *
from .utils import UNIVERSAL_FOR_AUTHENTICATION, UNIVERSAL_FOR_PERMISSION_CLASSES

from django.utils import timezone
from datetime import datetime


class TaskCreateAPIView(APIView):
    authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES

    def post(self, request, column_id):
        column = get_object_or_404(Column, id=column_id)
        title = request.data.get("title")
        if not title:
            return Response({"error": "Title is required"}, status=400)

        task = Task.objects.create(
            column=column,
            title=title,
            position=column.tasks.count() ,
            creator=request.user,
            priority=request.data.get("priority", "low")
        )
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=201)
    

class TaskRenameAPIView(APIView):
    authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES

    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        board = task.column.board

        # Проверка прав: либо владелец, либо участник
        if board.owner != request.user and not BoardPermit.objects.filter(board=board, user=request.user).exists():
                return Response(
                    {"error": "У вас нет прав для перемещения этой задачи"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        title = request.data.get("title")
        if not title:
            return Response(
                {"error": "Title is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        task.title = title
        task.save()

        serializer = TaskSerializer(task)
        return Response(serializer.data, status=200)


class TaskDeleteAPIView(APIView):
    authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES

    def delete(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        if task.creator != request.user:
            return Response(status=403)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskMoveView(APIView):
    authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES

    def patch(self, request, pk):
        print(f"\n=== MOVE TASK {pk} ===")
        print(f"Request data: {request.data}")
    
        task = Task.objects.select_for_update().get(pk=pk)
        print(f"BEFORE - Task {pk}: position={task.position}, column={task.column.id}")
        """
        Перемещает задачу в другую колонку и/или меняет её позицию.
        Пример JSON тела запроса:
        {
            "column": 2,       ID новой колонки (обязательно)
            "position": 0      Новая позиция в колонке (0-based, опционально)
        }
        """
        try:
            task = Task.objects.select_for_update().get(pk=pk)
            board = task.column.board

            # Проверяем права пользователя!Временно! Права будут разделегированы между мемберами
            if board.owner != request.user and not BoardPermit.objects.filter(board=board, user=request.user).exists():
                return Response(
                    {"error": "У вас нет прав для перемещения этой задачи"},
                    status=status.HTTP_403_FORBIDDEN
                )

            column_id = request.data.get('column')
            position = request.data.get('position')

            if column_id is None:
                return Response(
                    {"error": "Не указана колонка"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            new_column = get_object_or_404(Column, pk=column_id)

            # Проверяем, что новая колонка в той же доске
            if new_column.board != board:
                return Response(
                    {"error": "Колонка должна принадлежать той же доске"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Сохраняем старую колонку
            old_column = task.column

            with transaction.atomic():
                # Если задача перемещается в другую колонку
                if old_column.id != new_column.id:
                    #  Удаляем задачу из старой колонки и корректируем позиции
                    Task.objects.filter(
                        column=old_column,
                        position__gt=task.position
                    ).update(position=F('position') - 1)

                    #  Добавляем задачу в новую колонку
                    task.column = new_column
                    if position is not None:
                        # Освобождаем место для новой задачи в новой колонке
                        Task.objects.filter(
                            column=new_column,
                            position__gte=position
                        ).update(position=F('position') + 1)
                        task.position = position
                    else:
                        # Если позиция не указана, ставим в конец
                        last_position = Task.objects.filter(
                            column=new_column
                        ).aggregate(models.Max('position'))['position__max']
                        task.position = (last_position + 1) if last_position is not None else 0
                else:
                    # Перемещение внутри той же колонки
                    if position is not None and position != task.position:
                        old_position = task.position
                        if position > old_position:
                            # Перемещаем вниз
                            Task.objects.filter(
                                column=old_column,
                                position__gt=old_position,
                                position__lte=position
                            ).update(position=F('position') - 1)
                        else:
                            # Перемещаем вверх
                            Task.objects.filter(
                                column=old_column,
                                position__lt=old_position,
                                position__gte=position
                            ).update(position=F('position') + 1)
                        task.position = position

                task.save()
                task.refresh_from_db()
                print(f"AFTER  - Task {pk}: position={task.position}, column={task.column.id}")
    
                serializer = TaskSerializer(task)
                print(f"Response data size: {len(str(serializer.data))} bytes")
                print("=== END ===\n")
    
                return Response(serializer.data)

        except Task.DoesNotExist:
            return Response(
                {"error": "Задача не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TaskUpdateAPIView(APIView):
    authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES

    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk)

        board = task.column.board

        # Проверка прав
        if board.owner != request.user and not BoardPermit.objects.filter(
                board=board,
                user=request.user
        ).exists():
            return Response(
                {"error": "Нет прав на редактирование задачи"},
                status=status.HTTP_403_FORBIDDEN
            )

        description = request.data.get("description")

        if description is None:
            return Response(
                {"error": "description is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.description = description
        task.save()

        serializer = TaskSerializer(task)
        return Response(serializer.data, status=200)


class TaskFileUploadAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        board = task.column.board

        # проверка прав
        if board.owner != request.user and not BoardPermit.objects.filter(
                board=board,
                user=request.user
        ).exists():
            return Response({"error": "Нет прав"}, status=403)

        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return Response({"error": "Файл не передан"}, status=400)

        task_file = TaskFile.objects.create(
            task=task,
            file=uploaded_file,
            uploaded_by=request.user
        )

        serializer = TaskFileSerializer(task_file)
        return Response(serializer.data, status=201)


class TaskFilesListAPIView(APIView):
    authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES

    def get(self, request, pk):
        task = get_object_or_404(Task, id=pk)
        board = task.column.board

        # Ясная проверка: владелец ИЛИ участник
        is_owner = board.owner == request.user
        has_permit = BoardPermit.objects.filter(board=board, user=request.user).exists()

        if not (is_owner or has_permit):
            return Response({
                "error": "Нет прав на просмотр файлов",
                "debug": {
                    "user": request.user.username,
                    "is_owner": is_owner,
                    "has_permit": has_permit,
                    "required": "is_owner OR has_permit"
                }
            }, status=403)

        files = task.files.all()
        serializer = TaskFileSerializer(files, many=True, context={'request': request})
        return Response(serializer.data)


class TaskFileDeleteAPIView(APIView):
    authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES

    def delete(self, request, file_id):
        task_file = get_object_or_404(TaskFile, id=file_id)
        board = task_file.task.column.board

        # Проверка прав
        if board.owner != request.user and not BoardPermit.objects.filter(
                board=board,
                user=request.user
        ).exists():
            return Response(
                {"error": "Нет прав на удаление файла"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Удаляем файл
        task_file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskPriorityUpdateAPIView(APIView):
    authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES

    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk)

        board = task.column.board

        # Проверка прав
        if board.owner != request.user and not BoardPermit.objects.filter(
                board=board,
                user=request.user
        ).exists():
            return Response(
                {"error": "Нет прав на редактирование задачи"},
                status=status.HTTP_403_FORBIDDEN
            )

        priority = request.data.get("priority")

        if priority is None:
            return Response(
                {"error": "priority is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем, что приоритет допустимый
        valid_priorities = dict(Task.PRIORITY).keys()
        if priority not in valid_priorities:
            return Response(
                {"error": f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.priority = priority
        task.save()

        serializer = TaskSerializer(task)
        return Response(serializer.data, status=200)
    

class TaskDeadlineAPIView(APIView):
    authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES

    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk)

        board = task.column.board

        # Проверка прав
        if board.owner != request.user and not BoardPermit.objects.filter(
                board=board,
                user=request.user
        ).exists():
            return Response(
                {"error": "Нет прав на редактирование задачи"},
                status=status.HTTP_403_FORBIDDEN
            )

        deadline = request.data.get("deadline")

        # Если deadline равен null или пустой строке - удаляем дедлайн
        if deadline is None or deadline == "" or deadline == "null":
            task.deadline = None
        else:
            try:
                # Преобразуем строку в datetime
                from django.utils.dateparse import parse_datetime
                deadline_dt = parse_datetime(deadline)
                
                if not deadline_dt:
                    # Если parse_datetime не сработал, пробуем parse_date
                    from django.utils.dateparse import parse_date
                    deadline_date = parse_date(deadline)
                    if deadline_date:
                        deadline_dt = timezone.make_aware(
                            datetime.combine(deadline_date, datetime.min.time())
                        )
                    else:
                        return Response(
                            {"error": "Неверный формат даты. Используйте ISO формат: YYYY-MM-DDTHH:MM:SS"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
                # Проверяем, что дедлайн в будущем (опционально)
                if deadline_dt < timezone.now():
                    return Response(
                        {"error": "Дедлайн не может быть в прошлом"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                task.deadline = deadline_dt
            except (ValueError, TypeError) as e:
                return Response(
                    {"error": f"Ошибка обработки даты: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        task.save()
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=200)
    

class AddResponsibleToTaskAPIView(APIView):
    authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES
    
    def post(self, request, task_id):
        """
        Добавить ответственного к задаче
        """
        try:
            task = get_object_or_404(Task, id=task_id)
            user_id = request.data.get('user_id')
            
            if not user_id:
                return Response({'error': 'user_id обязателен'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Проверяем, что пользователь существует
            user = get_object_or_404(User, id=user_id)
            
            # Проверяем права доступа
            board = task.column.board
            if board.owner != request.user and not BoardPermit.objects.filter(board=board, user=request.user).exists():
                return Response({'error': 'Нет прав для изменения этой задачи'}, status=status.HTTP_403_FORBIDDEN)
            
            # Проверяем, что добавляемый пользователь является участником доски
            # Сначала проверяем владельца
            if user != board.owner:
                # Проверяем, что пользователь имеет доступ к доске
                if not BoardPermit.objects.filter(board=board, user=user).exists():
                    return Response({'error': 'Пользователь не является участником доски'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Добавляем пользователя к ответственным
            if task.responsible.filter(id=user.id).exists():
                return Response({'error': 'Пользователь уже является ответственным'}, status=status.HTTP_400_BAD_REQUEST)
            
            task.responsible.add(user)
            task.save()
            
            # Возвращаем обновленную задачу
            serializer = TaskSerializer(task)
            return Response({
                'success': True,
                'message': 'Пользователь добавлен к ответственным',
                'task': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RemoveResponsibleFromTaskAPIView(APIView):
    authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES
    
    def post(self, request, task_id):
        """
        Удалить ответственного из задачи
        """
        try:
            task = get_object_or_404(Task, id=task_id)
            user_id = request.data.get('user_id')
            
            if not user_id:
                return Response({'error': 'user_id обязателен'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Проверяем, что пользователь существует
            user = get_object_or_404(User, id=user_id)
            
            # Проверяем права доступа
            board = task.column.board
            if board.owner != request.user and not BoardPermit.objects.filter(board=board, user=request.user).exists():
                return Response({'error': 'Нет прав для изменения этой задачи'}, status=status.HTTP_403_FORBIDDEN)
            
            # Удаляем пользователя из ответственных
            if not task.responsible.filter(id=user.id).exists():
                return Response({'error': 'Пользователь не является ответственным'}, status=status.HTTP_400_BAD_REQUEST)
            
            task.responsible.remove(user)
            task.save()
            
            # Возвращаем обновленную задачу
            serializer = TaskSerializer(task)
            return Response({
                'success': True,
                'message': 'Пользователь удален из ответственных',
                'task': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetTaskResponsibleAPIView(APIView):
    authentication_classes = UNIVERSAL_FOR_AUTHENTICATION
    permission_classes = UNIVERSAL_FOR_PERMISSION_CLASSES
    
    def get(self, request, task_id):
        """
        Получить список ответственных за задачу
        """
        try:
            task = get_object_or_404(Task, id=task_id)
            
            # Проверяем права доступа
            board = task.column.board
            if board.owner != request.user and not BoardPermit.objects.filter(board=board, user=request.user).exists():
                return Response({'error': 'Нет прав для просмотра этой задачи'}, status=status.HTTP_403_FORBIDDEN)
            
            # Получаем список ответственных
            responsible_users = task.responsible.all()
            
            # Используем UserSerializer из ваших сериализаторов
            from ..serializers import UserSerializer
            serializer = UserSerializer(responsible_users, many=True)
            
            return Response({
                'success': True,
                'responsible': serializer.data,
                'count': responsible_users.count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)