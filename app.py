import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# ============================================================
# STREAMLIT PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Supply Chain Simulation Performance Review",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
        .main {
            background-color: #f7f9fc;
        }

        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2rem;
        }

        .hero-card {
            padding: 1.5rem 1.7rem;
            border-radius: 22px;
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #0f766e 100%);
            color: white;
            box-shadow: 0 14px 35px rgba(15, 23, 42, 0.20);
            margin-bottom: 1.3rem;
        }

        .hero-title {
            font-size: 2.1rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }

        .hero-subtitle {
            font-size: 1rem;
            opacity: 0.9;
            line-height: 1.5;
        }

        .kpi-card {
            padding: 1.05rem 1.1rem;
            border-radius: 18px;
            background: white;
            border: 1px solid #e5e7eb;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.07);
            height: 145px;
        }

        .kpi-label {
            color: #64748b;
            font-size: 0.88rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .kpi-value {
            color: #0f172a;
            font-size: 1.85rem;
            font-weight: 850;
            margin-top: 0.25rem;
        }

        .kpi-delta-positive {
            margin-top: 0.3rem;
            color: #059669;
            font-size: 0.92rem;
            font-weight: 700;
        }

        .kpi-delta-muted {
            margin-top: 0.3rem;
            color: #475569;
            font-size: 0.92rem;
            font-weight: 700;
        }

        .section-card {
            padding: 1.15rem 1.25rem;
            border-radius: 18px;
            background-color: white;
            border: 1px solid #e5e7eb;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
            margin-bottom: 1rem;
        }

        .insight-box {
            padding: 1rem 1.15rem;
            border-radius: 16px;
            background: #eef6ff;
            border-left: 6px solid #2563eb;
            color: #0f172a;
            font-size: 0.98rem;
            line-height: 1.6;
            margin-top: 0.4rem;
            margin-bottom: 1.2rem;
        }

        .insight-title {
            font-weight: 850;
            color: #1d4ed8;
            margin-bottom: 0.35rem;
            font-size: 1.03rem;
        }

        .small-muted {
            color: #64748b;
            font-size: 0.9rem;
        }

        div[data-testid="stMetric"] {
            background-color: white;
            border: 1px solid #e5e7eb;
            padding: 1rem;
            border-radius: 18px;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATASET — HARDCODED, SELF-CONTAINED
# ============================================================

DATA = {
    'Metric': [
        'ROI',
        'Realized Revenue',
        'Gross Margin',
        'Operating Profit',
        'Total Investment',
        'Total Penalties and Bonuses',
        'Overhead Costs',
        'Stock Costs',
        'Handling Costs',
        'Administration Costs',
        'Distribution Costs'
    ],
    'Round 0': [
        -0.0768,
        2306254.90,
        903148.15,
        -306503.26,
        3989512.92,
        -322708.25,
        28834.30,
        101918.42,
        59373.20,
        109717.10,
        192114.41
    ],
    'Round 1': [
        0.0138,
        2651675.99,
        1237981.45,
        55005.59,
        3981803.95,
        22712.84,
        28834.30,
        102434.93,
        59373.20,
        109718.84,
        192114.41
    ],
    'Round 2': [
        0.0311,
        2631324.28,
        1257474.15,
        122964.04,
        3957417.30,
        27707.38,
        28699.12,
        110996.34,
        59286.29,
        109565.92,
        191206.18
    ],
    'Round 3': [
        0.0278,
        2631197.80,
        1257520.15,
        110472.93,
        3972307.72,
        27580.69,
        28699.12,
        123282.72,
        59286.29,
        109562.44,
        191206.18
    ],
    'Round 4': [
        0.0378,
        2625101.40,
        1268849.52,
        146744.18,
        3878855.15,
        26482.34,
        28834.30,
        115998.65,
        59373.20,
        109830.51,
        191206.53
    ],
    'Round 5': [
        0.0383,
        2624969.33,
        1268728.51,
        148427.78,
        3878687.97,
        26350.74,
        28834.30,
        114251.78,
        59373.20,
        109844.43,
        191206.53
    ],
    'Round 6': [
        0.0386,
        2654146.90,
        1283853.47,
        149886.41,
        3882115.54,
        22485.94,
        28834.30,
        116263.31,
        59373.20,
        109853.14,
        191206.53
    ]
}


# ============================================================
# DATA PREPARATION
# ============================================================

@st.cache_data
def load_data():
    df = pd.DataFrame(DATA)
    rounds = [f"Round {i}" for i in range(7)]

    long_df = df.melt(
        id_vars="Metric",
        value_vars=rounds,
        var_name="Round",
        value_name="Value"
    )

    wide = df.set_index("Metric")[rounds].T.reset_index()
    wide = wide.rename(columns={"index": "Round"})
    wide["Round Number"] = wide["Round"].str.extract(r"(\d+)").astype(int)
    wide["ROI (%)"] = wide["ROI"] * 100
    wide["ROI Bubble Size"] = wide["ROI (%)"].abs() * 18 + 18

    return df, long_df, wide, rounds


df, long_df, wide, rounds = load_data()


# ============================================================
# FORMATTERS
# ============================================================

def money(value):
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.2f}K"
    return f"${value:,.2f}"


def money_signed(value):
    sign = "+" if value >= 0 else "-"
    return f"{sign}${abs(value):,.2f}"


def percentage(value):
    return f"{value * 100:.2f}%"


def percentage_points(value):
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f} pts"


