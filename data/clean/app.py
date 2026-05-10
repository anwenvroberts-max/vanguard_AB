import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. PAGE CONFIG & COLOR PALETTE
# ==========================================
st.set_page_config(page_title="Vanguard A-B Test Dashboard", layout="wide", initial_sidebar_state="expanded")

# Define Vanguard Color scheme
COLOR_MAP = {'Control': '#3D3D4E', 'Test': '#C41230'}
BG_COLOR = '#E5E7EB' # Platinum for gridlines & backgrounds

st.title("📊 Vanguard A/B Test Results")
st.markdown("### *A Quantitative Analysis of Vanguard UI Redesign*")
st.markdown("---")

# ==========================================
# 2. LOAD DATA
# ==========================================
@st.cache_data
def load_data():
    # Load client table
    try:
        df = pd.read_csv('client_kpi_table.csv')
    except FileNotFoundError:
        st.error("⚠️ File not found.")
        st.stop()
        
    # Clean Variation column just in case
    df = df.dropna(subset=['Variation'])
    
    # Cast completion_rate & error_rate to numeric (1/0) .astype()
    if df['completion_rate'].dtype == bool:
        df['completion_rate'] = df['completion_rate'].astype(int)
    if df['error_rate'].dtype == bool:
        df['error_rate'] = df['error_rate'].astype(int)
        
    return df

df_main = load_data()

# ==========================================
# 3. SIDEBAR FILTERS (Global)
# ==========================================
st.sidebar.header("Global Filters")

# 1. Age Filter
min_age, max_age = int(df_main['clnt_age'].min()), int(df_main['clnt_age'].max())
age_range = st.sidebar.slider("Client Age", min_age, max_age, (min_age, max_age))

# 2. Gender Filter
gender_options = df_main['gendr'].dropna().unique().tolist()
selected_genders = st.sidebar.multiselect("Gender", gender_options, default=gender_options)

# 3. Tenure Filter (Months)
min_tenure, max_tenure = int(df_main['clnt_tenure_mnth'].min()), int(df_main['clnt_tenure_mnth'].max())
tenure_range = st.sidebar.slider("Tenure (Months)", min_tenure, max_tenure, (min_tenure, max_tenure))

# 4. Balance Filter (Using numeric inputs because of "Whale" outliers)
st.sidebar.subheader("Account Balance")
min_bal = float(df_main['bal'].min())
max_bal = float(df_main['bal'].max())
bal_low = st.sidebar.number_input("Min Balance ($)", value=min_bal, step=1000.0)
bal_high = st.sidebar.number_input("Max Balance ($)", value=max_bal, step=1000.0)

# APPLY FILTERS
df_filtered = df_main[
    (df_main['clnt_age'] >= age_range[0]) & 
    (df_main['clnt_age'] <= age_range[1]) &
    (df_main['gendr'].isin(selected_genders)) &
    (df_main['clnt_tenure_mnth'] >= tenure_range[0]) &
    (df_main['clnt_tenure_mnth'] <= tenure_range[1]) &
    (df_main['bal'] >= bal_low) &
    (df_main['bal'] <= bal_high)
]

# ==========================================
# 4. A/B METRICS 
# ==========================================

# Calculate overall metrics per group
summary = df_filtered.groupby('Variation').agg(
    comp_rate=('completion_rate', 'mean'),
    avg_time=('avg_time_to_completion', 'mean'),
    err_rate=('error_rate', 'mean'),
    avg_steps=('avg_steps_client', 'mean')
).reset_index()

# Get percentages for Delta comparison
try:
    test_comp = summary.loc[summary['Variation'] == 'Test', 'comp_rate'].values[0] * 100
    ctrl_comp = summary.loc[summary['Variation'] == 'Control', 'comp_rate'].values[0] * 100
    
    test_time = summary.loc[summary['Variation'] == 'Test', 'avg_time'].values[0]
    ctrl_time = summary.loc[summary['Variation'] == 'Control', 'avg_time'].values[0]
    
    test_err = summary.loc[summary['Variation'] == 'Test', 'err_rate'].values[0] * 100
    ctrl_err = summary.loc[summary['Variation'] == 'Control', 'err_rate'].values[0] * 100
