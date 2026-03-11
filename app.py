import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import warnings

warnings.filterwarnings('ignore')
st.set_page_config(page_title="Crime Dashboard", layout="wide")

# ---------------- Load CSV ----------------
df_path = r"C:\Users\shiva\OneDrive\Documents\crime_project\crime_data.csv"
try:
    df = pd.read_csv(df_path)
except FileNotFoundError:
    st.error(f"CSV not found at {df_path}")
    st.stop()

df.columns = df.columns.str.strip()

# ---------------- Crime Columns ----------------
crime_columns = [
    'MURDER',
    'ATTEMPT TO MURDER',
    'RAPE',
    'CUSTODIAL RAPE',
    'OTHER RAPE',
    'KIDNAPPING & ABDUCTION',
    'KIDNAPPING AND ABDUCTION OF WOMEN AND GIRLS',
    'KIDNAPPING AND ABDUCTION OF OTHERS',
    'DOWRY DEATHS',
    'ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY',
    'INSULT TO MODESTY OF WOMEN',
    'CRUELTY BY HUSBAND OR HIS RELATIVES',
    'IMPORTATION OF GIRLS FROM FOREIGN COUNTRIES'
]

crime_columns = [col for col in crime_columns if col in df.columns]
for col in crime_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# ---------------- Tabs ----------------
tabs = st.tabs(["Overview", "State Analysis", "District Analysis", "Trends"])

# ---------------- Tab 1: Overview ----------------
with tabs[0]:
    st.title("📊 Crime Dashboard Overview")
    total_crimes = df[crime_columns].sum().sum()
    highest_crime_state = df.groupby('STATE/UT')[crime_columns].sum().sum(axis=1).idxmax()
    highest_crime_count = df.groupby('STATE/UT')[crime_columns].sum().sum(axis=1).max()
    
    col1, col2 = st.columns(2)
    col1.metric("Total Crimes", int(total_crimes))
    col2.metric("State with Highest Crime", f"{highest_crime_state} ({int(highest_crime_count)})")
    
    # State-level crime map
    st.subheader("State-wise Crime Map")
    state_summary = df.groupby('STATE/UT')[crime_columns].sum().sum(axis=1).reset_index()
    state_summary.columns = ['STATE/UT', 'Total Crimes']
    
    # Plotly choropleth map (state-level)
    fig_map = px.choropleth(
        state_summary,
        locations='STATE/UT',
        locationmode='country names',  # works if names match
        color='Total Crimes',
        color_continuous_scale='Reds',
        title="Total Crimes by State"
    )
    st.plotly_chart(fig_map, use_container_width=True)

# ---------------- Tab 2: State Analysis ----------------
with tabs[1]:
    st.title("🏛️ State Analysis")
    state = st.selectbox("Select State", df['STATE/UT'].unique())
    state_df = df[df['STATE/UT'] == state]
    
    year = st.selectbox("Select Year", sorted(state_df['YEAR'].unique()))
    year_df = state_df[state_df['YEAR'] == year]
    
    selected_crimes = st.multiselect("Select Crimes to Visualize", crime_columns, default=crime_columns[:5])
    
    st.subheader(f"Crime Data for {state} in {year}")
    st.dataframe(year_df[['DISTRICT'] + selected_crimes])
    
    # Bar chart
    st.subheader("Bar Chart")
    st.bar_chart(year_df[selected_crimes].T)
    
    # Heatmap
    st.subheader("Heatmap")
    plt.figure(figsize=(12,6))
    sns.heatmap(year_df[selected_crimes], annot=True, fmt=".0f", cmap="YlOrRd")
    st.pyplot(plt)
    
    # Export CSV
    csv_data = year_df[['DISTRICT'] + selected_crimes].to_csv(index=False)
    st.download_button("Download CSV", data=csv_data, file_name=f"{state}_{year}_crime.csv")

# ---------------- Tab 3: District Analysis ----------------
with tabs[2]:
    st.title("🏘️ District Analysis")
    state_d = st.selectbox("Select State for District Analysis", df['STATE/UT'].unique(), key="state_d")
    state_df_d = df[df['STATE/UT'] == state_d]
    
    year_d = st.selectbox("Select Year", sorted(state_df_d['YEAR'].unique()), key="year_d")
    year_df_d = state_df_d[state_df_d['YEAR'] == year_d]
    
    districts = year_df_d['DISTRICT'].unique()
    selected_districts = st.multiselect("Select District(s)", districts, default=districts[:1])
    district_df = year_df_d[year_df_d['DISTRICT'].isin(selected_districts)]
    
    selected_crimes_d = st.multiselect("Select Crimes to Visualize", crime_columns, default=crime_columns[:5], key="district_crime")
    
    st.subheader(f"Crime Data for {', '.join(selected_districts)}")
    st.dataframe(district_df[['DISTRICT'] + selected_crimes_d])
    
    # Bar chart
    st.subheader("District Bar Chart")
    st.bar_chart(district_df[selected_crimes_d].T)
    
    # Heatmap
    st.subheader("District Heatmap")
    plt.figure(figsize=(12,6))
    sns.heatmap(district_df[selected_crimes_d], annot=True, fmt=".0f", cmap="YlOrRd")
    st.pyplot(plt)
    
    # Export CSV
    csv_data_d = district_df[['DISTRICT'] + selected_crimes_d].to_csv(index=False)
    st.download_button("Download CSV", data=csv_data_d, file_name=f"{state_d}_{year_d}_district_crime.csv")

# ---------------- Tab 4: Trends ----------------
with tabs[3]:
    st.title("📈 Year-wise Crime Trends")
    state_trend = st.selectbox("Select State for Trend Analysis", df['STATE/UT'].unique(), key="trend_state")
    state_df_trend = df[df['STATE/UT'] == state_trend]
    
    selected_trend_crimes = st.multiselect("Select Crime(s) for Trend", crime_columns, default=crime_columns[:5], key="trend_crime")
    
    if selected_trend_crimes:
        trend_df = state_df_trend.groupby('YEAR')[selected_trend_crimes].sum().reset_index()
        trend_df.set_index('YEAR', inplace=True)
        st.line_chart(trend_df)
    else:
        st.info("Select at least one crime to show trend.")