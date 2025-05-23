from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Customer
from .forms import CustomerProfileForm
from shops.models import Shop
from products.models import Product
from cart.models import Cart

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if not hasattr(user, 'customer'):
                Customer.objects.create(user=user)
            login(request, user)
            return redirect('customer_dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('customer_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def customer_logout(request):
    logout(request)
    return redirect('index')

def index(request):
    """New view for the root URL"""
    return render(request, 'blank_layout.html')

@login_required
def customer_dashboard(request):
    selected_location = request.GET.get('location')
    
    if selected_location:
        shops = Shop.objects.filter(location=selected_location)
    else:
        shops = Shop.objects.all()

    locations = Shop.objects.values_list('location', flat=True).distinct()

    if request.method == 'POST':
        profile_form = CustomerProfileForm(request.POST, request.FILES, instance=request.user.customer)
        if profile_form.is_valid():
            profile_form.save()
    else:
        profile_form = CustomerProfileForm(instance=request.user.customer)

    return render(request, 'users/dashboard.html', {
        'shops': shops,
        'locations': locations,
        'selected_location': selected_location,
        'profile_form': profile_form,
    })

@login_required
def customer_profile(request):
    customer = request.user.customer
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_profile')
    else:
        form = CustomerProfileForm(instance=customer)
    
    return render(request, 'users/profile.html', {
        'form': form,
        'customer': customer
    })

@login_required
def shop_products(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    products = Product.objects.filter(outlet=shop)
    
    cart, created = Cart.objects.get_or_create(customer=request.user.customer, outlet=shop)
    
    total_calories = cart.total_calories
    calorie_limit = cart.calorie_limit
    total_calories_percentage = (total_calories / calorie_limit) * 100 if calorie_limit > 0 else 0
    
    return render(request, 'users/shop_products.html', {
        'shop': shop,
        'products': products,
        'cart': cart,
        'total_calories_percentage': total_calories_percentage,
    })