except IndexError:
    st.warning("Not enough data with current filter.")
    st.stop()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="🏆 Test Completion Rate", value=f"{test_comp:.1f}%", delta=f"{(test_comp - ctrl_comp):.1f}% vs Control")
with col2:
    st.metric(label="⏱️ Test Avg Time (Sec)", value=f"{test_time:.0f}s", delta=f"{(test_time - ctrl_time):.0f}s vs Control", delta_color="inverse")
with col3:
    st.metric(label="⚠️ Test Error Rate", value=f"{test_err:.1f}%", delta=f"{(test_err - ctrl_err):.1f}% vs Control", delta_color="inverse")

st.markdown("---")

# ==========================================
# 5. SECTION 1: CORE OUTCOMES
# ==========================================
st.subheader("Section 1: Completion Rates by A/B Group")

fig_comp = px.bar(
    summary, x='Variation', y='comp_rate', color='Variation',
    color_discrete_map=COLOR_MAP, text_auto='.1%',
    title="Frictionless Completion Rate by A/B Group",
    labels={'comp_rate': 'Completion Rate'}
)
fig_comp.update_layout(yaxis_tickformat='.0%', showlegend=False)
st.plotly_chart(fig_comp, use_container_width=True)

st.markdown("---")

# ==========================================
# 6. SECTION 2: WINS & TRADE-OFFS
# ==========================================
st.subheader("Section 2: The Cost of Friction")

st.markdown("The Test group achieved higher completion rates than the Control group, but took more time and more steps, and experienced more errors.")

c1, c2, c3 = st.columns(3)

# Time Chart
fig_time = px.bar(
    summary, x='Variation', y='avg_time', color='Variation',
    color_discrete_map=COLOR_MAP, text_auto='.0f',
    title="Avg Time to Completion (in s)"
)
fig_time.update_layout(showlegend=False)
c1.plotly_chart(fig_time, use_container_width=True)

# Steps Chart
fig_steps = px.bar(
    summary, x='Variation', y='avg_steps', color='Variation',
    color_discrete_map=COLOR_MAP, text_auto='.2f',
    title="Avg Steps per Session"
)
fig_steps.update_layout(showlegend=False)
c2.plotly_chart(fig_steps, use_container_width=True)

# Error Chart
fig_err = px.bar(
    summary, x='Variation', y='err_rate', color='Variation',
    color_discrete_map=COLOR_MAP, text_auto='.1%',
    title="Error Rate"
)
fig_err.update_layout(yaxis_tickformat='.0%', showlegend=False)
c3.plotly_chart(fig_err, use_container_width=True)

st.markdown("---")

# ==========================================
# 7. SECTION 3: RELIABILITY CHECKS
# ==========================================
st.subheader("Section 3: A/B Group Bias Check")

st.markdown("Shows the key metrics and statistics to assess the reliability of the A/B test.")

col_a, col_b = st.columns(2)

# Age Distribution (KDE/Histogram)
fig_age = px.histogram(
    df_filtered, x='clnt_age', color='Variation', barmode='overlay',
    color_discrete_map=COLOR_MAP, nbins=30, opacity=0.7,
    title="Age Distribution: Test vs. Control"
)
col_a.plotly_chart(fig_age, use_container_width=True)

# Balance Distribution 
# Filter out extreme outliers for a cleaner visual
fig_bal = px.box(
    df_filtered[df_filtered['bal'] > 0], x='Variation', y='bal', color='Variation',
    color_discrete_map=COLOR_MAP, title="Client Balance Spread (Removing $0)",
    log_y=True # Log scale 
)
fig_bal.update_layout(showlegend=False)
col_b.plotly_chart(fig_bal, use_container_width=True)
