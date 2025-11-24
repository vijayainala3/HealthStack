from django.urls import path
from . import views

urlpatterns = [
    path('shop/', views.shop_view, name='shop'),
    path('add-to-cart/<int:product_pk>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('remove-from-cart/<int:item_pk>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    path('order-details/<int:order_pk>/', views.order_details_view, name='order_details'),
]
