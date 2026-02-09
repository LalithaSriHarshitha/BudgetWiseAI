"""
Forms for budget and expense management.
"""
from django import forms
from .models import Budget, Expense
from datetime import datetime


class BudgetForm(forms.ModelForm):
    """
    Form for setting monthly budget.
    """
    month = forms.CharField(
        widget=forms.Select(attrs={
            'class': 'form-input',
        }),
        help_text="Select month"
    )

    class Meta:
        model = Budget
        fields = ['month', 'amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter budget amount',
                'step': '0.01',
                'min': '0.01'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Generate month choices for current and next 11 months
        months = []
        current_date = datetime.now()
        for i in range(12):
            month_date = datetime(current_date.year, current_date.month, 1)
            if current_date.month + i > 12:
                month_date = datetime(current_date.year + 1, (current_date.month + i) % 12, 1)
            else:
                month_date = datetime(current_date.year, current_date.month + i, 1)
            month_str = month_date.strftime('%Y-%m')
            month_display = month_date.strftime('%B %Y')
            months.append((month_str, month_display))
        
        self.fields['month'].widget = forms.Select(
            choices=months,
            attrs={'class': 'form-input'}
        )


class ExpenseForm(forms.ModelForm):
    """
    Form for adding expenses.
    """
    class Meta:
        model = Expense
        fields = ['date', 'amount', 'category', 'note']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter amount',
                'step': '0.01',
                'min': '0.01'
            }),
            'category': forms.Select(attrs={
                'class': 'form-input',
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Add a note (optional)',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default date to today
        if not self.instance.pk:
            self.fields['date'].initial = datetime.now().date()
