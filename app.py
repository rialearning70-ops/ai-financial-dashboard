import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json

st.set_page_config(page_title="AI Financial Health Dashboard", page_icon="💹", layout="wide")

st.markdown("""<style>
html,body,.stApp{background:#0a0e1a!important;color:#f1f5f9;font-family:'DM Sans',sans-serif}
h1,h2,h3{font-family:'Syne',sans-serif!important;font-weight:800}
#MainMenu,footer,header{visibility:hidden}
[data-testid="metric-container"]{background:#111827!important;border:1px solid rgba(255,255,255,0.07)!important;border-radius:12px!important;padding:1rem!important}
.stButton>button{background:linear-gradient(135deg,#00e5a0,#00b4d8)!important;color:#0a0e1a!important;font-weight:700!important;border:none!important;border-radius:8px!important}
</style>""", unsafe_allow_html=True)

CATS = {"Food & Dining":["zomato","swiggy","restaurant","cafe","food","pizza","burger"],"Transport":["uber","ola","rapido","metro","petrol","fuel","cab"],"Groceries":["bigbasket","blinkit","dmart","grocery","zepto","vegetables"],"Health":["pharmacy","hospital","doctor","apollo","medplus","medicine"],"Entertainment":["netflix","prime","hotstar","spotify","movie","pvr","inox"],"Shopping":["amazon","flipkart","myntra","meesho","nykaa"],"Utilities":["electricity","water","airtel","jio","vodafone","recharge"],"Rent & Housing":["rent","maintenance","society","emi","mortgage"],"Education":["udemy","fees","school","college","tuition"],"Investments":["sip","mutual fund","zerodha","groww","stocks","ppf","nps"],"Banking":["atm","neft","upi","charges"],"Travel":["flight","makemytrip","irctc","train"]}

def cat(d):
    d=str(d).lower()
    for c,ks in CATS.items():
        if any(k in d for k in ks): return c
    return "Other"


def parse_pdf_OLD(f):
    pass


def parse_pdf(f):
    try:
        import pdfplumber, io
        all_rows = []
        header = None
        with pdfplumber.open(f) as pdf:
            for page in pdf.pages:
                for table in (page.extract_tables() or []):
                    for row in table:
                        if not row: continue
                        clean = [str(c).strip() if c else '' for c in row]
                        if not any(clean): continue
                        if header is None:
                            header = clean
                        elif len(clean) == len(header):
                            all_rows.append(clean)
        if not header or not all_rows:
            st.error('Could not extract table from PDF. Please use CSV.')
            return pd.DataFrame()
        df = pd.DataFrame(all_rows, columns=[h.lower().strip() for h in header])
        buf = io.StringIO(); df.to_csv(buf,index=False); buf.seek(0)
        return parse(buf)
    except Exception as e:
        st.error(f'PDF error: {e}'); return pd.DataFrame()


def parse_pdf_SKIP(f):
    rows = []
        with pdfplumber.open(f) as pdf:
            for page in pdf.pages:
                for table in (page.extract_tables() or []):
                    for row in table:
                        if row: rows.append([str(c).strip() if c else '' for c in row])
        if not rows: return pd.DataFrame()
        df = pd.DataFrame(rows[1:], columns=[h.lower().strip() for h in rows[0]])
        buf = io.StringIO(); df.to_csv(buf,index=False); buf.seek(0)
        return parse(buf)
    except Exception as e:
        st.error(f'PDF error: {e}'); return pd.DataFrame()

def parse(f):
    try:
        try: df=pd.read_csv(f,encoding="utf-8")
        except:
            f.seek(0); df=pd.read_csv(f,encoding="latin1")
        df.columns=df.columns.str.strip().str.lower()
        cm={"date":["date","txn date","transaction date","value date","posting date"],"description":["description","narration","particulars","remarks","details"],"debit":["debit","withdrawal","dr","debit amount","withdrawals"],"credit":["credit","deposit","cr","credit amount","deposits"],"amount":["amount","transaction amount"]}
        rn={}
        for s,vs in cm.items():
            for v in vs:
                if v in df.columns: rn[v]=s; break
        df=df.rename(columns=rn).dropna(how="all")
        def cl(c): return pd.to_numeric(df[c].astype(str).str.replace(",","").str.replace("-","").str.strip(),errors="coerce").fillna(0)
        if "debit" in df.columns and "credit" in df.columns:
            df["debit"]=cl("debit"); df["credit"]=cl("credit")
            df["amount"]=df.apply(lambda r:r["credit"] if r["credit"]>0 else r["debit"],axis=1)
            df["type"]=df.apply(lambda r:"Credit" if r["credit"]>0 else "Debit",axis=1)
        elif "amount" in df.columns:
            df["amount"]=cl("amount").abs(); df["type"]="Debit"
        else:
            ns=df.select_dtypes(include="number").columns
            if len(ns): df["amount"]=df[ns[0]].abs(); df["type"]="Debit"
            else: return pd.DataFrame()
        if "type" not in df.columns: df["type"]="Debit"
        if "date" in df.columns:
            df["date"]=pd.to_datetime(df["date"],dayfirst=True,errors="coerce")
            df=df.dropna(subset=["date"])
            df["month"]=df["date"].dt.strftime("%b %Y")
            df["month_num"]=df["date"].dt.to_period("M")
        if "description" not in df.columns:
            tc=df.select_dtypes(include="object").columns
            df["description"]=df[tc[0]] if len(tc) else "Unknown"
        df["category"]=df["description"].astype(str).apply(cat)
        return df[df["amount"]>0].reset_index(drop=True)
    except Exception as e:
        st.error(f"Error: {e}"); return pd.DataFrame()

