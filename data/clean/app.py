import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. PAGE CONFIG & VANGUARD PALETTE
# ==========================================
st.set_page_config(page_title="Vanguard A/B Test Dashboard", layout="wide", initial_sidebar_state="expanded")

# Strict Vanguard Colors
COLOR_MAP = {'Control': '#3D3D4E', 'Test': '#C41230'}
BG_COLOR = '#E5E7EB' # Platinum Reserve for gridlines/backgrounds

st.title("📊 Vanguard Digital Experience: A/B Test Results")
st.markdown("### *The Trade-Off: Increased Completion vs. Increased Friction*")
st.markdown("---")

# ==========================================
# 2. DATA LOADING (Cached for Speed)
# ==========================================
@st.cache_data
def load_data():
    # Load your master client table
    try:
        df = pd.read_csv('client_kpi_table.csv')
    except FileNotFoundError:
        st.error("⚠️ `client_kpi_table.csv` not found. Please ensure it is in the same folder as this script.")
        st.stop()
        
    # Clean Variation column just in case
    df = df.dropna(subset=['Variation'])
    
    # Ensure completion_rate and error_rate are numeric (1/0) for math
    if df['completion_rate'].dtype == bool:
        df['completion_rate'] = df['completion_rate'].astype(int)
    if df['error_rate'].dtype == bool:
        df['error_rate'] = df['error_rate'].astype(int)
        
    return df

df_master = load_data()

# ==========================================
# 3. SIDEBAR FILTERS (Global)
# ==========================================
st.sidebar.header("Global Filters")

# Age Filter
min_age, max_age = int(df_master['clnt_age'].min()), int(df_master['clnt_age'].max())
age_range = st.sidebar.slider("Client Age", min_age, max_age, (min_age, max_age))

# Gender Filter
gender_options = df_master['gendr'].dropna().unique().tolist()
selected_genders = st.sidebar.multiselect("Gender", gender_options, default=gender_options)

# Apply Filters
df_filtered = df_master[
    (df_master['clnt_age'] >= age_range[0]) & 
    (df_master['clnt_age'] <= age_range[1]) &
    (df_master['gendr'].isin(selected_genders))
]

# ==========================================
# 4. TOPLINE METRICS (The Headline Story)
# ==========================================
# Calculate overall metrics per group
summary = df_filtered.groupby('Variation').agg(
    comp_rate=('completion_rate', 'mean'),
    avg_time=('avg_time_to_completion', 'mean'),
    err_rate=('error_rate', 'mean'),
    avg_steps=('avg_steps_client', 'mean')
).reset_index()

# Extract values for Delta comparison
try:
    test_comp = summary.loc[summary['Variation'] == 'Test', 'comp_rate'].values[0] * 100
    ctrl_comp = summary.loc[summary['Variation'] == 'Control', 'comp_rate'].values[0] * 100
    
    test_time = summary.loc[summary['Variation'] == 'Test', 'avg_time'].values[0]
    ctrl_time = summary.loc[summary['Variation'] == 'Control', 'avg_time'].values[0]
    
    test_err = summary.loc[summary['Variation'] == 'Test', 'err_rate'].values[0] * 100
    ctrl_err = summary.loc[summary['Variation'] == 'Control', 'err_rate'].values[0] * 100
except IndexError:
    st.warning("Not enough data with current filters.")
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
# 5. SECTION 1: CORE OUTCOME (The Win)
# ==========================================
st.subheader("Section 1: The Primary Outcome (Completion)")

fig_comp = px.bar(
    summary, x='Variation', y='comp_rate', color='Variation',
    color_discrete_map=COLOR_MAP, text_auto='.1%',
    title="Frictionless Completion Rate by Group",
    labels={'comp_rate': 'Completion Rate'}
)
fig_comp.update_layout(yaxis_tickformat='.0%', showlegend=False)
st.plotly_chart(fig_comp, use_container_width=True)

st.markdown("---")

# ==========================================
# 6. SECTION 2: THE TRADE-OFF (The Cost)
# ==========================================
st.subheader("Section 2: The Friction Cost")
st.markdown("The Test group achieved higher completion, but required more time, more steps, and experienced more errors.")

c1, c2, c3 = st.columns(3)

# Time Chart
fig_time = px.bar(
    summary, x='Variation', y='avg_time', color='Variation',
    color_discrete_map=COLOR_MAP, text_auto='.0f',
    title="Avg Time to Completion (s)"
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
    title="Friction / Error Rate"
)
fig_err.update_layout(yaxis_tickformat='.0%', showlegend=False)
c3.plotly_chart(fig_err, use_container_width=True)

st.markdown("---")

# ==========================================
# 7. SECTION 3: DEMOGRAPHIC BIAS CHECK
# ==========================================
st.subheader("Methodology: Pre-Flight Bias Check")
st.markdown("Confirming the A/B test was fair by checking demographic distributions.")

col_a, col_b = st.columns(2)

# Age Distribution (KDE / Histogram)
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

