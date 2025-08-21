from rest_framework import serializers
from django.db.models import Q
from .models import Item, ItemType

class ItemTypeSerializer(serializers.ModelSerializer):
    active_items_count = serializers.IntegerField(read_only=True)
    total_items = serializers.SerializerMethodField()
    

    class Meta:
        model = ItemType
        fields = ['id', 'name', 'description', 'active_items_count', 'total_items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_items(self, obj):
        """Get total items including soft deleted"""
        return obj.items.count()
    
    def validate_name(self, value):
        """Ensure item type name is unique (case insensitive)"""
        if ItemType.objects.filter(name__iexact=value).exists():
            if not self.instance or self.instance.name.lower() != value.lower():
                raise serializers.ValidationError("Item type with this name already exists.")
        return value

class ItemSerializer(serializers.ModelSerializer):
    item_type_name = serializers.CharField(source='item_type.name', read_only=True)
    grocery_name = serializers.CharField(source='grocery.name', read_only=True)
    grocery_location = serializers.CharField(source='grocery.location', read_only=True)
    added_by_name = serializers.CharField(source='added_by.get_full_name', read_only=True)
    formatted_price = serializers.CharField(read_only=True)
    stock_status = serializers.CharField(read_only=True)
    # is_low_stock = serializers.BooleanField(source='is_low_stock', read_only=True)
    is_low_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Item
        fields = [
            'id', 'name', 'item_type', 'item_type_name', 'location', 'price', 'formatted_price',
            'grocery', 'grocery_name', 'grocery_location', 'added_by', 'added_by_name',
            'sku', 'quantity_in_stock', 'reorder_level', 'stock_status', 'is_low_stock',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'added_by', 'created_at', 'updated_at']


    def get_is_low_stock(self, obj):
        return obj.is_low_stock     

class ItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['name', 'item_type', 'location', 'price', 'grocery', 'sku', 'quantity_in_stock', 'reorder_level']
    
    def validate_price(self, value):
        """Validate price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value
    
    def validate_grocery(self, value):
        """Validate grocery access and status"""
        user = self.context['request'].user
        
        # Check if grocery is soft deleted
        if value.is_deleted:
            raise serializers.ValidationError("Cannot add items to deleted grocery")
        
        # Supplier permission check
        if user.user_type == 'supplier':
            try:
                supplier_profile = user.supplier_profile
                if supplier_profile.assigned_grocery != value:
                    raise serializers.ValidationError(
                        "Suppliers can only add items to their assigned grocery"
                    )
            except AttributeError:
                raise serializers.ValidationError("Supplier profile not found")
        return value
    
    def validate_item_type(self, value):
        """Validate item type exists"""
        if not value:
            raise serializers.ValidationError("Item type is required")
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        name = attrs.get('name')
        grocery = attrs.get('grocery')
        
        # Check for duplicate item names in same grocery (excluding soft deleted)
        if name and grocery:
            existing_query = Item.objects.filter(
                name__iexact=name,
                grocery=grocery,
                is_deleted=False
            )
            
            # Exclude current instance during updates
            if self.instance:
                existing_query = existing_query.exclude(id=self.instance.id)
            
            if existing_query.exists():
                raise serializers.ValidationError({
                    'name': f"Item '{name}' already exists in {grocery.name}"
                })
        
        # Validate stock levels
        quantity = attrs.get('quantity_in_stock', 0)
        reorder_level = attrs.get('reorder_level', 10)
        
        if quantity < 0:
            raise serializers.ValidationError({
                'quantity_in_stock': 'Quantity cannot be negative'
            })
        
        if reorder_level < 0:
            raise serializers.ValidationError({
                'reorder_level': 'Reorder level cannot be negative'
            })
        
        return attrs

class ItemUpdateSerializer(serializers.ModelSerializer):
    """Separate serializer for updates with different validation"""
    class Meta:
        model = Item
        fields = ['name', 'item_type', 'location', 'price', 'sku', 'quantity_in_stock', 'reorder_level']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be positive")
        return value

class ItemListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    item_type_name = serializers.CharField(source='item_type.name', read_only=True)
    grocery_name = serializers.CharField(source='grocery.name', read_only=True)
    formatted_price = serializers.CharField(read_only=True)
    stock_status = serializers.CharField(read_only=True)
    
    class Meta:
        model = Item
        fields = ['id', 'name', 'item_type_name', 'location', 'formatted_price', 'grocery_name', 'stock_status']
