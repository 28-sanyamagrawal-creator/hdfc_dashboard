"""
content.py
----------
Text content for the dashboard: company background, services, timeline,
bull / bear thesis. Facts are taken from HDFC Bank's Integrated Annual Reports
FY2021-22 to FY2025-26 (standalone figures unless stated).
"""

COMPANY = {
    "name": "HDFC Bank Limited",
    "tagline": "India's largest private sector bank by assets",
    "nse": "HDFCBANK", "bse": "500180", "nyse": "HDB (ADS: 1 ADS = 3 shares)",
    "isin": "INE040A01034", "cin": "L65920MH1994PLC080618",
    "sector": "Financials - Banking (Private Sector Bank)",
    "industry": "Banks - Universal / Commercial Banking, regulated by the Reserve Bank of India",
    "classification": "Domestic Systemically Important Bank (D-SIB) - 'too big to fail' category",
    "incorporated": "30 August 1994 (operations began January 1995)",
    "hq": "HDFC Bank House, Senapati Bapat Marg, Lower Parel (W), Mumbai 400 013",
    "website": "www.hdfc.bank.in",
    "md_ceo": "Sashidhar Jagdishan",
    "chairman": "Keki Mistry (Interim Part-time Chairman since 19 Mar 2026)",
    "dmd": "Kaizad Bharucha (Deputy Managing Director)",
    "cfo": "Srinivasan Vaidyanathan",
    "auditors": "Batliboi & Purohit and B S R & Co. LLP (joint statutory auditors, FY26)",
    "promoter": "No identified promoter - professionally managed, widely held",
    "fy_end": "31 March",
}

ABOUT = [
    "HDFC Bank was set up in August 1994 after Housing Development Finance Corporation (HDFC) Ltd received "
    "an in-principle approval from the RBI to set up a private sector bank. It started as a "
    "wholesale bank in January 1995 and moved into retail banking, which is now its largest business.",
    "On **1 July 2023**, its parent **HDFC Ltd (India's largest housing finance company) merged into the bank**. "
    "The merger brought a large home-loan book, high-cost long-term borrowings and subsidiaries such as "
    "HDFC Life, HDFC ERGO and HDFC AMC into the group. That is why FY24 numbers jump sharply and are not "
    "directly comparable with earlier years.",
    "Today it serves **over 10 crore customers** through **9,689 branches**, **21,172 ATMs / cash recyclers** "
    "in **4,175 cities and towns**, plus net banking, mobile banking, PayZapp and WhatsApp banking, with "
    "about **2.1 lakh employees** (FY26).",
]

BUSINESS_MODEL = (
    "A bank earns mainly from the **spread** between what it charges borrowers and what it pays depositors "
    "(Net Interest Income, about two-thirds of HDFC Bank's revenue) and from **fees** on cards, payments, "
    "third-party products, forex and transaction banking. From this it pays operating costs and keeps "
    "provisions for loans that may not be repaid. The key things to watch are growth, margin (NIM), "
    "cost-to-income, asset quality (NPAs) and capital adequacy."
)

