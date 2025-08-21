from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, AdminProfile, SupplierProfile

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'user_type', 'password', 'password_confirm']
    
    def validate_email(self, value):
        """Ensure email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Use the custom manager method
        user = User.objects.create_user(
            email=validated_data['email'],
            password=password,
            **{k: v for k, v in validated_data.items() if k != 'email'}
        )
        
        return user

class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = ['department', 'phone_number']

class SupplierProfileSerializer(serializers.ModelSerializer):
    assigned_grocery_name = serializers.CharField(source='assigned_grocery.name', read_only=True)
    assigned_grocery_location = serializers.CharField(source='assigned_grocery.location', read_only=True)
    
    class Meta:
        model = SupplierProfile
        fields = ['assigned_grocery', 'assigned_grocery_name', 'assigned_grocery_location', 'phone_number', 'hire_date']

class UserSerializer(serializers.ModelSerializer):
    supplier_profile = SupplierProfileSerializer(read_only=True)
    admin_profile = AdminProfileSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'user_type', 'is_active', 'created_at', 'updated_at', 
            'supplier_profile', 'admin_profile'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserListSerializer(serializers.ModelSerializer):
    """Lighter serializer for user lists"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    assigned_grocery = serializers.CharField(
        source='supplier_profile.assigned_grocery.name', 
        read_only=True
    )
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'user_type', 'is_active', 'assigned_grocery']
