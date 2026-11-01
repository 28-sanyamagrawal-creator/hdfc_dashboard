"""
HDFC Bank - Interactive Financial Dashboard
===========================================
Run with:   streamlit run app.py

Data      : HDFC Bank Integrated Annual Reports FY2021-22 to FY2025-26 (standalone)
Live price: Yahoo Finance (HDFCBANK.NS) through the yfinance library
Built with: Python, Streamlit, Plotly, Pandas
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from modules import charts as ch
from modules import content as ct
from modules import finance as fin
from modules import market as mkt
from modules import scenarios as sc

st.set_page_config(page_title="HDFC Bank | Financial Dashboard", page_icon="🏦", layout="wide",
                   initial_sidebar_state="expanded")
PLOT_CFG = {"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"]}

# =============================================================================
# 1. STYLE (CSS)
# =============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stMarkdown, .stText, button, input { font-family: 'Inter', -apple-system, sans-serif; }
.block-container { padding-top: 3.2rem; padding-bottom: 3rem; max-width: 1400px; }
h1, h2, h3, h4 { color: #0b0b0b; letter-spacing: -0.01em; }

/* ---------- hero banner ---------- */
.hero { background: linear-gradient(120deg, #06264a 0%, #0b3a6e 55%, #124c8c 100%); border-radius: 18px;
        padding: 26px 30px; color: #fff; display: flex; justify-content: space-between; align-items: center;
        gap: 24px; flex-wrap: wrap; position: relative; overflow: hidden; margin-bottom: 8px; }
.hero-left { flex: 1 1 480px; min-width: 0; }
.hero:before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 6px; background: #e31e24; }
.hero h1 { color: #fff; font-size: 2.05rem; font-weight: 800; margin: 0 0 2px 0; }
.hero .tag { color: #c9d8ec; font-size: 0.98rem; margin-bottom: 12px; }
.chip { display: inline-block; background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.22);
        color: #fff; border-radius: 999px; padding: 3px 11px; font-size: 0.78rem; margin: 3px 6px 0 0; }
.pricebox { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18); border-radius: 14px;
            padding: 14px 20px; min-width: 260px; max-width: 360px; text-align: right; flex: 0 1 auto; }
.pricebox .lbl { color: #c9d8ec; font-size: 0.78rem; text-transform: uppercase; letter-spacing: .06em; }
.pricebox .px { font-size: 2.1rem; font-weight: 800; line-height: 1.15; }
.up { color: #34d27b; font-weight: 700; } .down { color: #ff7b7b; font-weight: 700; }
.badge { display:inline-block; padding: 2px 9px; border-radius: 999px; font-size: .72rem; font-weight: 700; }
.badge.live { background: #0ca30c; color: #fff; } .badge.off { background: #fab219; color: #1b1b1b; }

/* ---------- KPI cards ---------- */
.kpi { background: #fff; border: 1px solid #ebeae6; border-radius: 14px; padding: 14px 16px 12px;
       box-shadow: 0 1px 2px rgba(16,24,40,.04); height: 100%; }
.kpi .k-lbl { color: #52514e; font-size: .78rem; font-weight: 600; text-transform: uppercase; letter-spacing: .04em; }
.kpi .k-val { color: #0b0b0b; font-size: 1.55rem; font-weight: 800; margin-top: 2px; }
.kpi .k-sub { color: #8a8984; font-size: .76rem; margin-top: 2px; }
.kpi .k-good { color: #0a7d0a; font-size: .8rem; font-weight: 700; }
.kpi .k-bad { color: #c22f2f; font-size: .8rem; font-weight: 700; }
.kpi .k-neu { color: #52514e; font-size: .8rem; font-weight: 600; }

/* ---------- misc cards ---------- */
.card { background: #fff; border: 1px solid #ebeae6; border-radius: 14px; padding: 16px 18px; height: 100%; }
.card h4 { margin: 0 0 6px 0; font-size: 1.02rem; }
.card ul { margin: 4px 0 0 0; padding-left: 18px; } .card li { margin-bottom: 3px; color: #2c2b29; font-size: .9rem; }
.facts td { padding: 5px 8px; border-bottom: 1px solid #f0efec; font-size: .88rem; vertical-align: top; }
.facts td:first-child { color: #52514e; font-weight: 600; width: 38%; }
.note { background: #f3f7fc; border-left: 4px solid #2a78d6; padding: 10px 14px; border-radius: 8px;
        color: #24384f; font-size: .9rem; margin: 6px 0 10px 0; }
.warnnote { background: #fff8e8; border-left: 4px solid #fab219; padding: 10px 14px; border-radius: 8px;
            color: #4a3b10; font-size: .9rem; margin: 6px 0 10px 0; }
.thesis { background: #fff; border: 1px solid #ebeae6; border-radius: 12px; padding: 12px 14px; margin-bottom: 10px; }
.thesis b { color: #0b0b0b; } .thesis p { margin: 4px 0 0 0; color: #3b3a37; font-size: .89rem; }
.bull { border-left: 5px solid #1baf7a; } .bear { border-left: 5px solid #eb6834; }
.tl-item { display: flex; gap: 14px; margin-bottom: 10px; }
.tl-year { min-width: 82px; font-weight: 800; color: #0b3a6e; }
.tl-text { color: #2c2b29; font-size: .9rem; border-left: 2px solid #dfe7f2; padding-left: 12px; }
.tp-card { background: #fff; border: 1px solid #ebeae6; border-radius: 14px; padding: 14px 16px; text-align: left; }
.tp-card .nm { font-weight: 800; font-size: 1rem; } .tp-card .tp { font-size: 1.6rem; font-weight: 800; }
.dot { display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:6px; }
.section-title { font-size: 1.25rem; font-weight: 800; margin: 18px 0 4px 0; color: #0b0b0b; }
.section-sub { color: #6b6a66; font-size: .9rem; margin-bottom: 8px; }

/* ---------- tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #ebeae6; }
.stTabs [data-baseweb="tab"] { padding: 10px 14px; font-weight: 600; }
.stTabs [aria-selected="true"] { color: #0b3a6e !important; }
div[data-testid="stMetricValue"] { font-weight: 800; }
section[data-testid="stSidebar"] { background: #f6f8fb; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# 2. DATA (cached so it loads only once)
# =============================================================================
@st.cache_data(show_spinner=False)
def load_data():
    d = fin.load_all()
    stm = fin.build_statements(d)
    ratios = fin.compute_ratios(d, stm)
    dp = fin.dupont(d, stm)
    return d, stm, ratios, dp


@st.cache_data(ttl=60, show_spinner=False)
def live_quote():
    return mkt.get_quote()


@st.cache_data(ttl=300, show_spinner=False)
def price_history(ticker, period):
    return mkt.get_history(ticker, period)


D, STM, RAT, DUP = load_data()
ALL_YEARS = D["years"]
CORE = STM["core"]
LAST, PREV = ALL_YEARS[-1], ALL_YEARS[-2]


# =============================================================================
# 3. SMALL HELPERS
# =============================================================================
def inr(x, dec=0):
    """Indian digit grouping: 4364886 -> 43,64,886"""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "–"
    neg, x = x < 0, abs(float(x))
    s = f"{x:.{dec}f}"
    ip, fp = (s.split(".") + [""])[:2]
    if len(ip) > 3:
        head, tail = ip[:-3], ip[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        ip = ",".join(parts + [tail])
    return ("-" if neg else "") + ip + (f".{fp}" if fp else "")


def money(v_crore, unit=None, dec=None):
    """Format a Rs crore value in the unit chosen in the sidebar."""
    unit = unit or UNIT
    if v_crore is None or pd.isna(v_crore):
        return "–"
    if unit == "₹ Crore":
        return "₹" + inr(v_crore, 0 if dec is None else dec) + " cr"
    if unit == "₹ Lakh Crore":
        return f"₹{v_crore / 1e5:,.{2 if dec is None else dec}f} L cr"
    return f"₹{v_crore / 100:,.{1 if dec is None else dec}f} bn"


def conv(series_crore):
    return series_crore / UNIT_DIV


def kpi(label, value, delta=None, good_up=True, sub=None, delta_fmt="pct"):
    """HTML KPI card. delta: % change (pct) or absolute change (pp / x)."""
    dl = ""
    if delta is not None and not pd.isna(delta):
        up = delta >= 0
        good = up if good_up else not up
        arrow = "▲" if up else "▼"
        txt = {"pct": f"{abs(delta):.1f}% YoY", "pp": f"{abs(delta):.2f} pp YoY",
               "bps": f"{abs(delta) * 100:.0f} bps YoY"}[delta_fmt]
        dl = f'<div class="{"k-good" if good else "k-bad"}">{arrow} {txt}</div>'
    sb = f'<div class="k-sub">{sub}</div>' if sub else ""
    return f'<div class="kpi"><div class="k-lbl">{label}</div><div class="k-val">{value}</div>{dl}{sb}</div>'


def kpi_row(cards, n=5):
    for i in range(0, len(cards), n):
        cols = st.columns(n)
        for c, html in zip(cols, cards[i:i + n]):
            c.markdown(html, unsafe_allow_html=True)
        st.write("")


def ratio(key, year):
    return RAT.at[key, year] if key in RAT.index else np.nan


def yoy(key_series_or_value_now, before):
    if before in (0, None) or pd.isna(before) or pd.isna(key_series_or_value_now):
        return None
    return 100 * (key_series_or_value_now / before - 1)


def style_statement(df, years, mode, base_row=None):
    """Turn a statement frame into a styled table for st.dataframe."""
    levels = df["_level"]
    vals = df[years].copy()
    if mode == "YoY growth %":
        full = df[ALL_YEARS]
        vals = (100 * full.pct_change(axis=1, fill_method=None)).loc[:, years]
        vals = vals.replace([np.inf, -np.inf], np.nan)
        disp = vals.map(lambda v: "–" if pd.isna(v) else f"{v:+.1f}%")
    elif mode == "Common size %":
        disp = (100 * vals / df.loc[base_row, years]).map(lambda v: "–" if pd.isna(v) else f"{v:.1f}%")
    else:
        if UNIT == "₹ Crore":
            disp = vals.map(lambda v: "" if pd.isna(v) else inr(v, 0))
        else:
            disp = (vals / UNIT_DIV).map(lambda v: "" if pd.isna(v) else f"{v:,.2f}")
    disp.index.name = "Particulars"
    disp = disp.reset_index()

    def row_style(row):
        lvl = levels.iloc[row.name]
        if lvl == 2:
            return ["font-weight: 700; background-color: #eef4fb; color: #0b0b0b"] * len(row)
        if lvl == 3:
            return ["font-weight: 800; background-color: #0b3a6e; color: #ffffff"] * len(row)
        if lvl == 1:
            return ["color: #52514e"] * len(row)
        return ["font-weight: 600; color: #0b0b0b"] * len(row)
    return disp.style.apply(row_style, axis=1)


def section(title, sub=None):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="section-sub">{sub}</div>', unsafe_allow_html=True)


def plot(fig, key=None):
    st.plotly_chart(fig, config=PLOT_CFG, key=key, width="stretch")


# =============================================================================
# 4. SIDEBAR (global filters)
# =============================================================================
with st.sidebar:
    st.markdown("### 🏦 HDFC Bank Dashboard")
    st.caption("Standalone financials · FY = April–March")
    default_start = ALL_YEARS[-5] if len(ALL_YEARS) >= 5 else ALL_YEARS[0]
    y0, y1 = st.select_slider("Financial years to show", options=ALL_YEARS, value=(default_start, LAST),
                              help="FY21 is included only as a comparison base.")
    YEARS = ALL_YEARS[ALL_YEARS.index(y0): ALL_YEARS.index(y1) + 1]
    UNIT = st.radio("Show amounts in", ["₹ Crore", "₹ Lakh Crore", "₹ Billion"], horizontal=False)
    UNIT_DIV = {"₹ Crore": 1, "₹ Lakh Crore": 1e5, "₹ Billion": 100}[UNIT]
    UNIT_SHORT = {"₹ Crore": "₹ cr", "₹ Lakh Crore": "₹ lakh cr", "₹ Billion": "₹ bn"}[UNIT]
    st.divider()
    st.markdown("**Live share price**")
    AUTO = st.toggle("Auto-refresh every 60 sec", value=True)
    if st.button("🔄 Refresh price now", width="stretch"):
        live_quote.clear()
        price_history.clear()
    manual = st.number_input("Manual price override (₹, 0 = off)", min_value=0.0, value=0.0, step=1.0,
                             help="Use this if you are offline or want to test a price.")
    st.divider()
    st.caption("1 crore = 10 million · 1 lakh crore = 1 trillion")
    st.caption("Data: HDFC Bank Integrated Annual Reports FY22–FY26. Price: Yahoo Finance.")
    st.caption("For education only – not investment advice.")

Q = live_quote()
if manual > 0:
    Q = dict(Q, price=manual, source="Manual override", live=False)
    Q["change"] = Q["price"] - (Q["prev_close"] or Q["price"])
    Q["change_pct"] = 100 * Q["change"] / Q["prev_close"] if Q["prev_close"] else 0
PRICE = Q["price"]
SHARES_CR = CORE.at["capital", LAST]  # Rs 1 face value -> crore shares
EPS_LAST, BVPS_LAST, DPS_LAST = ratio("eps", LAST), ratio("bvps", LAST), ratio("dps", LAST)


# =============================================================================
# 5. HEADER
# =============================================================================
def header_html(q):
    chg_cls = "up" if q["change"] >= 0 else "down"
    arrow = "▲" if q["change"] >= 0 else "▼"
    badge = '<span class="badge live">● LIVE</span>' if q["live"] else '<span class="badge off">OFFLINE</span>'
    if q["live"]:
        change_html = f'<div class="{chg_cls}">{arrow} {q["change"]:+,.2f} ({q["change_pct"]:+.2f}%) today</div>'
    else:
        change_html = '<div style="color:#c9d8ec">Day change not available offline</div>'
    return f"""
