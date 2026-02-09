"""
Views for expense management dashboard.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.db.models import Sum
from datetime import datetime
from decimal import Decimal
from .models import Budget, Expense
from .forms import BudgetForm, ExpenseForm


class DashboardView(LoginRequiredMixin, View):
    """
    Main dashboard view showing budget and expenses.
    """
    def get(self, request):
        current_month = datetime.now().strftime('%Y-%m')
        current_date = datetime.now().date()
        
        # Get or create budget for current month
        budget = Budget.objects.filter(
            user=request.user,
            month=current_month
        ).first()
        
        # Get all expenses for current month
        expenses = Expense.objects.filter(
            user=request.user,
            date__year=current_date.year,
            date__month=current_date.month
        )
        
        # Get today's expenses
        today_expenses = expenses.filter(date=current_date)
        
        # Calculate totals
        total_spent = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        budget_amount = budget.amount if budget else Decimal('0.00')
        remaining_budget = budget_amount - total_spent
        
        # Prepare forms
        budget_form = BudgetForm(instance=budget)
        expense_form = ExpenseForm()
        
        context = {
            'budget': budget,
            'budget_amount': budget_amount,
            'total_spent': total_spent,
            'remaining_budget': remaining_budget,
            'expenses': expenses,
            'today_expenses': today_expenses,
            'budget_form': budget_form,
            'expense_form': expense_form,
            'current_month': datetime.now().strftime('%B %Y'),
        }
        
        return render(request, 'expenses/dashboard.html', context)


class SetBudgetView(LoginRequiredMixin, View):
    """
    Set or update monthly budget.
    """
    def post(self, request):
        form = BudgetForm(request.POST)
        
        if form.is_valid():
            month = form.cleaned_data['month']
            amount = form.cleaned_data['amount']
            
            # Update or create budget
            budget, created = Budget.objects.update_or_create(
                user=request.user,
                month=month,
                defaults={'amount': amount}
            )
            
            if created:
                messages.success(request, f'Budget set successfully for {month}!')
            else:
                messages.success(request, f'Budget updated successfully for {month}!')
        else:
            messages.error(request, 'Invalid budget data. Please try again.')
        
        return redirect('expenses:dashboard')


class AddExpenseView(LoginRequiredMixin, View):
    """
    Add a new expense.
    """
    def post(self, request):
        form = ExpenseForm(request.POST)
        
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, f'Expense of ${expense.amount} added successfully!')
        else:
            messages.error(request, 'Invalid expense data. Please check your input.')
        
        return redirect('expenses:dashboard')


class DeleteExpenseView(LoginRequiredMixin, View):
    """
    Delete an expense.
    """
    def post(self, request, expense_id):
        expense = get_object_or_404(Expense, id=expense_id, user=request.user)
        amount = expense.amount
        expense.delete()
        messages.success(request, f'Expense of ${amount} deleted successfully!')
        return redirect('expenses:dashboard')


class ChartDataView(LoginRequiredMixin, View):
    """
    API endpoint for chart data.
    """
    def get(self, request):
        current_month = datetime.now().strftime('%Y-%m')
        current_date = datetime.now().date()
        
        # Get budget
        budget = Budget.objects.filter(
            user=request.user,
            month=current_month
        ).first()
        
        # Get expenses for current month
        expenses = Expense.objects.filter(
            user=request.user,
            date__year=current_date.year,
            date__month=current_date.month
        )
        
        total_spent = float(expenses.aggregate(total=Sum('amount'))['total'] or 0)
        budget_amount = float(budget.amount if budget else 0)
        remaining = max(budget_amount - total_spent, 0)
        
        data = {
            'labels': ['Spent', 'Remaining'],
            'data': [total_spent, remaining],
            'colors': ['#ef4444', '#10b981']
        }
        
        return JsonResponse(data)