def sample():
    d={"date":pd.date_range("2025-09-01",periods=40,freq="7D"),"description":["Zomato","Uber","BigBasket","Netflix","Amazon","Airtel","Rent","Swiggy","Apollo","Petrol","Myntra","Udemy","PVR","Ola","DMart","Spotify","Electricity","Flipkart","Metro","Restaurant","SIP Nippon","Zerodha","ATM","MakeMyTrip","IRCTC","Parag Parikh SIP","MedPlus","Rapido","Blinkit","Hotstar","Axis SIP","Nykaa","Water Bill","Cafe","Groww MF","HDFC SIP","Inox","Ola Airport","Vegetables","Salary"],"amount":[350,180,2100,649,3200,399,18000,280,450,3200,1800,999,600,120,3500,129,1850,2400,200,1200,5000,10000,5000,4200,1800,8000,680,95,750,1499,3000,1650,400,380,2000,5000,500,950,320,85000],"type":["Debit"]*39+["Credit"]}
    df=pd.DataFrame(d)
    df["month"]=df["date"].dt.strftime("%b %Y")
    df["month_num"]=df["date"].dt.to_period("M")
    df["category"]=df["description"].apply(cat)
    return df

st.markdown("# 💹 AI Financial Health Dashboard")
st.markdown("---")
st.markdown("### 📂 Upload Your Bank Statement")
uploaded=st.file_uploader("Upload CSV or PDF bank statement", type=["csv","pdf"])
use_sample=st.button("🎲 Use Sample Data Instead")
st.markdown("---")

df=pd.DataFrame()
if uploaded:
    if uploaded.name.lower().endswith(".pdf"):
        df=parse_pdf(uploaded)
    else:
        df=parse(uploaded)
    if not df.empty: st.success(f"✅ Loaded {len(df)} transactions!")
elif use_sample or st.session_state.get("sample"):
    st.session_state["sample"]=True
    df=sample()
    st.info("Showing sample data")

if df.empty:
    st.markdown("<div style='text-align:center;padding:3rem;color:#475569'><div style='font-size:4rem'>💳</div><h3>Upload your bank statement above to get started</h3><p>Supports CSV and PDF from HDFC, SBI, ICICI, Axis, Kotak</p></div>",unsafe_allow_html=True)
    st.stop()

exp=df[df["type"]=="Debit"]; inc=df[df["type"]=="Credit"]
ts=exp["amount"].sum(); ti=inc["amount"].sum()
inv=df[df["category"]=="Investments"]["amount"].sum()
am=exp.groupby("month_num")["amount"].sum().mean() if not exp.empty else 0
sr=round(inv/ts*100,1) if ts>0 else 0

m1,m2,m3,m4,m5=st.columns(5)
m1.metric("Total Spend",f"₹{ts/1e5:.1f}L" if ts>=1e5 else f"₹{ts:,.0f}")
m2.metric("Total Income",f"₹{ti/1e5:.1f}L" if ti>=1e5 else f"₹{ti:,.0f}")
m3.metric("Total Invested",f"₹{inv:,.0f}")
m4.metric("Avg Monthly",f"₹{am:,.0f}")
m5.metric("Savings Rate",f"{sr}%",delta="On Track" if sr>=20 else "Below Target")
st.markdown("---")

COLS={"Food & Dining":"#f43f5e","Transport":"#f59e0b","Groceries":"#10b981","Health":"#06b6d4","Entertainment":"#8b5cf6","Shopping":"#ec4899","Utilities":"#3b82f6","Rent & Housing":"#6366f1","Education":"#14b8a6","Investments":"#00e5a0","Banking":"#64748b","Travel":"#f97316","Other":"#475569"}
TH=dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#94a3b8",size=12),margin=dict(l=10,r=10,t=30,b=10))

t1,t2,t3,t4=st.tabs(["📊 Expense Analysis","💼 Portfolio Risk","🤖 AI Suggestions","📋 Transactions"])

