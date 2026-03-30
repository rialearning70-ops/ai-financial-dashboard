"""
AI Financial Health Dashboard
Hackathon Starter  Python + Streamlit + Pandas + Plotly + Claude AI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import anthropic
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
import json
import io
from datetime import datetime

# ---------------------------------------------
# PAGE CONFIG
# ---------------------------------------------
st.set_page_config(
    page_title="AI Financial Health Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------
# CUSTOM CSS  Refined dark financial theme
# ---------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg-primary: #0a0e1a;
    --bg-card: #111827;
    --bg-card2: #1a2235;
    --accent-green: #00e5a0;
    --accent-amber: #f59e0b;
    --accent-red: #f43f5e;
    --accent-blue: #3b82f6;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --border: rgba(255,255,255,0.07);
}

html, body, .stApp {
    background-color: var(--bg-primary) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text-primary);
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* Headings */
h1, h2, h3 { font-family: 'Syne', sans-serif !important; font-weight: 800; }
h1 { font-size: 2rem !important; letter-spacing: -0.5px; }

/* Metric cards */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.2rem !important;
}
[data-testid="metric-container"] label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
    color: var(--text-secondary) !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.6rem !important;
    font-weight: 700;
}

/* File uploader */
[data-testid="stFileUploadDropzone"] {
    background: var(--bg-card2) !important;
    border: 2px dashed rgba(0,229,160,0.3) !important;
    border-radius: 12px !important;
}

/* Tabs */
[data-testid="stTabs"] button {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--text-secondary) !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--accent-green) !important;
    border-bottom-color: var(--accent-green) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #00e5a0, #00b4d8) !important;
    color: #0a0e1a !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
}

/* AI suggestion box */
.ai-box {
    background: linear-gradient(135deg, rgba(0,229,160,0.05), rgba(59,130,246,0.05));
    border: 1px solid rgba(0,229,160,0.2);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
    line-height: 1.7;
}

/* Category badges */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-family: 'DM Mono', monospace;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden;
}

/* Section headers */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
}

/* Risk score gauge label */
.risk-label {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    text-align: center;
}

.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------
# CONSTANTS  Expense Categories
# ---------------------------------------------
CATEGORY_KEYWORDS = {
    " Food & Dining":    ["zomato", "swiggy", "restaurant", "cafe", "food", "dining", "hotel", "pizza", "burger", "biryani"],
    " Transport":        ["uber", "ola", "rapido", "metro", "fuel", "petrol", "parking", "toll", "cab", "auto"],
    " Groceries":        ["bigbasket", "blinkit", "dmart", "supermarket", "grocery", "fresh", "zepto", "vegetables", "fruits"],
    " Health":           ["pharmacy", "hospital", "doctor", "clinic", "apollo", "medplus", "medicine", "health", "lab"],
    " Entertainment":    ["netflix", "prime", "hotstar", "spotify", "movie", "pvr", "inox", "game", "concert"],
    " Shopping":         ["amazon", "flipkart", "myntra", "meesho", "nykaa", "mall", "shop", "store", "fashion"],
    " Utilities":        ["electricity", "water", "gas", "internet", "airtel", "jio", "vodafone", "broadband", "mobile", "recharge"],
    " Rent & Housing":   ["rent", "maintenance", "society", "housing", "loan emi", "mortgage"],
    " Education":        ["udemy", "coursera", "fees", "school", "college", "book", "tuition", "coaching"],
    " Investments":      ["sip", "mutual fund", "zerodha", "groww", "stocks", "nps", "ppf", "fd", "rd"],
    " Banking":          ["atm", "withdrawal", "transfer", "neft", "upi", "charges", "interest"],
    " Travel":           ["flight", "hotel booking", "makemytrip", "goibibo", "irctc", "train", "bus"],
}

PORTFOLIO_KEYWORDS = {
    "Equity  Large Cap":    ["nifty 50", "sensex", "large cap", "bluechip", "hdfc top", "sbi bluechip"],
    "Equity  Mid Cap":      ["mid cap", "nippon growth", "kotak emerging", "motilal midcap"],
    "Equity  Small Cap":    ["small cap", "nippon small", "axis small", "quant small"],
    "Equity  Flexi/Multi":  ["flexi cap", "parag parikh", "multi cap"],
    "Hybrid":                ["hybrid", "balanced", "aggressive hybrid", "equity savings", "altiva", "long-short"],
    "Debt":                  ["debt", "liquid", "overnight", "gilt", "bond", "fd", "fixed deposit"],
    "Gold / Commodities":    ["gold", "silver", "commodity", "sgb", "goldbees"],
    "International":         ["us fund", "nasdaq", "global", "international", "fof"],
    "SIF":                   ["sif", "specialised investment", "edelweiss sif", "altiva"],
}

CATEGORY_COLORS = {
    " Food & Dining": "#f43f5e",
    " Transport": "#f59e0b",
    " Groceries": "#10b981",
    " Health": "#06b6d4",
    " Entertainment": "#8b5cf6",
    " Shopping": "#ec4899",
    " Utilities": "#3b82f6",
    " Rent & Housing": "#6366f1",
    " Education": "#14b8a6",
    " Investments": "#00e5a0",
    " Banking": "#64748b",
    " Travel": "#f97316",
    " Other": "#475569",
}

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#94a3b8", size=12),
    margin=dict(l=10, r=10, t=30, b=10),
)


# ---------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------

def categorize_transaction(description: str) -> str:
    desc = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in desc for kw in keywords):
            return category
    return " Other"


def categorize_portfolio(description: str) -> str:
    desc = description.lower()
    for asset_class, keywords in PORTFOLIO_KEYWORDS.items():
        if any(kw in desc for kw in keywords):
            return asset_class
    return " Other"



def parse_pdf_statement(uploaded_file) -> pd.DataFrame:
    """Parse PDF bank statement using pdfplumber."""
    try:
        import pdfplumber, re
        rows = []
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if row and any(cell for cell in row if cell):
                            rows.append([str(c).strip() if c else "" for c in row])

        if not rows:
            st.error("No tables found in PDF. Please try CSV format.")
            return pd.DataFrame()

        # Use first row as header
        headers = [h.lower().strip() for h in rows[0]]
        df = pd.DataFrame(rows[1:], columns=headers)
        df = df[df.apply(lambda r: r.astype(str).str.strip().ne("").any(), axis=1)]

        # Now run through the same CSV parser logic
        import io
        csv_buf = io.StringIO()
        df.to_csv(csv_buf, index=False)
        csv_buf.seek(0)
        return parse_bank_statement(csv_buf)

    except Exception as e:
        st.error(f"PDF parsing error: {e}. Please try downloading as CSV from your bank.")
        return pd.DataFrame()

def parse_bank_statement(uploaded_file) -> pd.DataFrame:
    """Parse uploaded CSV bank statement - handles any Indian bank format."""
    try:
        # Try reading with different encodings
        try:
            df = pd.read_csv(uploaded_file, encoding="utf-8")
        except Exception:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding="latin1")

        # Clean column names
        df.columns = df.columns.str.strip().str.lower().str.replace(r'\s+', ' ', regex=True)

        # Show detected columns in sidebar for debugging
        st.sidebar.caption(f"Detected columns: {list(df.columns)}")

        # Flexible column mapping - extended for all Indian banks
        col_map = {
            "date": ["date", "txn date", "transaction date", "value date",
                     "posting date", "trans date", "tran date", "book date",
                     "transaction\ndate", "valuedate"],
            "description": ["description", "narration", "particulars", "remarks",
                            "details", "transaction details", "transaction remarks",
                            "chq/ref no. / transaction remarks", "transaction narration",
                            "tran particular", "trans particulars", "ref no./cheque no.",
                            "transaction description", "trans description"],
            "debit": ["debit", "withdrawal", "dr", "debit amount", "withdrawals",
                      "withdrawal amt.", "debit(inr)", "dr amount", "withdrawal amount",
                      "debit amount(inr)", "amount(dr)", "tran amount(dr)"],
            "credit": ["credit", "deposit", "cr", "credit amount", "deposits",
                       "deposit amt.", "credit(inr)", "cr amount", "deposit amount",
                       "credit amount(inr)", "amount(cr)", "tran amount(cr)"],
            "amount": ["amount", "transaction amount", "tran amount",
                       "trans amount", "net amount"],
            "balance": ["balance", "closing balance", "available balance",
                        "running balance", "balance(inr)", "bal"],
        }

        rename = {}
        for standard, variants in col_map.items():
            for v in variants:
                if v in df.columns:
                    rename[v] = standard
                    break
        df = df.rename(columns=rename)

        # Drop completely empty rows
        df = df.dropna(how="all")

        # Normalize amounts - clean commas, spaces, dashes
        def clean_amount(col):
            return pd.to_numeric(
                df[col].astype(str)
                    .str.replace(",", "")
                    .str.replace(" ", "")
                    .str.replace("-", "")
                    .str.strip(),
                errors="coerce"
            ).fillna(0)

        if "debit" in df.columns and "credit" in df.columns:
            df["debit"] = clean_amount("debit")
            df["credit"] = clean_amount("credit")
            df["amount"] = df.apply(lambda r: r["credit"] if r["credit"] > 0 else r["debit"], axis=1)
            df["type"] = df.apply(lambda r: "Credit" if r["credit"] > 0 else "Debit", axis=1)

        elif "amount" in df.columns:
            df["amount"] = clean_amount("amount")
            # Try to detect credits from description keywords
            credit_keywords = ["salary", "credit", "deposit", "refund", "cashback",
                               "reversal", "dividend", "interest credit", "neft cr",
                               "imps cr", "upi cr", "cr-"]
            if "description" in df.columns:
                is_credit = df["description"].astype(str).str.lower().str.contains(
                    "|".join(credit_keywords), na=False)
                df["type"] = is_credit.map({True: "Credit", False: "Debit"})
            else:
                df["type"] = "Debit"
            df["amount"] = df["amount"].abs()

        else:
            # Last resort: find any numeric column and use it as amount
            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            if numeric_cols:
                df["amount"] = df[numeric_cols[0]].abs()
                df["type"] = "Debit"
            else:
                st.error("Could not find amount column in your CSV. Please check the format.")
                return pd.DataFrame()

        # Ensure type column always exists
        if "type" not in df.columns:
            df["type"] = "Debit"

        # Parse date
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
            df = df.dropna(subset=["date"])
            df["month"] = df["date"].dt.strftime("%b %Y")
            df["month_num"] = df["date"].dt.to_period("M")
        else:
            df["date"] = pd.Timestamp.now()
            df["month"] = "Current"
            df["month_num"] = pd.Period.now("M")

        # Ensure description column exists
        if "description" not in df.columns:
            text_cols = df.select_dtypes(include="object").columns.tolist()
            if text_cols:
                df["description"] = df[text_cols[0]]
            else:
                df["description"] = "Unknown"

        # Categorize
        df["category"] = df["description"].astype(str).apply(categorize_transaction)

        # Filter out zero-amount rows
        df = df[df["amount"] > 0].reset_index(drop=True)

        return df

    except Exception as e:
        st.error(f"Error parsing file: {str(e)}")
        st.info("Tip: Make sure your CSV has columns for Date, Description/Narration, and Debit/Credit or Amount.")
        return pd.DataFrame()


def get_sample_data() -> pd.DataFrame:
    """Generate realistic sample bank statement data."""
    data = {
        "date": pd.date_range("2025-09-01", periods=60, freq="5D"),
        "description": [
            "Zomato Order", "Uber Ride", "BigBasket Groceries", "Netflix Subscription",
            "Amazon Shopping", "Airtel Recharge", "Rent Payment", "Swiggy Delivery",
            "Apollo Pharmacy", "Petrol Station", "Myntra Purchase", "Udemy Course",
            "PVR Movie Tickets", "Ola Auto", "DMart Groceries", "Spotify Premium",
            "Electricity Bill", "Flipkart Order", "Metro Card Recharge", "Restaurant Dinner",
            "SIP - Nippon Mid Cap", "Zerodha Stocks", "ATM Withdrawal", "Hotel Booking MakeMyTrip",
            "IRCTC Train Ticket", "Parag Parikh Flexi Cap SIP", "MedPlus Medicine", "Rapido Bike",
            "Blinkit Quick Delivery", "Hotstar Annual", "SIP - Axis Small Cap", "Nykaa Order",
            "Water Bill", "Cafe Coffee Day", "Groww Mutual Fund", "HDFC Top 100 SIP",
            "Inox Movie", "Ola Cab Airport", "Fresh Vegetables Local", "Amazon Prime",
            "PPF Deposit", "NPS Contribution", "Food Court Mall", "Petrol Mahindra",
            "Meesho Shopping", "Jio Postpaid", "Coaching Fees", "Zepto Groceries",
            "Concert Tickets", "SGB Gold Bond", "ICICI Bank Charges", "Salary Credit",
            "Freelance Income", "EMI Home Loan", "Insurance Premium", "Gym Membership",
            "BookMyShow", "Society Maintenance", "Gas Cylinder", "Dividend Credit"
        ],
        "amount": [
            350, 180, 2100, 649, 3200, 399, 18000, 280, 450, 3200, 1800, 999,
            600, 120, 3500, 129, 1850, 2400, 200, 1200,
            5000, 10000, 5000, 4200, 1800, 8000, 680, 95,
            750, 1499, 3000, 1650, 400, 380, 2000, 5000,
            500, 950, 320, 1499,
            50000, 5000, 520, 4100,
            890, 799, 8500, 680,
            2500, 15000, 250, 85000,
            25000, 22000, 12000, 800,
            350, 2500, 900, 3200
        ],
        "type": [
            "Debit", "Debit", "Debit", "Debit", "Debit", "Debit", "Debit", "Debit",
            "Debit", "Debit", "Debit", "Debit", "Debit", "Debit", "Debit", "Debit",
            "Debit", "Debit", "Debit", "Debit",
            "Debit", "Debit", "Debit", "Debit", "Debit", "Debit", "Debit", "Debit",
            "Debit", "Debit", "Debit", "Debit",
            "Debit", "Debit", "Debit", "Debit",
            "Debit", "Debit", "Debit", "Debit",
            "Debit", "Debit", "Debit", "Debit",
            "Debit", "Debit", "Debit", "Debit",
            "Debit", "Debit", "Debit", "Credit",
            "Credit", "Debit", "Debit", "Debit",
            "Debit", "Debit", "Debit", "Credit"
        ]
    }
    df = pd.DataFrame(data)
    df["month"] = df["date"].dt.strftime("%b %Y")
    df["month_num"] = df["date"].dt.to_period("M")
    df["category"] = df["description"].apply(categorize_transaction)
    return df


def compute_risk_score(df: pd.DataFrame) -> dict:
    """Compute a portfolio risk score from transaction data."""
    invest_df = df[df["category"] == " Investments"]
    total_invested = invest_df["amount"].sum()
    total_spend = df[df["type"] == "Debit"]["amount"].sum()

    savings_rate = (total_invested / total_spend * 100) if total_spend > 0 else 0

    # Categorize investments by type
    invest_df = invest_df.copy()
    invest_df["asset_class"] = invest_df["description"].apply(categorize_portfolio)
    asset_alloc = invest_df.groupby("asset_class")["amount"].sum()

    equity = asset_alloc.get("Equity  Large Cap", 0) + asset_alloc.get("Equity  Mid Cap", 0) + \
             asset_alloc.get("Equity  Small Cap", 0) + asset_alloc.get("Equity  Flexi/Multi", 0)
    hybrid = asset_alloc.get("Hybrid", 0) + asset_alloc.get("SIF", 0)
    debt = asset_alloc.get("Debt", 0)
    gold = asset_alloc.get("Gold / Commodities", 0)
    intl = asset_alloc.get("International", 0)
    total_inv = max(total_invested, 1)

    equity_pct = equity / total_inv * 100
    hybrid_pct = hybrid / total_inv * 100
    debt_pct = debt / total_inv * 100

    # Risk score 1-10
    risk_score = round(
        (equity_pct * 0.07) +
        (hybrid_pct * 0.04) +
        (debt_pct * 0.01) +
        (intl / total_inv * 100 * 0.08)
    , 1)
    risk_score = min(max(risk_score, 1), 10)

    if risk_score >= 7.5:
        risk_label, risk_color = "Aggressive", "#f43f5e"
    elif risk_score >= 5:
        risk_label, risk_color = "Moderate-Aggressive", "#f59e0b"
    elif risk_score >= 3:
        risk_label, risk_color = "Moderate", "#3b82f6"
    else:
        risk_label, risk_color = "Conservative", "#10b981"

    return {
        "score": risk_score,
        "label": risk_label,
        "color": risk_color,
        "savings_rate": round(savings_rate, 1),
        "equity_pct": round(equity_pct, 1),
        "debt_pct": round(debt_pct, 1),
        "hybrid_pct": round(hybrid_pct, 1),
        "asset_alloc": asset_alloc,
        "total_invested": total_invested,
    }


def get_ai_suggestions(df: pd.DataFrame, risk: dict) -> str:
    """Call Claude API for personalized financial suggestions."""
    expenses_by_cat = df[df["type"] == "Debit"].groupby("category")["amount"].sum().sort_values(ascending=False)
    top_expenses = expenses_by_cat.head(5).to_dict()
    total_spend = df[df["type"] == "Debit"]["amount"].sum()
    total_income = df[df["type"] == "Credit"]["amount"].sum()

    summary = f"""