<div class="hero">
  <div class="hero-left">
    <h1>{ct.COMPANY['name']}</h1>
    <div class="tag">{ct.COMPANY['tagline']} · Financial dashboard {YEARS[0]}–{YEARS[-1]}</div>
    <span class="chip">NSE: {ct.COMPANY['nse']}</span><span class="chip">BSE: {ct.COMPANY['bse']}</span>
    <span class="chip">NYSE ADR: HDB</span><span class="chip">Sector: Banking · Private</span>
    <span class="chip">D-SIB</span><span class="chip">MD &amp; CEO: {ct.COMPANY['md_ceo']}</span>
  </div>
  <div class="pricebox">
    <div class="lbl">Share price (NSE) {badge}</div>
    <div class="px">₹{q['price']:,.2f}</div>
    {change_html}
    <div class="lbl" style="margin-top:6px;text-transform:none">Mkt cap ₹{inr(q['price'] * SHARES_CR, 0)} cr ·
      P/B {q['price'] / BVPS_LAST:.2f}x · P/E {q['price'] / EPS_LAST:.1f}x</div>
    <div class="lbl" style="text-transform:none;font-size:.7rem">{q['source']} · {q['fetched_at']}</div>
  </div>
</div>"""


@st.fragment(run_every=60 if AUTO else None)
def header():
    q = live_quote()
    if manual > 0:
        q = Q
    st.markdown(header_html(q), unsafe_allow_html=True)


header()

tabs = st.tabs(["🏠 Overview", "🏦 Company Profile", "📊 Financial Statements", "📐 Ratio Analysis",
                "🧩 Segments", "📈 Live Market", "🔮 Future Scenarios", "📚 Data & Notes"])

# =============================================================================
# TAB 1 - OVERVIEW
# =============================================================================
with tabs[0]:
    ly, py = YEARS[-1], (ALL_YEARS[ALL_YEARS.index(YEARS[-1]) - 1] if ALL_YEARS.index(YEARS[-1]) > 0 else None)
    c = CORE
    g = lambda k: yoy(c.at[k, ly], c.at[k, py]) if py else None  # noqa: E731
    dr = lambda k: (ratio(k, ly) - ratio(k, py)) if py else None  # noqa: E731
    section(f"Snapshot · {ly}", "Key numbers for the latest selected year, with change vs the previous year")
    kpi_row([
        kpi("Total Assets", money(c.at["total_assets", ly]), g("total_assets")),
        kpi("Deposits", money(c.at["deposits", ly]), g("deposits")),
        kpi("Advances (Loans)", money(c.at["advances", ly]), g("advances")),
        kpi("Net Interest Income", money(c.at["nii", ly]), g("nii")),
        kpi("Net Profit", money(c.at["pat", ly]), g("pat")),
        kpi("ROA", f"{ratio('roa', ly):.2f}%", dr("roa"), delta_fmt="pp"),
        kpi("ROE", f"{ratio('roe', ly):.2f}%", dr("roe"), delta_fmt="pp"),
        kpi("Gross NPA", f"{ratio('gnpa', ly):.2f}%", dr("gnpa"), good_up=False, delta_fmt="pp"),
        kpi("CASA Ratio", f"{ratio('casa', ly):.1f}%" if not pd.isna(ratio('casa', ly)) else "–",
            dr("casa"), delta_fmt="pp"),
        kpi("Capital Adequacy", f"{ratio('crar', ly):.2f}%", dr("crar"), delta_fmt="pp", sub="CET-1 "
            f"{ratio('cet1', ly):.2f}%"),
    ])

    if "FY24" in YEARS:
        st.markdown('<div class="note">ℹ️ <b>FY24 includes the HDFC Ltd merger (effective 1 July 2023)</b> – '
                    'that is why assets, loans, borrowings and profit jump that year. Growth rates for FY24 '
                    'are not like-for-like.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        df = pd.DataFrame({"Deposits": conv(c.loc["deposits", YEARS]), "Advances": conv(c.loc["advances", YEARS])})
        plot(ch.bar(df, YEARS, ["Deposits", "Advances"], title=f"Deposits vs Advances ({UNIT_SHORT})",
                    fmt=",.0f" if UNIT == "₹ Crore" else ",.2f"), "ov1")
    with col2:
        df = pd.DataFrame({"PAT": conv(c.loc["pat", YEARS])})
        plot(ch.bar(df, YEARS, ["PAT"], title=f"Net Profit ({UNIT_SHORT})", colors=[ch.BLUE], text_last=True,
                    fmt=",.0f" if UNIT == "₹ Crore" else ",.2f"), "ov2")
    col3, col4 = st.columns(2)
    with col3:
        df = pd.DataFrame({"NII": conv(c.loc["nii", YEARS]), "Other income": conv(c.loc["other_income", YEARS])})
        plot(ch.bar(df, YEARS, ["NII", "Other income"], barmode="stack",
                    title=f"Revenue mix: NII + Other income ({UNIT_SHORT})",
                    fmt=",.0f" if UNIT == "₹ Crore" else ",.2f"), "ov3")
    with col4:
        df = pd.DataFrame({"GNPA": RAT.loc["gnpa", YEARS].values, "NNPA": RAT.loc["nnpa", YEARS].values},
                          index=YEARS)
        plot(ch.line(df, YEARS, ["GNPA", "NNPA"], names=["Gross NPA %", "Net NPA %"], title="Asset quality (%)",
                     unit="%"), "ov4")

    # Auto-generated highlights (change with the year filter)
    section("What the numbers say")
    n = len(YEARS) - 1
    hl = []
    if n >= 1:
        f0, f1 = YEARS[0], YEARS[-1]
        hl.append(f"**Balance sheet** grew from {money(c.at['total_assets', f0])} to "
                  f"{money(c.at['total_assets', f1])} – a CAGR of "
                  f"**{fin.cagr(c.at['total_assets', f0], c.at['total_assets', f1], n):.1f}%** over {n} years.")
        hl.append(f"**Net profit** rose {c.at['pat', f1] / c.at['pat', f0]:.1f}x "
                  f"({fin.cagr(c.at['pat', f0], c.at['pat', f1], n):.1f}% CAGR), while **EPS** grew "
                  f"{fin.cagr(ratio('eps', f0), ratio('eps', f1), n):.1f}% a year (more shares after the merger).")
        hl.append(f"**NIM** moved from {ratio('nim', f0):.2f}% to {ratio('nim', f1):.2f}% and **ROE** from "
                  f"{ratio('roe', f0):.1f}% to {ratio('roe', f1):.1f}%.")
        if not pd.isna(ratio("casa", f0)):
            hl.append(f"**CASA ratio** changed from {ratio('casa', f0):.1f}% to {ratio('casa', f1):.1f}%, "
                      f"and the **CD ratio** is now {ratio('cd_ratio', f1):.1f}%.")
        hl.append(f"**Asset quality** stays strong: GNPA {ratio('gnpa', f1):.2f}%, NNPA {ratio('nnpa', f1):.2f}%, "
                  f"capital adequacy {ratio('crar', f1):.1f}%.")
    for h in hl:
        st.markdown(f"- {h}")

# =============================================================================
# TAB 2 - COMPANY PROFILE
# =============================================================================
with tabs[1]:
    left, right = st.columns([1.35, 1])
    with left:
        section("About HDFC Bank")
        for p in ct.ABOUT:
            st.markdown(p)
        section("How a bank like HDFC makes money")
        st.markdown(ct.BUSINESS_MODEL)
    with right:
        section("Quick facts")
        rows = [("Sector", ct.COMPANY["sector"]), ("Industry", ct.COMPANY["industry"]),
                ("RBI classification", ct.COMPANY["classification"]), ("Incorporated", ct.COMPANY["incorporated"]),
                ("Registered office", ct.COMPANY["hq"]), ("Listing", "NSE: HDFCBANK · BSE: 500180 · NYSE: HDB"),
                ("ISIN", ct.COMPANY["isin"]), ("MD & CEO", ct.COMPANY["md_ceo"]),
                ("Chairman", ct.COMPANY["chairman"]), ("Deputy MD", ct.COMPANY["dmd"]),
                ("CFO", ct.COMPANY["cfo"]), ("Promoter", ct.COMPANY["promoter"]),
                ("Auditors", ct.COMPANY["auditors"]), ("Website", ct.COMPANY["website"])]
        st.markdown('<div class="card"><table class="facts">' +
                    "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rows) + "</table></div>",
                    unsafe_allow_html=True)

    section("Products & services", "What HDFC Bank offers, segment by segment (from the FY26 annual report)")
    svc_tabs = st.tabs([f"{v['icon']} {k}" for k, v in ct.SERVICES.items()])
    for t, (name, v) in zip(svc_tabs, ct.SERVICES.items()):
        with t:
            st.caption(f"**Customers:** {v['who']}")
            cols = st.columns(min(3, len(v["items"])))
            for i, (grp, items) in enumerate(v["items"].items()):
                with cols[i % len(cols)]:
                    st.markdown(f'<div class="card"><h4>{grp}</h4><ul>' + "".join(f"<li>{x}</li>" for x in items)
                                + "</ul></div>", unsafe_allow_html=True)
                    st.write("")

    section("Group companies", "Key subsidiaries and the bank's ownership (31 March 2026)")
    sub = D["subsidiaries"].rename(columns={"name": "Company", "stake_pct": "Bank's stake",
                                            "business": "Business", "fy26_highlight": "FY26 highlight"})
    st.dataframe(sub, hide_index=True, width="stretch",
                 column_config={"Company": st.column_config.TextColumn(width="medium"),
                                "Bank's stake": st.column_config.ProgressColumn(
                                    "Bank's stake", min_value=0, max_value=100, format="%.2f%%", width="small"),
                                "Business": st.column_config.TextColumn(width="large"),
                                "FY26 highlight": st.column_config.TextColumn(width="large")})

    c1, c2, c3 = st.columns(3)
    ops = D["operations"]
    oy = [y for y in YEARS if y in ops.columns]
    with c1:
        df = pd.DataFrame({"Branches": fin.series(ops, "branches", oy)})
        plot(ch.bar(df, oy, ["Branches"], title="Branch network", colors=[ch.BLUE], text_last=True), "pr1")
    with c2:
        df = pd.DataFrame({"Employees": fin.series(ops, "employees", oy)})
        plot(ch.bar(df, oy, ["Employees"], title="Employees", colors=[ch.BLUE], text_last=True), "pr2")
    with c3:
        df = pd.DataFrame({"Customers": fin.series(ops, "customers_cr", oy)})
        plot(ch.bar(df, oy, ["Customers"], title="Customers (crore)", colors=[ch.BLUE], text_last=True,
                    fmt=",.1f"), "pr3")

    c1, c2 = st.columns([1.1, 1])
    with c1:
        sh = D["shareholding"].sort_values("pct", ascending=False)
        plot(ch.hbar(list(sh["category"]), list(sh["pct"]), title="Shareholding pattern (31-Mar-2026, %)",
                     unit="%", height=340), "pr4")
        st.caption("No promoter holding – foreign investors (FPIs + ADS) own about 52%.")
    with c2:
        section("Milestones")
        st.markdown("".join(f'<div class="tl-item"><div class="tl-year">{y}</div><div class="tl-text">{t}</div></div>'
                            for y, t in ct.TIMELINE), unsafe_allow_html=True)

# =============================================================================
# TAB 3 - FINANCIAL STATEMENTS
# =============================================================================
with tabs[2]:
    section("Financial statements", f"Standalone, audited · amounts in {UNIT} · {YEARS[0]}–{YEARS[-1]}")
    mode = st.radio("View", ["Values", "YoY growth %", "Common size %"], horizontal=True,
                    help="Common size: P&L as % of Total Net Revenue, Balance Sheet as % of Total Assets.")
    s_pl, s_bs, s_cf = st.tabs(["Profit & Loss", "Balance Sheet", "Cash Flow"])

    with s_pl:
        st.dataframe(style_statement(STM["pnl"], YEARS, mode, "Total Net Revenue"), hide_index=True, width="stretch",
                     height=35 * (len(STM["pnl"]) + 1) + 3)
        st.download_button("⬇️ Download P&L (CSV, ₹ crore)", STM["pnl"][ALL_YEARS].to_csv().encode(),
                           "hdfc_bank_pnl.csv", "text/csv")
        c1, c2 = st.columns([1.1, 1])
        with c1:
            wy = st.selectbox("Year for profit bridge", YEARS[::-1], key="wf_year")
            p = STM["pnl"][wy]
            vals = [p["Interest Earned"], -p["Interest Expended"], p["Net Interest Income (NII)"],
                    p["Other (Non-Interest) Income"], -p["Operating Expenses"], -p["Provisions & Contingencies"],
                    -p["Tax Expense"], p["Net Profit (PAT)"]]
            vals = [v / UNIT_DIV for v in vals]
            plot(ch.waterfall(["Interest earned", "Interest paid", "NII", "Other income", "Opex", "Provisions",
                               "Tax", "Net profit"], vals,
                              ["absolute", "relative", "total", "relative", "relative", "relative", "relative",
                               "total"], title=f"How {wy} profit is built ({UNIT_SHORT})"), "pl_wf")
        with c2:
            options = ["Net Interest Income (NII)", "Other (Non-Interest) Income", "Operating Expenses",
                       "Operating Profit (Pre-Provision)", "Provisions & Contingencies", "Net Profit (PAT)"]
            pick = st.multiselect("Compare line items", options, default=["Net Interest Income (NII)",
                                                                           "Operating Profit (Pre-Provision)",
                                                                           "Net Profit (PAT)"])
            if pick:
                df = pd.DataFrame({k: conv(STM["pnl"].loc[k, YEARS]) for k in pick})
                colors = [ch.SERIES[options.index(k)] for k in pick]  # colour follows the item
                plot(ch.bar(df, YEARS, pick, colors=colors, title=f"Trend ({UNIT_SHORT})",
                            fmt=",.0f" if UNIT == "₹ Crore" else ",.2f"), "pl_tr")
        c1, c2 = st.columns(2)
        with c1:
            items = ["   Fees & Commission", "   Forex & Derivatives", "   Treasury Gains (Investments)",
                     "   Dividend from Subsidiaries", "   Miscellaneous (incl. recoveries)"]
            df = pd.DataFrame({k.strip(): conv(STM["pnl"].loc[k, YEARS]) for k in items})
            plot(ch.bar(df, YEARS, list(df.columns), barmode="relative", title=f"Other income break-up ({UNIT_SHORT})",
                        fmt=",.0f" if UNIT == "₹ Crore" else ",.2f"), "pl_oi")
        with c2:
            items = ["   Employee Cost", "   Depreciation", "   Other Operating Expenses"]
            df = pd.DataFrame({k.strip(): conv(STM["pnl"].loc[k, YEARS]) for k in items})
            plot(ch.bar(df, YEARS, list(df.columns), barmode="stack", title=f"Operating expenses break-up ({UNIT_SHORT})",
                        fmt=",.0f" if UNIT == "₹ Crore" else ",.2f"), "pl_ox")

    with s_bs:
        st.dataframe(style_statement(STM["bs"], YEARS, mode, "Total Assets"), hide_index=True, width="stretch",
                     height=35 * (len(STM["bs"]) + 1) + 3)
        st.download_button("⬇️ Download Balance Sheet (CSV, ₹ crore)", STM["bs"][ALL_YEARS].to_csv().encode(),
                           "hdfc_bank_balance_sheet.csv", "text/csv")
        c1, c2 = st.columns(2)
        with c1:
            a_items = ["Advances (Loans)", "Investments", "Cash & Balances with RBI",
                       "Balances with Banks & Money at Call", "Other Assets", "Fixed Assets"]
            df = pd.DataFrame({k: conv(STM["bs"].loc[k, YEARS]) for k in a_items})
            plot(ch.bar(df, YEARS, a_items, barmode="stack", title=f"What the bank owns – assets ({UNIT_SHORT})",
                        height=400, fmt=",.0f" if UNIT == "₹ Crore" else ",.2f"), "bs_a")
        with c2:
            l_items = ["Deposits", "Borrowings", "Net Worth (Shareholders' Funds)", "Other Liabilities & Provisions"]
            df = pd.DataFrame({k: conv(STM["bs"].loc[k, YEARS]) for k in l_items})
            plot(ch.bar(df, YEARS, l_items, barmode="stack", title=f"How it is funded – liabilities ({UNIT_SHORT})",
                        height=400, fmt=",.0f" if UNIT == "₹ Crore" else ",.2f"), "bs_l")
        km = D["key_metrics"]
        dy = [y for y in YEARS if not pd.isna(fin.series(km, "sa_dep", ALL_YEARS)[y])]
        if dy:
            df = pd.DataFrame({"Savings (SA)": conv(fin.series(km, "sa_dep", dy)),
                               "Current (CA)": conv(fin.series(km, "ca_dep", dy)),
                               "Term deposits": conv(fin.series(km, "td_dep", dy))})
            plot(ch.bar(df, dy, list(df.columns), barmode="stack", title=f"Deposit mix ({UNIT_SHORT})",
                        fmt=",.0f" if UNIT == "₹ Crore" else ",.2f"), "bs_dep")

    with s_cf:
        mode_cf = "Values" if mode == "Common size %" else mode
        if mode == "Common size %":
            st.caption("Common size is not meaningful for cash flows – showing values.")
        st.dataframe(style_statement(STM["cf"], YEARS, mode_cf), hide_index=True, width="stretch",
                     height=35 * (len(STM["cf"]) + 1) + 3)
        st.download_button("⬇️ Download Cash Flow (CSV, ₹ crore)", STM["cf"][ALL_YEARS].to_csv().encode(),
                           "hdfc_bank_cash_flow.csv", "text/csv")
        st.markdown('<div class="note">💡 For a bank, <b>operating cash flow swings with loans and deposits</b> '
                    '(a loan given out is an operating outflow). So a negative CFO in a fast-growth year is normal '
                    'and is not a sign of stress.</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            df = pd.DataFrame({"Operating": conv(CORE.loc["cfo", YEARS]), "Investing": conv(CORE.loc["cfi", YEARS]),
                               "Financing": conv(CORE.loc["cff", YEARS])})
            plot(ch.bar(df, YEARS, list(df.columns), title=f"Cash flow by activity ({UNIT_SHORT})",
                        fmt=",.0f" if UNIT == "₹ Crore" else ",.2f"), "cf1")
        with c2:
            cy = st.selectbox("Year for cash bridge", YEARS[::-1], key="cf_year")
            cfs = STM["cf"][cy]
            amalg = cfs["   Cash Acquired on Amalgamation (HDFC Ltd)"]
            labels = ["Opening cash", "Operating", "Investing", "Financing", "FX effect"]
            vals = [cfs["   Opening Cash & Cash Equivalents"], cfs["Net Cash from Operating Activities (CFO)"],
                    cfs["Net Cash from Investing Activities (CFI)"], cfs["Net Cash from Financing Activities (CFF)"],
                    cfs["   FX Translation Effect"]]
            measures = ["absolute", "relative", "relative", "relative", "relative"]
            if amalg:
                labels.append("From merger")
                vals.append(amalg)
                measures.append("relative")
            labels.append("Closing cash")
            vals.append(cfs["Closing Cash & Cash Equivalents"])
            measures.append("total")
            plot(ch.waterfall(labels, [v / UNIT_DIV for v in vals], measures,
                              title=f"Cash bridge {cy} ({UNIT_SHORT})"), "cf2")
        df = pd.DataFrame({"Dividend paid": conv(CORE.loc["div_paid", YEARS]), "Capex": conv(CORE.loc["capex", YEARS])})
        plot(ch.bar(df, YEARS, list(df.columns), colors=[ch.AQUA, ch.YELLOW],
                    title=f"Dividends paid and capex ({UNIT_SHORT})", height=300,
                    fmt=",.0f" if UNIT == "₹ Crore" else ",.2f"), "cf3")

# =============================================================================
# TAB 4 - RATIOS
# =============================================================================
with tabs[3]:
    section("Ratio analysis", "Banking-specific ratios. 'Annual report' = as reported by the bank; "
                              "'Calculated' = computed by this dashboard from the statements.")
    cats = list(dict.fromkeys(RAT["category"]))
    cat = st.radio("Category", cats + ["DuPont (ROA → ROE)"], horizontal=True, label_visibility="collapsed")
    ly, py = YEARS[-1], YEARS[-2] if len(YEARS) > 1 else None

    if cat != "DuPont (ROA → ROE)":
        sub = RAT[RAT["category"] == cat]
        cards = []
        for k, r in sub.iterrows():
            v = r[ly]
            unit = r["unit"]
            if pd.isna(v):
                val = "–"
            elif unit == "%":
                val = f"{v:.2f}%"
            elif unit == "x":
                val = f"{v:.2f}x"
            elif unit == "Rs cr":
                val = money(v, "₹ Crore") if v > 1000 else f"₹{v:,.2f} cr"
            else:
                val = f"₹{v:,.2f}"
            delta, dfmt = None, "pct"
            if py and not pd.isna(r.get(py, np.nan)) and not pd.isna(v):
                if unit == "%":
                    delta, dfmt = v - r[py], "pp"
                else:
                    delta = yoy(v, r[py])
            cards.append(kpi(r["label"], val, delta, good_up=(r["better"] == "higher"), sub=r["source"],
                             delta_fmt=dfmt))
        kpi_row(cards, n=4)

        # Small multiples: one chart per ratio (so every chart has a single, honest scale)
        keys = list(sub.index)
        per_row = 3
        for i in range(0, len(keys), per_row):
            cols = st.columns(per_row)
            for col, k in zip(cols, keys[i:i + per_row]):
                r = RAT.loc[k]
                vals = pd.to_numeric(r[YEARS], errors="coerce")
                if vals.notna().sum() == 0:
                    continue
                unit = {"%": "%", "x": "x", "Rs": "", "Rs cr": ""}[r["unit"]]
                fmt = ",.2f" if r["unit"] in ("%", "x", "Rs") else ",.0f"
                df = pd.DataFrame({k: vals.values}, index=YEARS)
                with col:
                    if r["unit"] in ("%", "x"):
                        fig = ch.line(df, YEARS, [k], names=[r["label"]], colors=[ch.BLUE], title=r["label"],
                                      unit=unit, height=260, fmt=fmt)
                    else:
                        fig = ch.bar(df, YEARS, [k], names=[r["label"]], colors=[ch.BLUE], title=r["label"],
                                     height=260, text_last=True, fmt=fmt)
                    plot(fig, f"rat_{k}")

        with st.expander("📋 Ratio table with formulas and meaning", expanded=False):
            t = sub[["label"] + YEARS + ["unit", "formula", "meaning", "source"]].copy()
            for y in YEARS:
                t[y] = t[y].map(lambda v: "–" if pd.isna(v) else (inr(v, 0) if abs(v) >= 1000 else f"{v:,.2f}"))
            t = t.rename(columns={"label": "Ratio", "unit": "Unit", "formula": "Formula", "meaning": "What it tells you",
                                  "source": "Source"})
            st.dataframe(t, hide_index=True, width="stretch")
    else:
        dy = st.selectbox("Year", YEARS[::-1], key="dupont_year")
        dp = DUP[dy]
        c1, c2 = st.columns([1.3, 1])
        with c1:
            labels = ["NII", "Other income", "Opex", "Provisions", "Tax", "ROA"]
            vals = [dp["Net Interest Income"], dp["Other Income"], dp["Operating Expenses"], dp["Provisions"],
                    dp["Tax"], dp["ROA"]]
            fig = ch.waterfall(labels, vals, ["relative"] * 5 + ["total"],
                               title=f"ROA tree {dy} – each item as % of average assets")
            fig.update_traces(text=[f"{v:.2f}%" for v in vals], hovertemplate="%{x}: %{y:.2f}%<extra></extra>")
            plot(fig, "dupont_wf")
        with c2:
            st.markdown(kpi("ROA (calculated)", f"{dp['ROA']:.2f}%"), unsafe_allow_html=True)
            st.write("")
            st.markdown(kpi("× Equity multiplier", f"{dp['Equity Multiplier (x)']:.2f}x",
                            sub="Average assets / average net worth"), unsafe_allow_html=True)
            st.write("")
            st.markdown(kpi("= ROE (calculated)", f"{dp['ROE']:.2f}%", sub=f"Reported ROE: {ratio('roe', dy):.2f}%"),
                        unsafe_allow_html=True)
        t = DUP[YEARS].copy()
        t = t.map(lambda v: f"{v:.2f}")
        t.index.name = "% of average assets"
        st.dataframe(t.reset_index(), hide_index=True, width="stretch")
        st.caption("Calculated on simple averages of opening and closing balances, so values differ slightly "
                   "from the bank's reported ratios (which use daily averages).")

# =============================================================================
# TAB 5 - SEGMENTS
# =============================================================================
with tabs[4]:
    section("Segment performance", "As reported under AS-17 (₹ crore). Segment revenue includes inter-segment "
                                   "transfers, so it adds up to more than the bank's total income.")
    seg = D["segments"]
    sy = [y for y in YEARS if y in seg.columns]
    names = ["Retail Banking", "Wholesale Banking", "Treasury", "Other Banking Operations"]
    seg_colors = [ch.BLUE, ch.ORANGE, ch.AQUA, ch.YELLOW]
    rev = seg[seg.metric == "revenue"].set_index("segment").loc[names, sy].T
    res = seg[seg.metric == "result"].set_index("segment").loc[names, sy].T
    c1, c2 = st.columns(2)
    with c1:
        plot(ch.bar(rev / UNIT_DIV, sy, names, colors=seg_colors, barmode="stack",
                    title=f"Segment revenue ({UNIT_SHORT})", height=380,
                    fmt=",.0f" if UNIT == "₹ Crore" else ",.2f"), "seg1")
    with c2:
        plot(ch.bar(res / UNIT_DIV, sy, names, colors=seg_colors, title=f"Segment profit before tax ({UNIT_SHORT})",
                    height=380, fmt=",.0f" if UNIT == "₹ Crore" else ",.2f"), "seg2")
    c1, c2 = st.columns(2)
    with c1:
        share = 100 * res.loc[sy[-1]] / res.loc[sy[-1]].sum()
        plot(ch.hbar(names, list(share.values), title=f"Share of segment profit, {sy[-1]} (%)", unit="%",
                     height=300), "seg3")
    with c2:
        margin = 100 * res / rev
        plot(ch.line(margin, sy, names, colors=seg_colors, title="Segment margin (profit / revenue, %)", unit="%",
                     height=300, fmt=".1f"), "seg4")
    st.markdown('<div class="note">Retail is the largest by revenue; wholesale has historically produced the most '
                'profit. Treasury profit swings with bond yields (strong in FY24 and FY26, weak in FY23 and FY25).</div>',
                unsafe_allow_html=True)
    with st.expander("📋 Segment data table (₹ crore)"):
        st.dataframe(seg[["segment", "metric"] + sy], hide_index=True, width="stretch")

# =============================================================================
# TAB 6 - LIVE MARKET
# =============================================================================
with tabs[5]:
    @st.fragment(run_every=60 if AUTO else None)
    def live_panel():
        q = live_quote()
        if manual > 0:
            q = dict(q, price=manual, source="Manual override", live=False)
        if not q["live"]:
            st.markdown('<div class="warnnote">⚠️ <b>Live data could not be fetched</b> (no internet, or Yahoo blocked '
                        'the request). Showing the last price from the annual report. Connect to the internet and '
                        'press <b>Refresh price now</b> in the sidebar.</div>', unsafe_allow_html=True)
        p = q["price"]
        cards = [
            kpi("Last price (NSE)", f"₹{p:,.2f}", q["change_pct"] if q["live"] else None,
                sub=f"{q['source']} · {q['fetched_at']}"),
            kpi("Day range", f"₹{q['day_low']:,.1f} – ₹{q['day_high']:,.1f}" if q["day_low"] else "–",
                sub=f"Open ₹{q['open']:,.2f}" if q["open"] else None),
            kpi("52-week range", f"₹{q['low_52w']:,.0f} – ₹{q['high_52w']:,.0f}" if q["low_52w"] else "–",
                sub=f"{100 * (p / q['high_52w'] - 1):+.1f}% from 52-week high" if q["high_52w"] else None),
            kpi("Market cap", money(p * SHARES_CR, "₹ Lakh Crore"), sub=f"{inr(SHARES_CR * 1e7, 0)} shares"),
            kpi("P/E (on FY26 EPS)", f"{p / EPS_LAST:.1f}x", sub=f"EPS ₹{EPS_LAST:.2f}"),
            kpi("P/B (on FY26 book)", f"{p / BVPS_LAST:.2f}x", sub=f"BVPS ₹{BVPS_LAST:.2f}"),
            kpi("Dividend yield", f"{100 * DPS_LAST / p:.2f}%", sub=f"FY26 DPS ₹{DPS_LAST:.2f}"),
            kpi("Previous close", f"₹{q['prev_close']:,.2f}" if q["prev_close"] else "–",
                sub=f"Volume {inr(q['volume'], 0)}" if q["volume"] else None),
        ]
        kpi_row(cards, n=4)
    live_panel()

    c1, c2, c3, c4 = st.columns([2.2, 1.2, 1.6, 1])
    period = c1.radio("Period", list(mkt.PERIODS.keys()), index=5, horizontal=True)
    ctype = c2.radio("Chart", ["Candles", "Line"], horizontal=True)
    mas = c3.multiselect("Moving averages", ["20 DMA", "50 DMA", "200 DMA"], default=["50 DMA", "200 DMA"])
    show_vol = c4.toggle("Volume", value=True)

    hist, src = price_history(mkt.TICKER_NSE, period)
    if hist.empty:
        st.info("Price history is unavailable offline. Below: year-end prices from the annual reports.")
        df = pd.DataFrame({"Price": fin.series(D["key_metrics"], "price_mar31", ALL_YEARS)})
        plot(ch.line(df, ALL_YEARS, ["Price"], title="Share price on 31 March (₹, bonus-adjusted)", unit="",
                     colors=[ch.BLUE]), "px_off")
    else:
        # Long daily history for moving averages
        long_hist, _ = price_history(mkt.TICKER_NSE, "5Y")
        close_long = long_hist["Close"] if not long_hist.empty else hist["Close"]
        rows = 2 if show_vol else 1
        fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.04,
                            row_heights=[0.78, 0.22] if show_vol else [1])
        if ctype == "Candles":
            fig.add_trace(go.Candlestick(x=hist.index, open=hist["Open"], high=hist["High"], low=hist["Low"],
                                         close=hist["Close"], name="HDFCBANK",
                                         increasing=dict(line=dict(color=ch.GOOD, width=1), fillcolor=ch.GOOD),
                                         decreasing=dict(line=dict(color=ch.BAD, width=1), fillcolor=ch.BAD)),
                          row=1, col=1)
        else:
            fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name="Close", mode="lines",
                                     line=dict(color=ch.BLUE, width=2),
                                     hovertemplate="₹%{y:,.2f}<extra>Close</extra>"), row=1, col=1)
        daily = period not in ("1D", "5D")
        ma_colors = {"20 DMA": ch.YELLOW, "50 DMA": ch.ORANGE, "200 DMA": ch.VIOLET}
        if daily and not long_hist.empty and period not in ("5Y", "MAX"):
            for m in mas:
                w = int(m.split()[0])
                ma = close_long.rolling(w).mean().reindex(hist.index, method="nearest")
                fig.add_trace(go.Scatter(x=hist.index, y=ma, name=m, mode="lines",
                                         line=dict(color=ma_colors[m], width=1.6),
                                         hovertemplate=f"{m}: ₹%{{y:,.1f}}<extra></extra>"), row=1, col=1)
        if show_vol:
            vcol = [ch.GOOD if c >= o else ch.BAD for c, o in zip(hist["Close"], hist["Open"])]
            fig.add_trace(go.Bar(x=hist.index, y=hist["Volume"], name="Volume", marker=dict(color=vcol),
                                 opacity=0.55, hovertemplate="Vol: %{y:,.0f}<extra></extra>", showlegend=False),
                          row=2, col=1)
        fig = ch.base_layout(fig, f"HDFCBANK · {period} · {src}", height=520)
        fig.update_layout(xaxis_rangeslider_visible=False, hovermode="x unified")
        fig.update_yaxes(tickprefix="₹", row=1, col=1)
        if period not in ("1D", "5D"):
            fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
        plot(fig, "px_main")

        c1, c2 = st.columns([1, 1.2])
        with c1:
            section("Price returns")
            rets = mkt.period_returns(long_hist if not long_hist.empty else hist)
            if rets:
                t = pd.DataFrame([{"Period": k, "Return": f"{v[0]:+.1f}%",
                                   "Annualised": f"{v[1]:+.1f}%" if v[1] is not None else ""}
                                  for k, v in rets.items()])
                st.dataframe(t, hide_index=True, width="stretch")
        with c2:
            section("HDFC Bank vs Nifty Bank", "Both rebased to 100 at the start of the period")
            bench, _ = price_history(mkt.BENCHMARK, period if daily else "1M")
            if not bench.empty and daily:
                a = hist["Close"] / hist["Close"].iloc[0] * 100
                b = bench["Close"] / bench["Close"].iloc[0] * 100
                fig = go.Figure()
                fig.add_scatter(x=a.index, y=a, name="HDFC Bank", line=dict(color=ch.BLUE, width=2))
                fig.add_scatter(x=b.index, y=b, name="Nifty Bank", line=dict(color=ch.ORANGE, width=2))
                fig = ch.base_layout(fig, None, height=300)
                plot(fig, "bench")
            else:
                st.caption("Benchmark comparison available for daily periods when online.")
    st.caption("Source: Yahoo Finance (ticker HDFCBANK.NS) via yfinance. Quotes may be delayed by up to 15 minutes. "
               "investing.com has no public API, so Yahoo is used. Historical prices are adjusted for the FY26 1:1 bonus.")

# =============================================================================
# TAB 7 - FUTURE SCENARIOS
# =============================================================================
with tabs[6]:
    section("Future outlook: Bull · Base · Bear · Custom",
            f"5-year projections built on {LAST} actuals. Change the assumptions and watch profit, return ratios "
            "and the implied share price update instantly.")
    start = sc.starting_point(CORE, LAST, PREV)
    calib = sc.calibrate(CORE, LAST, PREV)
    proj_years = [f"FY{int(LAST[2:]) + i}E" for i in range(1, 6)]

    c1, c2, c3 = st.columns([1, 1, 1.4])
    method = c1.radio("Valuation method", ["P/B", "P/E"], horizontal=True,
                      help="P/B (price to book) is the standard way to value banks.")
    val_year = c2.selectbox("Value on", proj_years, index=1,
                            help="Target price = multiple × this year's projected book value (or EPS).")
    c3.markdown(f"<div class='note' style='margin-top:4px'>Current price used: <b>₹{PRICE:,.2f}</b> "
                f"({'live' if Q['live'] else Q['source']})</div>", unsafe_allow_html=True)

    # ---- Custom sliders (kept in session state)
    for k in sc.SLIDERS:
        st.session_state.setdefault(f"cu_{k}", float(sc.PRESETS["Base"][k]))
    with st.expander("🎛️ Custom scenario – set your own assumptions", expanded=True):
        visible = [k for k in sc.SLIDERS if not (method == "P/B" and k == "pe") and not (method == "P/E" and k == "pb")]
        cols = st.columns(5)
        for i, k in enumerate(visible):
            lab, lo, hi, step, hlp = sc.SLIDERS[k]
            cols[i % 5].slider(lab, lo, hi, step=step, key=f"cu_{k}", help=hlp)
        r1, r2, r3, r4 = st.columns(4)

        def _load_preset(name):
            for kk in sc.SLIDERS:
                st.session_state[f"cu_{kk}"] = float(sc.PRESETS[name][kk])

        r1.button("Copy Bear", on_click=_load_preset, args=("Bear",), width="stretch")
        r2.button("Copy Base", on_click=_load_preset, args=("Base",), width="stretch")
        r3.button("Copy Bull", on_click=_load_preset, args=("Bull",), width="stretch")
        r4.markdown(f"<span style='font-size:.82rem;color:#52514e'>{LAST} on the model's basis: NIM "
                    f"{calib['nim']:.2f}%, other income {calib['oth_inc']:.2f}%, C/I {calib['cti']:.1f}%, "
                    f"credit cost {calib['credit_cost']:.2f}%</span>", unsafe_allow_html=True)

    custom = {k: st.session_state[f"cu_{k}"] for k in sc.SLIDERS}
    ALL_SC = {"Bear": sc.PRESETS["Bear"], "Base": sc.PRESETS["Base"], "Bull": sc.PRESETS["Bull"], "Custom": custom}
    PROJ = {n: sc.project(start, a) for n, a in ALL_SC.items()}
    TP = {n: sc.target_price(PROJ[n], ALL_SC[n], method, val_year) for n in ALL_SC}

    # ---- Target price cards
    cols = st.columns(4)
    for col, n in zip(cols, ALL_SC):
        up = 100 * (TP[n] / PRICE - 1)
        cls = "up" if up >= 0 else "down"
        clr = "#0a7d0a" if up >= 0 else "#c22f2f"
        p5 = PROJ[n].iloc[-1]
        col.markdown(f"""<div class="tp-card" style="border-top:4px solid {ch.SCENARIO_COLORS[n]}">
            <div class="nm"><span class="dot" style="background:{ch.SCENARIO_COLORS[n]}"></span>{n} case</div>
            <div class="k-sub" style="color:#8a8984;font-size:.78rem">Implied price ({method} on {val_year})</div>
            <div class="tp">₹{TP[n]:,.0f}</div>
            <div style="color:{clr};font-weight:700">{'▲' if up >= 0 else '▼'} {up:+.1f}% vs ₹{PRICE:,.0f}</div>
            <div class="k-sub" style="color:#52514e;font-size:.8rem;margin-top:6px">{proj_years[-1]} PAT
              {money(p5['pat'], '₹ Crore')} · ROE {p5['roe']:.1f}% · ROA {p5['roa']:.2f}%</div>
            </div>""", unsafe_allow_html=True)
    st.write("")
    sel = st.radio("Scenario story", list(ALL_SC), index=1, horizontal=True)
    st.markdown(f"<div class='note'><b>{sel}:</b> {sc.DESCRIPTIONS[sel]}</div>", unsafe_allow_html=True)

    # ---- Charts: profit path and book value path (actual + projections)
    hist_years = YEARS

    def path_chart(metric_core, metric_proj, title, divisor=1.0, fmt=",.0f", per_share=False):
        fig, ends = go.Figure(), {}
        if per_share:
            actual = RAT.loc[metric_core, hist_years].astype(float)
        else:
            actual = CORE.loc[metric_core, hist_years].astype(float) / divisor
        fig.add_scatter(x=hist_years, y=actual, name="Actual", mode="lines+markers",
                        line=dict(color=ch.INK2, width=2.4), marker=dict(size=8, color=ch.INK2),
                        hovertemplate="Actual %{x}: %{y:" + fmt + "}<extra></extra>")
        for n in ALL_SC:
            y = [actual.iloc[-1]] + list(PROJ[n][metric_proj] / (1 if per_share else divisor))
            x = [hist_years[-1]] + proj_years
            fig.add_scatter(x=x, y=y, name=n, mode="lines+markers",
                            line=dict(color=ch.SCENARIO_COLORS[n], width=2, dash="dot"),
                            marker=dict(size=7, color=ch.SCENARIO_COLORS[n]),
                            hovertemplate=n + " %{x}: %{y:" + fmt + "}<extra></extra>")
            ends[n] = y[-1]
        # End labels, nudged apart so they never overlap (Custom is skipped when it equals another case)
        shown = {}
        for n, v in sorted(ends.items(), key=lambda kv: kv[1]):
            if n == "Custom" and any(abs(v / w - 1) < 0.01 for k, w in ends.items() if k != "Custom"):
                continue
            shown[n] = v
        lo, hi = min(ends.values()), max(ends.values())
        gap, prev, shift = 0.07 * (hi - lo if hi > lo else 1), None, 0
        for n, v in shown.items():
            shift = shift + 13 if prev is not None and v - prev < gap else 0
            fig.add_annotation(x=proj_years[-1], y=v, text=f"{n} {v:{fmt}}", showarrow=False, xanchor="left",
                               xshift=8, yshift=shift, font=dict(size=11, color=ch.INK))
            prev = v
        fig = ch.base_layout(fig, title, height=400)
        fig.update_layout(margin=dict(r=96))
        fig.update_xaxes(tickangle=0, tickfont=dict(size=10))
        return fig

    if LAST in hist_years:
        p1, p2, p3 = st.tabs(["Net profit path", "EPS path", "Book value per share path"])
        with p1:
            plot(path_chart("pat", "pat", f"Net profit: actual and projected ({UNIT_SHORT})", divisor=UNIT_DIV,
                            fmt=",.0f" if UNIT == "₹ Crore" else ",.2f"), "sc1")
        with p2:
            plot(path_chart("eps", "eps", "Earnings per share: actual and projected (₹)", fmt=",.1f",
                            per_share=True), "sc1b")
        with p3:
            plot(path_chart("bvps", "bvps", "Book value per share: actual and projected (₹)", fmt=",.0f",
                            per_share=True), "sc2")
    else:
        st.info(f"Include {LAST} in the sidebar year range to see the actual + projected paths.")

    c1, c2 = st.columns([1, 1.2])
    with c1:
        fig = go.Figure(go.Bar(x=list(TP.keys()), y=list(TP.values()),
                               marker=dict(color=[ch.SCENARIO_COLORS[n] for n in TP], cornerradius=4),
                               text=[f"₹{v:,.0f}" for v in TP.values()], textposition="inside",
                               insidetextanchor="end", textfont=dict(color="white", size=13), cliponaxis=False,
                               hovertemplate="%{x}: ₹%{y:,.0f}<extra></extra>"))
        fig.add_hline(y=PRICE, line=dict(color=ch.INK, width=1.5),
                      annotation_text=f"Current<br>₹{PRICE:,.0f}", annotation_position="right",
                      annotation_font=dict(color=ch.INK, size=11))
        fig = ch.base_layout(fig, f"Implied price vs current ({method}, {val_year})", height=360, legend=False)
        fig.update_layout(hovermode="closest", margin=dict(r=70))
        plot(fig, "sc3")
    with c2:
        st.markdown("**Assumptions side by side**")
        lab = {k: v[0] for k, v in sc.SLIDERS.items()}
        tbl = pd.DataFrame({n: {lab[k]: a[k] for k in sc.SLIDERS} for n, a in ALL_SC.items()})
        tbl.insert(0, f"{LAST} (model basis)", [calib.get(k, np.nan) for k in sc.SLIDERS])
        tbl = tbl.map(lambda v: "–" if pd.isna(v) else f"{v:.2f}")
        tbl.index.name = "Assumption"
        st.dataframe(tbl.reset_index(), hide_index=True, width="stretch", height=390)

    section(f"Projected financials – {sel} case", "₹ crore unless stated")
    pj = PROJ[sel].T
    show = {"advances": "Advances", "deposits": "Deposits", "cd_ratio": "CD ratio (%)", "total_assets": "Total assets",
            "nii": "Net interest income", "other_income": "Other income", "opex": "Operating expenses",
            "ppop": "Operating profit", "provisions": "Provisions", "pbt": "Profit before tax", "pat": "Net profit",
            "net_worth": "Net worth", "eps": "EPS (₹)", "bvps": "Book value / share (₹)", "dps": "Dividend / share (₹)",
            "roa": "ROA (%)", "roe": "ROE (%)"}
    pj = pj.loc[list(show)].rename(index=show)
    act = {"Advances": CORE.at["advances", LAST], "Deposits": CORE.at["deposits", LAST],
           "CD ratio (%)": ratio("cd_ratio", LAST), "Total assets": CORE.at["total_assets", LAST],
           "Net interest income": CORE.at["nii", LAST], "Other income": CORE.at["other_income", LAST],
           "Operating expenses": CORE.at["opex", LAST], "Operating profit": CORE.at["ppop", LAST],
           "Provisions": CORE.at["provisions", LAST], "Profit before tax": CORE.at["pbt", LAST],
           "Net profit": CORE.at["pat", LAST], "Net worth": CORE.at["net_worth", LAST], "EPS (₹)": EPS_LAST,
           "Book value / share (₹)": BVPS_LAST, "Dividend / share (₹)": DPS_LAST, "ROA (%)": ratio("roa", LAST),
           "ROE (%)": ratio("roe", LAST)}
    pj.insert(0, f"{LAST} (actual)", pd.Series(act))
    disp = pj.copy().astype(object)
    for idx in disp.index:
        is_small = any(s in idx for s in ("(%)", "(₹)"))
        disp.loc[idx] = [f"{v:,.2f}" if is_small else inr(v, 0) for v in pj.loc[idx]]
    disp.index.name = "Line item"
    st.dataframe(disp.reset_index(), hide_index=True, width="stretch", height=35 * (len(disp) + 1) + 3)
    pat_cagr = sc.cagr_series(CORE.at["pat", LAST], PROJ[sel]["pat"].iloc[-1], 5)
    st.caption(f"{sel} case: net profit CAGR {pat_cagr:.1f}% over {proj_years[0]}–{proj_years[-1]}. Share count "
               "held constant; projections are illustrative.")

    section("Sensitivity: implied price for different NIM and valuation multiples", f"{sel} case · {val_year}")
    a = ALL_SC[sel]
    nims = [round(a["nim"] + d, 2) for d in (-0.30, -0.15, 0, 0.15, 0.30)]
    base_m = a["pb"] if method == "P/B" else a["pe"]
    step = 0.25 if method == "P/B" else 2.0
    mults = [max(0.5, round(base_m + step * i, 2)) for i in (-2, -1, 0, 1, 2)]
    grid = sc.sensitivity(start, a, method, val_year, nims, mults)
    fig = go.Figure(go.Heatmap(z=grid.values, x=[f"{m:.2f}x" for m in mults], y=list(grid.index),
                               colorscale=[[0, "#cde2fb"], [0.5, "#5598e7"], [1, "#0d366b"]],
                               text=[[f"₹{v:,.0f}" for v in row] for row in grid.values], texttemplate="%{text}",
                               textfont=dict(size=12), hovertemplate="NIM %{y}, multiple %{x}: ₹%{z:,.0f}<extra></extra>",
                               colorbar=dict(title="₹", thickness=10)))
    fig = ch.base_layout(fig, None, height=320, legend=False)
    fig.update_xaxes(title_text=f"{method} multiple", side="bottom")
    fig.update_yaxes(title_text="NIM (% of avg assets)", autorange="reversed", ticksuffix="")
    fig.update_layout(hovermode="closest")
    plot(fig, "sens")

    section("Investment thesis", "Bull vs Bear arguments drawn from the annual reports")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🐂 Bull case – what could go right")
        for t, p in ct.BULL_POINTS:
            st.markdown(f'<div class="thesis bull"><b>{t}</b><p>{p}</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("#### 🐻 Bear case – what could go wrong")
        for t, p in ct.BEAR_POINTS:
            st.markdown(f'<div class="thesis bear"><b>{t}</b><p>{p}</p></div>', unsafe_allow_html=True)
    st.markdown("**👀 What to watch next:** " + " · ".join(ct.WATCHLIST))
    st.markdown('<div class="warnnote">This projection is a simplified academic model with assumed inputs. It is '
                'not a recommendation to buy or sell any security.</div>', unsafe_allow_html=True)

# =============================================================================
# TAB 8 - DATA & NOTES
# =============================================================================
with tabs[7]:
    section("Sources")
    st.markdown("""
