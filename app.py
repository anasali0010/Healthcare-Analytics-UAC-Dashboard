import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Healthcare Analytics Dashboard",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>

/* Sidebar width */
section[data-testid="stSidebar"]{
    width:320px !important;
}

/* Sidebar input width */
section[data-testid="stSidebar"] .stDateInput{
    width:100% !important;
}

/* Sidebar labels */
section[data-testid="stSidebar"] label{
    font-size:16px !important;
    font-weight:bold !important;
}

</style>
""", unsafe_allow_html=True)

st.title("🏥 System Capacity & Care Load Analytics")

st.markdown(
    "### Healthcare Analytics Dashboard for Unaccompanied Children Program"
)

@st.cache_data
def load_data():

    df = pd.read_excel("HHS_Unaccompanied_Alien_Children_Program.xlsx")

    df["Date"] = pd.to_datetime(df["Date"])

    df = df.sort_values("Date")

    df = df.rename(columns={
        "Children apprehended and placed in CBP custody*": "Apprehended",
        "Children in CBP custody": "CBP_Custody",
        "Children transferred out of CBP custody": "Transferred",
        "Children in HHS Care": "HHS_Care",
        "Children discharged from HHS Care": "Discharged"
    })

    df["Total_System_Load"] = df["CBP_Custody"] + df["HHS_Care"]
    df["Net_Intake"] = df["Transferred"] - df["Discharged"]
    df["Backlog"] = df["Net_Intake"].cumsum()
    df["Rolling_7"] = df["Total_System_Load"].rolling(7).mean()

    df["Month"] = df["Date"].dt.strftime("%b %Y")

    return df

df = load_data()


st.sidebar.title("📊 Filters")
st.sidebar.markdown("---")

date_range = st.sidebar.date_input(
    "📅 Select Date Range",
    value=(df["Date"].min(), df["Date"].max()),
    min_value=df["Date"].min().date(),
    max_value=df["Date"].max().date()
)

if len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = df[
        (df["Date"] >= pd.to_datetime(start_date)) &
        (df["Date"] <= pd.to_datetime(end_date))
    ]
else:
    filtered_df = df.copy()

if filtered_df.empty:
    st.warning("⚠️ No data available for the selected date range.")
    st.stop()  

monthly_load = (
    filtered_df
    .groupby(filtered_df["Date"].dt.to_period("M"))["Total_System_Load"]
    .mean()
    .reset_index()
)

monthly_load["Date"] = monthly_load["Date"].astype(str)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total System Load",
    f"{filtered_df['Total_System_Load'].sum():,}"
)

col2.metric(
    "Average Load",
    round(filtered_df["Total_System_Load"].mean(),2)
)

col3.metric(
    "Maximum Load",
    filtered_df["Total_System_Load"].max()
)

ratio = (
    filtered_df["Discharged"].sum()
    /
    filtered_df["Transferred"].sum()
) * 100

col4.metric(
    "Discharge Offset",
    f"{ratio:.2f}%"
)

st.markdown("---")
st.subheader("📈 Total System Load Trend")

fig1 = px.line(
    filtered_df,
    x="Date",
    y="Total_System_Load",
    markers=True,
    title="Total System Load Over Time"
)

fig1.update_layout(
    template="plotly_dark",
    height=500,
    xaxis_title="Date",
    yaxis_title="Total System Load"
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")
st.subheader("📊 CBP Custody vs HHS Care Comparison")

compare_df = filtered_df.melt(
    id_vars="Date",
    value_vars=["CBP_Custody", "HHS_Care"],
    var_name="Category",
    value_name="Children"
)

fig2 = px.line(
    compare_df,
    x="Date",
    y="Children",
    color="Category",
    markers=True,
    title="CBP Custody vs HHS Care"
)

fig2.update_layout(
    template="plotly_dark",
    height=500
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.subheader("📉 Net Intake Pressure")

fig3 = px.bar(
    filtered_df,
    x="Date",
    y="Net_Intake",
    title="Daily Net Intake"
)

fig3.update_layout(
    template="plotly_dark",
    height=500
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.subheader("📈 Backlog Accumulation Trend")

fig4 = px.line(
    filtered_df,
    x="Date",
    y="Backlog",
    markers=True,
    title="Backlog Accumulation"
)

fig4.update_layout(
    template="plotly_dark",
    height=500
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.subheader("📈 7-Day Rolling Average")

fig5 = px.line(
    filtered_df,
    x="Date",
    y="Rolling_7",
    title="7-Day Rolling Average"
)

fig5.update_layout(
    template="plotly_dark",
    height=500
)

st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")
st.subheader("📅 Monthly Average System Load")

fig6 = px.bar(
    monthly_load,
    x="Date",
    y="Total_System_Load",
    title="Monthly Average System Load"
)

fig6.update_layout(
    template="plotly_dark",
    height=500
)

st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.subheader("📋 Executive Insights")

highest_load = filtered_df["Total_System_Load"].max()
highest_date = filtered_df.loc[
    filtered_df["Total_System_Load"].idxmax(),
    "Date"
]

peak_backlog = abs(filtered_df["Backlog"].min())

average_load = round(filtered_df["Total_System_Load"].mean(), 2)

st.success(f"📈 Highest System Load : {highest_load}")

st.info(f"📅 Highest Load Recorded On : {highest_date.date()}")

st.warning(f"⚠️ Peak Backlog : {peak_backlog:,}")

st.write(f"🏥 Average Daily Load : {average_load}")

st.markdown("---")
st.subheader("📄 Dataset Preview")

st.dataframe(filtered_df)