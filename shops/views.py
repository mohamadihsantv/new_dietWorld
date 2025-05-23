from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from orders.models import Order, OrderItem
from .models import Shop
from products.models import Product
from .forms import ProductForm  # Import the ProductForm

@login_required
def shop_dashboard(request):
    # Get the shop (outlet) owned by the logged-in user
    shop = get_object_or_404(Shop, shop_owner=request.user)
    
    # Filter products by the outlet (shop)
    products = Product.objects.filter(outlet=shop)
    
    return render(request, 'shops/dashboard.html', {'shop': shop, 'products': products})

@login_required
def shop_profile(request):
    shop = get_object_or_404(Shop, shop_owner=request.user)
    return render(request, 'shops/shop_profile.html', {'shop': shop})




# shops/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from shops.models import Shop
from orders.models import Order

@login_required
def shop_orders(request):
    shop = get_object_or_404(Shop, shop_owner=request.user)
    
    # Create a prefetch queryset for order items with species
    order_items = OrderItem.objects.select_related('product', 'species')
    
    orders = Order.objects.filter(outlet=shop).select_related(
        'customer__user',
        'outlet'
    ).prefetch_related(
        Prefetch('items', queryset=order_items)
    ).order_by('-created_at')
    
    return render(request, 'shops/order_list.html', {
        'orders': orders,
        'shop': shop
    })

# Shop Owner Login
def shop_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and hasattr(user, 'shop'):  # Check if the user is a shop owner
                login(request, user)
                return redirect('shop_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'shops/shop_login.html', {'form': form})

def shop_logout(request):
    logout(request)
    return render(request,'blank_layout.html')