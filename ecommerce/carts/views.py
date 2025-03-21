from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Cart, Order
from produtos.models import Produto

class CartDetailView(LoginRequiredMixin, DetailView):
    model = Cart
    template_name = 'cart.html'
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if not product_id:
            messages.error(request, "Produto não especificado")
            return redirect('produtos:listar_produtos')
            
        product = get_object_or_404(Produto, id=product_id)
        
        # Obter ou criar um carrinho para o usuário
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Verificar se o produto já está no carrinho
        order, order_created = Order.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        # Se o produto já existir, atualizar a quantidade
        if not order_created:
            order.quantity += quantity
            order.save()
            
        messages.success(request, f"{product.nome} adicionado ao carrinho!")
        return redirect('carts:cart_detail', pk=cart.pk)
