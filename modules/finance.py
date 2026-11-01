"""
finance.py
----------
Loads the CSV files in /data (taken from HDFC Bank's annual reports) and
builds the P&L, Balance Sheet, Cash Flow and all ratios from them.

Everything is calculated from the CSVs, so if you add a new column
(for example FY27) to every CSV file, the whole dashboard updates itself.
All money values are in Rs crore, standalone basis.
"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FACE_VALUE = 1.0  # Rs per share


# ----------------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------------
def _load(name: str) -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / name)
    return df


def year_columns(df: pd.DataFrame) -> list:
    """Columns that look like FY21, FY22, ... in sorted order."""
    cols = [c for c in df.columns if str(c).startswith("FY") and str(c)[2:].isdigit()]
    return sorted(cols, key=lambda c: int(c[2:]))


def load_all() -> dict:
    """Read every CSV and return a dict of DataFrames indexed by key."""
    out = {}
    for name in ["profit_loss", "balance_sheet", "cash_flow", "key_metrics", "operations"]:
        df = _load(f"{name}.csv")
        out[name] = df.set_index("key")
    out["segments"] = _load("segments.csv")
    out["shareholding"] = _load("shareholding_fy26.csv")
    out["subsidiaries"] = _load("subsidiaries.csv")
    out["years"] = year_columns(out["profit_loss"])
    return out


def series(df: pd.DataFrame, key: str, years: list) -> pd.Series:
    """One row of a statement as a numeric Series (index = years)."""
    if key not in df.index:
        return pd.Series(np.nan, index=years, dtype=float)
    return pd.to_numeric(df.loc[key, years], errors="coerce").astype(float)


# ----------------------------------------------------------------------------
# Statements (derived lines are computed here, not typed in)
# ----------------------------------------------------------------------------
def build_statements(d: dict) -> dict:
    years = d["years"]
    pl, bs, cf = d["profit_loss"], d["balance_sheet"], d["cash_flow"]
    g = lambda df, k: series(df, k, years)  # noqa: E731

    # ---------- Profit & Loss ----------
    interest_earned = g(pl, "int_adv") + g(pl, "int_inv") + g(pl, "int_rbi") + g(pl, "int_oth")
    interest_expended = g(pl, "ie_dep") + g(pl, "ie_borr") + g(pl, "ie_oth")
    nii = interest_earned - interest_expended
    other_income = g(pl, "fees") + g(pl, "forex") + g(pl, "treasury") + g(pl, "divsub") + g(pl, "misc")
    net_revenue = nii + other_income
    opex = g(pl, "emp") + g(pl, "depn") + g(pl, "oth_opex")
    ppop = net_revenue - opex
    provisions = g(pl, "provisions")
    pbt = ppop - provisions
    tax = g(pl, "tax")
    pat = pbt - tax

    pnl_rows = [
        # (label, series, level)  level 0 = main line, 1 = sub-item, 2 = total/highlight
        ("Interest Earned", interest_earned, 0),
        ("   Interest on Advances", g(pl, "int_adv"), 1),
        ("   Income on Investments", g(pl, "int_inv"), 1),
        ("   Interest on RBI & Inter-bank Balances", g(pl, "int_rbi"), 1),
        ("   Other Interest Income", g(pl, "int_oth"), 1),
        ("Interest Expended", interest_expended, 0),
        ("   Interest on Deposits", g(pl, "ie_dep"), 1),
        ("   Interest on Borrowings", g(pl, "ie_borr"), 1),
        ("   Other Interest Expense", g(pl, "ie_oth"), 1),
        ("Net Interest Income (NII)", nii, 2),
        ("Other (Non-Interest) Income", other_income, 0),
        ("   Fees & Commission", g(pl, "fees"), 1),
        ("   Forex & Derivatives", g(pl, "forex"), 1),
        ("   Treasury Gains (Investments)", g(pl, "treasury"), 1),
        ("   Dividend from Subsidiaries", g(pl, "divsub"), 1),
        ("   Miscellaneous (incl. recoveries)", g(pl, "misc"), 1),
        ("Total Net Revenue", net_revenue, 2),
        ("Operating Expenses", opex, 0),
        ("   Employee Cost", g(pl, "emp"), 1),
        ("   Depreciation", g(pl, "depn"), 1),
        ("   Other Operating Expenses", g(pl, "oth_opex"), 1),
        ("Operating Profit (Pre-Provision)", ppop, 2),
        ("Provisions & Contingencies", provisions, 0),
        ("Profit Before Tax", pbt, 2),
        ("Tax Expense", tax, 0),
        ("Net Profit (PAT)", pat, 2),
    ]

    # ---------- Balance Sheet ----------
    net_worth = g(bs, "capital") + g(bs, "reserves")
    total_liab = net_worth + g(bs, "deposits") + g(bs, "borrowings") + g(bs, "other_liab")
    total_assets = (g(bs, "cash_rbi") + g(bs, "bank_bal") + g(bs, "investments") + g(bs, "advances")
                    + g(bs, "fixed_assets") + g(bs, "other_assets"))
    bs_rows = [
        ("CAPITAL & LIABILITIES", pd.Series(np.nan, index=years), 3),
        ("   Share Capital", g(bs, "capital"), 1),
        ("   Reserves & Surplus (incl. ESOP outstanding)", g(bs, "reserves"), 1),
        ("Net Worth (Shareholders' Funds)", net_worth, 2),
        ("Deposits", g(bs, "deposits"), 0),
        ("Borrowings", g(bs, "borrowings"), 0),
        ("Other Liabilities & Provisions", g(bs, "other_liab"), 0),
        ("Total Liabilities & Equity", total_liab, 2),
        ("ASSETS", pd.Series(np.nan, index=years), 3),
        ("Cash & Balances with RBI", g(bs, "cash_rbi"), 0),
        ("Balances with Banks & Money at Call", g(bs, "bank_bal"), 0),
        ("Investments", g(bs, "investments"), 0),
        ("Advances (Loans)", g(bs, "advances"), 0),
        ("Fixed Assets", g(bs, "fixed_assets"), 0),
        ("Other Assets", g(bs, "other_assets"), 0),
        ("Total Assets", total_assets, 2),
        ("Contingent Liabilities (off-balance sheet)", g(bs, "contingent"), 1),
    ]

    # ---------- Cash Flow ----------
    cf_rows = []
    labels = cf["label"].to_dict()
    level_of = {"cfo": 2, "cfi": 2, "cff": 2, "cf_net": 2, "cf_close": 2}
    section_before = {"cf_pbt": "A. OPERATING ACTIVITIES", "cf_capex": "B. INVESTING ACTIVITIES",
                      "cf_equity": "C. FINANCING ACTIVITIES", "cf_fx": "D. NET CHANGE IN CASH"}
    for k in cf.index:
        if k in section_before:
            cf_rows.append((section_before[k], pd.Series(np.nan, index=years), 3))
        lvl = level_of.get(k, 1)
        name = labels[k] if lvl == 2 else "   " + labels[k]
        cf_rows.append((name, g(cf, k), lvl))

    core = pd.DataFrame({
        "interest_earned": interest_earned, "interest_expended": interest_expended, "nii": nii,
        "other_income": other_income, "net_revenue": net_revenue, "opex": opex, "ppop": ppop,
        "provisions": provisions, "pbt": pbt, "tax": tax, "pat": pat,
        "fees": g(pl, "fees"), "treasury": g(pl, "treasury"), "emp": g(pl, "emp"),
        "int_adv": g(pl, "int_adv"), "int_inv": g(pl, "int_inv"), "ie_dep": g(pl, "ie_dep"),
        "ie_borr": g(pl, "ie_borr"),
        "net_worth": net_worth, "total_assets": total_assets, "deposits": g(bs, "deposits"),
        "borrowings": g(bs, "borrowings"), "advances": g(bs, "advances"),
        "investments": g(bs, "investments"), "capital": g(bs, "capital"),
        "cash": g(bs, "cash_rbi") + g(bs, "bank_bal"), "fixed_assets": g(bs, "fixed_assets"),
        "cfo": g(cf, "cfo"), "cfi": g(cf, "cfi"), "cff": g(cf, "cff"), "capex": -g(cf, "cf_capex"),
        "div_paid": -g(cf, "cf_div"),
    }).T

    return {"pnl": _to_frame(pnl_rows, years), "bs": _to_frame(bs_rows, years),
            "cf": _to_frame(cf_rows, years), "core": core}


def _to_frame(rows, years):
    df = pd.DataFrame([s.reindex(years).values for _, s, _ in rows],
                      index=[r[0] for r in rows], columns=years)
    df["_level"] = [r[2] for r in rows]
    return df


# ----------------------------------------------------------------------------
# Ratios
# ----------------------------------------------------------------------------
def avg(s: pd.Series) -> pd.Series:
    """Average of opening and closing balance (first year falls back to closing)."""
    return ((s + s.shift(1)) / 2).fillna(s)


def safe_div(a, b):
    return a / b.replace(0, np.nan)


def compute_ratios(d: dict, st: dict) -> pd.DataFrame:
    """Returns a DataFrame: rows = ratio keys, columns = years + meta columns."""
    years = d["years"]
    c = st["core"].loc[:, years].T  # rows = years
    km = d["key_metrics"]
    rep = lambda k: series(km, k, years)  # noqa: E731  (reported in annual report)
    ops = d["operations"]
    shares_cr = c["capital"] / FACE_VALUE  # number of shares in crore

    avg_assets, avg_adv, avg_nw = avg(c["total_assets"]), avg(c["advances"]), avg(c["net_worth"])
    avg_funds = avg(c["deposits"] + c["borrowings"])

    R = {}
    def add(key, label, values, unit, cat, formula, meaning, higher_is_better=True, source="Calculated"):
        R[key] = dict(label=label, unit=unit, category=cat, formula=formula, meaning=meaning,
                      better="higher" if higher_is_better else "lower", source=source,
                      **{y: v for y, v in zip(years, pd.Series(values, index=years).values)})

    P, M, A, K, L, E, V, G = ("Profitability", "Margins & Spreads", "Asset Quality", "Capital Adequacy",
                              "Liquidity & Funding", "Efficiency & Productivity", "Per Share & Valuation",
                              "Growth")
    # ---- Profitability
    add("roa", "Return on Assets (ROA)", rep("roa"), "%", P, "Net profit / average total assets",
        "Profit earned on every Rs 100 of assets. Above 1.5% is excellent for an Indian bank.",
        source="Annual report")
    add("roe", "Return on Equity (ROE)", rep("roe"), "%", P, "Net profit / average net worth",
        "Return generated on shareholders' money.", source="Annual report")
    add("roa_calc", "ROA (calculated, simple average)", 100 * c["pat"] / avg_assets, "%", P,
        "PAT / ((opening + closing assets) / 2)", "Same idea as ROA, recomputed from the statements.")
    add("pat_margin", "Net Profit Margin", 100 * c["pat"] / (c["interest_earned"] + c["other_income"]), "%", P,
        "PAT / total income (interest earned + other income)", "Share of total income that becomes profit.")
    add("ppop_assets", "Operating Profit / Avg Assets", 100 * c["ppop"] / avg_assets, "%", P,
        "Pre-provision operating profit / average assets", "Core earning power before bad-loan provisions.")
    add("tax_rate", "Effective Tax Rate", 100 * c["tax"] / c["pbt"], "%", P, "Tax / PBT",
        "FY24 is low because Rs 6,325 cr of old tax provisions were written back after favourable orders.",
        higher_is_better=False)
    # ---- Margins
    add("nim", "Net Interest Margin (NIM)", rep("nim_wf"), "%", M, "NII / average working funds (total assets)",
        "The core spread a bank earns on its balance sheet.", source="Annual report")
    add("nim_iea", "NII / Avg Interest-Earning Assets", rep("nim_iea"), "%", M,
        "NII / average interest-earning assets", "NIM measured only on assets that earn interest.",
        source="Annual report")
    add("yield_adv", "Yield on Advances", 100 * c["int_adv"] / avg_adv, "%", M,
        "Interest on advances / average advances", "Average interest rate the bank earns on its loans.")
    add("cost_dep", "Cost of Deposits", rep("cost_of_deposits"), "%", M,
        "Interest on deposits / average deposits", "Average rate paid to depositors.",
        higher_is_better=False, source="Annual report")
    add("cost_funds", "Cost of Funds", 100 * (c["ie_dep"] + c["ie_borr"]) / avg_funds, "%", M,
        "Interest on deposits & borrowings / average (deposits + borrowings)",
        "Blended cost of all borrowed money.", higher_is_better=False)
    add("spread", "Spread (Yield on Advances - Cost of Funds)",
        100 * c["int_adv"] / avg_adv - 100 * (c["ie_dep"] + c["ie_borr"]) / avg_funds, "%", M,
        "Yield on advances - cost of funds", "Gross lending spread.")
    add("nonint_share", "Other Income share of Net Revenue", 100 * c["other_income"] / c["net_revenue"], "%", M,
        "Other income / (NII + other income)", "How diversified revenue is beyond lending.")
    add("fee_assets", "Fee Income / Avg Assets", 100 * c["fees"] / avg_assets, "%", M,
        "Fees & commission / average assets", "Recurring fee earning power.")
    # ---- Asset quality
    gn, nn = rep("gnpa_amt"), rep("nnpa_amt")
    add("gnpa", "Gross NPA Ratio", rep("gnpa_pct"), "%", A, "Gross NPAs / gross advances",
        "Share of loans that have stopped paying (90+ days overdue).", higher_is_better=False,
        source="Annual report")
    add("nnpa", "Net NPA Ratio", rep("nnpa_pct"), "%", A, "Net NPAs / net advances",
        "Bad loans left after provisions.", higher_is_better=False, source="Annual report")
    add("pcr", "Provision Coverage Ratio (specific)", 100 * (1 - nn / gn), "%", A,
        "(Gross NPA - Net NPA) / Gross NPA", "How much of bad loans is already provided for.")
    add("pcr_total", "Coverage incl. floating & contingent provisions", rep("pcr_total"), "%", A,
        "All provisions / Gross NPAs", "Total cushion against bad loans.", source="Annual report")
    add("credit_cost", "Credit Cost", 100 * c["provisions"] / avg_adv, "%", A,
        "Provisions & contingencies / average advances",
        "Cost of bad loans per year. FY24 & FY26 include large floating provisions (Rs 10,900 cr & Rs 9,000 cr).",
        higher_is_better=False)
    add("prov_ppop", "Provisions / Operating Profit", 100 * c["provisions"] / c["ppop"], "%", A,
        "Provisions / pre-provision operating profit", "Share of operating profit eaten by provisions.",
        higher_is_better=False)
    add("nnpa_nw", "Net NPA / Net Worth", 100 * nn / c["net_worth"], "%", A, "Net NPAs / net worth",
        "How much unprovided bad loans could hurt equity.", higher_is_better=False)
    # ---- Capital
    add("crar", "Capital Adequacy Ratio (CRAR)", rep("crar"), "%", K, "Total capital / risk-weighted assets",
        "RBI minimum incl. buffers is ~11.9% for HDFC Bank (D-SIB).", source="Annual report")
    add("tier1", "Tier-1 Capital Ratio", rep("tier1"), "%", K, "Tier-1 capital / RWA", "Core + AT1 capital.",
        source="Annual report")
    add("cet1", "CET-1 Ratio", rep("cet1"), "%", K, "Common equity tier-1 / RWA", "Purest form of capital.",
        source="Annual report")
    add("leverage", "Basel III Leverage Ratio", rep("leverage_ratio"), "%", K, "Tier-1 capital / total exposure",
        "Non-risk-based backstop ratio.", source="Annual report")
    add("rwa_density", "RWA Density", 100 * rep("rwa") / c["total_assets"], "%", K, "RWA / total assets",
        "How risky the balance sheet is on average.", higher_is_better=False)
    add("equity_mult", "Equity Multiplier (Leverage)", avg_assets / avg_nw, "x", K,
        "Average assets / average net worth", "ROE = ROA x this number.", higher_is_better=False)
    add("debt_equity", "Debt-Equity Ratio", rep("debt_equity"), "x", K, "Borrowings (>1yr) / equity",
        "Jumped in FY24 because HDFC Ltd's bonds came onto the books.", higher_is_better=False,
        source="Annual report")
    # ---- Liquidity & funding
    add("cd_ratio", "Credit-Deposit (CD) Ratio", 100 * c["advances"] / c["deposits"], "%", L,
        "Advances / deposits", "Above 100% means loans are funded partly by borrowings (post-merger effect).",
        higher_is_better=False)
    add("casa", "CASA Ratio", rep("casa_pct"), "%", L, "(Current + Savings deposits) / total deposits",
        "Low-cost deposits. Higher = cheaper funding.", source="Annual report")
    add("inv_dep", "Investment-Deposit Ratio", 100 * c["investments"] / c["deposits"], "%", L,
        "Investments / deposits", "Share of deposits parked in securities (mostly G-secs).")
    add("liquid_assets", "Liquid Assets / Total Assets", 100 * c["cash"] / c["total_assets"], "%", L,
        "(Cash + bank balances) / total assets", "Immediate liquidity on the balance sheet.")
    add("dep_share", "Deposits / Total Liabilities", 100 * c["deposits"] / c["total_assets"], "%", L,
        "Deposits / total liabilities & equity", "How much of the bank is funded by deposits.")
    add("borr_share", "Borrowings / Total Liabilities", 100 * c["borrowings"] / c["total_assets"], "%", L,
        "Borrowings / total liabilities & equity", "Reliance on wholesale borrowings.", higher_is_better=False)
    # ---- Efficiency
    add("cti", "Cost-to-Income Ratio", 100 * c["opex"] / c["net_revenue"], "%", E, "Opex / net revenue",
        "Rs spent to earn Rs 100 of revenue. Lower is better.", higher_is_better=False)
    add("opex_assets", "Opex / Avg Assets", 100 * c["opex"] / avg_assets, "%", E, "Operating expenses / avg assets",
        "Cost of running the balance sheet.", higher_is_better=False)
    add("emp_share", "Employee Cost / Opex", 100 * c["emp"] / c["opex"], "%", E, "Employee cost / opex",
        "Share of costs going to staff.", higher_is_better=False)
    add("biz_emp", "Business per Employee", rep("business_per_emp"), "Rs cr", E, "(Deposits + advances) / employees",
        "Productivity of staff.", source="Annual report")
    add("profit_emp", "Profit per Employee", rep("profit_per_emp"), "Rs cr", E, "PAT / employees",
        "Profit generated per employee.", source="Annual report")
    add("profit_branch", "Profit per Branch", c["pat"] / series(ops, "branches", years), "Rs cr", E,
        "PAT / number of branches", "Profit generated per branch.")
    # ---- Per share & valuation (bonus-adjusted)
    eps, bvps, dps, px = rep("eps_adj"), rep("bvps_adj"), rep("dps_adj"), rep("price_mar31")
    add("eps", "Earnings per Share (bonus-adjusted)", eps, "Rs", V, "PAT / weighted shares",
        "Adjusted for the 1:1 bonus issue of FY26 so all years are comparable.", source="Annual report")
    add("bvps", "Book Value per Share (bonus-adjusted)", bvps, "Rs", V, "Net worth / shares",
        "Accounting value of one share.", source="Annual report")
    add("dps", "Dividend per Share (bonus-adjusted)", dps, "Rs", V, "Dividend declared / share",
        "FY26 includes a special interim dividend of Rs 2.5.", source="Annual report")
    add("payout", "Dividend Payout Ratio", rep("payout"), "%", V, "Dividend / PAT",
        "Share of profit paid out.", source="Annual report")
    add("pe", "P/E on 31-Mar price", px / eps, "x", V, "Price / EPS", "How many years of earnings the market pays.",
        higher_is_better=False)
    add("pb", "P/B on 31-Mar price", px / bvps, "x", V, "Price / book value per share",
        "The main valuation yardstick for banks.", higher_is_better=False)
    add("div_yield", "Dividend Yield on 31-Mar price", 100 * dps / px, "%", V, "DPS / price", "Cash return.")
    add("mcap", "Market Cap on 31-Mar", px * shares_cr, "Rs cr", V, "Price x shares outstanding",
        "Value the market puts on the bank.")
    # ---- Growth
    add("g_adv", "Advances Growth", 100 * c["advances"].pct_change(), "%", G, "YoY change in advances",
        "FY24 jump = HDFC Ltd merger (July 2023).")
    add("g_dep", "Deposit Growth", 100 * c["deposits"].pct_change(), "%", G, "YoY change in deposits",
        "Deposit growth above loan growth brings the CD ratio down.")
    add("g_nii", "NII Growth", 100 * c["nii"].pct_change(), "%", G, "YoY change in NII", "Core income growth.")
    add("g_pat", "Net Profit Growth", 100 * c["pat"].pct_change(), "%", G, "YoY change in PAT", "Bottom-line growth.")
    add("g_assets", "Total Asset Growth", 100 * c["total_assets"].pct_change(), "%", G, "YoY change in assets",
        "Balance sheet expansion.")
    add("g_eps", "EPS Growth", 100 * eps.pct_change(), "%", G, "YoY change in adjusted EPS",
        "Per-share growth (merger issued new shares in FY24).")

    df = pd.DataFrame(R).T
    for y in years:
        df[y] = pd.to_numeric(df[y], errors="coerce")
    return df


def dupont(d: dict, st: dict) -> pd.DataFrame:
    """ROA tree: each line as % of average total assets."""
    years = d["years"]
    c = st["core"].loc[:, years].T
    aa = avg(c["total_assets"])
    out = pd.DataFrame({
        "Net Interest Income": 100 * c["nii"] / aa,
        "Other Income": 100 * c["other_income"] / aa,
        "Operating Expenses": -100 * c["opex"] / aa,
        "Provisions": -100 * c["provisions"] / aa,
        "Tax": -100 * c["tax"] / aa,
    })
    out["ROA"] = out.sum(axis=1)
    out["Equity Multiplier (x)"] = aa / avg(c["net_worth"])
    out["ROE"] = out["ROA"] * out["Equity Multiplier (x)"]
    return out.T


def cagr(first: float, last: float, years: int) -> float:
    if first is None or last is None or first <= 0 or years <= 0:
        return np.nan
    return 100 * ((last / first) ** (1 / years) - 1)
