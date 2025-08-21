from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, Avg, Sum
from .models import Item, ItemType
from .serializers import (
    ItemSerializer, ItemTypeSerializer, ItemCreateSerializer, 
    ItemUpdateSerializer, ItemListSerializer
)
from apps.core.permissions import IsAdminUser

class ItemTypeViewSet(viewsets.ModelViewSet):
    """Item types management with proper permissions"""
    queryset = ItemType.objects.annotate(
        total_items=Count('items'),
        active_items=Count('items', filter=Q(items__is_deleted=False))
    )
    serializer_class = ItemTypeSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_destroy(self, instance):
        """Check if item type has active items before deletion"""
        if instance.items.filter(is_deleted=False).exists():
            raise PermissionError("Cannot delete item type with active items")
        instance.delete()
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Get all items of this type"""
        item_type = self.get_object()
        items = item_type.items.filter(is_deleted=False)
        
        serializer = ItemListSerializer(items, many=True)
        return Response(serializer.data)

class ItemViewSet(viewsets.ModelViewSet):
    """
    Comprehensive items management with proper permissions and business logic
    """
    queryset = Item.objects.select_related('item_type', 'grocery', 'added_by')
    serializer_class = ItemSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['grocery', 'item_type', 'location']
    search_fields = ['name', 'item_type__name', 'sku']
    ordering_fields = ['name', 'price', 'created_at', 'quantity_in_stock']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.user_type == 'supplier':
            if self.action in ['list', 'retrieve']:
                # Suppliers can read all items
                return queryset
            else:
                # For modification actions, only their assigned grocery
                try:
                    assigned_grocery = user.supplier_profile.assigned_grocery
                    if assigned_grocery:
                        return queryset.filter(grocery=assigned_grocery)
                except AttributeError:
                    pass
                return queryset.none()
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ItemCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ItemUpdateSerializer
        elif self.action == 'list':
            return ItemListSerializer
        return ItemSerializer
    
    def perform_create(self, serializer):
        """Create item with proper validation and Neo4j sync"""
        user = self.request.user
        
        # Additional supplier validation
        if user.user_type == 'supplier':
            try:
                supplier_profile = user.supplier_profile
                grocery = serializer.validated_data['grocery']
                if supplier_profile.assigned_grocery != grocery:
                    raise PermissionError("Cannot add items to other grocery stores")
            except AttributeError:
                raise PermissionError("Supplier profile not found")
        
        item = serializer.save(added_by=user)
        # Neo4j sync is handled by signal
    
    def perform_update(self, serializer):
        """Update item with permission checks"""
        user = self.request.user
        instance = self.get_object()
        
        if user.user_type == 'supplier':
            try:
                supplier_profile = user.supplier_profile
                if supplier_profile.assigned_grocery != instance.grocery:
                    raise PermissionError("Cannot modify items from other grocery stores")
            except AttributeError:
                raise PermissionError("Supplier profile not found")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Soft delete with permission checks"""
        user = self.request.user
        
        if user.user_type == 'supplier':
            try:
                supplier_profile = user.supplier_profile
                if supplier_profile.assigned_grocery != instance.grocery:
                    raise PermissionError("Cannot delete items from other grocery stores")
            except AttributeError:
                raise PermissionError("Supplier profile not found")
        
        instance.soft_delete()
    
    @action(detail=False, methods=['get'])
    def my_grocery_items(self, request):
        """Get items from supplier's assigned grocery"""
        if request.user.user_type != 'supplier':
            return Response({'error': 'Only suppliers can access this endpoint'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            supplier_profile = request.user.supplier_profile
            if supplier_profile.assigned_grocery:
                items = self.get_queryset().filter(grocery=supplier_profile.assigned_grocery)
                page = self.paginate_queryset(items)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)
                serializer = self.get_serializer(items, many=True)
                return Response(serializer.data)
            else:
                return Response({'error': 'No grocery assigned'}, 
                              status=status.HTTP_404_NOT_FOUND)
        except AttributeError:
            return Response({'error': 'Supplier profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def low_stock_items(self, request):
        """Get items with low stock levels"""
        low_stock_items = self.get_queryset().filter(
            quantity_in_stock__lte=models.F('reorder_level')
        )
        
        serializer = self.get_serializer(low_stock_items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def inventory_summary(self, request):
        """Get inventory summary statistics"""
        queryset = self.get_queryset()
        
        summary = queryset.aggregate(
            total_items=Count('id'),
            total_value=Sum(models.F('price') * models.F('quantity_in_stock')),
            average_price=Avg('price'),
            low_stock_count=Count('id', filter=Q(quantity_in_stock__lte=models.F('reorder_level'))),
            out_of_stock_count=Count('id', filter=Q(quantity_in_stock=0))
        )
        
        # Add breakdown by grocery for admins
        if request.user.user_type == 'admin':
            grocery_breakdown = queryset.values('grocery__name').annotate(
                item_count=Count('id'),
                total_value=Sum(models.F('price') * models.F('quantity_in_stock'))
            ).order_by('-item_count')
            summary['grocery_breakdown'] = list(grocery_breakdown)
        
        return Response(summary)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore soft deleted item - Admin only"""
        if request.user.user_type != 'admin':
            return Response({'error': 'Only admins can restore items'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            item = Item.all_objects.get(pk=pk, is_deleted=True)
            item.restore()
            return Response({'message': 'Item restored successfully'})
        except Item.DoesNotExist:
            return Response({'error': 'Deleted item not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Update item stock quantity"""
        item = self.get_object()
        new_quantity = request.data.get('quantity')
        
        if new_quantity is None:
            return Response({'error': 'Quantity is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_quantity = int(new_quantity)
            if new_quantity < 0:
                raise ValueError("Quantity cannot be negative")
        except (ValueError, TypeError):
            return Response({'error': 'Invalid quantity value'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Permission check for suppliers
        if request.user.user_type == 'supplier':
            try:
                supplier_profile = request.user.supplier_profile
                if supplier_profile.assigned_grocery != item.grocery:
                    return Response({'error': 'Cannot update stock for other grocery stores'}, 
                                  status=status.HTTP_403_FORBIDDEN)
            except AttributeError:
                return Response({'error': 'Supplier profile not found'}, 
                              status=status.HTTP_404_NOT_FOUND)
        
        item.quantity_in_stock = new_quantity
        item.save()
        
        return Response({
            'message': 'Stock updated successfully',
            'new_quantity': new_quantity,
            'stock_status': item.stock_status
        })
