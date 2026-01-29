from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from .forms import CustomForm, ProfileForm, MessageForm
from django.shortcuts import get_object_or_404
from .models import Message, Profile
from django.http import JsonResponse  # для поиска юзеров

from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from boards.models import Board
from django.db.models.signals import post_save


# from django.dispatch import receiver


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
    boards = Board.objects.filter(
        owner=request.user).order_by('-created')
    context = {
        "profile": profile,
        "boards": boards,
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
            # Проходим по всем ошибкам формы и показываем их через messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")

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
        form = MessageForm(request.POST, request.FILES)
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
    # Получаем данные из GET-параметров
    recipient_id = request.GET.get('recipient_id')
    recipient_name = request.GET.get('recipient_name')
    
    if request.method == "POST":
        recipient_id = request.POST.get("recipient_id")
        if not recipient_id:
            messages.error(request, "Вы должны выбрать получателя из списка.")
            return redirect('new-message')

        recipient = get_object_or_404(User, id=recipient_id)
        form = MessageForm(request.POST, request.FILES)
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

    users = User.objects.exclude(id=request.user.id)
    context = {
        "users": users, 
        "form": form,
        "preselected_recipient_id": recipient_id,
        "preselected_recipient_name": recipient_name
    }
    return render(request, 'users/new-message.html', context)




@login_required(login_url='login')
def delete_message(request, pk):
    message = get_object_or_404(Message, id=pk)
    if message.recipient == request.user:
        message.delete()

    return redirect('inbox')


@login_required(login_url='login')
def search_users(request):
    search = request.GET.get('search', '')  # значение параметра ?search= из URL
    users = User.objects.filter(username__icontains=search).exclude(id=request.user.id)[
            :10]  # поиск юзеров кроме отправителя первые 10шт
    data = list(users.values('id', 'username'))  # преобразуем QuerySet в список словарей
    return JsonResponse(data, safe=False)  # JSON-ответ

# @receiver(post_save, sender=User) # автосоздание профиля, если нет
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

@login_required(login_url='login')
def public_profile(request,pk):
    user = get_object_or_404(User, id=pk)
    profile = user.profile 
    boards = Board.objects.filter(owner=user).order_by('-created')
    
    context = {
        "profile": profile,
        "boards": boards,
    }
    return render(request, "users/profile_public.html", context)

def search_profile(request):
    # Получаем поисковый запрос
    search_query = request.GET.get('search', '')
    users = User.objects.all()
    
    # Фильтруем пользователей, если есть поисковый запрос
    if search_query:
        users = users.filter(username__icontains=search_query)
    
    context = {
        'users': users,
        'search_query': search_query
    }
    return render(request, "users/search-profile.html", context)


