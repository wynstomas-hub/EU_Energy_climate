# EU Energy & Climate Policy Data Tools

> **Open-source data analysis tools for European energy and climate policy research**

This repository contains Python programs, Streamlit dashboards, and data analysis scripts for examining EU energy markets, industrial policy, carbon pricing, and climate legislation.

---

## 📊 Repository Structure

```
EU_Energy_climate/
├── README.md                 # This file
├── electrification/          # Industrial electrification tools
│   └── elecspark.py         # Interactive electrification economics dashboard
├── chemicals/                # Chemical industry analysis
├── cbam/                     # Carbon Border Adjustment Mechanism tools
└── utils/                    # Shared utilities
```

---

## 🚀 Tools & Applications

### 1. Electrification Economics Dashboard (`elecspark.py`)

**What it does:**
Interactive Streamlit application that calculates the economic threshold where industrial electrification (heat pumps, electric boilers) becomes cheaper than natural gas, considering:
- Live Eurostat industrial energy prices (ex-VAT)
- EU ETS carbon price scenarios (€0-250/tCO₂)
- Country-specific grid emission factors
- Sector-specific thermodynamic constraints (COP)

**Key Features:**
- 📈 **Live Eurostat Integration**: Fetches trailing 12-month average industrial tariffs
- 🎚️ **Carbon Price Simulator**: Adjust EU ETS price and see real-time impact on competitiveness
- 🌡️ **Sector Profiles**: Pre-configured for Food & Beverage, Paper & Pulp, Chemicals (low/medium/high temp), Basic Metals, Non-Metallic Minerals
- 📊 **Interactive Phase Diagram**: Visual "viability map" showing which countries/regions can profitably electrify
- 🔬 **Thermodynamic Reality**: COP (Coefficient of Performance) locked to realistic engineering limits per sector

**Usage:**
```bash
pip install streamlit pandas plotly eurostat
streamlit run electrification/elecspark.py
```

**Methodology:**
The tool calculates the "electrification delta" — the cost difference between generating industrial heat via:
- **Gas pathway**: `(Gas Price + Carbon Cost) / Boiler Efficiency`
- **Electric pathway**: `(Electricity Price + Grid Carbon Cost) / COP`

When delta ≤ 0, electrification is economically viable.

---

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- pip or conda

### Dependencies
```bash
pip install streamlit pandas plotly eurostat numpy
```

### Clone Repository
```bash
git clone https://github.com/wynstomas-hub/EU_Energy_climate.git
cd EU_Energy_climate
```

---

## 📚 Data Sources

| Source | Datasets Used |
|--------|---------------|
| **Eurostat** | `nrg_pc_205` (industrial electricity), `nrg_pc_203` (industrial gas) |
| **EEA** | Grid emission factors by country |
| **EU ETS** | Carbon price scenarios (user-adjustable) |

---

## 🎯 Research Focus Areas

This repository supports analysis of:

1. **Industrial Decarbonisation Pathways**
   - Electrification economics
   - Hydrogen cost competitiveness
   - CCUS viability thresholds

2. **EU Carbon Border Adjustment (CBAM)**
   - Trade flow analysis
   - Embodied carbon calculations
   - Competitiveness impacts

3. **Chemical Industry Intelligence**
   - Production indices
   - Import/export competitiveness
   - Energy cost benchmarking

4. **Energy Market Dynamics**
   - Industrial energy prices across EU27
   - Grid emission factor variations
   - Carbon price pass-through effects

---

## 🤝 Contributing

This is a personal research repository, but suggestions and improvements are welcome. Tools here are used for:
- VUB research on EU industrial policy
- Consulting on chemical industry decarbonisation
- Policy briefings on CBAM and trade competitiveness

---

## 📧 Contact

**Tomas Wyns**
- Researcher, VUB (Vrije Universiteit Brussel)
- Focus: EU industrial policy, carbon pricing, chemical industry
- Location: Dilbeek, Belgium

---

## 📜 License

MIT License — feel free to use, modify, and distribute with attribution.

---

*Last updated: March 2025*