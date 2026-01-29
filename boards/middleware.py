# boards/middleware.py
import re
from django.http import HttpResponseRedirect

class FixReactPathsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        path = request.path
        
        # Проверяем неправильные пути React и делаем редирект
        patterns = [
            (r'^/boards/boards/\d+/static/frontend/static/static/media/(.*)$', r'/static/media/\1'),
            (r'^/static/frontend/static/static/media/(.*)$', r'/static/media/\1'),
            (r'^/static/static/media/(.*)$', r'/static/media/\1'),
            (r'^/boards/boards/\d+/static/(.*)$', r'/static/\1'),
        ]
        
        for pattern, replacement in patterns:
            match = re.match(pattern, path)
            if match:
                new_path = re.sub(pattern, replacement, path)
                print(f"Redirecting: {path} -> {new_path}")
                return HttpResponseRedirect(new_path)
        
        return self.get_response(request)