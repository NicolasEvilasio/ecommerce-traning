from django.test import TestCase
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from carts.models import Cart, Order
from produtos.models import Produto, Categoria
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

# Testes Unitários
@pytest.mark.unit
class TestCartModel:
    """Testes unitários para o modelo Cart"""
    
    @pytest.fixture
    def test_user(self, db):
        return User.objects.create_user(
            email='cart_test@example.com',
            password='testpassword'
        )
    
    @pytest.fixture
    def cart(self, db, test_user):
        return Cart.objects.create(user=test_user)
    
    def test_cart_creation(self, cart, test_user):
        """Testa se a criação de carrinho funciona corretamente"""
        assert cart.user == test_user
    
    def test_cart_str_method(self, cart, test_user):
        """Testa se o método __str__ do carrinho retorna o texto esperado"""
        assert str(cart) == f"Carrinho de {test_user.email}"

@pytest.mark.unit
class TestOrderModel:
    """Testes unitários para o modelo Order"""
    
    @pytest.fixture
    def test_user(self, db):
        return User.objects.create_user(
            email='order_test@example.com',
            password='testpassword'
        )
    
    @pytest.fixture
    def cart(self, db, test_user):
        return Cart.objects.create(user=test_user)
    
    @pytest.fixture
    def categoria(self, db):
        return Categoria.objects.create(nome="Teste")
    
    @pytest.fixture
    def produto(self, db, categoria):
        return Produto.objects.create(
            nome="Produto Teste",
            preco=Decimal('100.00'),
            categoria=categoria,
            imagem=SimpleUploadedFile("test_image.jpg", b"file_content")
        )
    
    @pytest.fixture
    def order(self, db, produto, cart):
        return Order.objects.create(
            product=produto,
            cart=cart,
            quantity=2
        )
    
    def test_order_creation(self, order, produto, cart):
        """Testa se a criação de ordem funciona corretamente"""
        assert order.product == produto
        assert order.cart == cart
        assert order.quantity == 2
    
    def test_order_str_method(self, order, produto):
        """Testa se o método __str__ da ordem retorna o texto esperado"""
        assert str(order) == f"2 x {produto.nome}"
    
    def test_order_total(self, order, produto):
        """Testa se o cálculo do total da ordem está correto"""
        expected_total = produto.preco * order.quantity
        assert order.total() == expected_total
    
    def test_order_with_discounted_product(self, order, produto):
        """Testa o cálculo do total com produto com desconto"""
        produto.discount = 10
        produto.save()
        expected_total = produto.discounted_price() * order.quantity
        assert order.total() == expected_total

