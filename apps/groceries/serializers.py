from rest_framework import serializers
from .models import Grocery

class GrocerySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    total_items = serializers.SerializerMethodField()
    total_suppliers = serializers.SerializerMethodField()
    
    class Meta:
        model = Grocery
        fields = ['id', 'name', 'location', 'created_by', 'created_by_name', 
                 'created_at', 'updated_at', 'total_items', 'total_suppliers']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_total_items(self, obj):
        return obj.item_count 
    
    def get_total_suppliers(self, obj):
        return obj.supplier_count 

class GroceryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grocery
        fields = ['name', 'location']
    
    def validate_name(self, value):
        """Ensure grocery name is unique"""
        if Grocery.objects.filter(name=value).exists():
            raise serializers.ValidationError("A grocery with this name already exists.")
        return value
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class GroceryListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Grocery
        fields = ['id', 'name', 'location', 'created_by_name', 'created_at']
