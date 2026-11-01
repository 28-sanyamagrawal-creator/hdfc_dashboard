# HDFC Bank – Interactive Financial Dashboard (Python + Streamlit)

An interactive, live dashboard on **HDFC Bank Ltd** built entirely in Python. It uses the bank's
last five Integrated Annual Reports (FY2021-22 to FY2025-26) plus the live NSE share price from Yahoo Finance.

| Tab | What's inside |
|---|---|
| 🏠 Overview | Live price, 10 KPI cards, growth charts, auto-written highlights |
| 🏦 Company Profile | Background, sector, business model, all products & services, subsidiaries, shareholding, milestones |
| 📊 Financial Statements | P&L, Balance Sheet, Cash Flow (values / YoY growth / common size), profit and cash waterfalls, CSV download |
| 📐 Ratio Analysis | 50+ banking ratios in 9 groups (profitability, NIM, asset quality, capital, liquidity, efficiency, valuation, growth) + DuPont |
| 🧩 Segments | Retail, Wholesale, Treasury, Other banking – revenue, profit, margins |
| 📈 Live Market | Live quote (auto-refresh 60 s), candlestick chart, moving averages, volume, returns, vs Nifty Bank |
| 🔮 Future Scenarios | Bull / Base / Bear / Custom 5-year projections, implied target price, sensitivity table, bull vs bear thesis |
| 📚 Data & Notes | Sources, method notes, glossary, raw data files |

**Dynamic:** the year-range slider, unit switch (₹ crore / lakh crore / billion), live price and every scenario
slider recalculate the whole dashboard instantly. All numbers are calculated from the CSV files in `/data`,
so adding a new year column (e.g. FY27) updates everything automatically.

---

## How to run it on a Mac (step by step)

1. **Install Python** (one time): go to https://www.python.org/downloads/ → download the latest
   **Python 3.12 or newer** for macOS → open the `.pkg` and click through the installer.
2. **Unzip** `hdfc_bank_dashboard.zip` (double-click). Move the `hdfc_dashboard` folder to, for example, your Desktop.
3. **Open Terminal**: press `Cmd + Space`, type `Terminal`, press Enter.
4. **Go into the folder**: type `cd ` (with a space), drag the `hdfc_dashboard` folder into the Terminal window, press Enter.
5. **Create a virtual environment** (one time):
   ```bash
   python3 -m venv .venv
   ```
6. **Activate it** (every time you open a new Terminal):
   ```bash
   source .venv/bin/activate
   ```
   You will see `(.venv)` at the start of the line.
7. **Install the libraries** (one time, needs internet, takes 1–3 minutes):
   ```bash
   pip install -r requirements.txt
   ```
8. **Run the dashboard**:
   ```bash
   python -m streamlit run app.py
   ```
   Your browser opens at **http://localhost:8501**. If it asks for an email the first time, just press Enter.
9. **Stop it**: go back to Terminal and press `Ctrl + C`.

**Next time:** open Terminal → `cd` into the folder → `source .venv/bin/activate` → `python -m streamlit run app.py`.

**Shortcut:** right-click `run_mac.command` → **Open** → **Open**. It does steps 5–8 for you.
(If macOS says it can't be opened, run `chmod +x run_mac.command` once in Terminal, inside the folder.)

## How to run it on Windows

1. Install Python 3.12+ from https://www.python.org/downloads/ – **tick "Add python.exe to PATH"** on the first screen.
2. Unzip the folder, open it, click the address bar, type `cmd` and press Enter.
3. Run:
   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python -m streamlit run app.py
   ```
   Or simply double-click `run_windows.bat`.

## Common problems

| Problem | Fix |
|---|---|
| `command not found: python3` | Python isn't installed – step 1. |
| `No module named streamlit` | You forgot to activate the environment (step 6) or install (step 7). |
| Price shows **OFFLINE** | No internet or Yahoo blocked the request (some college Wi-Fi does). Try a phone hotspot and click **Refresh price now**. You can also type a price in **Manual price override**. |
| Port 8501 busy | `python -m streamlit run app.py --server.port 8502` |
| Charts look old after editing code | Press `R` in the browser or click **Rerun**. |

## Project structure

```
hdfc_dashboard/
├── app.py                  ← main dashboard (all tabs / layout)
├── modules/
│   ├── finance.py          ← loads CSVs, builds statements, calculates all ratios
│   ├── market.py           ← live price from Yahoo Finance (with offline fallback)
│   ├── scenarios.py        ← Bull / Base / Bear / Custom projection model
│   ├── charts.py           ← Plotly chart styles
│   └── content.py          ← company background, services, bull/bear text
├── data/                   ← numbers from the annual reports (₹ crore, standalone)
├── .streamlit/config.toml  ← colour theme
├── requirements.txt
├── run_mac.command / run_windows.bat
└── README.md
```

## Data & method

- Source: HDFC Bank Integrated Annual Reports FY22, FY23, FY24, FY25, FY26 (standalone audited statements,
  schedules, Basel III disclosures, business ratios, segment reporting, 10-year highlights).
- Values converted from ₹ thousand to ₹ crore. Every year checked: assets = liabilities, cash flows = change in cash,
  and all derived lines match the bank's 10-year financial highlights table.
- **FY24 onward includes the HDFC Ltd merger (1 July 2023)** – FY24 growth is not like-for-like.
- Per-share figures are adjusted for the **1:1 bonus issue in FY26**.
- Live price: Yahoo Finance ticker `HDFCBANK.NS` via the `yfinance` library (may be delayed ~15 min).
  investing.com has no public API and blocks scripts, so Yahoo is used.
- Scenario projections are simplified assumptions for academic use – **not investment advice**.