| Financial year | Document | Used for |
|---|---|---|
| FY2025-26 | Integrated Annual Report 2025-26 (32nd AGM, July 2026) | FY26 statements, 10-year highlights, segments, subsidiaries, shareholding |
| FY2024-25 | Integrated Annual Report 2024-25 | FY25 statements, ratios, segments |
| FY2023-24 | Integrated Annual Report 2023-24 | FY24 statements (first year after the HDFC Ltd merger) |
| FY2022-23 | Integrated Annual Report 2022-23 | FY23 statements, ratios |
| FY2021-22 | Integrated Annual Report 2021-22 | FY22 statements and FY21 comparatives |
| Live | Yahoo Finance (HDFCBANK.NS, ^NSEBANK) | Share price, history, 52-week range |
""")
    section("Method notes")
    st.markdown("""
- **Standalone** audited figures are used (the bank alone, without subsidiaries) – the normal basis for analysing a bank.
- Statement values were taken from the reports in ₹ thousand and converted to **₹ crore** (÷ 10,000). Every year was cross-checked: assets = liabilities, and cash-flow totals = change in cash.
- **Provisions** in HDFC Bank's P&L include income tax; the dashboard shows provisions and tax separately (tax = PBT − PAT).
- **Per-share data are adjusted for the 1:1 bonus issue** of FY26 (as in the bank's own 10-year table), so EPS, BVPS and DPS are comparable across years.
- **FY24 onwards include the merger of HDFC Ltd** (1 July 2023) – growth in FY24 is not like-for-like.
- Ratios marked *Annual report* are the bank's reported numbers (daily averages). Ratios marked *Calculated* use simple averages of opening and closing balances.
- Projections in **Future Scenarios** are illustrative assumptions made for this project.
""")
    section("Glossary")
    st.dataframe(pd.DataFrame(list(ct.GLOSSARY.items()), columns=["Term", "Meaning"]), hide_index=True,
                 width="stretch")
    section("Raw data files", "Edit these CSVs in the /data folder (e.g. add an FY27 column) and the whole "
                              "dashboard recalculates.")
    pick = st.selectbox("Preview file", ["profit_loss", "balance_sheet", "cash_flow", "key_metrics", "operations"])
    raw = D[pick].reset_index()
    st.dataframe(raw, hide_index=True, width="stretch")
    st.download_button(f"⬇️ Download {pick}.csv", raw.to_csv(index=False).encode(), f"{pick}.csv", "text/csv")

st.markdown("<div style='text-align:center;color:#8a8984;font-size:.8rem;margin-top:30px'>Built with Python · "
            "Streamlit · Plotly · Pandas | Data: HDFC Bank annual reports FY22–FY26, Yahoo Finance | "
            "For academic use only</div>", unsafe_allow_html=True)
