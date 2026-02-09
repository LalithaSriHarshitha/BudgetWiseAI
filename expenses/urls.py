"""
URL patterns for expenses app.
"""
from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('set-budget/', views.SetBudgetView.as_view(), name='set_budget'),
    path('add-expense/', views.AddExpenseView.as_view(), name='add_expense'),
    path('delete-expense/<int:expense_id>/', views.DeleteExpenseView.as_view(), name='delete_expense'),
    path('chart-data/', views.ChartDataView.as_view(), name='chart_data'),
]
