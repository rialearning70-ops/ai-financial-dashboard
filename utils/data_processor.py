import pandas as pd
import io

def load_csv(uploaded_file):
    """Load and parse CSV file from Streamlit uploader"""
    try:
        df = pd.read_csv(uploaded_file)
        
        # Standardize column names
        df.columns = df.columns.str.strip().str.lower()
        
        # Ensure required columns exist
        required_cols = ['date', 'description', 'amount']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"CSV must contain columns: {', '.join(required_cols)}")
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Convert amount to float
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # Remove rows with null values
        df = df.dropna(subset=['date', 'amount'])
        
        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    
    except Exception as e:
        raise Exception(f"Error loading CSV: {str(e)}")

def validate_data(df):
    """Validate dataframe has required structure"""
    required_cols = ['date', 'description', 'amount']
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"DataFrame must contain columns: {', '.join(required_cols)}")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    return True

def get_monthly_summary(df):
    """Get monthly spending summary"""
    df['year_month'] = df['date'].dt.to_period('M')
    monthly = df.groupby('year_month')['amount'].agg(['sum', 'count', 'mean'])
    return monthly

def get_category_summary(df):
    """Get spending by category"""
    if 'category' not in df.columns:
        raise ValueError("DataFrame must have 'category' column")
    
    category_summary = df.groupby('category')['amount'].agg(['sum', 'count', 'mean'])
    category_summary.columns = ['Total', 'Count', 'Average']
    return category_summary.sort_values('Total')

def calculate_statistics(df):
    """Calculate spending statistics"""
    stats = {
        'total_transactions': len(df),
        'total_spent': abs(df[df['amount'] < 0]['amount'].sum()),
        'total_income': df[df['amount'] > 0]['amount'].sum(),
        'average_transaction': df['amount'].mean(),
        'median_transaction': df['amount'].median(),
        'std_deviation': df['amount'].std(),
        'min_transaction': df['amount'].min(),
        'max_transaction': df['amount'].max(),
    }
    return stats
