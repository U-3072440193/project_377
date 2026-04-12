import pytest
from django.urls import reverse, resolve
from users import views

class TestUsersUrls:
    """Тесты для URL приложения users."""
    
    def test_login_url(self):
        url = reverse('login')
        assert url == '/users/login/'  
        resolver = resolve('/users/login/')
        assert resolver.func == views.login_user
    
    def test_logout_url(self):
        url = reverse('logout')
        assert url == '/users/logout/'
        resolver = resolve('/users/logout/')
        assert resolver.func == views.logout_user
    
    def test_register_url(self):
        url = reverse('register')
        assert url == '/users/register/'
        resolver = resolve('/users/register/')
        assert resolver.func == views.register_user
    
    def test_profile_url(self):
        url = reverse('profile')
        assert url == '/users/profile/'
        resolver = resolve('/users/profile/')
        assert resolver.func == views.user_profile
    
    def test_public_profile_url(self):
        url = reverse('profile-public', kwargs={'pk': 1})
        assert url == '/users/profile-public/1/'
        resolver = resolve('/users/profile-public/1/')
        assert resolver.func == views.public_profile
    
    def test_edit_profile_url(self):
        url = reverse('edit-profile')
        assert url == '/users/edit-profile/'
        resolver = resolve('/users/edit-profile/')
        assert resolver.func == views.edit_profile
    
    def test_inbox_url(self):
        url = reverse('inbox')
        assert url == '/users/inbox/'
        resolver = resolve('/users/inbox/')
        assert resolver.func == views.inbox
    
    def test_view_message_url(self):
        url = reverse('message', kwargs={'pk': 'abc'})
        assert url == '/users/message/abc/'
        resolver = resolve('/users/message/abc/')
        assert resolver.func == views.view_message
    
    def test_create_message_url(self):
        url = reverse('create-message', kwargs={'pk': 1})
        assert url == '/users/inbox/1/'
        resolver = resolve('/users/inbox/1/')
        assert resolver.func == views.create_message
    
    def test_new_message_url(self):
        url = reverse('new-message')
        assert url == '/users/new-message/'
        resolver = resolve('/users/new-message/')
        assert resolver.func == views.new_message
    
    def test_delete_message_url(self):
        url = reverse('delete_message', kwargs={'pk': 1})
        assert url == '/users/delete_message/1/'
        resolver = resolve('/users/delete_message/1/')
        assert resolver.func == views.delete_message
    
    def test_search_users_url(self):
        url = reverse('search-users-profile')  # обновлённое имя
        assert url == '/users/search-users/'
        resolver = resolve('/users/search-users/')
        assert resolver.func == views.search_users
    
    def test_search_profile_url(self):
        url = reverse('search-profile')
        assert url == '/users/search_profile/'
        resolver = resolve('/users/search_profile/')
        assert resolver.func == views.search_profile