# Testes de Integração
@pytest.mark.integration
class TestCartViews:
    """Testes de integração para as views de carrinho"""
    
    @pytest.fixture
    def test_user(self, db):
        return User.objects.create_user(
            email='cart_view@example.com',
            password='testpassword'
        )
    
    @pytest.fixture
    def cart(self, db, test_user):
        return Cart.objects.create(user=test_user)
    
    @pytest.fixture
    def categoria(self, db):
        return Categoria.objects.create(nome="Teste")
    
    @pytest.fixture
    def produto(self, db, categoria):
        return Produto.objects.create(
            nome="Produto Teste",
            preco=Decimal('100.00'),
            categoria=categoria,
            imagem=SimpleUploadedFile("test_image.jpg", b"file_content")
        )
    
    def test_cart_detail_view_requires_login(self, client, cart):
        """Testa se a visualização do carrinho requer login"""
        response = client.get(reverse('carts:cart_detail', args=[cart.pk]))
        assert response.status_code == 302  # Redireciona para login
    
    def test_cart_detail_view_with_login(self, client, cart, test_user):
        """Testa se a visualização do carrinho funciona com login"""
        client.login(email='cart_view@example.com', password='testpassword')
        response = client.get(reverse('carts:cart_detail', args=[cart.pk]))
        assert response.status_code == 200
        assert 'cart.html' in [t.name for t in response.templates]
    
    def test_add_to_cart_requires_login(self, client, produto):
        """Testa se a adição ao carrinho requer login"""
        response = client.post(reverse('carts:add_to_cart'), {
            'product_id': produto.id,
            'quantity': 1
        })
        assert response.status_code == 302  # Redireciona para login
    
    def test_add_to_cart_with_login(self, client, produto, test_user, cart):
        """Testa se a adição ao carrinho funciona com login"""
        client.login(email='cart_view@example.com', password='testpassword')
        response = client.post(reverse('carts:add_to_cart'), {
            'product_id': produto.id,
            'quantity': 3
        })
        assert response.status_code == 302  # Redireciona para cart_detail
        
        # Verifica se o produto foi adicionado ao carrinho
        order = Order.objects.filter(cart=cart, product=produto).first()
        assert order is not None
        assert order.quantity == 3
    
    def test_add_same_product_twice(self, client, produto, test_user, cart):
        """Testa a adição do mesmo produto duas vezes ao carrinho"""
        client.login(email='cart_view@example.com', password='testpassword')
        
        # Primeira adição
        client.post(reverse('carts:add_to_cart'), {
            'product_id': produto.id,
            'quantity': 2
        })
        
        # Segunda adição
        client.post(reverse('carts:add_to_cart'), {
            'product_id': produto.id,
            'quantity': 3
        })
        
        # Verifica se as quantidades foram somadas
        order = Order.objects.get(cart=cart, product=produto)
        assert order.quantity == 5

# Testes de Regressão
@pytest.mark.regression
class TestCartRegression:
    """Testes de regressão para verificar comportamentos específicos do carrinho"""
    
    @pytest.fixture
    def test_user(self, db):
        return User.objects.create_user(
            email='regression@example.com',
            password='testpassword'
        )
    
    @pytest.fixture
    def cart(self, db, test_user):
        return Cart.objects.create(user=test_user)
    
    @pytest.fixture
    def categoria(self, db):
        return Categoria.objects.create(nome="Teste")
    
    @pytest.fixture
    def produto1(self, db, categoria):
        return Produto.objects.create(
            nome="Produto 1",
            preco=Decimal('50.00'),
            categoria=categoria,
            imagem=SimpleUploadedFile("test_image1.jpg", b"file_content")
        )
    
    @pytest.fixture
    def produto2(self, db, categoria):
        return Produto.objects.create(
            nome="Produto 2",
            preco=Decimal('30.00'),
            categoria=categoria,
            imagem=SimpleUploadedFile("test_image2.jpg", b"file_content"),
            discount=20
        )
    
    @pytest.fixture
    def orders(self, db, produto1, produto2, cart):
        order1 = Order.objects.create(
            product=produto1,
            cart=cart,
            quantity=2
        )
        order2 = Order.objects.create(
            product=produto2,
            cart=cart,
            quantity=1
        )
        return [order1, order2]
    
    def test_multiple_products_in_cart(self, orders, cart):
        """Testa se o carrinho pode conter múltiplos produtos"""
        cart_orders = Order.objects.filter(cart=cart)
        assert cart_orders.count() == 2
    
    def test_total_cart_calculation(self, orders, cart):
        """Testa o cálculo do total do carrinho (função adicional)"""
        # Produto 1: 50 * 2 = 100
        # Produto 2: 30 - 20% = 24 * 1 = 24
        # Total: 124
        total = sum(order.total() for order in Order.objects.filter(cart=cart))
        assert total == Decimal('124.00')
    
    def test_other_user_cannot_see_cart(self, client, cart, db):
        """Testa que um usuário não pode ver o carrinho de outro"""
        other_user = User.objects.create_user(
            email='other@example.com',
            password='testpassword'
        )
        client.login(email='other@example.com', password='testpassword')
        response = client.get(reverse('carts:cart_detail', args=[cart.pk]))
        assert response.status_code == 404  # Não encontrado
