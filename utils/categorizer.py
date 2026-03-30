import pandas as pd
from config import EXPENSE_CATEGORIES

def categorize_expenses(df):
    """Categorize expenses based on description keywords"""
    
    # Make a copy to avoid modifying original
    df = df.copy()
    
    # Initialize category column
    df['category'] = 'Other'
    
    # Convert description to lowercase for matching
    df['description_lower'] = df['description'].str.lower()
    
    # Match keywords to categories
    for category, keywords in EXPENSE_CATEGORIES.items():
        for keyword in keywords:
            mask = df['description_lower'].str.contains(keyword, case=False, na=False)
            df.loc[mask, 'category'] = category
    
    # Drop temporary column
    df = df.drop('description_lower', axis=1)
    
    return df

def get_category_spending(df, category=None):
    """Get spending for a specific category or all categories"""
    
    if 'category' not in df.columns:
        raise ValueError("DataFrame must have 'category' column")
    
    if category:
        return df[df['category'] == category]['amount'].sum()
    else:
        return df.groupby('category')['amount'].sum()

def get_spending_by_category_and_month(df):
    """Get spending breakdown by category and month"""
    
    if 'category' not in df.columns:
        raise ValueError("DataFrame must have 'category' column")
    
    df['year_month'] = df['date'].dt.to_period('M')
    pivot = df.pivot_table(
        values='amount',
        index='year_month',
        columns='category',
        aggfunc='sum',
        fill_value=0
    )
    
    return pivot

def detect_anomalies(df, threshold=2.0):
    """Detect spending anomalies using standard deviation"""
    
    if 'category' not in df.columns:
        raise ValueError("DataFrame must have 'category' column")
    
    anomalies = []
    
    for category in df['category'].unique():
        category_data = df[df['category'] == category]['amount']
        
        if len(category_data) < 3:
            continue
        
        mean = category_data.mean()
        std = category_data.std()
        
        # Find transactions outside threshold * std from mean
        outliers = category_data[abs(category_data - mean) > threshold * std]
        
        for idx, value in outliers.items():
            anomalies.append({
                'date': df.loc[idx, 'date'],
                'category': category,
                'amount': value,
                'description': df.loc[idx, 'description'],
                'deviation': abs(value - mean) / std if std > 0 else 0
            })
    
    return pd.DataFrame(anomalies) if anomalies else pd.DataFrame()

def categorize_by_custom_rules(df, rules_dict):
    """Apply custom categorization rules"""
    
    df = df.copy()
    df['category'] = 'Other'
    
    for category, keywords in rules_dict.items():
        mask = df['description'].str.lower().str.contains(
            '|'.join(keywords),
            case=False,
            na=False
        )
        df.loc[mask, 'category'] = category
    
    return df
