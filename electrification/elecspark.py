import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import eurostat

# --- 1. UI Configuration & Dynamic Setup ---
st.set_page_config(page_title="Industrial Electrification Monitor", layout="wide")

# --- 2. Country & Grid Emission Factor Dictionaries ---
eu_country_map = {
    'AT': 'Austria', 'BE': 'Belgium', 'BG': 'Bulgaria', 'CY': 'Cyprus', 
    'CZ': 'Czechia', 'DE': 'Germany', 'DK': 'Denmark', 'EE': 'Estonia', 
    'EL': 'Greece', 'ES': 'Spain', 'FI': 'Finland', 'FR': 'France', 
    'HR': 'Croatia', 'HU': 'Hungary', 'IE': 'Ireland', 'IT': 'Italy', 
    'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia', 'MT': 'Malta', 
    'NL': 'Netherlands', 'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania', 
    'SE': 'Sweden', 'SI': 'Slovenia', 'SK': 'Slovakia', 'NO': 'Norway'
}

grid_emission_factors = {
    'Sweden': 0.01, 'France': 0.05, 'Norway': 0.01, 'Austria': 0.08,
    'Belgium': 0.15, 'Finland': 0.05, 'Spain': 0.12, 'Portugal': 0.13,
    'Denmark': 0.12, 'Italy': 0.25, 'Netherlands': 0.22, 'Germany': 0.35,
    'Poland': 0.65, 'Czechia': 0.45, 'Greece': 0.35, 'Romania': 0.25,
    'Bulgaria': 0.40, 'Hungary': 0.25, 'Slovakia': 0.15, 'Slovenia': 0.22,
    'Ireland': 0.30, 'Latvia': 0.10, 'Lithuania': 0.15, 'Estonia': 0.50,
    'Croatia': 0.18, 'Cyprus': 0.60, 'Malta': 0.40
}

# --- 3. Sidebar Parameters (Thermodynamic & Economic Variables) ---
st.sidebar.header("Economic Parameters")

BASELINE_CARBON_PRICE = 75.0 
simulated_carbon_price = st.sidebar.slider(
    "Simulated EU ETS Carbon Price (€/tCO2)", 
    min_value=0.0, max_value=250.0, value=BASELINE_CARBON_PRICE, step=5.0
)
delta_carbon_price = simulated_carbon_price - BASELINE_CARBON_PRICE

st.sidebar.markdown("---")
st.sidebar.header("Thermodynamic Parameters")

eta_gas = st.sidebar.slider("Gas Boiler Efficiency (η)", min_value=0.70, max_value=1.00, value=0.85, step=0.01)
ef_gas = 0.202 # tCO2 per MWh of natural gas

sector_profiles = {
    "Food & Beverage (Low Temp: <150°C)": {"cop": 3.5, "scale": "Medium"},
    "Paper & Pulp (Low Temp: <150°C)": {"cop": 3.5, "scale": "Large"},
    "Chemicals (Low Temp: <150°C)": {"cop": 3.5, "scale": "Large"},
    "Chemicals (Medium Temp: 150-500°C)": {"cop": 2.0, "scale": "Large"},
    "Chemicals (High Temp: >500°C)": {"cop": 1.0, "scale": "Large"},
    "Basic Metals (High Temp: >1000°C)": {"cop": 1.0, "scale": "Large"},
    "Non-Metallic Minerals (Extreme Temp: >1000°C)": {"cop": 1.0, "scale": "Large"}
}

selected_sector = st.sidebar.selectbox("Select Industrial Sector", list(sector_profiles.keys()))
current_cop = sector_profiles[selected_sector]["cop"]
current_scale = sector_profiles[selected_sector]["scale"]

st.sidebar.info(f"Assigned Thermodynamic COP: **{current_cop}**\n\nAssigned Consumer Scale: **{current_scale}**")

tech_name = "industrial heat pumps" if current_cop > 1.0 else "direct electrification (e.g., arc furnaces or electric boilers)"

# --- 4. Main UI Header & Explanatory Text ---
st.title(f"Electrification Threshold Monitor: {selected_sector}")
st.markdown(f"Evaluate the exact economic threshold where **{tech_name}** outcompete natural gas boilers.")

