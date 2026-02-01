from django.http import JsonResponse
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
import os
import re
from django.conf import settings

UNIVERSAL_FOR_AUTHENTICATION = [SessionAuthentication]
UNIVERSAL_FOR_PERMISSION_CLASSES = [IsAuthenticated]


def json_login_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Вы не авторизованы'}, status=401)
        return view_func(request, *args, **kwargs)

    return wrapped_view


def get_react_js_filename():
    """Получает имя JS файла React (самый простой способ)"""
    js_dir = 'static/frontend/static/js'  # путь от корня проекта
    
    try:
        # Получаем все файлы .js
        js_files = [f for f in os.listdir(js_dir) if f.endswith('.js')]
        
        # Ищем файл, который начинается с 'main.'
        for filename in js_files:
            if filename.startswith('main.'):
                print(filename)
                return filename  # например: main.23c0e5d0.js
                
    except Exception:
        pass
    
    return 'main.js'  # fallback

def get_react_css_filename():
    """Получает имя CSS файла React"""
    css_dir = 'static/frontend/static/css'
    
    try:
        css_files = [f for f in os.listdir(css_dir) if f.endswith('.css')]
        for filename in css_files:
            if filename.startswith('main.'):
                return filename
    except Exception:
        pass
    
    return 'main.css'