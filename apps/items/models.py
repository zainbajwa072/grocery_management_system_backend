from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.core.models import TimeStampedModel, SoftDeleteModel
from apps.accounts.models import User
from apps.groceries.models import Grocery

class ItemType(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Item Type'
        verbose_name_plural = 'Item Types'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def active_items_count(self):
        """Count of non-deleted items of this type"""
        return self.item_set.filter(is_deleted=False).count()

class Item(TimeStampedModel, SoftDeleteModel):
    LOCATION_CHOICES = (
        ('first_floor', 'First Floor'),
        ('second_floor', 'Second Floor'),
        ('basement', 'Basement'),
        ('storage', 'Storage'),
        ('freezer', 'Freezer'),
        ('display', 'Display Area'),
    )
    
    name = models.CharField(max_length=255)
    item_type = models.ForeignKey(
        ItemType, 
        on_delete=models.PROTECT,  
        related_name='items'
    )
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]  
    )
    grocery = models.ForeignKey(
        Grocery, 
        on_delete=models.CASCADE,  
        related_name='items'
    )
    added_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='added_items'
    )
    

    sku = models.CharField(max_length=50, blank=True, help_text="Stock Keeping Unit")
    quantity_in_stock = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'grocery'],
                condition=models.Q(is_deleted=False),
                name='unique_active_item_per_grocery'
            )
        ]
        ordering = ['-created_at']
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
        indexes = [
            models.Index(fields=['grocery', 'item_type']),
            models.Index(fields=['name']),
            models.Index(fields=['price']),
            models.Index(fields=['is_deleted']),
        ]
    
    def clean(self):
        """Model validation"""
        if self.price and self.price <= 0:
            raise ValidationError("Price must be positive")
        
        if self.grocery and self.grocery.is_deleted:
            raise ValidationError("Cannot add items to deleted grocery")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.grocery.name if self.grocery else 'No Grocery'}"
    
    @property
    def formatted_price(self):
        """Return formatted price as string"""
        return f"${self.price:,.2f}"
    
    @property
    def is_low_stock(self):
        """Check if item is below reorder level"""
        return self.quantity_in_stock <= self.reorder_level
    
    @property
    def stock_status(self):
        """Return stock status"""
        if self.quantity_in_stock == 0:
            return "Out of Stock"
        elif self.is_low_stock:
            return "Low Stock"
        else:
            return "In Stock"

# Signal handlers for Neo4j sync
@receiver(post_save, sender=Item)
def sync_item_to_neo4j(sender, instance, created, **kwargs):
    """Sync item data to Neo4j when created/updated"""
    if created and not instance.is_deleted:
        try:
            from neo4j_integration.queries import GroceryGraphQueries
            GroceryGraphQueries.create_item_node(
                instance.id, 
                instance.name, 
                instance.item_type.name, 
                float(instance.price), 
                instance.grocery.id
            )
        except Exception as e:
            print(f"Neo4j sync error: {e}")

@receiver(post_delete, sender=Item)
def remove_item_from_neo4j(sender, instance, **kwargs):
    """Remove item from Neo4j when hard deleted"""
    try:
        from neo4j_integration.queries import GroceryGraphQueries
        GroceryGraphQueries.delete_item_node(instance.id)
    except Exception as e:
        print(f"Neo4j delete error: {e}")
