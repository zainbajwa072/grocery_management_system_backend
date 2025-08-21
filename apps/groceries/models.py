from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.core.models import TimeStampedModel, SoftDeleteModel
from apps.accounts.models import User

class Grocery(TimeStampedModel, SoftDeleteModel):
    name = models.CharField(max_length=255, unique=True)  
    location = models.CharField(max_length=500)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  
        null=True,  #
        related_name='created_groceries'
    )
    
    class Meta:
        verbose_name_plural = "Groceries"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['location']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.location}"
    
    @property
    def supplier_count(self):
        """Count of suppliers assigned to this grocery"""
        return self.suppliers.filter(user__is_active=True).count()
    
    @property
    def item_count(self):
        """Count of active items in this grocery"""
        return self.items.filter(is_deleted=False).count()


@receiver(post_save, sender=Grocery)
def sync_grocery_to_neo4j(sender, instance, created, **kwargs):
    """Sync grocery data to Neo4j when created/updated"""
    from neo4j_integration.queries import GroceryGraphQueries
    
    if created:
        GroceryGraphQueries.create_grocery_node(
            instance.id, 
            instance.name, 
            instance.location
        )
    else:
        GroceryGraphQueries.update_grocery_node(
            instance.id,
            instance.name,
            instance.location
        )
