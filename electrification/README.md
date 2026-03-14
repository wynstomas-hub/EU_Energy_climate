# Electrification Economics Tools

## elecspark.py — Industrial Electrification Monitor

### Overview

`elecspark.py` is an interactive Streamlit dashboard that answers a critical question for EU industry:

> **"At what carbon price does electrification become cheaper than gas?"**

The tool calculates real-time economic viability of industrial heat pumps and electric boilers versus natural gas, using live Eurostat data and accounting for:
- Country-specific energy prices (industrial scale, ex-VAT)
- Grid emission factors (Sweden 0.01 → Poland 0.65 tCO₂/MWh)
- Thermodynamic constraints (COP 3.5 for low temp → 1.0 for high temp)
- EU ETS carbon price scenarios

### How It Works

#### 1. Price Architecture

The tool pulls the **two most recent semesters** from Eurostat to create a trailing 12-month average, eliminating seasonal volatility:

| Component | Data Source | Filter |
|-----------|-------------|--------|
| Electricity | `nrg_pc_205` | Industrial bands (ID/IE/IF), Ex-VAT |
| Natural Gas | `nrg_pc_203` | Industrial bands (I3-I5), Ex-VAT |

#### 2. Carbon Cost Integration

```
Gas Heat Cost = (Gas_Price + (Carbon_Price × 0.202)) / η_boiler
Electric Heat Cost = (Elec_Price + (ΔCarbon × Grid_EF)) / COP
```

Where:
- `0.202` = Natural gas emission factor (tCO₂/MWh)
- `η_boiler` = Gas boiler efficiency (default 85%)
- `COP` = Coefficient of Performance (sector-dependent)
- `ΔCarbon` = Simulated price - baseline (€75)

#### 3. Sector-Specific Thermodynamics

| Sector | Temperature | COP | Technology |
|--------|-------------|-----|------------|
| Food & Beverage | <150°C | 3.5 | Industrial heat pumps |
| Paper & Pulp | <150°C | 3.5 | Industrial heat pumps |
| Chemicals (Low) | <150°C | 3.0 | Industrial heat pumps |
| Chemicals (Medium) | 150-500°C | 2.0 | High-temp heat pumps |
| Chemicals (High) | >500°C | 1.0 | Electric boilers |
| Basic Metals | >1000°C | 1.0 | Arc furnaces |
| Non-Metallic Minerals | >1000°C | 1.0 | Electric kilns |

### The Phase Diagram

The central visualization is an economic "phase diagram" showing:

- **Red dashed line**: Parity threshold (where elec cost = gas cost)
- **Green dots**: Countries where electrification is already viable
- **Red dots**: Countries where gas remains cheaper
- **Green shaded zone**: Viable electrification region

Countries position based on their actual Eurostat energy prices.

### Key Insights

**High COP sectors** (Food, Paper): Viability strongly favors electrification in countries with:
- Low electricity prices (Nordics: €30-50/MWh)
- Clean grids (Sweden, France, Norway)

**Low COP sectors** (Metals, Minerals): Viability requires:
- Very high carbon prices (>€150/t)
- AND/OR low electricity/high gas price spreads

**Grid factor matters**: Poland (EF=0.65) sees electricity costs rise €65/MWh per €100 carbon price. Sweden (EF=0.01) sees only €1/MWh increase.

### Usage Examples

**Scenario 1: Current EU ETS (€75/t)**
- Most Nordic countries: Heat pumps viable for low-temp processes
- Poland, Czechia: Gas still wins even for low-temp

**Scenario 2: High Carbon (€150/t)**
- France, Sweden: Competitive even for medium-temp chemicals
- Germany: Low-temp viable, medium-temp marginal

**Scenario 3: Extreme Carbon (€250/t)**
- Most EU27: Low and medium temp competitive
- High-temp still challenging without cheap power

### Running the Tool

```bash
cd EU_Energy_climate
cd electrification
pip install -r ../requirements.txt
streamlit run elecspark.py
```

### Data Refresh

Eurostat updates industrial energy prices twice yearly. The tool automatically:
1. Detects latest available semesters
2. Calculates trailing 12-month averages
3. Updates all calculations in real-time

### Future Enhancements

- [ ] Add hydrogen cost comparison pathway
- [ ] Include biomass/biogas alternatives
- [ ] Time-series view of electrification viability trends
- [ ] Regional disaggregation (e.g., German Länder)

---

*Part of the EU Energy & Climate Policy Research Toolkit*