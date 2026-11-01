"""
charts.py
---------
Plotly chart helpers with one consistent, clean style.
Colour rules: one colour per entity (never by rank), thin marks, light gridlines,
no dual axes, hover tooltips everywhere.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

# Categorical colours (fixed order, colour-blind checked)
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = (
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948")
SERIES = [BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED]
# Status colours - only for good / bad meaning
GOOD, WARN, BAD = "#0ca30c", "#fab219", "#d03b3b"
# Ink & chrome
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#8a8984", "#ebeae6", "#ffffff"
NAVY = "#0b3a6e"
SCENARIO_COLORS = {"Bear": ORANGE, "Base": BLUE, "Bull": AQUA, "Custom": VIOLET, "Actual": INK2}

FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


def base_layout(fig: go.Figure, title: str | None = None, height: int = 360, yaxis_title: str | None = None,
                legend: bool = True, ysuffix: str = "", yprefix: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>" if title else None, x=0, xanchor="left", font=dict(size=15, color=INK)),
        height=height, margin=dict(l=8, r=16, t=48 if title else 16, b=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=12, color=INK2),
        hovermode="x unified", hoverlabel=dict(bgcolor="white", font=dict(family=FONT, color=INK), bordercolor=GRID),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0, font=dict(size=11),
                    bgcolor="rgba(0,0,0,0)", traceorder="normal"),
        bargap=0.28, bargroupgap=0.08,
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, tickfont=dict(color=INK2), ticks="")
    fig.update_yaxes(gridcolor=GRID, gridwidth=1, zeroline=True, zerolinecolor="#d6d5d0", zerolinewidth=1,
                     linecolor="rgba(0,0,0,0)", tickfont=dict(color=MUTED), title_text=yaxis_title,
                     title_font=dict(size=11, color=MUTED), ticksuffix=ysuffix, tickprefix=yprefix,
                     tickformat=",", separatethousands=True)
    return fig


def bar(df: pd.DataFrame, x: list, cols: list, names: list | None = None, colors: list | None = None,
        title: str | None = None, barmode: str = "group", height: int = 360, unit: str = "",
        yaxis_title: str | None = None, text_last: bool = False, fmt: str = ",.0f") -> go.Figure:
    """df has one column per series, index = x labels."""
    fig = go.Figure()
    names = names or cols
    colors = colors or SERIES
    for i, (c, n) in enumerate(zip(cols, names)):
        fig.add_bar(x=x, y=df[c], name=n, marker=dict(color=colors[i % len(colors)], cornerradius=4,
                                                      line=dict(width=0)),
                    hovertemplate=f"{n}: %{{y:{fmt}}}{unit}<extra></extra>")
    fig.update_layout(barmode=barmode)
    if barmode in ("stack", "relative"):
        fig.update_traces(marker_line=dict(width=1.5, color=SURFACE))
    if text_last and len(cols) == 1:
        vals = list(df[cols[0]])
        fig.data[0].text = [f"{v:{fmt}}{unit}" if i == len(vals) - 1 else "" for i, v in enumerate(vals)]
        fig.data[0].textposition = "outside"
        fig.data[0].textfont = dict(color=INK, size=11)
        fig.data[0].cliponaxis = False
    return base_layout(fig, title, height, yaxis_title, legend=len(cols) > 1)


def line(df: pd.DataFrame, x: list, cols: list, names: list | None = None, colors: list | None = None,
         title: str | None = None, height: int = 360, unit: str = "", yaxis_title: str | None = None,
         label_ends: bool = True, fmt: str = ",.2f") -> go.Figure:
    fig = go.Figure()
    names = names or cols
    colors = colors or SERIES
    for i, (c, n) in enumerate(zip(cols, names)):
        col = colors[i % len(colors)]
        fig.add_scatter(x=x, y=df[c], name=n, mode="lines+markers",
                        line=dict(color=col, width=2), marker=dict(size=8, color=col, line=dict(width=2, color=SURFACE)),
                        hovertemplate=f"{n}: %{{y:{fmt}}}{unit}<extra></extra>")
    if label_ends:
        add_end_labels(fig, {n: (x[list(df.index).index(df[c].dropna().index[-1])], df[c].dropna().iloc[-1])
                             for c, n in zip(cols, names) if df[c].notna().any()},
                       lambda n, v: f"{v:{fmt}}{unit}")
    fig = base_layout(fig, title, height, yaxis_title, legend=len(cols) > 1, ysuffix=unit)
    vals = pd.concat([pd.to_numeric(df[c], errors="coerce") for c in cols]).dropna()
    if len(vals):
        lo, hi = float(vals.min()), float(vals.max())
        span = max(hi - lo, abs(hi) * 0.05, 1e-9)
        bottom = lo - 0.6 * span
        if lo >= 0 and bottom < 0:
            bottom = 0
        fig.update_yaxes(range=[bottom, hi + 0.4 * span])
    fig.update_layout(margin=dict(r=56))
    return fig


def add_end_labels(fig: go.Figure, ends: dict, text_fn, min_gap_frac: float = 0.06, px: int = 13):
    """Direct labels at line ends, nudged apart vertically so they never overlap.
    ends = {name: (x, y)}"""
    if not ends:
        return
    ys = [v[1] for v in ends.values()]
    span = (max(ys) - min(ys)) or abs(max(ys)) or 1
    prev, shift = None, 0
    for n, (xv, yv) in sorted(ends.items(), key=lambda kv: kv[1][1]):
        shift = shift + px if prev is not None and (yv - prev) < min_gap_frac * span * 2 else 0
        fig.add_annotation(x=xv, y=yv, text=text_fn(n, yv), showarrow=False, xanchor="left", xshift=8,
                           yshift=shift, font=dict(size=11, color=INK))
        prev = yv


def waterfall(labels: list, values: list, measures: list, title: str | None = None, height: int = 400,
              unit: str = "") -> go.Figure:
    fig = go.Figure(go.Waterfall(
        x=labels, y=values, measure=measures, connector=dict(line=dict(color=GRID, width=1)),
        increasing=dict(marker=dict(color=BLUE)), decreasing=dict(marker=dict(color=ORANGE)),
        totals=dict(marker=dict(color=NAVY)),
        text=[f"{v:,.0f}" for v in values], textposition="outside", textfont=dict(size=11, color=INK),
        hovertemplate="%{x}: %{y:,.0f}" + unit + "<extra></extra>", cliponaxis=False))
    fig = base_layout(fig, title, height, legend=False)
    fig.update_layout(hovermode="closest")
    return fig


def hbar(labels: list, values: list, title: str | None = None, color: str = BLUE, height: int = 320,
         unit: str = "", fmt: str = ",.1f") -> go.Figure:
    fig = go.Figure(go.Bar(x=values, y=labels, orientation="h", marker=dict(color=color, cornerradius=4),
                           text=[f"{v:{fmt}}{unit}" for v in values], textposition="outside",
                           textfont=dict(color=INK, size=11), cliponaxis=False,
                           hovertemplate="%{y}: %{x:" + fmt + "}" + unit + "<extra></extra>"))
    fig = base_layout(fig, title, height, legend=False)
    fig.update_layout(hovermode="closest", margin=dict(r=48))
    fig.update_yaxes(autorange="reversed", tickfont=dict(color=INK2))
    fig.update_xaxes(showgrid=True, gridcolor=GRID, showticklabels=False)
    return fig