Client Financial Summary:
- Total Income (Credits): {total_income:,.0f}
- Total Expenses (Debits): {total_spend:,.0f}
- Total Invested: {risk['total_invested']:,.0f}
- Savings/Investment Rate: {risk['savings_rate']}%
- Portfolio Risk Profile: {risk['label']} (Score: {risk['score']}/10)
- Equity Allocation: {risk['equity_pct']}%
- Debt Allocation: {risk['debt_pct']}%
- Hybrid Allocation: {risk['hybrid_pct']}%

Top 5 Expense Categories:
{json.dumps({k: f'{v:,.0f}' for k, v in top_expenses.items()}, indent=2)}
"""

    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system="""You are an expert Indian financial advisor (RIA). 
Analyze the client's financial data and provide 4-5 specific, actionable suggestions.
Format each suggestion as a short heading followed by 1-2 sentences of explanation.
Use  for Indian rupees. Be warm, practical, and encouraging.
Focus on: expense optimization, investment suggestions, savings improvements, and risk management.
Keep it concise  no more than 250 words total.""",
            messages=[{"role": "user", "content": summary}]
        )
        return response.content[0].text
    except Exception as e:
        return f"""** Spending Pattern Alert**
Your top expense category warrants attention. Consider setting monthly caps using UPI app limits.

