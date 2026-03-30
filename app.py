import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json

st.set_page_config(page_title="AI Financial Health Dashboard", layout="wide")

st.markdown("""<style>
html,body,.stApp{background:#0a0e1a;color:#f1f5f9;font-family:sans-serif}
#MainMenu,footer,header{visibility:hidden}
[data-testid="metric-container"]{background:#111827;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:1rem}
.stButton>button{background:linear-gradient(135deg,#00e5a0,#00b4d8);color:#0a0e1a;font-weight:700;border:none;border-radius:8px}
</style>""", unsafe_allow_html=True)

CATS={"Food":["zomato","swiggy","restaurant","cafe","food","pizza"],"Transport":["uber","ola","petrol","fuel","metro","cab"],"Groceries":["bigbasket","blinkit","dmart","grocery","zepto"],"Health":["pharmacy","hospital","doctor","apollo","medicine"],"Entertainment":["netflix","prime","hotstar","spotify","movie","pvr"],"Shopping":["amazon","flipkart","myntra","meesho","nykaa"],"Utilities":["electricity","water","airtel","jio","recharge"],"Rent":["rent","maintenance","society","emi"],"Education":["udemy","fees","school","college"],"Investments":["sip","mutual fund","zerodha","groww","stocks","ppf"],"Banking":["atm","neft","upi","charges"],"Travel":["flight","makemytrip","irctc","train"]}

def cat(d):
    d=str(d).lower()
    for c,ks in CATS.items():
        if any(k in d for k in ks): return c
    return "Other"

def parse_csv(f):
    try:
        try: df=pd.read_csv(f,encoding="utf-8")
        except:
            f.seek(0); df=pd.read_csv(f,encoding="latin1")
        df.columns=df.columns.str.strip().str.lower()
        cm={"date":["date","txn date","transaction date","value date"],"description":["description","narration","particulars","remarks"],"debit":["debit","withdrawal","dr","debit amount"],"credit":["credit","deposit","cr","credit amount"],"amount":["amount","transaction amount"]}
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

def parse_pdf(f):
    try:
        import pdfplumber,io
        rows,header=[],None
        with pdfplumber.open(f) as pdf:
            for page in pdf.pages:
                for table in (page.extract_tables() or []):
                    for row in table:
                        if not row: continue
                        clean=[str(x).strip() if x else "" for x in row]
                        if not any(clean): continue
                        if header is None: header=clean
                        elif len(clean)==len(header): rows.append(clean)
        if not rows: st.error("No data in PDF. Try CSV."); return pd.DataFrame()
        if header is None: header=[f"col{i}" for i in range(len(rows[0]))]
        max_len=max(len(r) for r in rows)
        padded=[r+[""]*(max_len-len(r)) for r in rows]
        df=pd.DataFrame(padded,columns=[str(h).lower().strip() for h in header[:max_len]])
        buf=io.StringIO(); df.to_csv(buf,index=False); buf.seek(0)
        return parse_csv(buf)
    except Exception as e:
        st.error(f"PDF Error: {e}"); return pd.DataFrame()

def sample():
    d={"date":pd.date_range("2025-09-01",periods=40,freq="7D"),"description":["Zomato","Uber","BigBasket","Netflix","Amazon","Airtel","Rent","Swiggy","Apollo","Petrol","Myntra","Udemy","PVR","Ola","DMart","Spotify","Electricity","Flipkart","Metro","Restaurant","SIP Nippon","Zerodha","ATM","MakeMyTrip","IRCTC","Parag Parikh SIP","MedPlus","Rapido","Blinkit","Hotstar","Axis SIP","Nykaa","Water Bill","Cafe","Groww MF","HDFC SIP","Inox","Ola Airport","Vegetables","Salary"],"amount":[350,180,2100,649,3200,399,18000,280,450,3200,1800,999,600,120,3500,129,1850,2400,200,1200,5000,10000,5000,4200,1800,8000,680,95,750,1499,3000,1650,400,380,2000,5000,500,950,320,85000],"type":["Debit"]*39+["Credit"]}
    df=pd.DataFrame(d)
    df["month"]=df["date"].dt.strftime("%b %Y")
    df["month_num"]=df["date"].dt.to_period("M")
    df["category"]=df["description"].apply(cat)
    return df

st.title("AI Financial Health Dashboard")
st.markdown("---")
st.subheader("Upload Your Bank Statement")
uploaded=st.file_uploader("Upload CSV or PDF",type=["csv","pdf"])
use_sample=st.button("Use Sample Data Instead")
st.markdown("---")

df=pd.DataFrame()
if uploaded is not None:
    if uploaded.name.lower().endswith(".pdf"): df=parse_pdf(uploaded)
    else: df=parse_csv(uploaded)
    if not df.empty: st.success(f"Loaded {len(df)} transactions")
elif use_sample or st.session_state.get("s"):
    st.session_state["s"]=True; df=sample(); st.info("Showing sample data")

if df.empty:
    st.markdown("<div style='text-align:center;padding:3rem'><h3>Upload your bank statement above to get started</h3></div>",unsafe_allow_html=True)
    st.stop()

exp=df[df["type"]=="Debit"]; inc=df[df["type"]=="Credit"]
ts=exp["amount"].sum(); ti=inc["amount"].sum()
inv=df[df["category"]=="Investments"]["amount"].sum()
am=exp.groupby("month_num")["amount"].sum().mean() if not exp.empty else 0
sr=round(inv/ts*100,1) if ts>0 else 0

