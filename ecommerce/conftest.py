import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

@pytest.fixture
def common_image():
    """Fixture para criar uma imagem para uso em testes"""
    return SimpleUploadedFile(
        "test_image.jpg",
        b"file_content",
        content_type="image/jpeg"
    )

@pytest.fixture
def common_user(db):
    """Fixture para criar um usuário comum para testes"""
    return User.objects.create_user(
        email='testuser@example.com',
        password='password123'
    )

@pytest.fixture
def admin_user(db):
    """Fixture para criar um usuário administrador para testes"""
    return User.objects.create_superuser(
        email='admin@example.com',
        password='admin123'
    )

@pytest.fixture
def authenticated_client(client, common_user):
    """Fixture para criar um cliente autenticado com usuário comum"""
    client.login(email='testuser@example.com', password='password123')
    return client

@pytest.fixture
def admin_client(client, admin_user):
    """Fixture para criar um cliente autenticado com usuário administrador"""
    client.login(email='admin@example.com', password='admin123')
    return client 