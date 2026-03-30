# Configuration settings for the app

# Expense categories with keywords for automatic detection
EXPENSE_CATEGORIES = {
    'Groceries': ['grocery', 'supermarket', 'whole foods', 'trader joe', 'safeway', 'kroger', 'food market'],
    'Transportation': ['uber', 'lyft', 'gas', 'shell', 'chevron', 'parking', 'transit', 'metro'],
    'Dining': ['restaurant', 'coffee', 'cafe', 'pizza', 'burger', 'sushi', 'diner', 'bar'],
    'Entertainment': ['cinema', 'movie', 'spotify', 'netflix', 'game', 'steam', 'theatre'],
    'Shopping': ['amazon', 'target', 'walmart', 'mall', 'clothing', 'store', 'retail'],
    'Utilities': ['electric', 'water', 'gas bill', 'internet', 'phone', 'utility'],
    'Healthcare': ['pharmacy', 'doctor', 'hospital', 'clinic', 'medical', 'health'],
    'Fitness': ['gym', 'yoga', 'fitness', 'trainer', 'sports'],
    'Travel': ['airline', 'hotel', 'booking', 'airbnb', 'flight'],
    'Subscriptions': ['subscription', 'membership', 'premium'],
}

# Chart colors
CHART_COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
}

# Dashboard thresholds
MONTHLY_BUDGET_WARNING = 0.8  # Warn if spending reaches 80% of typical
CATEGORY_SPENDING_WARNING = 0.9  # Warn if category exceeds 90% of typicaly