SERVICES = {
    "Retail Banking": {
        "icon": "🧑‍💼",
        "who": "Individuals, salaried professionals, NRIs, small businesses, kirana stores, self-help groups",
        "items": {
            "Accounts & Deposits": ["Savings, Current & Corporate Salary accounts", "Fixed & Recurring deposits",
                                    "NRI deposits (NRE / NRO / FCNR)"],
            "Loans": ["Personal loans (Rs 2.18 lakh cr book in FY26, 99% originated digitally)",
                      "Auto / Xpress car loans, two-wheeler loans", "Gold loans (+34% in FY26)",
                      "Loan against securities & digital loan against mutual funds",
                      "Commercial vehicle & equipment finance", "Healthcare finance, small-ticket working capital"],
            "Mortgages (from HDFC Ltd merger)": ["Home loans, NRI & affordable housing loans",
                                                 "Loan against property, rural housing, refinance",
                                                 "Gross retail mortgages Rs 8.89 lakh cr (FY26)"],
            "Cards & Payments": ["Credit, debit & prepaid cards (9+ crore cards issued in FY26)",
                                 "UPI, PayZapp, SmartHub Vyapar for merchants",
                                 "Co-branded cards (e.g. Tata Neu, Swiggy)"],
            "Wealth & Third-party Products": ["Mutual funds, life, general & health insurance distribution",
                                              "Wealth management (SmartWealth), broking via HDFC SKY"],
        },
    },
    "Wholesale Banking": {
        "icon": "🏢",
        "who": "Large corporates, MNCs, PSUs, government bodies, emerging corporates, MSME / business banking",
        "items": {
            "Loans & Deposits": ["Working capital & term loans", "Project & infrastructure finance",
                                 "Supply-chain & export finance", "Realty finance", "Wholesale deposits"],
            "Transaction Banking": ["Cash management services", "Trade finance, letters of credit & guarantees",
                                    "Custodial & correspondent banking"],
            "Investment Banking": ["Debt & equity capital markets, IPOs", "M&A advisory, loan syndication",
                                   "Private equity / VC fund raising"],
        },
    },
    "Treasury": {
        "icon": "💹",
        "who": "The bank's own balance sheet plus customers who need hedging",
        "items": {
            "For customers": ["Foreign exchange & derivatives", "Hedging solutions",
                              "Domestic & cross-border trade solutions, bullion"],
            "For the bank": ["Asset-liability management", "Government securities portfolio (SLR)",
                             "Liquidity, FX & interest-rate risk management, CRR / SLR compliance"],
        },
    },
    "Rural & Inclusive Banking": {
        "icon": "🌾",
        "who": "Farmers, rural households, priority sector",
        "items": {
            "Products": ["Kisan Gold Card & agri / tractor loans", "Rural housing", "Financial-inclusion "
                         "outreach through business correspondents and semi-urban / rural branches "
                         "(3,213 semi-urban and 1,645 rural branches in FY26)"],
        },
    },
    "Digital Banking": {
        "icon": "📱",
        "who": "All customers",
        "items": {
            "Channels": ["NetBanking, MobileBanking app, WhatsApp banking", "Digital Banking Units (DBUs)",
                         "In-house AI foundation 'Neev' for GenAI use-cases (FY26)"],
        },
    },
}

TIMELINE = [
    ("1994", "Incorporated as HDFC Bank Ltd (30 Aug) after RBI's in-principle approval to HDFC Ltd"),
    ("1995", "Starts operations as a scheduled commercial bank; lists on the stock exchanges"),
    ("2000", "Merges with Times Bank - first merger of two new-generation private banks"),
    ("2008", "Acquires Centurion Bank of Punjab"),
    ("2019-20", "Stock split: Rs 2 share split into two shares of Rs 1"),
    ("Jul 2023", "Mega-merger: parent HDFC Ltd merges into HDFC Bank (effective 1 July 2023)"),
    ("FY24", "Sells stake in HDFC Credila (education loans); creates Rs 10,900 cr floating provision"),
    ("Jul 2025", "Subsidiary HDB Financial Services lists after IPO (Rs 10,000 cr offer-for-sale by the bank)"),
    ("FY26", "First-ever 1:1 bonus issue; special interim dividend Rs 2.5 / share"),
    ("Mar 2026", "Part-time Chairman Atanu Chakraborty resigns; Keki Mistry appointed interim Chairman"),
]

