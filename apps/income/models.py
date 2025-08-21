from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedModel
from datetime import date
from apps.accounts.models import User
from apps.groceries.models import Grocery

class DailyIncome(TimeStampedModel):
    grocery = models.ForeignKey(
        Grocery, 
        on_delete=models.PROTECT,  
        related_name='daily_incomes'
    )
    date = models.DateField()
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)]  
    )
    recorded_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,  
        related_name='recorded_incomes'
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['grocery', 'date']
        ordering = ['-date']
        verbose_name = 'Daily Income'
        verbose_name_plural = 'Daily Incomes'
        indexes = [
            models.Index(fields=['grocery', 'date']),
            models.Index(fields=['date']),
        ]
    
    def clean(self):
        """Model validation"""
        if self.date and self.date > date.today():
            raise ValidationError("Cannot record income for future dates")
        
        if self.amount and self.amount <= 0:
            raise ValidationError("Income amount must be positive")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.grocery.name} - {self.date} - ${self.amount}"
    
    @property
    def formatted_amount(self):
        """Return formatted amount as string"""
        return f"${self.amount:,.2f}"
