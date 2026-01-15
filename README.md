# Measuring Spatial Associations of Intercity Flows between Depopulation Regions Considering Nearest Neighborhoods 
> *Published in the Journal of the Korean Geographical Society (2023), Vol. 58, No. 6, pp. 644–656.*

This repository contains the Python implementation and analysis notebooks for exploring spatial associations of intercity flows (population movement, credit card consumption) within depopulation-hit regions in South Korea.

---

## 📌 Project Overview
As regional depopulation accelerates, understanding the functional connectivity between regions becomes crucial. This research identifies spatial cluster patterns of flows by applying **BiFlow-LISA** (Local Indicators of Spatial Association for Bivariate Flows) and incorporating **Nearest Neighborhood** concepts to define spatial weights.

### Key Features
- **Data Integration:** Combines mobile-based floating population and credit card transaction data.
- **Spatial Weighting:** Implements KNN-based spatial weight matrices for flow data.
- **BiFlowLISA:** Detects Hot-spots (HH) and Cold-spots (LL) of inter-regional bivariate interactions.

---

## 📂 Repository Structure

```text
├── data/                 # Sampled data (Raw data not uploaded for security)
└── codes/                # Step-by-step analysis workflows
    ├── 01_pop_preprocessing.py
    ├── 02_card_preprocessing.py    
    ├── 03_filtering-depopulated-areas.py
    └── 04_knn_sensitivity_test.py