# Create a dedicated pop-up modal function for the methodology
@st.dialog("📚 Methodology & Price Architecture")
def show_methodology():
    st.markdown(f"""
    **1. Energy Prices & Timeframe (Trailing 12-Month Average)**
    To eliminate seasonal volatility (e.g., winter gas spikes or summer solar gluts) and provide a robust OPEX/CAPEX baseline, this tool pulls the **two most recent reporting semesters** from Eurostat and calculates a trailing 12-month mathematical average. 
    * **Taxes:** Prices reflect actual corporate expenditure by **excluding recoverable VAT** (`X_VAT` flag in Eurostat).
    * **Scale Filtering:** Energy costs scale with volume. Because you selected a **{current_scale}** consumer, the API dynamically targets the exact purchasing bands reflecting this industry size.
    
    **2. The Carbon Price Coupling Mechanism**
    * **Natural Gas:** Direct fossil fuel consumption is fully penalised by the simulated EU ETS carbon price via an emission factor of 0.202 tCO₂/MWh. 
    * **Electricity:** The Eurostat electricity price already embeds today's baseline carbon price (~€75/t). Therefore, when you adjust the carbon slider, the model calculates the *delta* and multiplies it by each country's specific **Grid Emission Factor**. Dirty grids (e.g., Poland) will see power prices spike, while clean grids remain insulated.
    
    **3. Thermodynamic Reality (COP)**
    Heat pumps upgrade waste heat, allowing them to break the 1:1 efficiency limit. However, as industrial temperature requirements increase, this thermodynamic advantage degrades. This model locks the COP to realistic engineering limits based on your selected sector.
    """)

# Create a highly visible button to trigger the pop-up
if st.button("ℹ️ Click here to read the Methodology & Price Architecture"):
    show_methodology()

# --- 5. Dynamic Live Data Fetching via Eurostat API ---
@st.cache_data
def fetch_energy_prices(consumer_scale):
    df_elec_raw = eurostat.get_data_df('nrg_pc_205')
    df_gas_raw = eurostat.get_data_df('nrg_pc_203')
    
    for df in [df_elec_raw, df_gas_raw]:
        if 'geo\\TIME_PERIOD' in df.columns:
            df.rename(columns={'geo\\TIME_PERIOD': 'geo'}, inplace=True)
        elif 'geo\\time' in df.columns:
            df.rename(columns={'geo\\time': 'geo'}, inplace=True)
            
    if consumer_scale == "Medium":
        valid_elec_bands = ['ID', 'MWH2000-19999']
        valid_gas_bands = ['I3', 'GJ10000-99999']
    else: 
        valid_elec_bands = ['IE', 'IF', 'MWH20000-69999', 'MWH70000-149999']
        valid_gas_bands = ['I4', 'I5', 'GJ100000-999999', 'GJ1000000-3999999']
        
    df_elec = df_elec_raw[
        df_elec_raw['nrg_cons'].isin(valid_elec_bands) & 
        (df_elec_raw['tax'] == 'X_VAT') & 
        (df_elec_raw['currency'] == 'EUR')
    ].copy()
    
    df_gas = df_gas_raw[
        df_gas_raw['nrg_cons'].isin(valid_gas_bands) & 
        (df_gas_raw['tax'] == 'X_VAT') & 
        (df_gas_raw['currency'] == 'EUR')
    ].copy()
    
    time_cols_elec = [str(col) for col in df_elec.columns if str(col).startswith('20')]
    time_cols_gas = [str(col) for col in df_gas.columns if str(col).startswith('20')]
    
    common_periods = sorted(list(set(time_cols_elec) & set(time_cols_gas)))
    last_two_periods = common_periods[-2:]
    data_timeframe = " and ".join(last_two_periods)
    
    df_elec = df_elec[['geo'] + last_two_periods].copy()
    df_gas = df_gas[['geo'] + last_two_periods].copy()
    
    for col in last_two_periods:
        df_elec[col] = pd.to_numeric(df_elec[col], errors='coerce')
        df_gas[col] = pd.to_numeric(df_gas[col], errors='coerce')
    
    df_elec = df_elec.groupby('geo', as_index=False).mean()
    df_gas = df_gas.groupby('geo', as_index=False).mean()
    
    df_elec['Elec_Price_EUR_kWh'] = df_elec[last_two_periods].mean(axis=1)
    df_gas['Gas_Price_EUR_GJ'] = df_gas[last_two_periods].mean(axis=1)
    
    df_elec = df_elec.dropna(subset=['Elec_Price_EUR_kWh'])
    df_gas = df_gas.dropna(subset=['Gas_Price_EUR_GJ'])
    
    df_merged = pd.merge(df_elec[['geo', 'Elec_Price_EUR_kWh']], df_gas[['geo', 'Gas_Price_EUR_GJ']], on='geo', how='inner')
    df_merged = df_merged[df_merged['geo'].apply(lambda x: len(str(x)) == 2)]
    
    df_merged['Code'] = df_merged['geo']
    df_merged['Elec_Price_EUR_MWh'] = df_merged['Elec_Price_EUR_kWh'] * 1000
    df_merged['Gas_Price_EUR_MWh'] = df_merged['Gas_Price_EUR_GJ'] * 3.6
    
    df_merged['Country'] = df_merged['geo'].map(eu_country_map)
    df_merged = df_merged.dropna(subset=['Country'])
    
    return df_merged[['Code', 'Country', 'Elec_Price_EUR_MWh', 'Gas_Price_EUR_MWh']], data_timeframe

