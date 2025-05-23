from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from shops.models import Shop
from .models import Cart, CartItem
from orders.models import Order, OrderItem

# views.py
# views.py
@login_required
def view_cart(request):
    # Fetch all carts for the current customer that have items
    carts = Cart.objects.filter(
        customer=request.user.customer
    ).exclude(
        items__isnull=True
    ).select_related(
        'outlet'
    ).prefetch_related(
        'items__product__species'
    )
    return render(request, 'cart/cart.html', {'carts': carts})


from django.http import JsonResponse

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    outlet = product.outlet
    cart, created = Cart.objects.get_or_create(customer=request.user.customer, outlet=outlet)
    
    action = request.POST.get("action")
    species_id = request.POST.get("species_id")
    
    if action == "increase":
        total_calories = cart.total_calories + product.calories_per_100g
        if total_calories > cart.calorie_limit:
            return JsonResponse({
                "success": False,
                "message": f"Adding this product will exceed your calorie limit of {cart.calorie_limit} kcal."
            })

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            species_id=species_id if species_id else None
        )
        if not created:
            cart_item.quantity += 1
        cart_item.save()
        
        return JsonResponse({
            "success": True,
            "total_calories": cart.total_calories,
            "new_quantity": cart_item.quantity
        })
        
    elif action == "decrease":
        cart_item = CartItem.objects.filter(
            cart=cart,
            product=product,
            species_id=species_id if species_id else None
        ).first()
        
        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                new_quantity = cart_item.quantity
            else:
                cart_item.delete()
                new_quantity = 0
                
            return JsonResponse({
                "success": True,
                "total_calories": cart.total_calories,
                "new_quantity": new_quantity
            })
            
    return JsonResponse({"success": False, "message": "Invalid action"})

@login_required
def check_calorie_bucket(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    cart = get_object_or_404(Cart, customer=request.user.customer, outlet=shop)

    if cart.total_calories >= cart.calorie_limit:
        return redirect('view_cart')
    else:
        messages.error(request, "Your calorie bucket is not full yet.")
        return redirect('shop_products', shop_id=shop.id)



@login_required
def update_quantity(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__customer=request.user.customer)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1
        cart_item.save()
    return redirect('view_cart')

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__customer=request.user.customer)
    cart_item.delete()
    return redirect('view_cart')

@login_required
def place_order(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id, customer=request.user.customer)

    # Check if the total calories exceed the limit
    if cart.total_calories > 10000:  # Updated calorie limit to 10,000 kcal
        messages.error(request, "Your calorie bucket exceeds the limit of 10,000 kcal. Remove some items to proceed.")
        return redirect('view_cart')

    # Check if the cart is empty
    if cart.items.count() == 0:
        messages.error(request, "Your cart is empty. Add items to proceed.")
        return redirect('view_cart')

    # Create the order
    order = Order.objects.create(
        customer=request.user.customer,
        outlet=cart.outlet,
        total_calories=cart.total_calories
    )

    # Add cart items to the order
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            species=cart_item.species,  # Copy the species from cart item
            quantity=cart_item.quantity
        )

    # Delete the cart after placing the order
    cart.delete()

    messages.success(request, "Order placed successfully.")
    return redirect('order_success')