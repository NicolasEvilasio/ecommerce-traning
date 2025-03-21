import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings

# Testes Unitários
@pytest.mark.unit
class TestCoreConfig:
    """Testes unitários para configuração do core"""
    
    def test_secret_key_strength(self):
        """Verifica se a SECRET_KEY tem comprimento adequado"""
        assert len(settings.SECRET_KEY) >= 50
    
    def test_debug_setting(self):
        """Verifica se o DEBUG está configurado como um boolean"""
        assert isinstance(settings.DEBUG, bool)

# Testes de Integração
@pytest.mark.integration
class TestCoreURLs:
    """Testes de integração para as URLs do core"""
    
    def test_home_redirect(self, client):
        """Testa se a URL raiz redireciona para produtos"""
        response = client.get('/')
        assert response.status_code == 302
        assert response.url == '/produtos/'
    
    def test_admin_url(self, client):
        """Testa se a URL do admin está funcionando"""
        response = client.get('/admin/')
        assert response.status_code == 302  # Redireciona para login
        assert '/admin/login/' in response.url

# Testes de Sistema
@pytest.mark.system
class TestCoreSystem:
    """Testes de sistema para o core"""
    
    @pytest.fixture
    def admin_user(self, db):
        User = get_user_model()
        return User.objects.create_superuser(
            email='admin@teste.com',
            password='senha12345'
        )
    
    def test_admin_login(self, client, admin_user):
        """Testa se o login do admin funciona corretamente"""
        client.login(email='admin@teste.com', password='senha12345')
        response = client.get('/admin/')
        assert response.status_code == 200 