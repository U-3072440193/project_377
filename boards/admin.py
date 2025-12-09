from django.contrib import admin
from .models import Board, BoardMember, Column, Task, Comment


admin.site.register(Board)
admin.site.register(BoardMember)
admin.site.register(Column)
admin.site.register(Task)
admin.site.register(Comment)
