from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .forms import CustomForm, ProfileForm, MessageForm
from django.shortcuts import get_object_or_404
from .models import Message

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


@login_required(login_url='login')
def user_profile(request):
    profile = request.user.profile  # сам User
    context = {
        "profile": profile
    }
    return render(request, "users/profile.html", context)


@login_required(login_url='login')
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


@login_required(login_url='login')
def inbox(request):
    user = request.user
    message_request = user.messages.all()
    unread = message_request.filter(is_read=False).count()
    context = {
        'message_request': message_request,
        'unread': unread
    }
    return render(request, 'users/inbox.html', context)


@login_required(login_url='login')
def view_message(request, pk):
    message = get_object_or_404(request.user.messages, id=pk)
    if message.is_read is False:
        message.is_read = True
        message.save()
    context = {'message': message}
    return render(request, 'users/message.html', context)


@login_required(login_url='login')
def create_message(request, pk):
    recipient = User.objects.get(id=pk)
    form = MessageForm()

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user  # текущий залогиненный пользователь
            message.recipient = recipient
            message.name = request.user.username
            message.email = request.user.email
            message.save()
            messages.success(request, "Сообщение отправлено")
            return redirect('profile')
    context = {'recipient': recipient, 'form': form}
    return render(request, 'users/message.html', context)


@login_required(login_url='login')
def new_message(request):
    users = User.objects.exclude(id=request.user.id)  # всех кроме себя
    if request.method == "POST":
        recipient_id = request.POST.get("recipient")
        recipient = get_object_or_404(User, id=recipient_id)
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.name = request.user.username
            message.email = request.user.email
            message.save()
            messages.success(request, "Сообщение отправлено")
            return redirect('inbox')
    else:
        form = MessageForm()
    context = {"users": users, "form": form}
    return render(request, 'users/new-message.html', context)


def delete_message(request, pk):
    message = get_object_or_404(Message, id=pk)
    if message.recipient == request.user:
        message.delete()

    return redirect('inbox')
