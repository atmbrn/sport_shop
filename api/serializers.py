from rest_framework import serializers
from products.models import Category, Product, ProductImage
from reviews.models import Review
from orders.models import Order, OrderItem, Cart, CartItem
from django.contrib.auth.models import User
from users.models import UserProfile


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'image', 'is_active')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text', 'is_primary')


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'slug',
            'category',
            'category_name',
            'price',
            'discount_price',
            'current_price',
            'stock',
            'image',
            'is_featured',
        )


class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'category',
            'category_name',
            'price',
            'discount_price',
            'current_price',
            'stock',
            'size',
            'color',
            'brand',
            'material',
            'image',
            'images',
            'is_featured',
            'is_active',
            'views_count',
            'avg_rating',
            'discount_percentage',
        )

    def get_avg_rating(self, obj):
        reviews = Review.objects.filter(product=obj, is_approved=True)
        if reviews.exists():
            from django.db.models import Avg
            return reviews.aggregate(avg=Avg('rating'))['avg']
        return 0


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = (
            'id',
            'product',
            'user',
            'username',
            'rating',
            'title',
            'content',
            'helpful_count',
            'unhelpful_count',
            'is_verified_purchase',
            'created_at',
            'updated_at',
        )


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price', 'subtotal')


class OrderListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'order_number',
            'status',
            'status_display',
            'total_amount',
            'final_amount',
            'created_at',
            'is_paid',
        )


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'order_number',
            'status',
            'status_display',
            'payment_method',
            'is_paid',
            'total_amount',
            'discount_amount',
            'shipping_cost',
            'final_amount',
            'shipping_address',
            'shipping_city',
            'shipping_postal_code',
            'phone_number',
            'notes',
            'items',
            'created_at',
            'updated_at',
        )


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.DecimalField(
        source='product.current_price',
        read_only=True,
        max_digits=10,
        decimal_places=2
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price', 'subtotal')

    def get_subtotal(self, obj):
        return obj.subtotal


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_price', 'total_items')

    def get_total_price(self, obj):
        return float(obj.get_total_price())

    def get_total_items(self, obj):
        return obj.get_total_items()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'id',
            'phone_number',
            'address',
            'city',
            'postal_code',
            'gender',
            'birth_date',
            'profile_image',
            'bio',
        )


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'profile',
        )
