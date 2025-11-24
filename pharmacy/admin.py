from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem # <-- Import Cart, CartItem

# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)         # <-- Add this line
admin.site.register(CartItem)     # <-- Add this line
admin.site.register(Order)         # <-- Add this line
admin.site.register(OrderItem)     # <-- Add this line