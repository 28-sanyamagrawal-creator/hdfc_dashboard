"""
scenarios.py
------------
A simple, transparent 5-year projection model for HDFC Bank.

How the model works (each year):
    Advances        = last year x (1 + loan growth)
    Deposits        = last year x (1 + deposit growth)
    Total assets    = last year x (1 + loan growth)     (balance sheet grows with loans)
    NII             = NIM x average total assets
    Other income    = other-income yield x average total assets
    Opex            = cost-to-income x (NII + other income)
    Provisions      = credit cost x average advances
    Tax             = tax rate x PBT
    Net worth       = last year + PAT x (1 - payout)
    EPS / BVPS      = PAT / shares, net worth / shares   (share count kept constant)
    Target price    = P/B x BVPS   (or P/E x EPS) of the chosen valuation year

NIM, other-income yield and credit cost are measured on SIMPLE averages of opening and
closing balances, so the model starts exactly from the last reported year.
These are illustrative assumptions for a student project - not investment advice.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

PRESETS = {
    "Bear": dict(adv_growth=8.0, dep_growth=10.0, nim=2.95, oth_inc=1.20, cti=40.5, credit_cost=0.70,
                 tax_rate=25.2, payout=25.0, pb=1.5, pe=12.0),
    "Base": dict(adv_growth=12.0, dep_growth=13.0, nim=3.10, oth_inc=1.30, cti=39.0, credit_cost=0.55,
                 tax_rate=25.0, payout=25.0, pb=1.9, pe=15.0),
    "Bull": dict(adv_growth=16.0, dep_growth=15.0, nim=3.30, oth_inc=1.40, cti=37.0, credit_cost=0.40,
                 tax_rate=24.5, payout=25.0, pb=2.4, pe=18.0),
}

DESCRIPTIONS = {
    "Bear": "Loan growth slows to single digits, deposit competition and rate cuts squeeze NIM, unsecured "
            "retail stress lifts credit costs and governance worries keep the stock de-rated.",
    "Base": "Mid-teens deposit growth lets loan growth settle near 12%; NIM holds near FY26 levels as "
            "high-cost HDFC Ltd borrowings run off; credit costs normalise without big floating provisions.",
    "Bull": "With the CD ratio back below 95%, loan growth re-accelerates to mid/high-teens, cheaper "
            "funding lifts NIM, operating leverage improves cost-to-income and the market re-rates the stock.",
    "Custom": "Your own assumptions - move the sliders and every number, chart and target price updates.",
}

SLIDERS = {  # key: (label, min, max, step, help)
    "adv_growth": ("Loan (advances) growth % p.a.", 0.0, 25.0, 0.5, "FY26 actual: 12.1%"),
    "dep_growth": ("Deposit growth % p.a.", 0.0, 25.0, 0.5, "FY26 actual: 14.4%"),
    "nim": ("NIM % (NII / avg total assets)", 2.4, 4.0, 0.05, "FY26 on the same basis: ~3.11%"),
    "oth_inc": ("Other income % of avg assets", 0.8, 2.0, 0.05, "FY26: ~1.51% incl. HDB stake-sale gain; ~1.29% without"),
    "cti": ("Cost-to-income %", 30.0, 50.0, 0.5, "FY26 actual: 38.0%"),
    "credit_cost": ("Credit cost % of avg advances", 0.1, 2.0, 0.05, "FY26: 0.84% incl. Rs 9,000 cr floating provision; ~0.52% without"),
    "tax_rate": ("Tax rate %", 15.0, 30.0, 0.5, "Statutory rate ~25.2%"),
    "payout": ("Dividend payout %", 0.0, 60.0, 1.0, "FY26 actual: 31.9% (incl. special dividend)"),
    "pb": ("Target P/B multiple (x)", 1.0, 4.0, 0.05, "31-Mar P/B: FY22 3.4x, FY24 2.5x, FY26 2.0x"),
    "pe": ("Target P/E multiple (x)", 8.0, 30.0, 0.5, "31-Mar P/E: FY22 22x, FY24 17x, FY26 15x"),
}


def starting_point(core: pd.DataFrame, last_year: str, prev_year: str) -> dict:
    """Pull the opening balances the model needs from the last reported year."""
    c = core
    return dict(year=last_year, total_assets=c.at["total_assets", last_year], advances=c.at["advances", last_year],
                deposits=c.at["deposits", last_year], net_worth=c.at["net_worth", last_year],
                shares_cr=c.at["capital", last_year], pat=c.at["pat", last_year],
                prev_total_assets=c.at["total_assets", prev_year], prev_advances=c.at["advances", prev_year])


def calibrate(core: pd.DataFrame, last_year: str, prev_year: str) -> dict:
    """Last reported year's ratios on the model's own (simple-average) basis."""
    c = core
    aa = (c.at["total_assets", last_year] + c.at["total_assets", prev_year]) / 2
    aadv = (c.at["advances", last_year] + c.at["advances", prev_year]) / 2
    return dict(
        adv_growth=100 * (c.at["advances", last_year] / c.at["advances", prev_year] - 1),
        dep_growth=100 * (c.at["deposits", last_year] / c.at["deposits", prev_year] - 1),
        nim=100 * c.at["nii", last_year] / aa,
        oth_inc=100 * c.at["other_income", last_year] / aa,
        cti=100 * c.at["opex", last_year] / c.at["net_revenue", last_year],
        credit_cost=100 * c.at["provisions", last_year] / aadv,
        tax_rate=100 * c.at["tax", last_year] / c.at["pbt", last_year],
    )


def project(start: dict, a: dict, n_years: int = 5) -> pd.DataFrame:
    """Run the projection. a = assumptions dict (percent values as numbers, e.g. 12 = 12%)."""
    rows = []
    ta, adv, dep, nw = start["total_assets"], start["advances"], start["deposits"], start["net_worth"]
    fy = int(start["year"][2:])
    shares = start["shares_cr"]
    for i in range(1, n_years + 1):
        ta_new = ta * (1 + a["adv_growth"] / 100)
        adv_new = adv * (1 + a["adv_growth"] / 100)
        dep_new = dep * (1 + a["dep_growth"] / 100)
        avg_ta, avg_adv = (ta + ta_new) / 2, (adv + adv_new) / 2
        nii = a["nim"] / 100 * avg_ta
        oi = a["oth_inc"] / 100 * avg_ta
        rev = nii + oi
        opex = a["cti"] / 100 * rev
        ppop = rev - opex
        prov = a["credit_cost"] / 100 * avg_adv
        pbt = ppop - prov
        tax = a["tax_rate"] / 100 * pbt
        pat = pbt - tax
        div = pat * a["payout"] / 100
        nw_new = nw + pat - div
        rows.append(dict(year=f"FY{fy + i}E", advances=adv_new, deposits=dep_new, total_assets=ta_new,
                         cd_ratio=100 * adv_new / dep_new, nii=nii, other_income=oi, net_revenue=rev, opex=opex,
                         ppop=ppop, provisions=prov, pbt=pbt, tax=tax, pat=pat, dividend=div, net_worth=nw_new,
                         eps=pat / shares, bvps=nw_new / shares, dps=div / shares,
                         roa=100 * pat / avg_ta, roe=100 * pat / ((nw + nw_new) / 2)))
        ta, adv, dep, nw = ta_new, adv_new, dep_new, nw_new
    return pd.DataFrame(rows).set_index("year")


def target_price(proj: pd.DataFrame, a: dict, method: str, val_year: str) -> float:
    if val_year not in proj.index:
        val_year = proj.index[min(1, len(proj) - 1)]
    if method == "P/E":
        return a["pe"] * proj.at[val_year, "eps"]
    return a["pb"] * proj.at[val_year, "bvps"]


def sensitivity(start: dict, a: dict, method: str, val_year: str,
                nim_values: list, multiple_values: list) -> pd.DataFrame:
    """Implied price grid: rows = NIM, columns = valuation multiple."""
    grid = []
    for nim in nim_values:
        row = []
        for m in multiple_values:
            aa = dict(a, nim=nim)
            aa["pb" if method == "P/B" else "pe"] = m
            row.append(target_price(project(start, aa), aa, method, val_year))
        grid.append(row)
    return pd.DataFrame(grid, index=[f"{v:.2f}%" for v in nim_values],
                        columns=[f"{m:.1f}x" for m in multiple_values])


def cagr_series(first: float, last: float, years: int) -> float:
    if first <= 0 or years <= 0:
        return np.nan
    return 100 * ((last / first) ** (1 / years) - 1)
