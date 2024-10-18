from django.contrib import admin
from django.utils.html import format_html
from .models import (
    User, UserProfile, Customer, Seller, Category, Product, 
    Cart, CartItem, Order, OrderItem, Review, WishlistItem, Registration
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_customer', 'is_seller', 'is_active', 'is_staff')
    list_filter = ('is_customer', 'is_seller', 'is_active', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'phone_number', 'city', 'state', 'pincode')
    search_fields = ('user__username', 'phone_number', 'city')
    list_filter = ('user_type',)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'loyalty_points')
    search_fields = ('user_profile__user__username',)
    ordering = ('-loyalty_points',)

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user_profile', 'gst_number', 'is_verified')
    search_fields = ('company_name', 'gst_number', 'user_profile__user__username')
    list_filter = ('is_verified',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'display_image', 'created_at')
    search_fields = ('name',)
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Image'

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('user', 'rating', 'comment', 'created_at')
    can_delete = False

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discounted_price', 'stock', 'is_featured', 'display_image')
    list_filter = ('category', 'is_featured', 'seller')
    search_fields = ('name', 'description', 'seller__company_name')
    list_editable = ('price', 'stock', 'is_featured')
    inlines = [ReviewInline]
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    display_image.short_description = 'Image'

    def discounted_price(self, obj):
        return obj.discounted_price()
    discounted_price.short_description = 'Discounted Price'

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'quantity')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_total', 'created_at', 'updated_at')
    inlines = [CartItemInline]
    
    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'Total'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'get_subtotal')
    
    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'Subtotal'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'total_amount', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'shipping_address')
    inlines = [OrderItemInline]
    
    def total_amount(self, obj):
        return obj.total_amount
    total_amount.short_description = 'Total'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'get_subtotal')
    search_fields = ('order__user__username', 'product__name')
    
    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'Subtotal'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    search_fields = ('product__name', 'user__username')
    list_filter = ('rating', 'created_at')

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('added_at',)

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_first_name', 'get_last_name', 'get_email', 'date_registered')
    search_fields = ('user__username', 'user__email')

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
