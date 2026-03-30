import pandas as pd
from config import EXPENSE_CATEGORIES, MONTHLY_BUDGET_WARNING, CATEGORY_SPENDING_WARNING

def generate_suggestions(df):
    """Generate AI-powered financial suggestions based on spending patterns"""
    
    suggestions = []
    
    # 1. High spending categories
    category_spending = df[df['amount'] < 0].groupby('category')['amount'].sum().abs()
    top_category = category_spending.idxmax()
    top_amount = category_spending.max()
    
    suggestions.append({
        'title': f'🎯 Reduce {top_category} Spending',
        'description': f"Your highest spending category is {top_category} at ${top_amount:,.2f}. Consider cutting back by 10-15% to save ${top_amount * 0.10:,.2f}-${top_amount * 0.15:,.2f} per month.",
        'savings': top_amount * 0.10
    })
    
    # 2. Subscription check
    subscriptions = df[df['description'].str.contains('subscription|membership|premium', case=False, na=False)]
    if not subscriptions.empty:
        monthly_subs = abs(subscriptions['amount'].sum())
        suggestions.append({
            'title': '📺 Review Your Subscriptions',
            'description': f"You're spending ${monthly_subs:,.2f} on subscriptions and memberships. Review unused services and cancel them.",
            'savings': monthly_subs * 0.3
        })
    
    # 3. Dining out analysis
    dining = df[df['category'] == 'Dining']
    if not dining.empty:
        dining_total = abs(dining['amount'].sum())
        dining_count = len(dining)
        avg_dining = dining_total / dining_count if dining_count > 0 else 0
        
        suggestions.append({
            'title': '🍽️ Cook More at Home',
            'description': f"You spent ${dining_total:,.2f} on dining ({dining_count} times). Cooking at home could save you ${dining_total * 0.5:,.2f}/month.",
            'savings': dining_total * 0.5
        })
    
    # 4. Transportation optimization
    transportation = df[df['category'] == 'Transportation']
    if not transportation.empty:
        trans_total = abs(transportation['amount'].sum())
        suggestions.append({
            'title': '🚗 Optimize Transportation',
            'description': f"Consider carpooling or public transit to reduce your ${trans_total:,.2f} transportation costs.",
            'savings': trans_total * 0.2
        })
    
    # 5. Shopping patterns
    shopping = df[df['category'] == 'Shopping']
    if not shopping.empty:
        shopping_total = abs(shopping['amount'].sum())
        suggestions.append({
            'title': '🛍️ Smart Shopping',
            'description': f"Plan purchases ahead and use coupons/cashback apps to reduce ${shopping_total:,.2f} shopping expenses.",
            'savings': shopping_total * 0.15
        })
    
    # 6. Budget alerts
    total_spending = abs(df[df['amount'] < 0]['amount'].sum())
    if total_spending > 0:
        suggestions.append({
            'title': '📊*

