from django.test import TestCase
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from clientes.forms import UserCreateForm

User = get_user_model()

# Create your tests here.

# Testes Unitários
@pytest.mark.unit
class TestUserModel:
    """Testes unitários para o modelo User"""
    
    @pytest.fixture
    def test_user(self, db):
        return User.objects.create_user(
            email='test@example.com',
            password='testpassword'
        )
    
    @pytest.fixture
    def admin_user(self, db):
        return User.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword'
        )
    
    def test_create_user(self, test_user):
        """Testa se a criação de usuário funciona corretamente"""
        assert test_user.email == 'test@example.com'
        assert test_user.is_active is True
        assert test_user.is_admin is False
        assert test_user.is_staff is False
    
    def test_create_superuser(self, admin_user):
        """Testa se a criação de superusuário funciona corretamente"""
        assert admin_user.email == 'admin@example.com'
        assert admin_user.is_active is True
        assert admin_user.is_admin is True
        assert admin_user.is_staff is True
        
    def test_user_str_method(self, test_user):
        """Testa se o método __str__ retorna o email do usuário"""
        assert str(test_user) == 'test@example.com'
        
    def test_user_has_perm(self, test_user):
        """Testa se o método has_perm funciona corretamente"""
        assert test_user.has_perm('any_perm') is True
        
    def test_user_has_module_perms(self, test_user):
        """Testa se o método has_module_perms funciona corretamente"""
        assert test_user.has_module_perms('any_app') is True

@pytest.mark.unit
class TestUserForm:
    """Testes unitários para o formulário de criação de usuário"""
    
    @pytest.mark.django_db
    def test_valid_user_form(self):
        """Testa se o formulário válido é aceito"""
        form_data = {
            'email': 'new@example.com',
            'password': 'newpassword'
        }
        form = UserCreateForm(data=form_data)
        assert form.is_valid() is True
    
    def test_invalid_email_form(self):
        """Testa se o formulário com email inválido é rejeitado"""
        form_data = {
            'email': 'invalid-email',
            'password': 'password'
        }
        form = UserCreateForm(data=form_data)
        assert form.is_valid() is False

# Testes de Integração
@pytest.mark.integration
class TestUserViews:
    """Testes de integração para as views de usuário"""
    
    @pytest.fixture
    def test_user(self, db):
        return User.objects.create_user(
            email='test@example.com',
            password='testpassword'
        )
    
    def test_login_view_get(self, client):
        """Testa se a página de login é carregada corretamente"""
        response = client.get(reverse('clientes:login'))
        assert response.status_code == 200
        assert 'login.html' in [t.name for t in response.templates]
    
    def test_login_success(self, client, test_user):
        """Testa se o login é bem-sucedido com credenciais corretas"""
        response = client.post(reverse('clientes:login'), {
            'username': 'test@example.com',
            'password': 'testpassword'
        })
        assert response.status_code == 302
        assert response.url == '/'
    
    def test_login_failure(self, client, test_user):
        """Testa se o login falha com credenciais incorretas"""
        response = client.post(reverse('clientes:login'), {
            'username': 'test@example.com',
            'password': 'wrongpassword'
        })
        assert response.status_code == 200  # Permanece na página de login
    
    def test_logout(self, client, test_user):
        """Testa se o logout funciona corretamente"""
        client.login(username='test@example.com', password='testpassword')
        response = client.post(reverse('clientes:logout'))
        assert response.status_code == 302
        assert response.url == '/'
    
    def test_create_user_view(self, client):
        """Testa se a view de criação de usuário funciona corretamente"""
        response = client.get(reverse('clientes:criar_cliente'))
        assert response.status_code == 200
        assert 'criar_cliente.html' in [t.name for t in response.templates]
    
    def test_update_user_protected(self, client, test_user):
        """Testa se a view de atualização de usuário requer login"""
        response = client.get(reverse('clientes:atualizar_cliente', args=[test_user.pk]))
        assert response.status_code == 302  # Redireciona para página de login
        assert '/clientes/entrar/' in response.url

# Testes de Regressão
@pytest.mark.regression
class TestUserRegression:
    """Testes de regressão para verificar comportamentos específicos"""
    
    @pytest.fixture
    def test_user(self, db):
        return User.objects.create_user(
            email='test@example.com',
            password='testpassword'
        )
    
    def test_get_user_by_email(self, test_user):
        """Testa se é possível recuperar um usuário pelo email"""
        retrieved_user = User.objects.get(email='test@example.com')
        assert retrieved_user == test_user
    
    def test_email_normalized(self, db):
        """Testa se o email é normalizado durante a criação"""
        mixed_case_user = User.objects.create_user(
            email='MiXeD@ExAmPle.CoM',
            password='password'
        )
        assert mixed_case_user.email == 'MiXeD@example.com'
    
    def test_create_user_without_email_fails(self, db):
        """Testa se a criação de usuário sem email falha"""
        with pytest.raises(ValueError):
            User.objects.create_user(email='', password='password')
