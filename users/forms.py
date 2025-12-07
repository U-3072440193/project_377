from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Profile, Message
from django.forms import ModelForm
from django.core.exceptions import ValidationError


class CustomForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            'username': 'Имя пользователя',
            'email': 'Email',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }

        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'input',  # класс
                'placeholder': placeholders[name]  # плейсхолдер
            })


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = [
            'username',
            'first_name',
            'last_name',
            'avatar',
            'bio',
            'social_media_link',
            'social_media_link2',
            'social_media_link3',
            'email'
        ]

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Проверяем, есть ли пользователь с таким ником, кроме текущего
            if User.objects.filter(username=username).exclude(pk=self.instance.user.pk).exists():
                raise ValidationError("Этот ник уже занят")
        return username


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body', 'file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'input'})
        }