with st.spinner(f"Fetching live {current_scale.lower()} industrial tariffs from Eurostat..."):
    df_prices, data_timeframe = fetch_energy_prices(current_scale)

if df_prices.empty:
    st.error("Eurostat did not return valid data.")
    st.stop()

st.info(f"📊 **Data Source:** Eurostat Trailing 12-Month Average (**{data_timeframe}**) | **Scale:** {current_scale} Consumer | **Tax:** Excl. VAT")

# --- 6. The Scientific Calculation (Grid & Carbon Coupling) ---
df_prices['Grid_EF'] = df_prices['Country'].map(grid_emission_factors).fillna(0.25)
df_prices['Adjusted_Elec_Price'] = df_prices['Elec_Price_EUR_MWh'] + (delta_carbon_price * df_prices['Grid_EF'])
df_prices['Adjusted_Elec_Price'] = df_prices['Adjusted_Elec_Price'].clip(lower=0)

df_prices['Gas_Heat_Cost'] = (df_prices['Gas_Price_EUR_MWh'] + (simulated_carbon_price * ef_gas)) / eta_gas
df_prices['HP_Heat_Cost'] = df_prices['Adjusted_Elec_Price'] / current_cop

df_prices['Electrification_Delta'] = df_prices['HP_Heat_Cost'] - df_prices['Gas_Heat_Cost']
df_prices['Electrification_Viable'] = df_prices['Electrification_Delta'] <= 0

# --- 7. The Dynamic Phase Diagram ---
max_gas_price = int(df_prices['Gas_Price_EUR_MWh'].max()) + 30
gas_price_range = pd.Series(range(10, max_gas_price))

parity_elec_prices = current_cop * ((gas_price_range + (simulated_carbon_price * ef_gas)) / eta_gas)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=gas_price_range, 
    y=parity_elec_prices, 
    mode='lines', 
    name=f'Parity Threshold (COP={current_cop})',
    line=dict(color='red', width=2, dash='dash')
))

fig.add_trace(go.Scatter(
    x=df_prices['Gas_Price_EUR_MWh'],
    y=df_prices['Adjusted_Elec_Price'],
    mode='markers+text',
    name='European Nations',
    text=df_prices['Code'], 
    textposition="top center",
    hovertext=df_prices['Country'], 
    marker=dict(
        size=12,
        color=df_prices['Electrification_Viable'].map({True: '#00cc96', False: '#EF553B'}),
        line=dict(width=1, color='DarkSlateGrey')
    )
))

fig.update_layout(
    title=f"Economic Phase Diagram: {selected_sector}",
    xaxis_title=f"Price for Industry ({current_scale}): Natural Gas (€/MWh) [Excl. VAT]",
    yaxis_title=f"Price for Industry ({current_scale}): Electricity (€/MWh) [Carbon Adjusted, Excl. VAT]",
    plot_bgcolor='rgba(240,240,240,0.8)',
    showlegend=True,
    height=600
)

fig.add_trace(go.Scatter(
    x=list(gas_price_range) + [max_gas_price, max_gas_price, 10],
    y=list(parity_elec_prices) + [0, 0, 0],
    fill='toself',
    fillcolor='rgba(0, 204, 150, 0.1)',
    line=dict(color='rgba(255,255,255,0)'),
    name='Viable Electrification Zone',
    hoverinfo='skip'
))

st.plotly_chart(fig, use_container_width=True)

# --- 8. Data Table Output ---
st.markdown(f"### Country-by-Country Analysis Matrix ({current_scale} Consumers)")
st.dataframe(
    df_prices[['Code', 'Country', 'Gas_Price_EUR_MWh', 'Elec_Price_EUR_MWh', 'Adjusted_Elec_Price', 'Gas_Heat_Cost', 'HP_Heat_Cost', 'Electrification_Delta', 'Electrification_Viable']]
    .sort_values(by='Electrification_Delta')
    .style.format({
        'Gas_Price_EUR_MWh': '€{:.2f}', 
        'Elec_Price_EUR_MWh': '€{:.2f}', 
        'Adjusted_Elec_Price': '€{:.2f}',
        'Gas_Heat_Cost': '€{:.2f}', 
        'HP_Heat_Cost': '€{:.2f}',
        'Electrification_Delta': '€{:.2f}'
    })
)