** Investment Opportunity**
Your current savings rate of {risk['savings_rate']}% can be improved. Target 20-30% of income for long-term wealth creation.

** Portfolio Rebalancing**
With {risk['equity_pct']}% equity exposure, ensure you have adequate emergency fund (6 months of expenses) before increasing equity allocation.

** Tax Efficiency**
Explore ELSS funds (1.5L under 80C), NPS (additional 50K under 80CCD), and HRA benefits if applicable.

** Goal-Based Investing**
Map each SIP to a specific goal (retirement, home, child education) with a defined timeline for better discipline.

*(AI suggestions unavailable  API key not configured. Add ANTHROPIC_API_KEY to enable.)*"""


# ---------------------------------------------
# CHART HELPERS
# ---------------------------------------------

def chart_expense_donut(df: pd.DataFrame):
    expenses = df[df["type"] == "Debit"].groupby("category")["amount"].sum().reset_index()
    expenses = expenses[expenses["amount"] > 0]
    colors = [CATEGORY_COLORS.get(c, "#475569") for c in expenses["category"]]

    fig = go.Figure(go.Pie(
        labels=expenses["category"],
        values=expenses["amount"],
        hole=0.65,
        marker_colors=colors,
        textinfo="percent",
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_THEME,
        showlegend=True,
        legend=dict(font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
        annotations=[dict(text="Expenses", x=0.5, y=0.5, font_size=14,
                         font_family="Syne", font_color="#f1f5f9", showarrow=False)]
    )
    return fig


def chart_monthly_trend(df: pd.DataFrame):
    monthly = df[df["type"] == "Debit"].groupby("month_num")["amount"].sum().reset_index()
    monthly["month_str"] = monthly["month_num"].dt.strftime("%b %Y")
    monthly = monthly.sort_values("month_num")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly["month_str"], y=monthly["amount"],
        marker_color="#00e5a0", marker_opacity=0.8,
        name="Expenses",
        hovertemplate="<b>%{x}</b><br>%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_THEME,
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickprefix=""),
        showlegend=False,
    )
    return fig


def chart_category_bar(df: pd.DataFrame):
    expenses = df[df["type"] == "Debit"].groupby("category")["amount"].sum().reset_index()
    expenses = expenses.sort_values("amount", ascending=True)
    colors = [CATEGORY_COLORS.get(c, "#475569") for c in expenses["category"]]

    fig = go.Figure(go.Bar(
        x=expenses["amount"], y=expenses["category"],
        orientation="h",
        marker_color=colors,
        hovertemplate="<b>%{y}</b><br>%{x:,.0f}<extra></extra>",
        text=[f"{v:,.0f}" for v in expenses["amount"]],
        textposition="outside",
        textfont=dict(size=10, color="#94a3b8"),
    ))
    fig.update_layout(
        **PLOTLY_THEME,
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickprefix=""),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        height=400,
    )
    return fig


def chart_risk_gauge(score: float, color: str):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "/10", "font": {"size": 28, "family": "Syne", "color": color}},
        gauge={
            "axis": {"range": [0, 10], "tickcolor": "#475569", "tickfont": {"size": 9}},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 3], "color": "rgba(16,185,129,0.15)"},
                {"range": [3, 5], "color": "rgba(59,130,246,0.15)"},
                {"range": [5, 7.5], "color": "rgba(245,158,11,0.15)"},
                {"range": [7.5, 10], "color": "rgba(244,63,94,0.15)"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "value": score},
        },
    ))
    fig.update_layout(**PLOTLY_THEME, height=220)
    return fig


def chart_asset_allocation(asset_alloc: pd.Series):
    if asset_alloc.empty:
        return None
    fig = go.Figure(go.Bar(
        x=asset_alloc.values,
        y=asset_alloc.index,
        orientation="h",
        marker_color=["#00e5a0", "#3b82f6", "#f59e0b", "#8b5cf6", "#f43f5e", "#06b6d4", "#10b981"],
        hovertemplate="<b>%{y}</b><br>%{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_THEME,
        xaxis=dict(tickprefix="", gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        height=260,
    )
    return fig


# ---------------------------------------------
# SIDEBAR
# ---------------------------------------------
with st.sidebar:
    st.markdown("##  FinHealth AI")
    st.markdown('<p class="section-label">Data Source</p>', unsafe_allow_html=True)
    st.markdown("## Upload Data"); data_source = st.radio("", [" Upload CSV", " Use Sample Data"], label_visibility="collapsed")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    uploaded_file = None
    if data_source == " Upload CSV":
        uploaded_file = st.file_uploader("Upload Bank Statement", type=["csv", "pdf"], label_visibility="collapsed")
        st.caption("Supports CSV and PDF bank statements (HDFC, SBI, ICICI, Axis, Kotak)")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-label">Filters</p>', unsafe_allow_html=True)
    show_credits = st.toggle("Include Credits/Income", value=False)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-label">About</p>', unsafe_allow_html=True)
    st.caption("AI Financial Health Dashboard\nHackathon Project  Powered by Claude AI")


# ---------------------------------------------
# LOAD DATA
# ---------------------------------------------
if uploaded_file:
    if uploaded_file.name.lower().endswith(".pdf"):
        df = parse_pdf_statement(uploaded_file)
    else:
        df = parse_bank_statement(uploaded_file)
else:
    df = get_sample_data()

if df.empty:
    st.error("Could not parse the uploaded file. Please check the format.")
    st.stop()

expenses_df = df[df["type"] == "Debit"]
income_df = df[df["type"] == "Credit"]
risk = compute_risk_score(df)


# ---------------------------------------------
# HEADER
# ---------------------------------------------
col_title, col_badge = st.columns([3, 1])
with col_title:
    st.markdown("# AI Financial Health Dashboard")
    source_label = "Live Data" if uploaded_file else "Sample Data"
    st.markdown(f'<p class="section-label"> {source_label}  {len(df)} Transactions Analyzed</p>', unsafe_allow_html=True)
with col_badge:
    st.markdown(f"""
    <div style="text-align:right; padding-top:0.8rem;">
        <span style="background:rgba(0,229,160,0.1); border:1px solid rgba(0,229,160,0.3);
              color:#00e5a0; padding:4px 14px; border-radius:20px;
              font-family:'DM Mono',monospace; font-size:0.7rem; letter-spacing:1px;">
             LIVE ANALYSIS
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ---------------------------------------------
# KPI METRICS
# ---------------------------------------------
m1, m2, m3, m4, m5 = st.columns(5)
total_spend = expenses_df["amount"].sum()
total_income = income_df["amount"].sum()
total_invested = risk["total_invested"]
avg_monthly = expenses_df.groupby("month_num")["amount"].sum().mean() if not expenses_df.empty else 0
net_savings = total_income - total_spend