m1,m2,m3,m4,m5=st.columns(5)
m1.metric("Total Spend",f"Rs{ts:,.0f}"); m2.metric("Total Income",f"Rs{ti:,.0f}")
m3.metric("Total Invested",f"Rs{inv:,.0f}"); m4.metric("Avg Monthly",f"Rs{am:,.0f}")
m5.metric("Savings Rate",f"{sr}%",delta="On Track" if sr>=20 else "Below Target")
st.markdown("---")

COLS={"Food":"#f43f5e","Transport":"#f59e0b","Groceries":"#10b981","Health":"#06b6d4","Entertainment":"#8b5cf6","Shopping":"#ec4899","Utilities":"#3b82f6","Rent":"#6366f1","Education":"#14b8a6","Investments":"#00e5a0","Banking":"#64748b","Travel":"#f97316","Other":"#475569"}
TH=dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="#94a3b8",size=12),margin=dict(l=10,r=10,t=30,b=10))

t1,t2,t3,t4=st.tabs(["Expense Analysis","Portfolio Risk","AI Suggestions","Transactions"])
with t1:
    c1,c2=st.columns(2)
    with c1:
        cd=exp.groupby("category")["amount"].sum().reset_index()
        fig=go.Figure(go.Pie(labels=cd["category"],values=cd["amount"],hole=0.6,marker_colors=[COLS.get(c,"#475569") for c in cd["category"]]))
        fig.update_layout(**TH,annotations=[dict(text="Spend",x=0.5,y=0.5,font_size=14,font_color="#f1f5f9",showarrow=False)])
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    with c2:
        mo=exp.groupby("month_num")["amount"].sum().reset_index()
        mo["m"]=mo["month_num"].dt.strftime("%b %Y"); mo=mo.sort_values("month_num")
        fig2=go.Figure(go.Bar(x=mo["m"],y=mo["amount"],marker_color="#00e5a0"))
        fig2.update_layout(**TH); st.plotly_chart(fig2,use_container_width=True,config={"displayModeBar":False})
    t10=exp.nlargest(10,"amount")[["date","description","category","amount"]].copy()
    if "date" in t10.columns: t10["date"]=t10["date"].dt.strftime("%d %b %Y")
    t10["amount"]=t10["amount"].apply(lambda x:f"Rs{x:,.0f}")
    st.dataframe(t10,use_container_width=True,hide_index=True)
with t2:
    sc=min(max(round(sr*0.1,1),1),10)
    lb="Aggressive" if sc>=7.5 else "Moderate-Aggressive" if sc>=5 else "Moderate" if sc>=3 else "Conservative"
    cl2="#f43f5e" if sc>=7.5 else "#f59e0b" if sc>=5 else "#3b82f6" if sc>=3 else "#10b981"
    r1,r2=st.columns(2)
    with r1:
        fig3=go.Figure(go.Indicator(mode="gauge+number",value=sc,number={"suffix":"/10","font":{"size":28,"color":cl2}},gauge={"axis":{"range":[0,10]},"bar":{"color":cl2,"thickness":0.3},"bgcolor":"rgba(0,0,0,0)","borderwidth":0,"steps":[{"range":[0,3],"color":"rgba(16,185,129,0.15)"},{"range":[3,5],"color":"rgba(59,130,246,0.15)"},{"range":[5,7.5],"color":"rgba(245,158,11,0.15)"},{"range":[7.5,10],"color":"rgba(244,63,94,0.15)"}]}))
        fig3.update_layout(**TH,height=220); st.plotly_chart(fig3,use_container_width=True,config={"displayModeBar":False})
        st.markdown(f"<div style='text-align:center;font-size:1.2rem;font-weight:700;color:{cl2}'>{lb}</div>",unsafe_allow_html=True)
    with r2:
        st.markdown(f"**Savings Rate:** {sr}%"); st.progress(min(int(sr),100))
        st.markdown(f"**Total Invested:** Rs{inv:,.0f}"); st.markdown(f"**Risk:** {lb}")
with t3:
    if st.button("Generate AI Insights"):
        try:
            import anthropic
            client=anthropic.Anthropic()
            resp=client.messages.create(model="claude-sonnet-4-20250514",max_tokens=800,system="You are an expert Indian financial advisor. Give 4-5 actionable suggestions. Use Rs for rupees.",messages=[{"role":"user","content":f"Spend:Rs{ts:,.0f},Income:Rs{ti:,.0f},Invested:Rs{inv:,.0f},Rate:{sr}%,Risk:{lb}"}])
            st.markdown(resp.content[0].text)
        except Exception as ex:
            st.markdown(f"**Alert:** Review top expenses and set monthly limits.\n\n**Invest:** Target 20-30% savings (yours: {sr}%).\n\n**Tax:** Use ELSS Rs1.5L under 80C and NPS Rs50K under 80CCD.")
with t4:
    s=st.text_input("Search",placeholder="Search transactions...")
    fl=df[df["description"].str.contains(s,case=False,na=False)] if s else df
    sh=fl[["date","description","category","amount","type"]].copy()
    if "date" in sh.columns: sh["date"]=sh["date"].dt.strftime("%d %b %Y")
    sh["amount"]=sh["amount"].apply(lambda x:f"Rs{x:,.0f}")
    st.dataframe(sh,use_container_width=True,hide_index=True,height=400)
    st.download_button("Export CSV",fl.to_csv(index=False),"transactions.csv","text/csv")
