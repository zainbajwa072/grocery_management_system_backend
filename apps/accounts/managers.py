from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

class UserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier"""
    
    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a user with the given email and password"""
        if not email:
            raise ValueError('The Email field must be set')
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError('Invalid email format')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        # Set default user_type if not provided
        if 'user_type' not in extra_fields:
            extra_fields['user_type'] = 'supplier'
        
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self._create_user(email, password, **extra_fields)
    
    def get_admins(self):
        """Get all admin users"""
        return self.filter(user_type='admin', is_active=True)
    
    def get_suppliers(self):
        """Get all supplier users"""
        return self.filter(user_type='supplier', is_active=True)
    
    def get_suppliers_with_grocery(self):
        """Get suppliers who have assigned grocery"""
        return self.filter(
            user_type='supplier', 
            is_active=True,
            supplier_profile__assigned_grocery__isnull=False
        ).select_related('supplier_profile__assigned_grocery')
