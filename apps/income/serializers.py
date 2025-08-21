# from rest_framework import serializers
# from django.utils import timezone
# from .models import DailyIncome
# from apps.groceries.models import Grocery

# class DailyIncomeSerializer(serializers.ModelSerializer):
#     grocery_name = serializers.CharField(source='grocery.name', read_only=True)
#     grocery_location = serializers.CharField(source='grocery.location', read_only=True)
#     recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)
#     formatted_amount = serializers.CharField(source='formatted_amount', read_only=True)
    
#     class Meta:
#         model = DailyIncome
#         fields = [
#             'id', 'grocery', 'grocery_name', 'grocery_location', 'date', 
#             'amount', 'formatted_amount', 'notes', 'recorded_by', 
#             'recorded_by_name', 'created_at', 'updated_at'
#         ]
#         read_only_fields = ['id', 'recorded_by', 'created_at', 'updated_at']

# class DailyIncomeCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DailyIncome
#         fields = ['grocery', 'date', 'amount', 'notes']
    
#     def validate_date(self, value):
#         """Validate date is not in future"""
#         if value > timezone.now().date():
#             raise serializers.ValidationError("Cannot record income for future dates")
#         return value
    
#     def validate_amount(self, value):
#         """Validate amount is positive"""
#         if value <= 0:
#             raise serializers.ValidationError("Income amount must be positive")
#         return value
    
#     def validate_grocery(self, value):
#         """Validate grocery access for suppliers"""
#         user = self.context['request'].user
        
#         # Check if grocery exists and is not soft deleted
#         if value.is_deleted:
#             raise serializers.ValidationError("Cannot add income for deleted grocery")
        
#         if user.user_type == 'supplier':
#             try:
#                 supplier_profile = user.supplier_profile
#                 if supplier_profile.assigned_grocery != value:
#                     raise serializers.ValidationError(
#                         "Suppliers can only add income for their assigned grocery"
#                     )
#             except AttributeError:
#                 raise serializers.ValidationError("Supplier profile not found")
#         return value
    
#     def validate(self, attrs):
#         """Cross-field validation"""
#         grocery = attrs['grocery']
#         date = attrs['date']
        
#         # Check for duplicate entries
#         queryset = DailyIncome.objects.filter(grocery=grocery, date=date)
        
#         if self.instance:
#             # Update case - exclude current instance
#             queryset = queryset.exclude(id=self.instance.id)
        
#         if queryset.exists():
#             raise serializers.ValidationError({
#                 'date': f"Income for {grocery.name} on {date} already exists"
#             })
        
#         return attrs

# class DailyIncomeListSerializer(serializers.ModelSerializer):
#     """Lighter serializer for list views"""
#     grocery_name = serializers.CharField(source='grocery.name', read_only=True)
#     formatted_amount = serializers.CharField(source='formatted_amount', read_only=True)
    
#     class Meta:
#         model = DailyIncome
#         fields = ['id', 'grocery_name', 'date', 'formatted_amount', 'notes']


from rest_framework import serializers
from django.utils import timezone
from .models import DailyIncome
from apps.groceries.models import Grocery


class DailyIncomeSerializer(serializers.ModelSerializer):
    grocery_name = serializers.CharField(source='grocery.name', read_only=True)
    grocery_location = serializers.CharField(source='grocery.location', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)
    formatted_amount = serializers.CharField(read_only=True) 
    
    class Meta:
        model = DailyIncome
        fields = [
            'id', 'grocery', 'grocery_name', 'grocery_location', 'date',
            'amount', 'formatted_amount', 'notes', 'recorded_by',
            'recorded_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'recorded_by', 'created_at', 'updated_at']


class DailyIncomeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyIncome
        fields = ['grocery', 'date', 'amount', 'notes']

    def validate_date(self, value):
        """Validate date is not in future"""
        if value > timezone.now().date():
            raise serializers.ValidationError("Cannot record income for future dates")
        return value

    def validate_amount(self, value):
        """Validate amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Income amount must be positive")
        return value

    def validate_grocery(self, value):
        """Validate grocery access for suppliers"""
        user = self.context['request'].user

        if value.is_deleted:
            raise serializers.ValidationError("Cannot add income for deleted grocery")

        if user.user_type == 'supplier':
            try:
                supplier_profile = user.supplier_profile
                if supplier_profile.assigned_grocery != value:
                    raise serializers.ValidationError(
                        "Suppliers can only add income for their assigned grocery"
                    )
            except AttributeError:
                raise serializers.ValidationError("Supplier profile not found")
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        grocery = attrs['grocery']
        date = attrs['date']

        queryset = DailyIncome.objects.filter(grocery=grocery, date=date)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)

        if queryset.exists():
            raise serializers.ValidationError({
                'date': f"Income for {grocery.name} on {date} already exists"
            })

        return attrs


class DailyIncomeListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    grocery_name = serializers.CharField(source='grocery.name', read_only=True)
    formatted_amount = serializers.CharField(read_only=True) 

    class Meta:
        model = DailyIncome
        fields = ['id', 'grocery_name', 'date', 'formatted_amount', 'notes']
