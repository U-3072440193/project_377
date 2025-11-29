from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .forms import CustomForm, ProfileForm

from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            messages.error(request, 'такой пользователь не существует')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Неправильный логин или пароль')
            return redirect('login')

    # если GET-запрос — просто показать форму
    return render(request, 'users/login.html')


def logout_user(request):
    logout(request)
    messages.info(request, 'Пользователь вышел из аккаунта')
    return redirect('login')


def register_user(request):
    page = 'register'
    form = CustomForm()
    if request.method == "POST":
        form = CustomForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, "Новый аккаунт создан")
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Произошла ошибка при регистрации")

    context = {
        'page': page,
        'form': form
    }
    return render(request, 'users/register.html', context)


@login_required
def user_profile(request):
    profile = request.user.profile  # сам User
    context = {
        "profile": profile
    }
    return render(request, "users/profile.html", context)


@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён")
            return redirect('profile')
        else:
            messages.error(request, "Ошибка при обновлении профиля")
    else:
        form = ProfileForm(instance=profile)

    context = {'form': form, 'profile': profile}
    return render(request, 'users/profile_form.html', context)
