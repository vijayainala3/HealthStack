from django.db import models
from accounts.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories" # Fixes "Categorys" in admin

class Product(models.Model):
    # Link to Category
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    # Product Details
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    
    # We can add an image later
    # image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return self.name

# --- ADD THIS MODEL ---
class Cart(models.Model):
    # Link to the user who owns this cart
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

# --- ADD THIS MODEL ---
class CartItem(models.Model):
    # Link to the specific cart
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    # Link to the specific product
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # Quantity of this product
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s cart"
    
    # This function calculates the total price for this item
    def get_total_price(self):
        return self.product.price * self.quantity

# --- ADD THIS MODEL ---
class Order(models.Model):
    STATUS_CHOICES = (
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    # Link to the user who placed the order
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Store the details at the time of order
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Processing')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} for {self.user.username}"

# --- ADD THIS MODEL ---
class OrderItem(models.Model):
    # Link to the specific order
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    # Link to the product
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    
    # Store the price and quantity at the time of order
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price at time of purchase

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for Order {self.order.id}"