import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from config import CHART_COLORS

def create_pie_chart(df):
    """Create a pie chart of spending by category"""
    
    if 'category' not in df.columns:
        raise ValueError("DataFrame must have 'category' column")
    
    # Calculate spending by category
    category_spending = df[df['amount'] < 0].groupby('category')['amount'].sum().abs()
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=category_spending.index,
        values=category_spending.values,
        marker=dict(
            colors=[CHART_COLORS['primary'], CHART_COLORS['secondary'], 
                   CHART_COLORS['success'], CHART_COLORS['danger']]
        ),
        hovertemplate='<b>%{label}</b><br>Spending: $%{value:,.2f}<br>%{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title="💰 Spending Breakdown by Category",
        font=dict(size=12),
        height=500
    )
    
    return fig

def create_line_chart(df):
    """Create a line chart of spending over time"""
    
    # Group by date and sum amounts
    daily_spending = df.groupby('date')['amount'].sum().reset_index()
    daily_spending['cumulative'] = daily_spending['amount'].cumsum()
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_spending['date'],
        y=daily_spending['amount'],
        name='Daily Spending',
        mode='lines',
        line=dict(color=CHART_COLORS['primary'], width=2),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Spending: $%{y:,.2f}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_spending['date'],
        y=daily_spending['cumulative'],
        name='Cumulative',
        mode='lines',
        line=dict(color=CHART_COLORS['secondary'], width=2, dash='dash'),
        yaxis='y2',
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Cumulative: $%{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="📈 Spending Trend Over Time",
        xaxis_title="Date",
        yaxis_title="Daily Spending ($)",
        yaxis2=dict(
            title="Cumulative Spending ($)",
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        height=500,
        font=dict(size=11)
    )
    
    return fig

def create_bar_chart(df, category=None):
    """Create a bar chart of spending by category or time period"""
    
    if category:
        data = df[df['category'] == category].groupby('date')['amount'].sum()
    else:
        data = df.groupby('category')['amount'].sum().abs()
    
    fig = go.Figure(data=[go.Bar(
        x=data.index,
        y=data.values,
        marker=dict(color=CHART_COLORS['primary']),
        hovertemplate='%{x}<br>Amount: $%{y:,.2f}<extra></extra>'
    )])
    
    fig.update_layout(
        title=f"📊 {'Spending by Category' if not category else f'{category} Spending Over Time'}",
        xaxis_title="Category" if not category else "Date",
        yaxis_title="Amount ($)",
        height=500,
        font=dict(size=11)
    )
    
    return fig

def create_heatmap(df):
    """Create a heatmap of spending by day of week and hour"""
    
    df['day_of_week'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    
    # Pivot table for heatmap
    heatmap_data = df.pivot_table(
        values='amount',
        index='day_of_week',
        columns='hour',
        aggfunc='sum',
        fill_value=0
    )
    
    # Reorder days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = heatmap_data.reindex([d for d in day_order if d in heatmap_data.index])
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='RdYlGn_r',
        hovertemplate='Day: %{y}<br>Hour: %{x}<br>Spending: $%{z:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="🔥 Spending Heatmap (Day & Hour)",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        height=400,
        font=dict(size=11)
    )
    
    return fig

def create_box_plot(df):
    """Create a box plot of spending distribution by category"""
    
    fig

