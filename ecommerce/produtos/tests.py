from django.test import TestCase
import pytest
from django.urls import reverse
from decimal import Decimal
from produtos.models import Produto, Categoria
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.

# Testes Unitários
@pytest.mark.unit
class TestProdutoModel:
    """Testes unitários para o modelo Produto"""
    
    @pytest.fixture
    def categoria(self, db):
        return Categoria.objects.create(nome="Eletrônicos")
    
    @pytest.fixture
    def produto_sem_desconto(self, db, categoria):
        return Produto.objects.create(
            nome="Produto Teste",
            preco=Decimal('100.00'),
            categoria=categoria,
            imagem=SimpleUploadedFile("test_image.jpg", b"file_content"),
            discount=0
        )
    
    @pytest.fixture
    def produto_com_desconto(self, db, categoria):
        return Produto.objects.create(
            nome="Produto com Desconto",
            preco=Decimal('200.00'),
            categoria=categoria,
            imagem=SimpleUploadedFile("discount_image.jpg", b"file_content"),
            discount=10
        )
    
    def test_produto_creation(self, produto_sem_desconto, categoria):
        """Testa se a criação de produto funciona corretamente"""
        assert produto_sem_desconto.nome == "Produto Teste"
        assert produto_sem_desconto.preco == Decimal('100.00')
        assert produto_sem_desconto.categoria == categoria
    
    def test_produto_str_method(self, produto_sem_desconto):
        """Testa se o método __str__ retorna o nome do produto"""
        assert str(produto_sem_desconto) == "Produto Teste"
    
    def test_discounted_price_without_discount(self, produto_sem_desconto):
        """Testa se o preço com desconto é igual ao preço quando não há desconto"""
        assert produto_sem_desconto.discounted_price() == Decimal('100.00')
    
    def test_discounted_price_with_discount(self, produto_com_desconto):
        """Testa se o cálculo do preço com desconto está correto"""
        # 200 - 10% = 180
        assert produto_com_desconto.discounted_price() == Decimal('180.00')

@pytest.mark.unit
class TestCategoriaModel:
    """Testes unitários para o modelo Categoria"""
    
    @pytest.fixture
    def categoria(self, db):
        return Categoria.objects.create(nome="Roupas")
    
    def test_categoria_creation(self, categoria):
        """Testa se a criação de categoria funciona corretamente"""
        assert categoria.nome == "Roupas"
    
    def test_categoria_str_method(self, categoria):
        """Testa se o método __str__ retorna o nome da categoria"""
        assert str(categoria) == "Roupas"

# Testes de Integração
@pytest.mark.integration
class TestProdutoViews:
    """Testes de integração para as views de produto"""
    
    @pytest.fixture
    def categoria(self, db):
        return Categoria.objects.create(nome="Roupa")
    
    @pytest.fixture
    def produto(self, db, categoria):
        return Produto.objects.create(
            nome="Camisa Teste",
            preco=Decimal('50.00'),
            categoria=categoria,
            imagem=SimpleUploadedFile("test_image.jpg", b"file_content")
        )
    
    def test_home_view(self, client, produto):
        """Testa se a HomeView retorna código 200 e usa o template correto"""
        response = client.get(reverse('produtos:listar_produtos'))
        assert response.status_code == 200
        assert 'listar_produtos.html' in [t.name for t in response.templates]
        assert 'produtos_recentes' in response.context
        assert 'roupas' in response.context
    
    def test_produto_detail_view(self, client, produto):
        """Testa se o detalhe do produto retorna código 200 e usa o template correto"""
        response = client.get(reverse('produtos:detalhar_produto', args=[produto.id]))
        assert response.status_code == 200
        assert 'detalhar_produto.html' in [t.name for t in response.templates]
        assert response.context['produto'] == produto
    
    @pytest.mark.django_db
    def test_nonexistent_produto_detail(self, client):
        """Testa se o detalhe de um produto inexistente retorna 404"""
        response = client.get(reverse('produtos:detalhar_produto', args=[9999]))
        assert response.status_code == 404

# Testes de Regressão
@pytest.mark.regression
class TestProdutoRegression:
    """Testes de regressão para verificar comportamentos específicos"""
    
    @pytest.fixture
    def categoria(self, db):
        return Categoria.objects.create(nome="Teste")
    
    @pytest.fixture
    def produto(self, db, categoria):
        return Produto.objects.create(
            nome="Produto Regressão",
            preco=Decimal('150.00'),
            categoria=categoria,
            imagem=SimpleUploadedFile("test_image.jpg", b"file_content"),
            discount=5
        )
    
    def test_discount_rounding(self, produto):
        """Testa se o arredondamento do desconto está correto"""
        # 150 - 5% = 142.5 -> 142.50
        assert produto.discounted_price() == Decimal('142.50')
    
    def test_zero_price_handling(self, produto):
        """Testa o tratamento de preço zero"""
        produto.preco = Decimal('0.00')
        produto.save()
        assert produto.discounted_price() == Decimal('0.00')
    
    def test_large_discount_handling(self, produto):
        """Testa o tratamento de desconto grande"""
        produto.discount = Decimal('99.99')
        produto.save()
        # 150 - 99.99% = 0.015 -> 0.02
        discounted = produto.discounted_price()
        assert discounted < Decimal('0.03')

# Testes de Carga (Simulados)
@pytest.mark.performance
class TestProdutoLoad:
    """Simulação de testes de carga para produtos"""
    
    @pytest.fixture
    def categoria(self, db):
        return Categoria.objects.create(nome="Carga")
    
    @pytest.fixture
    def produtos(self, db, categoria):
        produtos = []
        for i in range(10):
            produto = Produto.objects.create(
                nome=f"Produto {i}",
                preco=Decimal(i * 10),
                categoria=categoria,
                imagem=SimpleUploadedFile(f"test_image_{i}.jpg", b"file_content")
            )
            produtos.append(produto)
        return produtos
    
    def test_list_many_products(self, client, produtos):
        """Testa se a listagem de muitos produtos funciona corretamente"""
        response = client.get(reverse('produtos:listar_produtos'))
        assert response.status_code == 200
        # Verificar que temos os produtos recentes no contexto
        assert len(response.context['produtos_recentes']) == 4
