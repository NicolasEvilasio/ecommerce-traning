from django.urls import path
from .views import CartDetailView, AddToCartView

app_name = 'carts'

urlpatterns = [
    path('<int:pk>/', CartDetailView.as_view(), name="cart_detail"),
    path('adicionar/', AddToCartView.as_view(), name="add_to_cart"),
] 