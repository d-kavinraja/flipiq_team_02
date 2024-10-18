from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from flipkart_app import views

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # Home Page
    path('', views.HomeView.as_view(), name='home'),  # Class-based view for the homepage (product list)

    # Product Listings and Detail Views
    path('products/', views.product_list, name='product_list'),  # Product list page with filtering
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),  # Product detail page

    # Cart Management
    path('cart/', views.cart_detail, name='cart'),  # View the cart
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),  # Add a product to the cart
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),  # Update cart (e.g., change quantity)

    # Checkout Process
    path('checkout/', views.checkout, name='checkout'),  # Checkout page
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),  # Order confirmation

    # User Profile and Order History
    path('user_profile/', views.profile, name='profile'),  # User profile management
    path('order-history/', views.order_history, name='order_history'),  # View past orders

    # User Authentication (Login, Register, Logout)
    path('login/', views.user_login, name='login'),  # User login
    path('register/', views.user_register, name='register'),  # User registration
    path('logout/', views.user_logout, name='logout'),  # User logout

    # Seller Dashboard
    path('seller-dashboard/', views.seller_dashboard, name='seller_dashboard'),  # Seller dashboard page

    # Wishlist Management
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    # Wishlist page
    path('wishlist/', views.wishlist, name='wishlist'),
    path('track-order/<int:order_id>/', views.track_order, name='track_order'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),



    # Static and Media Files (for media uploads like product images)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

