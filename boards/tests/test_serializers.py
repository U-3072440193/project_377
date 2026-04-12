import pytest
from django.contrib.auth import get_user_model
from users.models import Profile
from boards.serializers import UserSerializer, TaskFileSerializer,TaskSerializer
from boards.models import TaskFile, Task
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()

@pytest.mark.django_db
def test_user_avatar_url_when_profile_exists(user):
    profile = Profile.objects.get(user=user)
    from django.core.files.uploadedfile import SimpleUploadedFile
    test_file = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
    profile.avatar.save("test.jpg", test_file, save=True)  # используем save()!
    
    profile.refresh_from_db()  # обновляем из БД
    serializer = UserSerializer(user)
    assert serializer.data['avatar'] is not None
    assert serializer.data['avatar'] != '/media/avatars/default/user.png'
    assert 'test' in serializer.data['avatar']  # должно содержать test
    
@pytest.mark.django_db
def test_user_avatar_none_when_no_profile(user):
    # удаляем профиль (хотя он создаётся сигналом, но можно замокать)
    Profile.objects.filter(user=user).delete()
    serializer = UserSerializer(user)
    assert serializer.data['avatar'] is None
    
@pytest.mark.django_db
def test_task_file_url_with_request(task_file, rf):
    request = rf.get('/')
    serializer = TaskFileSerializer(task_file, context={'request': request})
    assert serializer.data['file_url'].startswith('http://testserver')
    
@pytest.mark.django_db
def test_task_file_url_without_request(task_file):
    serializer = TaskFileSerializer(task_file)
    assert not serializer.data['file_url'].startswith('http')
    
    
@pytest.mark.django_db
def test_task_serializer_with_responsible_ids(user, column, user2):
    data = {
        'title': 'Test',
        'column': column.id,
        'position': 1,
        'creator': user.id,
        'responsible_ids': [user2.id]
    }
    serializer = TaskSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    task = serializer.save(creator=user, column=column)  # передаём обязательные поля
    task.refresh_from_db()
    assert user2 in task.responsible.all()