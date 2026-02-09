"""
Models for expense tracking and budget management.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Budget(models.Model):
    """
    Monthly budget for a user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    month = models.CharField(max_length=7, help_text="Format: YYYY-MM")
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'month')
        ordering = ['-month']

    def __str__(self):
        return f"{self.user.username} - {self.month}: ${self.amount}"


class Expense(models.Model):
    """
    Individual expense entry.
    """
    CATEGORY_CHOICES = [
        ('Groceries', 'Groceries'),
        ('Rent', 'Rent'),
        ('Travel', 'Travel'),
        ('Food', 'Food'),
        ('Utilities', 'Utilities'),
        ('Entertainment', 'Entertainment'),
        ('Healthcare', 'Healthcare'),
        ('Shopping', 'Shopping'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    note = models.TextField(blank=True, null=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.category}: ${self.amount} on {self.date}"
