"""
Utils module for AI Financial Dashboard
Exports all utility functions for easy importing
"""

from .data_processor import (
    load_csv,
    validate_data,
    get_monthly_summary,
    get_category_summary,
    calculate_statistics
)

from .categorizer import (
    categorize_expenses,
    get_category_spending,
    get_spending_by_category_and_month,
    detect_anomalies,
    categorize_by_custom_rules
)

from .charts import (
    create_pie_chart,
    create_line_chart,
    create_bar_chart,
    create_heatmap,
    create_box_plot
)

from .ai_suggestions import (
    generate_suggestions,
    get_spending_forecast,
    get_budget_recommendations,
    detect_spending_anomalies
)

__all__ = [
    # Data Processor
    'load_csv',
    'validate_data',
    'get_monthly_summary',
    'get_category_summary',
    'calculate_statistics',
    # Categorizer
    'categorize_expenses',
    'get_category_spending',
    'get_spending_by_category_and_month',
    'detect_anomalies',
    'categorize_by_custom_rules',
    # Charts
    'create_pie_chart',
    'create_line_chart',
    'create_bar_chart',
    'create_heatmap',
    'create_box_plot',
    # AI Suggestions
    'generate_suggestions',
    'get_spending_forecast',
    'get_budget_recommendations',
    'detect_spending_anomalies',
]
