from django.http import JsonResponse
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated

UNIVERSAL_FOR_AUTHENTICATION = [BasicAuthentication, SessionAuthentication]
UNIVERSAL_FOR_PERMISSION_CLASSES = [IsAuthenticated]


def json_login_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Вы не авторизованы'}, status=401)
        return view_func(request, *args, **kwargs)

    return wrapped_view
