"""
AI Expense Forecasting Module
Uses Linear Regression to predict future expenses based on historical data.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from expenses.models import Expense


class ExpenseForecastEngine:
    """
    Machine Learning engine for expense forecasting.
    """
    
    def __init__(self, user):
        self.user = user
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.min_data_points = 10  # Minimum days of data required
    
    def get_historical_data(self, days=30):
        """
        Fetch and aggregate user's historical expense data by day.
        Returns DataFrame with day index and total expenses.
        """
        # Get expenses from last N days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get daily expenses
        daily_expenses = Expense.objects.filter(
            user=self.user,
            date__gte=start_date
        ).values('date').annotate(
            total=Sum('amount')
        ).order_by('date')
        
        if not daily_expenses:
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(list(daily_expenses))
        df['day_index'] = range(1, len(df) + 1)
        df['total'] = df['total'].apply(lambda x: float(x))
        
        return df
    
    def prepare_training_data(self, df):
        """
        Prepare data for model training.
        Returns X (day indices) and y (expense totals).
        """
        if df is None or len(df) < self.min_data_points:
            return None, None
        
        X = df[['day_index']].values
        y = df['total'].values
        
        return X, y
    
    def train_model(self, X, y):
        """
        Train Linear Regression model on historical data.
        """
        if X is None or y is None:
            return False
        
        try:
            # Fit the model
            self.model.fit(X, y)
            return True
        except Exception as e:
            print(f"Model training error: {e}")
            return False
    
    def predict_next_day(self):
        """
        Predict expense for the next day based on 10+ days of data.
        Returns predicted amount or None if insufficient data.
        """
        # Get historical data (last 30 days)
        df = self.get_historical_data(days=30)
        
        if df is None or len(df) < self.min_data_points:
            return {
                'success': False,
                'message': f'Insufficient data. Need at least {self.min_data_points} days of expense history.',
                'predicted_amount': None,
                'confidence': None
            }
        
        # Prepare training data
        X, y = self.prepare_training_data(df)
        
        # Train model
        if not self.train_model(X, y):
            return {
                'success': False,
                'message': 'Model training failed.',
                'predicted_amount': None,
                'confidence': None
            }
        
        # Predict next day (day_index = last_day + 1)
        next_day_index = len(df) + 1
        predicted_amount = self.model.predict([[next_day_index]])[0]
        
        # Calculate confidence (R² score)
        confidence = self.model.score(X, y) * 100
        
        # Get trend
        if len(df) >= 3:
            recent_avg = df.tail(5)['total'].mean()
            trend = 'increasing' if predicted_amount > recent_avg else 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'success': True,
            'predicted_amount': round(predicted_amount, 2),
            'confidence': round(confidence, 1),
            'trend': trend,
            'historical_data': df.to_dict('records'),
            'data_points': len(df)
        }
    
    def predict_next_n_months(self, n=3):
        """
        Predict expenses for the next N months.
        """
        df = self.get_historical_data(months=12)
        
        if df is None or len(df) < self.min_data_points:
            return None
        
        X, y = self.prepare_training_data(df)
        
        if not self.train_model(X, y):
            return None
        
        predictions = []
        last_month_index = len(df)
        
        for i in range(1, n + 1):
            month_index = last_month_index + i
            predicted = self.model.predict([[month_index]])[0]
            predictions.append({
                'month_offset': i,
                'predicted_amount': round(predicted, 2)
            })
        
        return predictions
    
    def get_spending_pattern(self):
        """
        Analyze spending pattern (increasing, decreasing, stable).
        """
        df = self.get_historical_data(months=6)
        
        if df is None or len(df) < 2:
            return 'insufficient_data'
        
        # Calculate trend using linear regression slope
        X, y = self.prepare_training_data(df)
        self.train_model(X, y)
        
        slope = self.model.coef_[0]
        
        if slope > 50:  # Increasing by more than $50/month
            return 'increasing'
        elif slope < -50:  # Decreasing by more than $50/month
            return 'decreasing'
        else:
            return 'stable'


def predict_next_day_expense(user):
    """
    Convenience function to predict next day's expense for a user.
    
    Args:
        user: Django User object
    
    Returns:
        dict: Prediction results
    """
    engine = ExpenseForecastEngine(user)
    return engine.predict_next_day()


def get_expense_forecast(user, months=3):
    """
    Get expense forecast for next N months.
    
    Args:
        user: Django User object
        months: Number of months to forecast
    
    Returns:
        list: Predictions for each month
    """
    engine = ExpenseForecastEngine(user)
    return engine.predict_next_n_months(months)
