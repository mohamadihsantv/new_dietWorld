from django.db import models
from shops.models import Shop
from users.models import Customer
from products.models import Species  # Make sure to import Species

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    outlet = models.ForeignKey(Shop, on_delete=models.CASCADE)
    calorie_limit = models.PositiveIntegerField(default=10000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.outlet.shop_name} by {self.customer.user.username}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    @property
    def total_calories(self):
        return sum(item.product.calories_per_100g * item.quantity for item in self.items.all())

    def is_within_calorie_limit(self):
        return self.total_calories <= self.calorie_limit

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    species = models.ForeignKey(Species, on_delete=models.SET_NULL, null=True, blank=True)  # Add this line
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
        unique_together = ('cart', 'product', 'species')  # Ensure unique product-species combinations