m1.metric("Total Spend", f"{total_spend/1e5:.1f}L" if total_spend >= 1e5 else f"{total_spend:,.0f}")
m2.metric("Total Income", f"{total_income/1e5:.1f}L" if total_income >= 1e5 else f"{total_income:,.0f}")
m3.metric("Total Invested", f"{total_invested/1e5:.1f}L" if total_invested >= 1e5 else f"{total_invested:,.0f}")
m4.metric("Avg Monthly Spend", f"{avg_monthly:,.0f}")
m5.metric("Savings Rate", f"{risk['savings_rate']}%", delta="Target: 20%+" if risk["savings_rate"] < 20 else " On Track")

st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------------------------
# TABS
# ---------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([" Expense Analysis", " Portfolio Risk", " AI Suggestions", " Transactions"])


# -- TAB 1: EXPENSE ANALYSIS ------------------
with tab1:
    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown('<p class="section-label">Expense Breakdown</p>', unsafe_allow_html=True)
        st.plotly_chart(chart_expense_donut(expenses_df), use_container_width=True, config={"displayModeBar": False})

    with c2:
        st.markdown('<p class="section-label">Monthly Trend</p>', unsafe_allow_html=True)
        st.plotly_chart(chart_monthly_trend(expenses_df), use_container_width=True, config={"displayModeBar": False})

    st.markdown('<p class="section-label">Category Comparison</p>', unsafe_allow_html=True)
    st.plotly_chart(chart_category_bar(expenses_df), use_container_width=True, config={"displayModeBar": False})

    # Top transactions
    st.markdown('<p class="section-label">Top 10 Transactions</p>', unsafe_allow_html=True)
    top10 = expenses_df.nlargest(10, "amount")[["date", "description", "category", "amount"]].copy()
    top10["date"] = top10["date"].dt.strftime("%d %b %Y")
    top10["amount"] = top10["amount"].apply(lambda x: f"{x:,.0f}")
    st.dataframe(top10, use_container_width=True, hide_index=True)


