from django.shortcuts import render


def home(request):
    return render(request, 'index.html')


def index(request):
    return render(request, 'index.html')


def page_404(request, exception):
    return render(request, '404.html', status=404)
