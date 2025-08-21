from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Grocery
from .serializers import GrocerySerializer, GroceryCreateSerializer, GroceryListSerializer
from apps.core.permissions import IsAdminUser

class GroceryViewSet(viewsets.ModelViewSet):
    queryset = Grocery.objects.all()
    serializer_class = GrocerySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['location']
    search_fields = ['name', 'location']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return GroceryCreateSerializer
        elif self.action == 'list':
            return GroceryListSerializer
        return GrocerySerializer
    
    def perform_create(self, serializer):
        grocery = serializer.save(created_by=self.request.user)
        # Neo4j sync is handled by signal
    
    def perform_destroy(self, instance):
        """Soft delete the grocery"""
        instance.soft_delete()
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        grocery = self.get_object()
        try:
            from neo4j_integration.queries import GroceryGraphQueries
            analytics = GroceryGraphQueries.get_grocery_analytics(grocery.id)
            return Response(analytics)
        except Exception as e:
            return Response(
                {'error': 'Analytics service unavailable', 'detail': str(e)}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    @action(detail=False, methods=['get'])
    def my_grocery(self, request):
        """Get grocery assigned to current supplier"""
        if request.user.user_type != 'supplier':
            return Response({'error': 'Only suppliers can access this endpoint'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            supplier_profile = request.user.supplier_profile
            if supplier_profile.assigned_grocery:
                serializer = self.get_serializer(supplier_profile.assigned_grocery)
                return Response(serializer.data)
            else:
                return Response({'error': 'No grocery assigned'}, 
                              status=status.HTTP_404_NOT_FOUND)
        except AttributeError:
            return Response({'error': 'Supplier profile not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def suppliers(self, request, pk=None):
        """Get all suppliers assigned to this grocery"""
        grocery = self.get_object()
        from apps.accounts.serializers import UserListSerializer
        
        suppliers = grocery.suppliers.filter(user__is_active=True).select_related('user')
        supplier_users = [sp.user for sp in suppliers]
        
        serializer = UserListSerializer(supplier_users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Get all items in this grocery"""
        grocery = self.get_object()
        from apps.items.serializers import ItemSerializer
        
        items = grocery.items.filter(is_deleted=False)
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore soft deleted grocery - Admin only"""
        if request.user.user_type != 'admin':
            return Response({'error': 'Only admins can restore groceries'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        try:
            grocery = Grocery.all_objects.get(pk=pk, is_deleted=True)
            grocery.restore()
            return Response({'message': 'Grocery restored successfully'})
        except Grocery.DoesNotExist:
            return Response({'error': 'Deleted grocery not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
