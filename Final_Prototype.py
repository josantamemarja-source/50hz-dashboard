import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="50HZ Control Area Energy Dashboard",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .scenario-card {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .scenario-card:hover {
        transform: translateY(-5px);
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem;
    }
    .info-box {
        background-color: #e8f4fd;
        border-left: 5px solid #1E3A8A;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .methodology-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and introduction
st.markdown('<h1 class="main-header">⚡ 50HZ Control Area Energy Dashboard</h1>', unsafe_allow_html=True)

st.markdown("""
This dashboard provides a comprehensive analysis of energy generation, consumption, and forecasts for the **50HZ Control Area** - one of Germany's four transmission system operators, 
covering Berlin, Brandenburg, Hamburg, Mecklenburg-Vorpommern, Saxony, Saxony-Anhalt, and Thuringia.
""")

# 50HZ Control Area Information
with st.expander("📍 **50HZ Control Area Coverage**", expanded=False):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Covered Regions:
        - **Thüringen** (Thuringia)
        - **Berlin** 
        - **Brandenburg**
        - **Hamburg**
        - **Mecklenburg-Vorpommern** (Mecklenburg-Western Pomerania)
        - **Saxony** (Sachsen)
        - **Saxony-Anhalt** (Sachsen-Anhalt)
        
        ### Key Facts:
        - Covers approximately **30%** of Germany's territory
        - Serves about **18 million people**
        - High share of renewable energy production
        - Strategic importance for energy transmission
        """)
    
    with col2:
        st.markdown("""
        ### Grid Statistics:
        - **Grid Length:** ~10,000 km
        - **Peak Load:** ~15 GW
        - **Renewable Capacity:** ~40 GW
        - **CO₂ Reduction Target:** Climate neutral by 2035
        """)

# Data Loading Functions (from previous code)
@st.cache_data
def load_generation_data():
    """Load and process actual generation data"""
    try:
        excel_path = r"C:\Users\josea\OneDrive\Escritorio\Master\Third Semester\Scientific Project\New data\SMARD\Actual Generation\All_years_by_sheet-2.xlsx"
        xl = pd.ExcelFile(excel_path)
        all_data = []
        
        for sheet_name in xl.sheet_names:
            if sheet_name.isdigit():
                df_sheet = pd.read_excel(excel_path, sheet_name=sheet_name)
                df_sheet['Year'] = int(sheet_name)
                all_data.append(df_sheet)
        
        if all_data:
            df = pd.concat(all_data, ignore_index=True)
            df['Start date'] = pd.to_datetime(df['Start date'])
            df['Year'] = df['Start date'].dt.year
            
            annual_data = []
            for year in df['Year'].unique():
                year_data = df[df['Year'] == year]
                solar_total = year_data['Photovoltaics [MWh] Original resolutions'].sum()
                wind_onshore_total = year_data['Wind onshore [MWh] Original resolutions'].sum()
                wind_offshore_total = year_data['Wind offshore [MWh] Original resolutions'].sum()
                
                annual_data.append({
                    'Year': year,
                    'Photovoltaics [MWh]': solar_total,
                    'Wind Onshore [MWh]': wind_onshore_total,
                    'Wind Offshore [MWh]': wind_offshore_total,
                    'Total Generation [MWh]': solar_total + wind_onshore_total + wind_offshore_total
                })
            
            return pd.DataFrame(annual_data)
        
    except Exception as e:
        st.error(f"Error loading generation data: {e}")
    return pd.DataFrame()

@st.cache_data
def load_consumption_data():
    """Load actual consumption data"""
    try:
        csv_path = r"C:\Users\josea\OneDrive\Escritorio\Master\Third Semester\Scientific Project\New data\SMARD\Consumption\Actual Consumption\yearly_load_summary.csv"
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        st.error(f"Error loading consumption data: {e}")
    return pd.DataFrame()

@st.cache_data
def load_forecasted_consumption():
    """Load forecasted consumption data"""
    try:
        csv_path = r"C:\Users\josea\OneDrive\Escritorio\Master\Third Semester\Scientific Project\New data\SMARD\Consumption\Forecasted Consumption\Annual_Load_Summary.csv"
        df = pd.read_csv(csv_path)
        df.rename(columns={'grid_load_mwh': 'Forecasted Grid Load [MWh]',
                          'residual_load_mwh': 'Forecasted Residual Load [MWh]'}, inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading forecasted consumption: {e}")
    return pd.DataFrame()

@st.cache_data
def load_generation_forecast():
    """Load generation forecast data"""
    try:
        csv_path = r"C:\Users\josea\OneDrive\Escritorio\Master\Third Semester\Scientific Project\New data\SMARD\Generation Forecast Intraday 2018\processed\FINALS\annual_totals_by_year.csv"
        df = pd.read_csv(csv_path)
        df.rename(columns={'Photovoltaics': 'Forecasted Photovoltaics [MWh]',
                          'Wind Onshore': 'Forecasted Wind Onshore [MWh]',
                          'Wind Offshore': 'Forecasted Wind Offshore [MWh]'}, inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading generation forecast: {e}")
    return pd.DataFrame()

@st.cache_data
def load_installed_capacity():
    """Load installed capacity data"""
    try:
        csv_path = r"C:\Users\josea\OneDrive\Escritorio\Master\Third Semester\Scientific Project\New data\ENTSO\Installed Capacity per Production Type\processed_installed_capacity_MW.csv"
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        st.error(f"Error loading capacity data: {e}")
    return pd.DataFrame()

# Load all historical data
generation_df = load_generation_data()
consumption_df = load_consumption_data()
forecast_consumption_df = load_forecasted_consumption()
generation_forecast_df = load_generation_forecast()
capacity_df = load_installed_capacity()

# Main tabs for the entire dashboard
main_tab1, main_tab2 = st.tabs([
    "📊 HISTORICAL DATA ANALYSIS (2015-2025)", 
    "🔮 FUTURE SCENARIOS & SIMULATIONS (2026-2050)"
])

# ============================================
# TAB 1: HISTORICAL DATA ANALYSIS
# ============================================
with main_tab1:
    st.header("📊 Historical Data Analysis (2015-2025)")
    
    # Sidebar controls for historical data (inside this tab)
    with st.sidebar:
        if main_tab1:
            st.header("⚙️ Historical Data Controls")
            
            # Year range selector
            start_year, end_year = st.slider(
                "Select Year Range",
                min_value=2015,
                max_value=2025,
                value=(2015, 2025),
                step=1
            )
            
            # Technology filter
            st.subheader("Technology Filter")
            show_solar = st.checkbox("Photovoltaics", value=True)
            show_wind_onshore = st.checkbox("Wind Onshore", value=True)
            show_wind_offshore = st.checkbox("Wind Offshore", value=True)
            
            # Analysis parameters
            st.subheader("Analysis Parameters")
            aggregation_method = st.selectbox(
                "Data Aggregation",
                ["Annual Total", "Annual Average", "Cumulative"],
                help="How to aggregate time-series data"
            )
    
    # Filter historical data based on selected year range
    generation_df_filtered = generation_df[(generation_df['Year'] >= start_year) & (generation_df['Year'] <= end_year)]
    consumption_df_filtered = consumption_df[(consumption_df['year'] >= start_year) & (consumption_df['year'] <= end_year)]
    forecast_consumption_df_filtered = forecast_consumption_df[(forecast_consumption_df['year'] >= start_year) & (forecast_consumption_df['year'] <= end_year)]
    generation_forecast_df_filtered = generation_forecast_df[(generation_forecast_df['Year'] >= start_year) & (generation_forecast_df['Year'] <= end_year)]
    capacity_df_filtered = capacity_df[(capacity_df['Year'] >= start_year) & (capacity_df['Year'] <= end_year)]
    
    # Data availability notes
    if start_year < 2018:
        st.markdown("""
        <div class="info-box">
        ⚠️ <strong>Note:</strong> Generation Forecast Intraday data is only available from 2018 onwards. 
        Previous years are shown as missing in forecast comparison charts.
        </div>
        """, unsafe_allow_html=True)
    
    # Historical data subtabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Annual Generation Overview", 
        "🎯 Generation vs Forecast Accuracy",
        "🏭 Installed Capacity Analysis", 
        "🔌 Grid Load & Consumption"
    ])
    
    with tab1:
        st.header("Annual Generation Overview")
        
        if not generation_df_filtered.empty:
            # Prepare data for plotting
            plot_df = generation_df_filtered.melt(id_vars=['Year'], 
                                                 value_vars=['Photovoltaics [MWh]', 'Wind Onshore [MWh]', 'Wind Offshore [MWh]'],
                                                 var_name='Technology', value_name='Generation [MWh]')
            
            # Filter based on sidebar selections
            tech_filter = []
            if show_solar:
                tech_filter.append('Photovoltaics [MWh]')
            if show_wind_onshore:
                tech_filter.append('Wind Onshore [MWh]')
            if show_wind_offshore:
                tech_filter.append('Wind Offshore [MWh]')
            
            plot_df = plot_df[plot_df['Technology'].isin(tech_filter)]
            
            # Create two columns for charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Stacked area chart
                fig1 = px.area(plot_df, x='Year', y='Generation [MWh]', color='Technology',
                              title='Annual Generation by Technology',
                              labels={'Generation [MWh]': 'Generation (MWh)', 'Year': 'Year'},
                              color_discrete_map={
                                  'Photovoltaics [MWh]': '#FFD700',
                                  'Wind Onshore [MWh]': '#1E90FF',
                                  'Wind Offshore [MWh]': '#00008B'
                              })
                fig1.update_layout(height=400)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Line chart for trends
                fig2 = px.line(plot_df, x='Year', y='Generation [MWh]', color='Technology',
                              title='Generation Trends',
                              labels={'Generation [MWh]': 'Generation (MWh)', 'Year': 'Year'},
                              color_discrete_map={
                                  'Photovoltaics [MWh]': '#FFD700',
                                  'Wind Onshore [MWh]': '#1E90FF',
                                  'Wind Offshore [MWh]': '#00008B'
                              })
                fig2.update_layout(height=400)
                st.plotly_chart(fig2, use_container_width=True)
            
            # Yearly breakdown table
            st.subheader("Annual Generation Breakdown")
            display_df = generation_df_filtered.copy()
            display_df.columns = [col.replace('[MWh]', '(MWh)') for col in display_df.columns]
            st.dataframe(display_df.style.format({
                'Photovoltaics (MWh)': '{:,.0f}',
                'Wind Onshore (MWh)': '{:,.0f}',
                'Wind Offshore (MWh)': '{:,.0f}',
                'Total Generation (MWh)': '{:,.0f}'
            }), use_container_width=True)
            
            # Key metrics
            st.subheader("Key Metrics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_gen = generation_df_filtered['Total Generation [MWh]'].sum()
                st.metric("Total Generation", f"{total_gen:,.0f} MWh")
            
            with col2:
                avg_annual = generation_df_filtered['Total Generation [MWh]'].mean()
                st.metric("Average Annual Generation", f"{avg_annual:,.0f} MWh")
            
            with col3:
                solar_share = (generation_df_filtered['Photovoltaics [MWh]'].sum() / total_gen * 100)
                st.metric("Solar Share", f"{solar_share:.1f}%")
            
            with col4:
                wind_share = ((generation_df_filtered['Wind Onshore [MWh]'].sum() + 
                              generation_df_filtered['Wind Offshore [MWh]'].sum()) / total_gen * 100)
                st.metric("Wind Share", f"{wind_share:.1f}%")
        else:
            st.warning("No generation data available for the selected period.")
    
    with tab2:
        st.header("Generation vs Forecast Accuracy")
        
        if not generation_df_filtered.empty and not generation_forecast_df_filtered.empty:
            # Merge actual and forecast data
            comparison_df = pd.merge(
                generation_df_filtered[['Year', 'Photovoltaics [MWh]', 'Wind Onshore [MWh]', 'Wind Offshore [MWh]']],
                generation_forecast_df_filtered,
                on='Year',
                how='left',
                suffixes=('_Actual', '_Forecast')
            )
            
            # Filter for available years (2018+)
            comparison_df = comparison_df[comparison_df['Year'] >= 2018]
            
            if not comparison_df.empty:
                # Create comparison charts
                col1, col2 = st.columns(2)
                
                with col1:
                    # Solar comparison
                    fig_solar = go.Figure()
                    fig_solar.add_trace(go.Bar(
                        name='Actual Solar',
                        x=comparison_df['Year'],
                        y=comparison_df['Photovoltaics [MWh]'],
                        marker_color='#FFD700'
                    ))
                    fig_solar.add_trace(go.Bar(
                        name='Forecasted Solar',
                        x=comparison_df['Year'],
                        y=comparison_df['Forecasted Photovoltaics [MWh]'],
                        marker_color='#FFA500',
                        opacity=0.7
                    ))
                    fig_solar.update_layout(
                        title='Solar Generation: Actual vs Forecast',
                        barmode='group',
                        height=400,
                        yaxis_title='Generation (MWh)'
                    )
                    st.plotly_chart(fig_solar, use_container_width=True)
                
                with col2:
                    # Wind Onshore comparison
                    fig_wind = go.Figure()
                    fig_wind.add_trace(go.Bar(
                        name='Actual Wind Onshore',
                        x=comparison_df['Year'],
                        y=comparison_df['Wind Onshore [MWh]'],
                        marker_color='#1E90FF'
                    ))
                    fig_wind.add_trace(go.Bar(
                        name='Forecasted Wind Onshore',
                        x=comparison_df['Year'],
                        y=comparison_df['Forecasted Wind Onshore [MWh]'],
                        marker_color='#87CEEB',
                        opacity=0.7
                    ))
                    fig_wind.update_layout(
                        title='Wind Onshore Generation: Actual vs Forecast',
                        barmode='group',
                        height=400,
                        yaxis_title='Generation (MWh)'
                    )
                    st.plotly_chart(fig_wind, use_container_width=True)
                
                # Calculate forecast errors
                comparison_df['Solar Forecast Error [%]'] = (
                    (comparison_df['Forecasted Photovoltaics [MWh]'] - comparison_df['Photovoltaics [MWh]']) / 
                    comparison_df['Photovoltaics [MWh]'] * 100
                )
                comparison_df['Wind Onshore Forecast Error [%]'] = (
                    (comparison_df['Forecasted Wind Onshore [MWh]'] - comparison_df['Wind Onshore [MWh]']) / 
                    comparison_df['Wind Onshore [MWh]'] * 100
                )
                
                # Forecast accuracy metrics
                st.subheader("Forecast Accuracy Metrics")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    mae_solar = abs(comparison_df['Solar Forecast Error [%]']).mean()
                    st.metric("Solar Mean Absolute Error", f"{mae_solar:.1f}%")
                
                with col2:
                    mae_wind = abs(comparison_df['Wind Onshore Forecast Error [%]']).mean()
                    st.metric("Wind Onshore Mean Absolute Error", f"{mae_wind:.1f}%")
                
                with col3:
                    overall_accuracy = 100 - (abs(comparison_df[['Solar Forecast Error [%]', 
                                                               'Wind Onshore Forecast Error [%]']]).mean().mean())
                    st.metric("Overall Forecast Accuracy", f"{overall_accuracy:.1f}%")
                
                # Error visualization
                st.subheader("Forecast Error Analysis")
                fig_error = px.line(comparison_df, x='Year', 
                                   y=['Solar Forecast Error [%]', 'Wind Onshore Forecast Error [%]'],
                                   title='Forecast Error Percentage Over Time',
                                   labels={'value': 'Forecast Error (%)', 'variable': 'Technology'})
                fig_error.update_layout(height=400)
                st.plotly_chart(fig_error, use_container_width=True)
                
            else:
                st.info("Forecast comparison data is only available from 2018 onwards. Adjust year range to include 2018-2025.")
        else:
            st.warning("Insufficient data for forecast comparison.")
    
    with tab3:
        st.header("Installed Capacity Analysis")
        
        if not capacity_df_filtered.empty and not generation_df_filtered.empty:
            # Merge capacity with generation data
            capacity_analysis = pd.merge(
                capacity_df_filtered,
                generation_df_filtered[['Year', 'Photovoltaics [MWh]', 'Wind Onshore [MWh]', 'Wind Offshore [MWh]']],
                on='Year',
                how='left'
            )
            
            # Visualization
            col1, col2 = st.columns(2)
            
            with col1:
                # Installed capacity over time
                fig_cap = px.line(capacity_analysis, x='Year', y='Installed Capacity (MW)', 
                                 color='Production Type',
                                 title='Installed Capacity Development',
                                 labels={'Installed Capacity (MW)': 'Capacity (MW)', 'Year': 'Year'},
                                 color_discrete_map={'Solar': '#FFD700', 'Wind': '#1E90FF'})
                fig_cap.update_layout(height=400)
                st.plotly_chart(fig_cap, use_container_width=True)
            
            with col2:
                # Prepare data for generation vs capacity
                solar_data = capacity_analysis[capacity_analysis['Production Type'] == 'Solar']
                wind_data = capacity_analysis[capacity_analysis['Production Type'] == 'Wind']
                
                fig_scatter = go.Figure()
                
                if not solar_data.empty:
                    fig_scatter.add_trace(go.Scatter(
                        x=solar_data['Year'],
                        y=solar_data['Photovoltaics [MWh]'] / (solar_data['Installed Capacity (MW)'] * 8760) * 100,
                        mode='lines+markers',
                        name='Solar Capacity Factor',
                        marker=dict(color='#FFD700', size=10)
                    ))
                
                if not wind_data.empty:
                    wind_data = wind_data.copy()
                    wind_data['Total Wind Generation'] = (wind_data['Wind Onshore [MWh]'].fillna(0) + 
                                                         wind_data['Wind Offshore [MWh]'].fillna(0))
                    fig_scatter.add_trace(go.Scatter(
                        x=wind_data['Year'],
                        y=wind_data['Total Wind Generation'] / (wind_data['Installed Capacity (MW)'] * 8760) * 100,
                        mode='lines+markers',
                        name='Wind Capacity Factor',
                        marker=dict(color='#1E90FF', size=10)
                    ))
                
                fig_scatter.update_layout(
                    title='Capacity Factors Over Time',
                    xaxis_title='Year',
                    yaxis_title='Capacity Factor (%)',
                    height=400
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Summary statistics
            st.subheader("Capacity Statistics")
            summary_stats = capacity_analysis.groupby('Production Type').agg({
                'Installed Capacity (MW)': ['min', 'max', 'mean']
            }).round(2)
            
            st.dataframe(summary_stats, use_container_width=True)
            
        else:
            st.warning("Insufficient data for capacity analysis.")
    
    with tab4:
        st.header("Grid Load & Consumption Analysis")
        
        if not consumption_df_filtered.empty and not forecast_consumption_df_filtered.empty:
            # Merge actual and forecast consumption
            consumption_comparison = pd.merge(
                consumption_df_filtered,
                forecast_consumption_df_filtered,
                on='year',
                how='left',
                suffixes=('_Actual', '_Forecast')
            )
            
            consumption_comparison.rename(columns={'year': 'Year'}, inplace=True)
            
            # Create visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Grid load comparison
                fig_grid = go.Figure()
                fig_grid.add_trace(go.Scatter(
                    name='Actual Grid Load',
                    x=consumption_comparison['Year'],
                    y=consumption_comparison['grid_load_mwh'],
                    mode='lines+markers',
                    line=dict(color='#2E8B57', width=3)
                ))
                fig_grid.add_trace(go.Scatter(
                    name='Forecasted Grid Load',
                    x=consumption_comparison['Year'],
                    y=consumption_comparison['Forecasted Grid Load [MWh]'],
                    mode='lines+markers',
                    line=dict(color='#3CB371', width=2, dash='dash')
                ))
                fig_grid.update_layout(
                    title='Grid Load: Actual vs Forecast',
                    xaxis_title='Year',
                    yaxis_title='Grid Load (MWh)',
                    height=400,
                    hovermode='x unified'
                )
                st.plotly_chart(fig_grid, use_container_width=True)
            
            with col2:
                # Residual load comparison
                fig_residual = go.Figure()
                fig_residual.add_trace(go.Scatter(
                    name='Actual Residual Load',
                    x=consumption_comparison['Year'],
                    y=consumption_comparison['residual_load_mwh'],
                    mode='lines+markers',
                    line=dict(color='#8B0000', width=3)
                ))
                fig_residual.add_trace(go.Scatter(
                    name='Forecasted Residual Load',
                    x=consumption_comparison['Year'],
                    y=consumption_comparison['Forecasted Residual Load [MWh]'],
                    mode='lines+markers',
                    line=dict(color='#DC143C', width=2, dash='dash')
                ))
                fig_residual.update_layout(
                    title='Residual Load: Actual vs Forecast',
                    xaxis_title='Year',
                    yaxis_title='Residual Load (MWh)',
                    height=400,
                    hovermode='x unified'
                )
                st.plotly_chart(fig_residual, use_container_width=True)
            
            # Load forecast accuracy
            st.subheader("Load Forecast Accuracy")
            
            # Calculate forecast errors
            consumption_comparison['Grid Load Forecast Error [%]'] = (
                (consumption_comparison['Forecasted Grid Load [MWh]'] - 
                 consumption_comparison['grid_load_mwh']) / 
                consumption_comparison['grid_load_mwh'] * 100
            )
            
            # Display accuracy metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                mae_grid = abs(consumption_comparison['Grid Load Forecast Error [%]']).mean()
                st.metric("Grid Load MAE", f"{mae_grid:.2f}%")
            
            with col2:
                total_actual_load = consumption_comparison['grid_load_mwh'].sum()
                st.metric("Total Actual Load", f"{total_actual_load:,.0f} MWh")
            
            with col3:
                avg_annual_load = consumption_comparison['grid_load_mwh'].mean()
                st.metric("Average Annual Load", f"{avg_annual_load:,.0f} MWh")
            
            with col4:
                peak_year = consumption_comparison.loc[consumption_comparison['grid_load_mwh'].idxmax(), 'Year']
                peak_load = consumption_comparison['grid_load_mwh'].max()
                st.metric("Peak Load Year", f"{peak_year}: {peak_load:,.0f} MWh")
            
            # Data table
            st.subheader("Consumption Data")
            display_consumption = consumption_comparison.copy()
            display_consumption.columns = [col.replace('_', ' ').title() for col in display_consumption.columns]
            st.dataframe(display_consumption.style.format({
                'Grid Load Mwh': '{:,.0f}',
                'Residual Load Mwh': '{:,.0f}',
                'Forecasted Grid Load [Mwh]': '{:,.0f}',
                'Forecasted Residual Load [Mwh]': '{:,.0f}'
            }), use_container_width=True)
            
        else:
            st.warning("Insufficient consumption data available.")

# ============================================
# TAB 2: FUTURE SCENARIOS & SIMULATIONS
# ============================================
with main_tab2:
    st.header("🔮 Future Energy Scenarios 2026-2050")
    
    # Methodology explanation
    with st.expander("📊 **Projection Methodology**", expanded=True):
        st.markdown("""
        ### Four Statistical Methods for Projections:
        
        1. **Last Year Available (2025):** Uses only the most recent data point as baseline
        2. **3-Year Average (2023-2025):** Averages the last three years to smooth fluctuations
        3. **5-Year Trend (2021-2025):** Uses linear regression on recent 5-year trend
        4. **Full Historical Trend (2015-2025):** Uses complete dataset for long-term trend
        
        ### Why Multiple Methods Matter:
        - **Last Year:** Sensitive to recent events (good for current policy impact)
        - **3-Year Average:** Reduces impact of anomalous years
        - **5-Year Trend:** Captures medium-term momentum  
        - **Full Trend:** Provides most stable long-term view
        
        *Note: All methods then apply scenario-specific growth multipliers*
        """)
    
    # Sidebar controls for future scenarios
    with st.sidebar:
        if main_tab2:
            st.header("⚙️ Scenario Controls")
            
            # Projection method selection
            st.subheader("Projection Methodology")
            projection_method = st.selectbox(
                "Select Projection Method",
                [
                    "Last Year Available (2025)",
                    "3-Year Average (2023-2025)", 
                    "5-Year Trend (2021-2025)",
                    "Full Historical Trend (2015-2025)"
                ],
                index=1,
                help="Statistical method used for baseline calculations"
            )
            
            # Scenario selection
            scenario_type = st.selectbox(
                "Select Scenario Type",
                ["Business as Usual", "Conservative", "Ambitious", "Custom"],
                index=0
            )
            
            # Year for detailed view
            selected_year = st.slider(
                "Select Target Year for Analysis",
                min_value=2026,
                max_value=2050,
                value=2040,
                step=5
            )
            
            # Custom parameters
            if scenario_type == "Custom":
                st.subheader("Custom Scenario Parameters")
                
                col1, col2 = st.columns(2)
                with col1:
                    solar_growth = st.slider(
                        "Annual Solar Growth (%)",
                        min_value=0.5,
                        max_value=15.0,
                        value=7.5,
                        step=0.5
                    )
                    wind_onshore_growth = st.slider(
                        "Annual Wind Onshore Growth (%)",
                        min_value=0.5,
                        max_value=10.0,
                        value=4.0,
                        step=0.5
                    )
                
                with col2:
                    wind_offshore_growth = st.slider(
                        "Annual Wind Offshore Growth (%)",
                        min_value=0.5,
                        max_value=20.0,
                        value=12.0,
                        step=0.5
                    )
                    efficiency_improvement = st.slider(
                        "Annual Efficiency Improvement (%)",
                        min_value=0.0,
                        max_value=3.0,
                        value=1.5,
                        step=0.1
                    )
            
            # Display methodology info
            st.markdown("---")
            st.caption(f"**Active Method:** {projection_method}")
            st.caption(f"**Scenario:** {scenario_type}")
    
    # Enhanced function with multiple projection methods
    def generate_future_scenarios_enhanced(base_df, scenario_type="Business as Usual", 
                                         projection_method="3-Year Average (2023-2025)",
                                         custom_params=None):
        """Generate future scenarios with multiple projection methods"""
        
        if base_df.empty:
            # Default values if no data
            base_year = 2025
            base_values = {
                'solar_mwh': 15000000,
                'wind_onshore_mwh': 35000000,
                'wind_offshore_mwh': 5000000,
            }
        else:
            # Determine base year and values based on method
            if projection_method == "Last Year Available (2025)":
                base_year = base_df['Year'].max()
                base_data = base_df[base_df['Year'] == base_year]
                
            elif projection_method == "3-Year Average (2023-2025)":
                recent_years = base_df[base_df['Year'] >= 2023]
                base_year = 2025  # Use latest year as reference
                base_data = recent_years.mean(numeric_only=True).to_frame().T
                base_data['Year'] = base_year
                
            elif projection_method == "5-Year Trend (2021-2025)":
                # Linear regression for last 5 years
                recent_years = base_df[base_df['Year'] >= 2021].copy()
                base_year = 2025
                
                # Fit linear trend and project to base_year
                trend_values = {}
                for tech in ['Photovoltaics [MWh]', 'Wind Onshore [MWh]', 'Wind Offshore [MWh]']:
                    if tech in recent_years.columns:
                        slope, intercept, r_value, p_value, std_err = stats.linregress(
                            recent_years['Year'], 
                            recent_years[tech]
                        )
                        trend_values[tech] = slope * base_year + intercept
                
                base_data = pd.DataFrame([trend_values])
                base_data['Year'] = base_year
                
            else:  # Full Historical Trend (2015-2025)
                # Linear regression on all data
                base_year = 2025
                trend_values = {}
                for tech in ['Photovoltaics [MWh]', 'Wind Onshore [MWh]', 'Wind Offshore [MWh]']:
                    if tech in base_df.columns:
                        slope, intercept, r_value, p_value, std_err = stats.linregress(
                            base_df['Year'], 
                            base_df[tech]
                        )
                        trend_values[tech] = slope * base_year + intercept
                
                base_data = pd.DataFrame([trend_values])
                base_data['Year'] = base_year
            
            # Extract base values
            base_values = {
                'solar_mwh': base_data['Photovoltaics [MWh]'].values[0] if 'Photovoltaics [MWh]' in base_data.columns else 15000000,
                'wind_onshore_mwh': base_data['Wind Onshore [MWh]'].values[0] if 'Wind Onshore [MWh]' in base_data.columns else 35000000,
                'wind_offshore_mwh': base_data['Wind Offshore [MWh]'].values[0] if 'Wind Offshore [MWh]' in base_data.columns else 5000000,
            }
        
        # Define scenario parameters
        if scenario_type == "Conservative":
            params = {
                'solar_growth': 0.04,  # 4% annual growth
                'wind_onshore_growth': 0.02,  # 2%
                'wind_offshore_growth': 0.06,  # 6%
                'efficiency_improvement': 0.005,  # 0.5% annual reduction
                'renewable_target_2050': 0.70  # 70% renewable by 2050
            }
        elif scenario_type == "Business as Usual":
            params = {
                'solar_growth': 0.075,  # 7.5%
                'wind_onshore_growth': 0.04,  # 4%
                'wind_offshore_growth': 0.12,  # 12%
                'efficiency_improvement': 0.015,  # 1.5%
                'renewable_target_2050': 0.85  # 85%
            }
        elif scenario_type == "Ambitious":
            params = {
                'solar_growth': 0.12,  # 12%
                'wind_onshore_growth': 0.07,  # 7%
                'wind_offshore_growth': 0.18,  # 18%
                'efficiency_improvement': 0.025,  # 2.5%
                'renewable_target_2050': 0.95  # 95%
            }
        else:  # Custom
            params = custom_params if custom_params else {
                'solar_growth': solar_growth / 100,
                'wind_onshore_growth': wind_onshore_growth / 100,
                'wind_offshore_growth': wind_offshore_growth / 100,
                'efficiency_improvement': efficiency_improvement / 100,
                'renewable_target_2050': 0.90
            }
        
        # Generate future years
        years = list(range(base_year + 1, 2051))
        scenario_data = []
        
        for i, year in enumerate(years):
            years_from_base = year - base_year
            
            # Calculate growth with compounding
            solar = base_values['solar_mwh'] * ((1 + params['solar_growth']) ** years_from_base)
            wind_onshore = base_values['wind_onshore_mwh'] * ((1 + params['wind_onshore_growth']) ** years_from_base)
            wind_offshore = base_values['wind_offshore_mwh'] * ((1 + params['wind_offshore_growth']) ** years_from_base)
            
            total_renewable = solar + wind_onshore + wind_offshore
            renewable_share = min(params['renewable_target_2050'], 
                                (0.45 + (params['renewable_target_2050'] - 0.45) * (years_from_base / (2050 - base_year))))
            
            scenario_data.append({
                'Year': year,
                'Photovoltaics [MWh]': solar,
                'Wind Onshore [MWh]': wind_onshore,
                'Wind Offshore [MWh]': wind_offshore,
                'Total Renewable [MWh]': total_renewable,
                'Renewable Share [%]': renewable_share * 100,
                'Scenario': scenario_type,
                'Projection_Method': projection_method
            })
        
        return pd.DataFrame(scenario_data), base_year, base_values
    
    # Prepare custom parameters if needed
    custom_params = None
    if scenario_type == "Custom" and 'solar_growth' in locals():
        custom_params = {
            'solar_growth': solar_growth / 100,
            'wind_onshore_growth': wind_onshore_growth / 100,
            'wind_offshore_growth': wind_offshore_growth / 100,
            'efficiency_improvement': efficiency_improvement / 100,
            'renewable_target_2050': 0.90
        }
    
    # Generate scenario data
    scenario_data, base_year, base_values = generate_future_scenarios_enhanced(
        generation_df, 
        scenario_type, 
        projection_method,
        custom_params
    )
    
    # Display methodology details
    st.markdown(f"""
    <div class="methodology-box">
    <h4>📈 Active Projection Settings:</h4>
    <ul>
        <li><strong>Method:</strong> {projection_method}</li>
        <li><strong>Base Year:</strong> {base_year}</li>
        <li><strong>Scenario:</strong> {scenario_type}</li>
        <li><strong>Base Solar Generation:</strong> {base_values['solar_mwh']:,.0f} MWh</li>
        <li><strong>Base Wind Onshore:</strong> {base_values['wind_onshore_mwh']:,.0f} MWh</li>
        <li><strong>Base Wind Offshore:</strong> {base_values['wind_offshore_mwh']:,.0f} MWh</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Display scenario cards
    st.subheader("Scenario Overview")
    
    col1, col2, col3 = st.columns(3)
    
    scenario_colors = {
        "Conservative": "#FF6B6B",
        "Business as Usual": "#4ECDC4", 
        "Ambitious": "#1DD1A1",
        "Custom": "#9B59B6"
    }
    
    with col1:
        st.markdown(f"""
        <div class="scenario-card" style="border-left: 5px solid {scenario_colors.get('Conservative', '#FF6B6B')};">
            <h3>🌲 Conservative</h3>
            <p><strong>Slow transition pathway</strong></p>
            <ul>
                <li>4% annual solar growth</li>
                <li>2% annual onshore wind growth</li>
                <li>70% renewable share by 2050</li>
                <li>Limited policy changes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="scenario-card" style="border-left: 5px solid {scenario_colors.get('Business as Usual', '#4ECDC4')};">
            <h3>⚖️ Business as Usual</h3>
            <p><strong>Current policy trajectory</strong></p>
            <ul>
                <li>7.5% annual solar growth</li>
                <li>4% annual onshore wind growth</li>
                <li>85% renewable share by 2050</li>
                <li>Moderate electrification</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="scenario-card" style="border-left: 5px solid {scenario_colors.get('Ambitious', '#1DD1A1')};">
            <h3>🚀 Ambitious</h3>
            <p><strong>Accelerated transition</strong></p>
            <ul>
                <li>12% annual solar growth</li>
                <li>7% annual onshore wind growth</li>
                <li>95% renewable share by 2050</li>
                <li>Strong policy support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Display metrics for selected scenario and year
    st.subheader(f"Scenario Metrics: {scenario_type}")
    
    if not scenario_data.empty:
        # Filter for selected year
        year_data = scenario_data[scenario_data['Year'] == selected_year]
        
        if not year_data.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                solar_val = year_data['Photovoltaics [MWh]'].values[0]
                st.metric("Solar Generation", f"{solar_val:,.0f} MWh")
            
            with col2:
                wind_onshore_val = year_data['Wind Onshore [MWh]'].values[0]
                st.metric("Wind Onshore", f"{wind_onshore_val:,.0f} MWh")
            
            with col3:
                wind_offshore_val = year_data['Wind Offshore [MWh]'].values[0]
                st.metric("Wind Offshore", f"{wind_offshore_val:,.0f} MWh")
            
            with col4:
                renewable_share = year_data['Renewable Share [%]'].values[0]
                st.metric("Renewable Share", f"{renewable_share:.1f}%")
    
    # Scenario visualizations
    st.subheader("Scenario Visualizations")
    
    tab_scenario1, tab_scenario2, tab_scenario3, tab_scenario4 = st.tabs([
        "Generation Projections", 
        "Renewable Share Development",
        "Method Comparison",
        "Scenario Comparison"
    ])
    
    with tab_scenario1:
        # Generation projections
        fig_gen = go.Figure()
        
        fig_gen.add_trace(go.Scatter(
            name='Solar',
            x=scenario_data['Year'],
            y=scenario_data['Photovoltaics [MWh]'],
            mode='lines',
            line=dict(color='#FFD700', width=3),
            fill='tozeroy',
            fillcolor='rgba(255, 215, 0, 0.1)'
        ))
        
        fig_gen.add_trace(go.Scatter(
            name='Wind Onshore',
            x=scenario_data['Year'],
            y=scenario_data['Wind Onshore [MWh]'],
            mode='lines',
            line=dict(color='#1E90FF', width=3),
            fill='tonexty',
            fillcolor='rgba(30, 144, 255, 0.1)'
        ))
        
        fig_gen.add_trace(go.Scatter(
            name='Wind Offshore',
            x=scenario_data['Year'],
            y=scenario_data['Wind Offshore [MWh]'],
            mode='lines',
            line=dict(color='#00008B', width=3),
            fill='tonexty',
            fillcolor='rgba(0, 0, 139, 0.1)'
        ))
        
        fig_gen.update_layout(
            title=f'{scenario_type} Scenario: Generation Projections ({projection_method})',
            xaxis_title='Year',
            yaxis_title='Generation (MWh)',
            height=500,
            hovermode='x unified',
            showlegend=True
        )
        
        st.plotly_chart(fig_gen, use_container_width=True)
        
        # Add historical data for context
        if not generation_df.empty:
            # Combine historical and projected data
            historical_for_plot = generation_df[['Year', 'Photovoltaics [MWh]', 'Wind Onshore [MWh]', 'Wind Offshore [MWh]']].copy()
            historical_for_plot['Type'] = 'Historical'
            
            projected_for_plot = scenario_data[['Year', 'Photovoltaics [MWh]', 'Wind Onshore [MWh]', 'Wind Offshore [MWh]']].copy()
            projected_for_plot['Type'] = 'Projected'
            
            combined_df = pd.concat([historical_for_plot, projected_for_plot])
            
            # Create combined chart
            fig_combined = go.Figure()
            
            for tech, color, name in [('Photovoltaics [MWh]', '#FFD700', 'Solar'),
                                     ('Wind Onshore [MWh]', '#1E90FF', 'Wind Onshore'),
                                     ('Wind Offshore [MWh]', '#00008B', 'Wind Offshore')]:
                
                # Historical
                hist_data = historical_for_plot[['Year', tech]].dropna()
                fig_combined.add_trace(go.Scatter(
                    name=f'{name} (Historical)',
                    x=hist_data['Year'],
                    y=hist_data[tech],
                    mode='lines+markers',
                    line=dict(color=color, width=2),
                    marker=dict(size=6)
                ))
                
                # Projected
                proj_data = projected_for_plot[['Year', tech]].dropna()
                fig_combined.add_trace(go.Scatter(
                    name=f'{name} (Projected)',
                    x=proj_data['Year'],
                    y=proj_data[tech],
                    mode='lines',
                    line=dict(color=color, width=2, dash='dash')
                ))
            
            fig_combined.update_layout(
                title='Historical vs Projected Generation',
                xaxis_title='Year',
                yaxis_title='Generation (MWh)',
                height=500,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_combined, use_container_width=True)
    
    with tab_scenario2:
        # Renewable share development
        fig_share = px.line(scenario_data, x='Year', y='Renewable Share [%]',
                           title=f'{scenario_type} Scenario: Renewable Share Development',
                           labels={'Renewable Share [%]': 'Renewable Share (%)', 'Year': 'Year'})
        
        fig_share.update_layout(
            height=500,
            yaxis_range=[0, 100],
            shapes=[
                # Add target lines
                dict(type="line", x0=2026, x1=2050, y0=80, y1=80,
                     line=dict(color="green", width=2, dash="dot")),
                dict(type="line", x0=2026, x1=2050, y0=95, y1=95,
                     line=dict(color="red", width=2, dash="dot"))
            ],
            annotations=[
                dict(x=2050, y=80, xref="x", yref="y",
                     text="EU 2040 Target", showarrow=True, arrowhead=1, ax=-50, ay=0),
                dict(x=2050, y=95, xref="x", yref="y",
                     text="Climate Neutrality", showarrow=True, arrowhead=1, ax=50, ay=0)
            ]
        )
        
        st.plotly_chart(fig_share, use_container_width=True)
        
        # Key milestones
        st.subheader("Key Milestones")
        
        milestones = []
        for threshold in [50, 65, 80, 90, 95]:
            year_reached = scenario_data[scenario_data['Renewable Share [%]'] >= threshold]['Year'].min()
            if not pd.isna(year_reached):
                milestones.append(f"**{threshold}% renewable share:** {int(year_reached)}")
        
        if milestones:
            st.markdown("\n".join(milestones))
    
    with tab_scenario3:
        st.subheader("Projection Method Comparison")
        
        # Generate scenarios with all methods
        methods = ["Last Year Available (2025)", "3-Year Average (2023-2025)", 
                  "5-Year Trend (2021-2025)", "Full Historical Trend (2015-2025)"]
        
        method_comparison = []
        for method in methods:
            method_data, _, _ = generate_future_scenarios_enhanced(
                generation_df, scenario_type, method, custom_params
            )
            method_comparison.append(method_data)
        
        comparison_methods_df = pd.concat(method_comparison, ignore_index=True)
        
        # Compare renewable shares by method
        fig_methods = px.line(comparison_methods_df, x='Year', y='Renewable Share [%]', 
                             color='Projection_Method',
                             title='Impact of Projection Method on Renewable Share',
                             labels={'Renewable Share [%]': 'Renewable Share (%)', 
                                    'Projection_Method': 'Projection Method'})
        
        fig_methods.update_layout(height=500, hovermode='x unified')
        st.plotly_chart(fig_methods, use_container_width=True)
        
        # Show 2050 values by method
        st.subheader("2050 Projections by Method")
        
        year_2050_methods = comparison_methods_df[comparison_methods_df['Year'] == 2050]
        
        if not year_2050_methods.empty:
            cols = st.columns(len(year_2050_methods))
            for idx, (_, row) in enumerate(year_2050_methods.iterrows()):
                with cols[idx]:
                    st.metric(
                        row['Projection_Method'].split('(')[0].strip(),
                        f"{row['Renewable Share [%]']:.1f}%",
                        delta=f"{(row['Renewable Share [%]'] - 85):+.1f}%" if idx > 0 else None
                    )
    
    with tab_scenario4:
        # Generate all scenarios for comparison
        all_scenarios = []
        
        for sc_type in ["Conservative", "Business as Usual", "Ambitious"]:
            sc_data, _, _ = generate_future_scenarios_enhanced(generation_df, sc_type, projection_method)
            sc_data['Scenario'] = sc_type
            all_scenarios.append(sc_data)
        
        if scenario_type == "Custom":
            custom_sc_data, _, _ = generate_future_scenarios_enhanced(generation_df, "Custom", projection_method, custom_params)
            custom_sc_data['Scenario'] = "Custom"
            all_scenarios.append(custom_sc_data)
        
        comparison_df = pd.concat(all_scenarios, ignore_index=True)
        
        # Compare renewable shares
        fig_comparison = px.line(comparison_df, x='Year', y='Renewable Share [%]', color='Scenario',
                                title='Scenario Comparison: Renewable Share Development',
                                labels={'Renewable Share [%]': 'Renewable Share (%)', 'Year': 'Year'},
                                color_discrete_map=scenario_colors)
        
        fig_comparison.update_layout(
            height=500,
            yaxis_range=[0, 100],
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # 2050 comparison
        year_2050_data = comparison_df[comparison_df['Year'] == 2050]
        
        if not year_2050_data.empty:
            st.subheader("2050 Scenario Comparison")
            
            fig_2050 = px.bar(year_2050_data, x='Scenario', y='Renewable Share [%]',
                             color='Scenario',
                             title='2050 Renewable Share by Scenario',
                             labels={'Renewable Share [%]': 'Renewable Share (%)'},
                             color_discrete_map=scenario_colors)
            
            fig_2050.update_layout(height=400)
            st.plotly_chart(fig_2050, use_container_width=True)
            
            # Display 2050 metrics
            cols = st.columns(len(year_2050_data))
            for idx, (_, row) in enumerate(year_2050_data.iterrows()):
                with cols[idx]:
                    st.metric(
                        row['Scenario'],
                        f"{row['Renewable Share [%]']:.1f}%",
                        delta=f"{(row['Renewable Share [%]'] - 85):+.1f}%" if row['Scenario'] != 'Business as Usual' else None
                    )
    
    # Policy targets context
    st.markdown("---")
    st.subheader("🇪🇺 Policy Context & Targets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### German National Targets:
        - **2030:** 80% renewable electricity
        - **2035:** Near 100% renewable electricity
        - **2045:** Climate neutrality
        
        ### EU Fit for 55 Package:
        - 55% GHG reduction by 2030 (vs 1990)
        - Increased renewable energy targets
        - Carbon border adjustment mechanism
        """)
    
    with col2:
        st.markdown("""
        ### 50HZ Specific Goals:
        - Grid expansion for renewable integration
        - Baltic Sea offshore wind development
        - Hydrogen-ready infrastructure
        - Digital grid management
        
        ### Regional Considerations:
        - High offshore wind potential
        - Industrial load centers
        - Cross-border interconnections
        """)
    
    # Download scenario data
    st.markdown("---")
    st.subheader("📥 Download Scenario Data")
    
    if not scenario_data.empty:
        csv = scenario_data.to_csv(index=False)
        st.download_button(
            label=f"Download {scenario_type} Scenario Data (CSV)",
            data=csv,
            file_name=f"50hz_{scenario_type.lower().replace(' ', '_')}_scenario_2026_2050.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p><strong>Dashboard Version:</strong> 3.0 | <strong>Data Sources:</strong> SMARD, ENTSO-E, 50HZ | 
    <strong>Scenario Methodology:</strong> Multiple statistical projection methods</p>
    <p><strong>Disclaimer:</strong> Scenario projections are illustrative and based on simplified assumptions. 
    Actual outcomes may vary based on policy decisions, technological developments, and market conditions.</p>
</div>
""", unsafe_allow_html=True)

# Add refresh button
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh All Data"):
    st.cache_data.clear()
    st.rerun()