# -- TAB 2: PORTFOLIO RISK --------------------
with tab2:
    r1, r2, r3 = st.columns([1, 1.2, 1])

    with r1:
        st.markdown('<p class="section-label">Risk Score</p>', unsafe_allow_html=True)
        st.plotly_chart(chart_risk_gauge(risk["score"], risk["color"]), use_container_width=True, config={"displayModeBar": False})
        st.markdown(f"""
        <div style="text-align:center; margin-top:-1rem;">
            <span style="background:rgba(0,0,0,0.3); border:1px solid {risk['color']}40;
                  color:{risk['color']}; padding:4px 16px; border-radius:20px;
                  font-family:'Syne',sans-serif; font-weight:700; font-size:0.9rem;">
                {risk['label']}
            </span>
        </div>
        """, unsafe_allow_html=True)

    with r2:
        st.markdown('<p class="section-label">Asset Allocation</p>', unsafe_allow_html=True)
        if not risk["asset_alloc"].empty:
            fig_alloc = chart_asset_allocation(risk["asset_alloc"])
            if fig_alloc:
                st.plotly_chart(fig_alloc, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No investment transactions detected.")

    with r3:
        st.markdown('<p class="section-label">Allocation Mix</p>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        metrics_data = [
            ("Equity", risk["equity_pct"], "#00e5a0"),
            ("Hybrid / SIF", risk["hybrid_pct"], "#3b82f6"),
            ("Debt", risk["debt_pct"], "#f59e0b"),
        ]
        for label, pct, color in metrics_data:
            st.markdown(f"""
            <div style="margin-bottom:1rem;">
                <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                    <span style="font-size:0.8rem; color:#94a3b8; font-family:'DM Mono',monospace;">{label}</span>
                    <span style="font-size:0.8rem; color:{color}; font-family:'DM Mono',monospace; font-weight:500;">{pct}%</span>
                </div>
                <div style="background:rgba(255,255,255,0.06); border-radius:4px; height:6px;">
                    <div style="background:{color}; width:{min(pct,100)}%; height:100%; border-radius:4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size:0.8rem; color:#94a3b8; line-height:1.8; font-family:'DM Sans',sans-serif;">
            <b style="color:#f1f5f9;">Risk Score Logic</b><br>
            13  Conservative<br>
            35  Moderate<br>
            57.5  Mod-Aggressive<br>
            7.510  Aggressive
        </div>
        """, unsafe_allow_html=True)


# -- TAB 3: AI SUGGESTIONS -------------------
with tab3:
    st.markdown('<p class="section-label">Powered by Claude AI</p>', unsafe_allow_html=True)

    col_btn, _ = st.columns([1, 3])
    with col_btn:
        generate = st.button(" Generate AI Insights", use_container_width=True)

    if generate or "ai_suggestions" in st.session_state:
        if generate or "ai_suggestions" not in st.session_state:
            with st.spinner("Analyzing your financial data..."):
                st.session_state["ai_suggestions"] = get_ai_suggestions(df, risk)

        suggestions = st.session_state["ai_suggestions"]
        st.markdown(f'<div class="ai-box">{suggestions.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-label">Quick Financial Snapshot</p>', unsafe_allow_html=True)

        snap1, snap2, snap3 = st.columns(3)
        top_cat = expenses_df.groupby("category")["amount"].sum().idxmax() if not expenses_df.empty else "N/A"
        with snap1:
            st.markdown(f"""
            <div style="background:var(--bg-card); border:1px solid var(--border); border-radius:10px; padding:1rem;">
                <p style="font-family:'DM Mono',monospace; font-size:0.65rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; margin:0 0 0.4rem;">Top Spend Category</p>
                <p style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700; margin:0;">{top_cat}</p>
            </div>""", unsafe_allow_html=True)
        with snap2:
            debt_ratio = (total_spend / total_income * 100) if total_income > 0 else 0
            color = "#f43f5e" if debt_ratio > 80 else "#f59e0b" if debt_ratio > 60 else "#00e5a0"
            st.markdown(f"""
            <div style="background:var(--bg-card); border:1px solid var(--border); border-radius:10px; padding:1rem;">
                <p style="font-family:'DM Mono',monospace; font-size:0.65rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; margin:0 0 0.4rem;">Expense-to-Income Ratio</p>
                <p style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700; color:{color}; margin:0;">{debt_ratio:.1f}%</p>
            </div>""", unsafe_allow_html=True)
        with snap3:
            st.markdown(f"""
            <div style="background:var(--bg-card); border:1px solid var(--border); border-radius:10px; padding:1rem;">
                <p style="font-family:'DM Mono',monospace; font-size:0.65rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; margin:0 0 0.4rem;">Portfolio Risk Level</p>
                <p style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700; color:{risk['color']}; margin:0;">{risk['label']}</p>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:3rem; color:#475569;">
            <div style="font-size:3rem; margin-bottom:1rem;"></div>
            <p style="font-family:'Syne',sans-serif; font-size:1.1rem; color:#64748b;">
                Click "Generate AI Insights" to get personalized<br>financial recommendations powered by Claude AI.
            </p>
        </div>
        """, unsafe_allow_html=True)


# -- TAB 4: TRANSACTIONS ---------------------
with tab4:
    st.markdown('<p class="section-label">All Transactions</p>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1:
        all_cats = ["All"] + sorted(df["category"].unique().tolist())
        cat_filter = st.selectbox("Category", all_cats, label_visibility="collapsed")
    with f2:
        type_filter = st.selectbox("Type", ["All", "Debit", "Credit"], label_visibility="collapsed")
    with f3:
        search = st.text_input("Search description", placeholder="Search...", label_visibility="collapsed")

    filtered = df.copy()
    if cat_filter != "All":
        filtered = filtered[filtered["category"] == cat_filter]
    if type_filter != "All":
        filtered = filtered[filtered["type"] == type_filter]
    if search:
        filtered = filtered[filtered["description"].str.contains(search, case=False, na=False)]

    display_cols = ["date", "description", "category", "amount", "type"]
    available_cols = [c for c in display_cols if c in filtered.columns]
    show_df = filtered[available_cols].copy()
    if "date" in show_df.columns:
        show_df["date"] = show_df["date"].dt.strftime("%d %b %Y")
    if "amount" in show_df.columns:
        show_df["amount"] = show_df["amount"].apply(lambda x: f"{x:,.0f}")

    st.dataframe(show_df, use_container_width=True, hide_index=True, height=420)
    st.caption(f"Showing {len(filtered):,} of {len(df):,} transactions")

    # Export
    csv_data = filtered.to_csv(index=False)
    st.download_button(" Export Filtered Data", csv_data, "filtered_transactions.csv", "text/csv")