def chart_layout(fig, title, height=520):
    fig.update_layout(
        title={
            "text": title,
            "x": 0.02,
            "xanchor": "left",
            "font": {"size": 22}
        },
        height=height,
        template="plotly_white",
        margin=dict(l=40, r=40, t=80, b=45),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified"
    )
    return fig


def insight_box(text):
    st.markdown(
        f"""
        <div class="insight-box">
            <div class="insight-title">Supply Chain Head Actionable Insight</div>
            <div>{text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.title("📦 Control Tower")
    st.markdown(
        """
        This executive dashboard reviews supply chain simulation performance from 
        **Round 0 to Round 6**.
        """
    )

    selected_view = st.radio(
        "Navigate dashboard",
        [
            "Executive Overview",
            "Turnaround Journey",
            "SLA Reliability",
            "Cost Efficiency Matrix",
            "Margin Optimization",
            "Capital Efficiency",
            "Raw Data"
        ]
    )

    st.divider()

    st.subheader("Round 6 Snapshot")
    st.metric("ROI", percentage(wide.loc[6, "ROI"]))
    st.metric("Operating Profit", money(wide.loc[6, "Operating Profit"]))
    st.metric("Revenue", money(wide.loc[6, "Realized Revenue"]))

    st.divider()

    st.caption(
        "Built with Streamlit, Pandas, and Plotly. "
        "No external Excel or CSV dependency is required."
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">Supply Chain Simulation Performance Review</div>
        <div class="hero-subtitle">
            Executive-ready control tower tracking profitability recovery, SLA stabilization,
            indirect cost containment, margin conversion, and capital efficiency from Round 0 to Round 6.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# KPI CARDS
# ============================================================

r0 = wide.iloc[0]
r6 = wide.iloc[6]

roi_delta_points = (r6["ROI"] - r0["ROI"]) * 100
revenue_delta = r6["Realized Revenue"] - r0["Realized Revenue"]
profit_delta = r6["Operating Profit"] - r0["Operating Profit"]
investment_delta = r6["Total Investment"] - r0["Total Investment"]

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Final ROI</div>
            <div class="kpi-value">{percentage(r6["ROI"])}</div>
            <div class="kpi-delta-positive">
                ▲ {roi_delta_points:.2f} pts from {percentage(r0["ROI"])}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Realized Revenue</div>
            <div class="kpi-value">{money(r6["Realized Revenue"])}</div>
            <div class="kpi-delta-positive">
                ▲ {money(revenue_delta)} vs Round 0
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Operating Profit</div>
            <div class="kpi-value">{money(r6["Operating Profit"])}</div>
            <div class="kpi-delta-positive">
                ▲ {money(profit_delta)} from a {money(r0["Operating Profit"])} loss
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Capital Investment</div>
            <div class="kpi-value">{money(r6["Total Investment"])}</div>
            <div class="kpi-delta-muted">
                ▼ {money(abs(investment_delta))} capital released vs Round 0
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# CHART 1 — MULTI-AXIS TURNAROUND JOURNEY
# ============================================================

def render_chart_1():
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=wide["Round"],
            y=wide["Operating Profit"],
            name="Operating Profit",
            marker=dict(
                color=wide["Operating Profit"],
                colorscale="RdYlGn",
                showscale=False
            ),
            hovertemplate="<b>%{x}</b><br>Operating Profit: $%{y:,.0f}<extra></extra>"
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=wide["Round"],
            y=wide["ROI (%)"],
            name="ROI (%)",
            mode="lines+markers",
            line=dict(width=4, color="#2563eb"),
            marker=dict(size=10, color="#1d4ed8"),
            hovertemplate="<b>%{x}</b><br>ROI: %{y:.2f}%<extra></extra>"
        ),
        secondary_y=True
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#475569",
        annotation_text="Break-even line",
        annotation_position="bottom right",
        secondary_y=False
    )

    fig.update_yaxes(
        title_text="Operating Profit ($)",
        tickprefix="$",
        separatethousands=True,
        secondary_y=False
    )

    fig.update_yaxes(
        title_text="ROI (%)",
        ticksuffix="%",
        secondary_y=True
    )

    fig.update_xaxes(title_text="Simulation Round")

    fig = chart_layout(
        fig,
        "Chart 1: The Multi-Axis Turnaround Journey"
    )

    st.plotly_chart(fig, use_container_width=True)

    insight_box(
        "Round 0 started with a severe operating loss and negative ROI, signaling that the network was carrying "
        "too much friction across fulfillment, cost absorption, and service reliability. By Round 6, operating profit "
        "stabilized at approximately $149.89K while ROI reached 3.86%. The key leadership takeaway is that the "
        "supply chain moved beyond one-time recovery and entered a more repeatable profitability zone."
    )


# ============================================================
# CHART 2 — SLA & DELIVERY RELIABILITY PERFORMANCE
# ============================================================

def render_chart_2():
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=wide["Round"],
            y=wide["Total Penalties and Bonuses"],
            mode="lines+markers",
            fill="tozeroy",
            name="Total Penalties and Bonuses",
            line=dict(width=4, color="#0f766e"),
            marker=dict(size=10, color="#0f766e"),
            hovertemplate="<b>%{x}</b><br>Penalty / Bonus: $%{y:,.0f}<extra></extra>"
        )
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#64748b",
        annotation_text="Penalty / Bonus Neutral Point",
        annotation_position="bottom right"
    )

    fig.update_yaxes(
        title_text="Penalties and Bonuses ($)",
        tickprefix="$",
        separatethousands=True
    )

    fig.update_xaxes(title_text="Simulation Round")

    fig = chart_layout(
        fig,
        "Chart 2: SLA & Delivery Reliability Performance"
    )

    st.plotly_chart(fig, use_container_width=True)

    insight_box(
        "The penalty position improved from a major Round 0 drag of approximately -$322.7K to positive bonus territory "
        "from Round 1 onward. This indicates that customer-facing execution improved quickly, likely through stronger "
        "delivery cadence planning, more reliable OTIF performance, and tighter service-level governance. The next move "
        "should be to protect this reliability while avoiding over-buffering inventory or capacity."
    )


# ============================================================
# CHART 3 — INDIRECT SUPPLY CHAIN EFFICIENCY MATRIX
# ============================================================

def render_chart_3():
    cost_categories = [
        "Overhead Costs",
        "Stock Costs",
        "Handling Costs",
        "Administration Costs",
        "Distribution Costs"
    ]

    heatmap_df = df[df["Metric"].isin(cost_categories)].set_index("Metric")[rounds]

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_df.values,
            x=heatmap_df.columns,
            y=heatmap_df.index,
            colorscale="Blues",
            colorbar=dict(title="Expense Intensity"),
            hovertemplate="<b>%{y}</b><br>%{x}: $%{z:,.0f}<extra></extra>"
        )
    )

    fig.update_xaxes(title_text="Simulation Round")
    fig.update_yaxes(title_text="Indirect Cost Category")

    fig = chart_layout(
        fig,
        "Chart 3: Indirect Supply Chain Efficiency Matrix"
    )

    st.plotly_chart(fig, use_container_width=True)

    insight_box(
        "The heatmap separates fixed-like cost behavior from operationally sensitive cost movement. Distribution, "
        "handling, overhead, and administration costs remained broadly controlled, while stock costs fluctuated more "
        "visibly across rounds. For a Supply Chain Head, this points directly to safety stock policy, warehouse capacity "
        "utilization, reorder timing, and demand-supply synchronization as the next levers for cost containment."
    )


# ============================================================
# CHART 4 — MARGIN OPTIMIZATION ANALYSIS
# ============================================================

def render_chart_4():
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=wide["Round"],
            y=wide["Gross Margin"],
            name="Gross Margin",
            marker_color="#1d4ed8",
            hovertemplate="<b>%{x}</b><br>Gross Margin: $%{y:,.0f}<extra></extra>"
        )
    )

    fig.add_trace(
        go.Bar(
            x=wide["Round"],
            y=wide["Operating Profit"],
            name="Operating Profit",
            marker_color="#16a34a",
            hovertemplate="<b>%{x}</b><br>Operating Profit: $%{y:,.0f}<extra></extra>"
        )
    )

    fig.update_layout(barmode="group")

    fig.update_yaxes(
        title_text="Financial Value ($)",
        tickprefix="$",
        separatethousands=True
    )

    fig.update_xaxes(title_text="Simulation Round")

    fig = chart_layout(
        fig,
        "Chart 4: Margin Optimization Analysis"
    )

    st.plotly_chart(fig, use_container_width=True)

    insight_box(
        "Gross margin expanded materially from Round 0 and stayed above $1.23M from Round 1 onward. More importantly, "
        "operating profit moved from a deep loss into sustained positive territory, proving that production margin was "
        "not being consumed by downstream inefficiency. The leadership implication is clear: preserve gross margin gains "
        "while continuing to compress fulfillment friction, inventory holding waste, and avoidable service penalties."
    )


# ============================================================
# CHART 5 — INVESTMENT RETURN EFFICIENCY
# ============================================================

def render_chart_5():
    fig = px.scatter(
        wide,
        x="Total Investment",
        y="Operating Profit",
        size="ROI Bubble Size",
        color="ROI (%)",
        text="Round",
        color_continuous_scale="Viridis",
        hover_data={
            "Round": True,
            "Total Investment": ":,.0f",
            "Operating Profit": ":,.0f",
            "ROI (%)": ":.2f",
            "ROI Bubble Size": False
        }
    )

    fig.update_traces(
        textposition="top center",
        marker=dict(
            sizemode="diameter",
            line=dict(width=1, color="white")
        )
    )

    fig.update_xaxes(
        title_text="Total Investment ($)",
        tickprefix="$",
        separatethousands=True
    )

    fig.update_yaxes(
        title_text="Operating Profit ($)",
        tickprefix="$",
        separatethousands=True
    )

    fig = chart_layout(
        fig,
        "Chart 5: Investment Return Efficiency"
    )

    st.plotly_chart(fig, use_container_width=True)

    insight_box(
        "The bubble scatter shows the capital productivity story: the business reduced total investment from roughly "
        "$3.99M in Round 0 to about $3.88M in Round 6 while moving operating profit from a loss to approximately $149.89K. "
        "This suggests better capital discipline, improved asset utilization, and stronger return generation per dollar "
        "tied up in the supply chain. The next executive question is where additional capital can be released without "
        "weakening SLA reliability."
    )


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

def render_executive_overview():
    st.markdown(
        """
        <div class="section-card">
            <h3>Executive Summary</h3>
            <p>
                The simulation demonstrates a decisive financial and operational turnaround. 
                Round 0 began with negative ROI, severe operating losses, and heavy service penalties.
                By Round 6, the supply chain achieved positive ROI, stable operating profit,
                stronger gross margin conversion, and lower capital tied up in the system.
            </p>
            <p class="small-muted">
                Use the sidebar to move through each strategic lens: profitability, SLA reliability,
                indirect cost control, margin conversion, and investment productivity.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:
        render_chart_1()

    with c2:
        render_chart_2()

    c3, c4 = st.columns(2)

    with c3:
        render_chart_4()

    with c4:
        render_chart_5()

    render_chart_3()


# ============================================================
# RAW DATA VIEW
# ============================================================

def render_raw_data():
    st.subheader("Hardcoded Dataset Used by the Dashboard")
    st.dataframe(df, use_container_width=True)

    st.subheader("Round-Level Analytical Table")
    display_cols = [
        "Round",
        "ROI (%)",
        "Realized Revenue",
        "Gross Margin",
        "Operating Profit",
        "Total Investment",
        "Total Penalties and Bonuses",
        "Overhead Costs",
        "Stock Costs",
        "Handling Costs",
        "Administration Costs",
        "Distribution Costs"
    ]

    formatted = wide[display_cols].copy()
    formatted["ROI (%)"] = formatted["ROI (%)"].map(lambda x: f"{x:.2f}%")

    money_cols = [
        "Realized Revenue",
        "Gross Margin",
        "Operating Profit",
        "Total Investment",
        "Total Penalties and Bonuses",
        "Overhead Costs",
        "Stock Costs",
        "Handling Costs",
        "Administration Costs",
        "Distribution Costs"
    ]

    for col in money_cols:
        formatted[col] = formatted[col].map(lambda x: f"${x:,.2f}")

    st.dataframe(formatted, use_container_width=True)


# ============================================================
# ROUTER
# ============================================================

if selected_view == "Executive Overview":
    render_executive_overview()

elif selected_view == "Turnaround Journey":
    render_chart_1()

elif selected_view == "SLA Reliability":
    render_chart_2()

elif selected_view == "Cost Efficiency Matrix":
    render_chart_3()

elif selected_view == "Margin Optimization":
    render_chart_4()

elif selected_view == "Capital Efficiency":
    render_chart_5()

elif selected_view == "Raw Data":
    render_raw_data()


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption(
    "Supply Chain Simulation Performance Review | Streamlit Cloud-ready | "
    "Flat GitHub deployment: app.py + requirements.txt only"
)
