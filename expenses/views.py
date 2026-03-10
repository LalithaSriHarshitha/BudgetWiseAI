"""
Views for expense management dashboard with analytics.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from datetime import datetime
from decimal import Decimal
from .models import Budget, Expense
from .forms import BudgetForm, ExpenseForm, ExpenseFilterForm
from .services import ExpenseAnalytics


class DashboardView(LoginRequiredMixin, View):
    """
    Enhanced dashboard with analytics, charts, and AI insights.
    """
    def get(self, request):
        from expenses.services import UnifiedDataService
        
        data_service = UnifiedDataService(request.user)
        summary = data_service.get_consistent_summary()
        kpi_data = data_service.get_kpi_data()
        
        # Get AI prediction and insights
        from ai_engine.forecast import predict_next_day_expense
        from ai_engine.insights import generate_user_insights
        
        ai_prediction = predict_next_day_expense(request.user)
        ai_insights = generate_user_insights(request.user)
        
        # Get budget form
        current_month = datetime.now().strftime('%Y-%m')
        budget = Budget.objects.filter(
            user=request.user,
            month=current_month
        ).first()
        budget_form = BudgetForm(instance=budget)
        
        # Get recent expenses
        recent_expenses = Expense.objects.filter(user=request.user)[:5]
        
        context = {
            'summary': summary,
            'kpi_data': kpi_data,
            'budget_form': budget_form,
            'recent_expenses': recent_expenses,
            'current_month': datetime.now().strftime('%B %Y'),
            'ai_prediction': ai_prediction,
            'ai_insights': ai_insights,
        }
        
        return render(request, 'expenses/dashboard_modern.html', context)


class AddExpenseView(LoginRequiredMixin, View):
    """
    Add new expense.
    """
    def get(self, request):
        form = ExpenseForm()
        return render(request, 'expenses/add_expense_modern.html', {'form': form})
    
    def post(self, request):
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, f'Expense of ₹{expense.amount} added successfully!')
            return redirect('expenses:dashboard')
        return render(request, 'expenses/add_expense_modern.html', {'form': form})


class EditExpenseView(LoginRequiredMixin, View):
    """
    Edit existing expense.
    """
    def get(self, request, expense_id):
        expense = get_object_or_404(Expense, id=expense_id, user=request.user)
        form = ExpenseForm(instance=expense)
        return render(request, 'expenses/edit_expense.html', {
            'form': form,
            'expense': expense
        })
    
    def post(self, request, expense_id):
        expense = get_object_or_404(Expense, id=expense_id, user=request.user)
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('expenses:list_expenses')
        return render(request, 'expenses/edit_expense.html', {
            'form': form,
            'expense': expense
        })


class DeleteExpenseView(LoginRequiredMixin, View):
    """
    Delete an expense.
    """
    def post(self, request, expense_id):
        expense = get_object_or_404(Expense, id=expense_id, user=request.user)
        amount = expense.amount
        expense.delete()
        messages.success(request, f'Expense of ₹{amount} deleted successfully!')
        
        # Redirect to referring page or dashboard
        next_url = request.POST.get('next', 'expenses:dashboard')
        return redirect(next_url)


class ListExpensesView(LoginRequiredMixin, View):
    """
    List all expenses with filtering and pagination.
    """
    def get(self, request):
        # Get all user expenses
        expenses = Expense.objects.filter(user=request.user)
        
        # Apply filters
        filter_form = ExpenseFilterForm(request.GET)
        if filter_form.is_valid():
            category = filter_form.cleaned_data.get('category')
            month = filter_form.cleaned_data.get('month')
            search = filter_form.cleaned_data.get('search')
            
            if category:
                expenses = expenses.filter(category=category)
            
            if month:
                year, month_num = month.split('-')
                expenses = expenses.filter(date__year=year, date__month=month_num)
            
            if search:
                expenses = expenses.filter(
                    Q(description__icontains=search) | Q(category__icontains=search)
                )
        
        # Pagination
        paginator = Paginator(expenses, 15)  # 15 expenses per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Calculate total
        total = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        context = {
            'page_obj': page_obj,
            'filter_form': filter_form,
            'total': total,
            'count': expenses.count(),
            'average': total / expenses.count() if expenses.count() > 0 else 0,
        }
        
        return render(request, 'expenses/list_expenses_modern.html', context)


class AnalyticsView(LoginRequiredMixin, View):
    """
    Detailed analytics page.
    """
    def get(self, request):
        analytics = ExpenseAnalytics(request.user)
        
        context = {
            'category_breakdown': analytics.get_category_breakdown(),
            'monthly_totals': analytics.get_monthly_totals(12),
            'budget_status': analytics.get_budget_status(),
            'total_expenses': analytics.get_current_month_total(),
            'transaction_count': analytics.get_transaction_count(),
            'average_transaction': analytics.get_current_month_total() / analytics.get_transaction_count() if analytics.get_transaction_count() > 0 else 0,
        }
        
        return render(request, 'expenses/analytics_modern.html', context)


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


# API Views for Chart Data

class CategoryChartDataView(LoginRequiredMixin, View):
    """
    API endpoint for category distribution chart.
    """
    def get(self, request):
        analytics = ExpenseAnalytics(request.user)
        breakdown = analytics.get_category_breakdown()
        
        labels = [item['category'] for item in breakdown]
        data = [float(item['total']) for item in breakdown]
        
        colors = [
            '#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
            '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
        ]
        
        return JsonResponse({
            'labels': labels,
            'data': data,
            'colors': colors[:len(labels)]
        })


class MonthlyChartDataView(LoginRequiredMixin, View):
    """
    API endpoint for monthly expenses chart.
    """
    def get(self, request):
        analytics = ExpenseAnalytics(request.user)
        monthly_data = analytics.get_monthly_totals(6)
        
        labels = [item['month'].strftime('%b %Y') for item in monthly_data]
        data = [float(item['total']) for item in monthly_data]
        
        return JsonResponse({
            'labels': labels,
            'data': data
        })


class TrendChartDataView(LoginRequiredMixin, View):
    """
    API endpoint for spending trend chart.
    """
    def get(self, request):
        analytics = ExpenseAnalytics(request.user)
        trend_data = analytics.get_spending_trend(30)
        
        labels = [item['date'].strftime('%b %d') for item in trend_data]
        data = [float(item['total']) for item in trend_data]
        
        return JsonResponse({
            'labels': labels,
            'data': data
        })
