from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, CartItem, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def shop_view(request):
    # Fetch all products from the database
    products = Product.objects.all()

    context = {
        'products': products
    }
    return render(request, 'shop.html', context)

# --- ADD THIS NEW VIEW ---
@login_required(login_url='login')
def add_to_cart_view(request, product_pk):
    # 1. Get the product the user wants to add
    product = get_object_or_404(Product, pk=product_pk)
    
    # 2. Get (or create) the user's cart
    # We use request.user (from @login_required) to find their cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # 3. Check if the item is already in the cart
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        # If it is, just increase the quantity
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"Added another '{product.name}' to your cart.")
    except CartItem.DoesNotExist:
        # If it's not, create a new cart item
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        messages.success(request, f"Added '{product.name}' to your cart.")
    
    # 4. Send the user back to the shop page
    return redirect('shop')

@login_required(login_url='login')
def cart_view(request):
    # Get the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Get all items in that cart
    cart_items = cart.items.all()

    # Calculate the total price
    total_price = 0
    for item in cart_items:
        total_price += item.get_total_price()

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'cart.html', context)

@login_required(login_url='login')
def remove_from_cart_view(request, item_pk):
    # Get the specific cart item by its ID
    cart_item = get_object_or_404(CartItem, pk=item_pk)
    
    # Security check: Ensure the item belongs to the logged-in user's cart
    if cart_item.cart.user == request.user:
        cart_item.delete()
        messages.success(request, f"Removed '{cart_item.product.name}' from your cart.")
    else:
        messages.error(request, "You are not authorized to remove this item.")
    
    # Send the user back to their cart
    return redirect('cart')

@login_required(login_url='login')
def checkout_view(request):
    # Get the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items:
        # Don't let them checkout an empty cart
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    # Calculate the total price
    total_price = 0
    for item in cart_items:
        total_price += item.get_total_price()
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'checkout.html', context)

@login_required(login_url='login')
def checkout_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    # Calculate total price
    total_price = sum(item.get_total_price() for item in cart_items)
    
    # This is the "Place Order" logic
    if request.method == 'POST':
        try:
            # 1. Get the address from the patient's profile
            shipping_address = request.user.patient.address
            if not shipping_address:
                messages.error(request, "Please add an address to your profile before placing an order.")
                return redirect('profile')

            # 2. Create the Order
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                shipping_address=shipping_address,
                status='Processing'
            )

            # 3. Create OrderItems from CartItems
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price  # Lock in the price
                )

            # 4. Clear the cart
            cart_items.delete()
            
            messages.success(request, "Your order has been placed successfully!")
            return redirect('shop') # Or a "My Orders" page, which we'll make next
            
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('checkout')

    # This is the GET request logic (show the summary)
    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'checkout.html', context)

@login_required(login_url='login')
def my_orders_view(request):
    # Get all orders for the current user, with the newest one first
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders
    }
    return render(request, 'my_orders.html', context)

@login_required(login_url='login')
def order_details_view(request, order_pk):
    # Get the specific order or show 404
    order = get_object_or_404(Order, pk=order_pk)
    
    # Security Check: Ensure the logged-in user owns this order
    if order.user != request.user:
        messages.error(request, 'You are not authorized to view this order.')
        return redirect('my_orders')

    # Get all items related to this order
    order_items = OrderItem.objects.filter(order=order)
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'order_details.html', context)