from django.contrib import admin
from .models import Board, BoardPermit, Column, Task, Comment


admin.site.register(Board)
admin.site.register(BoardPermit)
admin.site.register(Column)
admin.site.register(Task)
admin.site.register(Comment)
