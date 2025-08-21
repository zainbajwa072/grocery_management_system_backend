from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .models import User, SupplierProfile
from .serializers import UserRegistrationSerializer, UserSerializer, SupplierProfileSerializer
from apps.core.permissions import IsAdminUser
from apps.groceries.models import Grocery

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    Admin can CRUD all users
    Suppliers can only read their own profile
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'list']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['post'])
    def create_supplier(self, request):
        """Admin creates supplier and assigns grocery"""
        if request.user.user_type != 'admin':
            return Response({'error': 'Only admins can create suppliers'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['user_type'] = 'supplier'
            user = serializer.save()
            

            grocery_id = request.data.get('grocery_id')
            if grocery_id:
                try:
                    grocery = Grocery.objects.get(id=grocery_id)
                    user.supplier_profile.assigned_grocery = grocery
                    user.supplier_profile.save()
                except Grocery.DoesNotExist:
                    return Response({'error': 'Grocery not found'}, 
                                  status=status.HTTP_400_BAD_REQUEST)
            
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def assign_grocery(self, request, pk=None):
        """Admin assigns grocery to supplier"""
        if request.user.user_type != 'admin':
            return Response({'error': 'Only admins can assign groceries'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        if user.user_type != 'supplier':
            return Response({'error': 'Can only assign grocery to suppliers'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        grocery_id = request.data.get('grocery_id')
        try:
            grocery = Grocery.objects.get(id=grocery_id)
            user.supplier_profile.assigned_grocery = grocery
            user.supplier_profile.save()
            return Response({'message': f'Grocery {grocery.name} assigned successfully'})
        except Grocery.DoesNotExist:
            return Response({'error': 'Grocery not found'}, 
                          status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login with user details"""
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            from rest_framework_simplejwt.tokens import UntypedToken
            from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
            try:
                token = response.data['access']
                user_id = UntypedToken(token)['user_id']
                user = User.objects.get(id=user_id)
                response.data['user'] = UserSerializer(user).data
            except (InvalidToken, TokenError, User.DoesNotExist):
                pass
        return response
