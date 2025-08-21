from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.core.models import TimeStampedModel
from .managers import UserManager


class User(AbstractUser, TimeStampedModel):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('supplier', 'Supplier'),
    )
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'user_type']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between"""
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip() or self.username
    
    @property
    def is_admin(self):
        return self.user_type == 'admin'
    
    @property
    def is_supplier(self):
        return self.user_type == 'supplier'

class AdminProfile(TimeStampedModel):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='admin_profile'
    )
    
    department = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    class Meta:
        verbose_name = 'Admin Profile'
        verbose_name_plural = 'Admin Profiles'
    
    def __str__(self):
        return f"Admin Profile: {self.user.get_full_name()}"

class SupplierProfile(TimeStampedModel):
    from apps.groceries.models import Grocery
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='supplier_profile'
    )
    assigned_grocery = models.ForeignKey(
        Grocery, 
        on_delete=models.SET_NULL,  
        null=True, 
        blank=True,
        related_name='suppliers'
    )
    
    phone_number = models.CharField(max_length=20, blank=True)
    hire_date = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Supplier Profile'
        verbose_name_plural = 'Supplier Profiles'
    
    def __str__(self):
        grocery_name = self.assigned_grocery.name if self.assigned_grocery else "Unassigned"
        return f"Supplier: {self.user.get_full_name()} - {grocery_name}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create profile when user is created"""
    if created:
        if instance.user_type == 'admin':
            AdminProfile.objects.get_or_create(user=instance)
        elif instance.user_type == 'supplier':
            SupplierProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save profile when user is saved"""
    if instance.user_type == 'admin' and hasattr(instance, 'admin_profile'):
        instance.admin_profile.save()
    elif instance.user_type == 'supplier' and hasattr(instance, 'supplier_profile'):
        instance.supplier_profile.save()
