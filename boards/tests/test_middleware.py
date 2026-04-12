import pytest
from django.test import RequestFactory
from django.http import HttpResponseRedirect
from ..middleware import FixReactPathsMiddleware

class TestFixReactPathsMiddleware:
    
    def setup_method(self):
        self.factory = RequestFactory()
        self.middleware = FixReactPathsMiddleware(lambda req: None)
    
    def test_redirects_boards_media_path(self):
        """Должен редиректить /boards/boards/1/static/frontend/static/static/media/..."""
        request = self.factory.get('/boards/boards/1/static/frontend/static/static/media/image.jpg')
        response = self.middleware(request)
        
        assert isinstance(response, HttpResponseRedirect)
        assert response.url == '/static/media/image.jpg'
    
    def test_redirects_frontend_media_path(self):
        """Должен редиректить /static/frontend/static/static/media/..."""
        request = self.factory.get('/static/frontend/static/static/media/image.jpg')
        response = self.middleware(request)
        
        assert isinstance(response, HttpResponseRedirect)
        assert response.url == '/static/media/image.jpg'
    
    def test_redirects_double_static_media_path(self):
        """Должен редиректить /static/static/media/..."""
        request = self.factory.get('/static/static/media/image.jpg')
        response = self.middleware(request)
        
        assert isinstance(response, HttpResponseRedirect)
        assert response.url == '/static/media/image.jpg'
    
    def test_redirects_boards_static_path(self):
        """Должен редиректить /boards/boards/1/static/css/style.css"""
        request = self.factory.get('/boards/boards/1/static/css/style.css')
        response = self.middleware(request)
        
        assert isinstance(response, HttpResponseRedirect)
        assert response.url == '/static/css/style.css'
    
    def test_ignores_normal_paths(self):
        """Не должен трогать нормальные пути."""
        request = self.factory.get('/boards/1/')
        response = self.middleware(request)
        
        assert response is None  # middleware пропустил запрос дальше
    
    def test_ignores_api_paths(self):
        """Не должен трогать API пути."""
        request = self.factory.get('/api/boards/1/')
        response = self.middleware(request)
        
        assert response is None
    
    def test_multiple_redirects_not_needed(self):
        """После редиректа путь должен быть чистым."""
        request = self.factory.get('/boards/boards/1/static/frontend/static/static/media/image.jpg')
        response = self.middleware(request)
        
        # После редиректа паттерн не должен снова сработать
        second_request = self.factory.get(response.url)
        second_response = self.middleware(second_request)
        
        assert second_response is None
        
    @pytest.mark.parametrize('old_path, expected_new_path', [
    ('/boards/boards/1/static/frontend/static/static/media/image.jpg', 
     '/static/media/image.jpg'),
    ('/static/frontend/static/static/media/image.png', 
     '/static/media/image.png'),
    ('/static/static/media/image.gif', 
     '/static/media/image.gif'),
    ('/boards/boards/1/static/js/app.js', 
     '/static/js/app.js'),
    ('/boards/boards/42/static/css/style.css', 
     '/static/css/style.css'),
    ])
    
    def test_redirect_patterns(self, old_path, expected_new_path):
        request = self.factory.get(old_path)
        response = self.middleware(request)
        
        assert isinstance(response, HttpResponseRedirect)
        assert response.url == expected_new_path