BULL_POINTS = [
    ("Deposits are growing faster than loans",
     "Deposits +14.4% vs advances +12.1% in FY26. The credit-deposit ratio has fallen from ~104% after the "
     "merger (FY24) to ~95%, giving room to grow loans faster again."),
    ("Costly HDFC Ltd borrowings are running off",
     "Borrowings fell from Rs 6.62 lakh cr (FY24) to Rs 4.89 lakh cr (FY26). Of the legacy HDFC Ltd bonds "
     "(Rs 2.25 lakh cr), ~20% mature by FY28 - replacing them with deposits lowers funding cost."),
    ("Very strong capital",
     "CRAR 19.7% and CET-1 17.3% vs a regulatory need of ~11.9% total capital. Growth can be funded "
     "without raising fresh equity."),
    ("Asset quality among the best in India",
     "GNPA 1.15%, NNPA 0.38% in FY26, plus big floating provisions (Rs 10,900 cr in FY24 and Rs 9,000 cr in "
     "FY26). Coverage including all provisions is 210%."),
    ("Valuable subsidiaries",
     "Listed stakes in HDFC Life (50.2%), HDFC AMC (52.4%), HDB Financial (74.1%) plus HDFC ERGO (50.3%) - "
     "the HDB IPO showed this value can be unlocked."),
    ("Unmatched distribution and cross-sell",
     "9,689 branches and 10+ crore customers. 95%+ of home-loan customers open a savings account and 50%+ "
     "take another product - the merger's cross-sell story is still early."),
    ("Valuation has come down",
     "P/B on 31-March fell from 3.4x (FY22) to about 2.0x (FY26) even as book value grew 69%."),
]

BEAR_POINTS = [
    ("Margins are shrinking",
     "NIM (on average assets) fell from 4.1% in FY23 to 3.34% in FY26. The RBI cut the repo rate by "
     "1.25 percentage points between Feb and Dec 2025, so loan yields re-price down faster than deposit costs."),
    ("Cheaper CASA deposits have shrunk",
     "CASA ratio dropped from 48.2% (FY22) to 34.1% (FY26). Term deposits are costlier, keeping "
     "cost of deposits above 5%."),
    ("Return ratios are lower after the merger",
     "ROE fell from 17.4% (FY23) to 14.3% (FY26); ROA is ~1.9%. The mortgage book earns thinner spreads."),
    ("Governance overhang",
     "The part-time Chairman resigned on 18 Mar 2026 and a statement in his resignation letter raised "
     "questions on governance. The board ordered an external legal review (findings received 26 Jun 2026). "
     "Any further surprise could hurt sentiment."),
    ("Bad-loan stock has doubled in rupee terms",
     "Gross NPAs rose from Rs 18,019 cr (FY23) to Rs 34,061 cr (FY26) as the book grew and merged. "
     "Specific provision coverage fell from 75.8% to 67.2%."),
    ("Cost pressures",
     "One-time gratuity provision under the new labour code, rising UPI and deposit-insurance costs and "
     "continued branch expansion keep cost-to-income near 38-40%."),
    ("Macro risks",
     "El Nino and uneven monsoon, global tariff uncertainty, a 9.4% fall in the rupee against the dollar "
     "in FY26 and geopolitical tension can slow credit demand."),
]

WATCHLIST = [
    "Quarterly NIM trend vs 3.3-3.4% range",
    "Deposit growth vs loan growth (CD ratio)",
    "CASA ratio and cost of deposits",
    "Unsecured retail / credit-card slippages",
    "Any follow-up on the governance review",
    "Pace of HDFC Ltd legacy borrowing repayment",
]

GLOSSARY = {
    "NII": "Net Interest Income = interest earned - interest paid.",
    "NIM": "Net Interest Margin = NII / average assets (or interest-earning assets).",
    "CASA": "Current Account + Savings Account deposits - the cheapest source of funds.",
    "GNPA / NNPA": "Gross / Net Non-Performing Assets - loans overdue 90+ days, before / after provisions.",
    "PCR": "Provision Coverage Ratio - share of bad loans already provided for.",
    "CRAR": "Capital to Risk-weighted Assets Ratio - capital cushion as per Basel III.",
    "CET-1": "Common Equity Tier-1 - the strongest form of capital (equity + reserves).",
    "PPOP": "Pre-Provision Operating Profit = net revenue - operating expenses.",
    "Credit cost": "Provisions as % of average loans.",
    "CD ratio": "Credit-Deposit ratio = advances / deposits.",
    "RWA": "Risk-Weighted Assets - assets weighted by riskiness for capital rules.",
    "P/B": "Price to Book value - the standard valuation multiple for banks.",
    "D-SIB": "Domestic Systemically Important Bank - must hold extra capital (0.40% for HDFC Bank).",
}