with t1:
    c1,c2=st.columns(2)
    with c1:
        st.markdown("**Expense Breakdown**")
        cd=exp.groupby("category")["amount"].sum().reset_index()
        fig=go.Figure(go.Pie(labels=cd["category"],values=cd["amount"],hole=0.6,marker_colors=[COLS.get(c,"#475569") for c in cd["category"]],hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>"))
        fig.update_layout(**TH,annotations=[dict(text="Spend",x=0.5,y=0.5,font_size=14,font_color="#f1f5f9",showarrow=False)])
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    with c2:
        st.markdown("**Monthly Trend**")
        mo=exp.groupby("month_num")["amount"].sum().reset_index()
        mo["m"]=mo["month_num"].dt.strftime("%b %Y")
        mo=mo.sort_values("month_num")
        fig2=go.Figure(go.Bar(x=mo["m"],y=mo["amount"],marker_color="#00e5a0",hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>"))
        fig2.update_layout(**TH,yaxis=dict(tickprefix="₹",gridcolor="rgba(255,255,255,0.04)"))
        st.plotly_chart(fig2,use_container_width=True,config={"displayModeBar":False})
    st.markdown("**Top 10 Transactions**")
    t10=exp.nlargest(10,"amount")[["date","description","category","amount"]].copy()
    if "date" in t10.columns: t10["date"]=t10["date"].dt.strftime("%d %b %Y")
    t10["amount"]=t10["amount"].apply(lambda x:f"₹{x:,.0f}")
    st.dataframe(t10,use_container_width=True,hide_index=True)

with t2:
    eq=df[df["category"]=="Investments"]["amount"].sum()
    ep=round(eq/max(inv,1)*100,1)
    sc=min(max(round(ep*0.08,1),1),10)
    lb="Aggressive" if sc>=7.5 else "Moderate-Aggressive" if sc>=5 else "Moderate" if sc>=3 else "Conservative"
    cl2="#f43f5e" if sc>=7.5 else "#f59e0b" if sc>=5 else "#3b82f6" if sc>=3 else "#10b981"
    r1,r2=st.columns(2)
    with r1:
        fig3=go.Figure(go.Indicator(mode="gauge+number",value=sc,number={"suffix":"/10","font":{"size":28,"color":cl2}},gauge={"axis":{"range":[0,10]},"bar":{"color":cl2,"thickness":0.3},"bgcolor":"rgba(0,0,0,0)","borderwidth":0,"steps":[{"range":[0,3],"color":"rgba(16,185,129,0.15)"},{"range":[3,5],"color":"rgba(59,130,246,0.15)"},{"range":[5,7.5],"color":"rgba(245,158,11,0.15)"},{"range":[7.5,10],"color":"rgba(244,63,94,0.15)"}]}))
        fig3.update_layout(**TH,height=220)
        st.plotly_chart(fig3,use_container_width=True,config={"displayModeBar":False})
        st.markdown(f"<div style='text-align:center;font-size:1.2rem;font-weight:700;color:{cl2}'>{lb}</div>",unsafe_allow_html=True)
    with r2:
        st.markdown(f"**Equity Allocation:** {ep}%"); st.progress(min(int(ep),100))
        st.markdown(f"**Savings Rate:** {sr}%"); st.progress(min(int(sr),100))
        st.markdown(f"**Total Invested:** ₹{inv:,.0f}")

with t3:
    if st.button("✨ Generate AI Insights"):
        t5=exp.groupby("category")["amount"].sum().nlargest(5).to_dict()
        try:
            import anthropic
            cl3=anthropic.Anthropic()
            r=cl3.messages.create(model="claude-sonnet-4-20250514",max_tokens=800,system="You are an expert Indian financial advisor. Give 4-5 specific actionable suggestions. Use Rs for rupees. Be concise.",messages=[{"role":"user","content":f"Spend:Rs{ts:,.0f},Income:Rs{ti:,.0f},Invested:Rs{inv:,.0f},SavingsRate:{sr}%,Risk:{lb},TopExpenses:{json.dumps({k:f'Rs{v:,.0f}' for k,v in t5.items()})}"}])
            st.markdown(r.content[0].text)
        except:
            st.markdown(f"""**Spending Alert:** Review your top expense categories and set monthly limits.

**Investment:** At {sr}% savings rate — target 20-30% for long-term wealth creation.

**Portfolio:** With {ep}% equity exposure, ensure 6-month emergency fund first.

**Tax:** Explore ELSS (Rs1.5L under 80C) and NPS (Rs50K under 80CCD).

**Goal Planning:** Link each SIP to a specific goal with a clear timeline.""")

with t4:
    s=st.text_input("Search transactions","",placeholder="Search...")
    fl=df[df["description"].str.contains(s,case=False,na=False)] if s else df
    sh=fl[["date","description","category","amount","type"]].copy()
    if "date" in sh.columns: sh["date"]=sh["date"].dt.strftime("%d %b %Y")
    sh["amount"]=sh["amount"].apply(lambda x:f"₹{x:,.0f}")
    st.dataframe(sh,use_container_width=True,hide_index=True,height=400)
    st.download_button("⬇️ Export CSV",fl.to_csv(index=False),"transactions.csv","text/csv")
