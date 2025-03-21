from django.db import models
from produtos.models import Produto
from clientes.models import User
from decimal import Decimal

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    
    def __str__(self):
        return f"Carrinho de {self.user.email}"
    
    def total(self):
        """Calcula o total de todos os itens no carrinho"""
        return sum(order.total() for order in self.order_set.all())

class Order(models.Model):
    product = models.ForeignKey(Produto, on_delete=models.PROTECT)
    cart = models.ForeignKey(Cart, on_delete=models.PROTECT)
    
    quantity = models.IntegerField()
    
    def __str__(self):
        return f"{self.quantity} x {self.product.nome}"
    
    def total(self):
        return self.quantity * self.product.discounted_price()
