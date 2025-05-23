# orders/models.py
from django.db import models
from shops.models import Shop
from users.models import Customer
from products.models import Species, Product

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    outlet = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    total_calories = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Order {self.id} by {self.customer.user.username}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    species = models.ForeignKey(Species, on_delete=models.SET_NULL, null=True, blank=True)  # Added this line
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        species_name = self.species.name if self.species else "No Species"
        return f"{self.quantity} x {self.product.name} ({species_name})"

    @property
    def total_price(self):
        return self.product.price * self.quantity

    @property
    def total_calories(self):
        return self.product.calories_per_100g * self.quantity

    class Meta:
        unique_together = ('order', 'product', 'species')  # Ensures unique product-species combinations