from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import login, logout, authenticate
from django.views.generic import ListView, DetailView
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Review, Seller, WishlistItem, UserProfile, User
from django.http import JsonResponse

class HomeView(ListView):
    model = Product
    template_name = 'flipkart_app/home.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(stock__gt=0)
        category = self.request.GET.get('category')
        search = self.request.GET.get('search')
        if category:
            queryset = queryset.filter(category__name=category)
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'flipkart_app/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = Product.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:4]
        context['reviews'] = Review.objects.filter(product=self.object)
        return context

def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        user_type = request.POST.get('user_type')  

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already in use.')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.is_customer = True if user_type == 'customer' else False
        user.is_seller = True if user_type == 'seller' else False
        user.save()

        user_profile = UserProfile.objects.create(
            user=user,
            phone_number=phone_number,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            user_type=user_type
        )

        if user_type == 'seller':
            Seller.objects.create(user_profile=user_profile, is_verified=False)

        messages.success(request, 'Registration successful! You can now log in.')
        return redirect('login')

    return render(request, 'flipkart_app/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_seller:
                return redirect('seller_dashboard') 
            else:
                return redirect('home') 
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')

    return render(request, 'flipkart_app/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    if created:
        cart_items = []
    else:
        cart_items = cart.items.all()
        
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    
    return render(request, 'flipkart_app/cart.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'{product.name} added to cart.')
    return redirect('cart')

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    action = request.POST.get('action')

    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()  # Delete if quantity is 0 or less
        else:
            cart_item.save()  # Save the decreased quantity
    elif action == 'remove':
        cart_item.delete()  # Remove the cart item
    else:
        messages.error(request, 'Invalid action.')

    return redirect('cart')




@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    if cart.items.count() == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        phone_number = request.POST.get('phone_number')
        payment_method = request.POST.get('payment_method')
        if not shipping_address or not phone_number or not payment_method:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('checkout')
        
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            phone_number=phone_number,
            payment_method=payment_method,
            total_amount=cart.get_total()
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.discounted_price(),
            )

        cart.items.all().delete()

        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'flipkart_app/checkout.html', {'cart': cart})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'flipkart_app/order_confirmation.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'flipkart_app/order_history.html', {'orders': orders})

@login_required
def profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')

        if phone_number and address and city and state and pincode:
            profile.phone_number = phone_number
            profile.address = address
            profile.city = city
            profile.state = state
            profile.pincode = pincode
            profile.save()
            messages.success(request, 'Profile updated successfully.')
        else:
            messages.error(request, 'Please fill in all fields.')
    return render(request, 'flipkart_app/user_profile.html', {'profile': profile})

@login_required
def wishlist(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user)
    return render(request, 'flipkart_app/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    WishlistItem.objects.get_or_create(user=request.user, product=product)
    return JsonResponse({'added': True}, status=200)  # Valid JSON response

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    WishlistItem.objects.filter(user=request.user, product=product).delete()
    return JsonResponse({'removed': True}, status=200)  # Valid JSON response

@login_required
def seller_dashboard(request):
    if not request.user.is_seller:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home')

    seller = request.user.seller
    orders = Order.objects.filter(items__product__seller=seller).distinct()

    return render(request, 'flipkart_app/seller_dashboard.html', {'orders': orders})

def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured=True)  
    context = {
        'categories': categories,
        'featured_products': featured_products,
    }
    return render(request, 'flipkart_app/home.html', context)
from django.core.paginator import Paginator
def product_list(request):
    categories = Category.objects.all()

    selected_categories = request.GET.getlist('category')
    products = Product.objects.all()
    if selected_categories:
        products = products.filter(category__name__in=selected_categories)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort_by = request.GET.get('sort')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')

    paginator = Paginator(products, 9)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    query_string = request.GET.copy()
    if 'page' in query_string:
        query_string.pop('page')
    query_string = query_string.urlencode()

    context = {
        'categories': categories,
        'products': page_obj,
        'selected_categories': selected_categories,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'query_string': query_string
    }
    return render(request, 'flipkart_app/product_list.html', context)


def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'flipkart_app/track_order.html', context)

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ['delivered', 'cancelled']:
        messages.error(request, 'You cannot cancel a delivered or already cancelled order.')
    else:
        order.status = 'cancelled'
        order.save()
        messages.success(request, 'Your order has been cancelled.')

    return redirect('order_history')  