# BiFlowLISA-Depopultaion-Study

**Measuring Spatial Associations of Intercity Flows between Depopulation Regions Considering Nearest Neighborhoods** 
> *Published in the Journal of the Korean Geographical Society (2023), Vol. 58, No. 6, pp. 644–656.*

This repository contains the Python implementation and analysis notebooks for exploring spatial associations of intercity flows (population movement, credit card consumption) within depopulation-hit regions in South Korea.

---

## 📌 Project Overview
As regional depopulation accelerates, understanding the functional connectivity between regions becomes crucial. This research identifies spatial cluster patterns of flows by applying **BiFlow-LISA** (Local Indicators of Spatial Association for Bivariate Flows) and incorporating **Nearest Neighborhood** concepts to define spatial weights.

### Key Features
- **Data Integration:** Combines mobile-based floating population and credit card transaction data.
- **Spatial Weighting:** Implements KNN-based spatial weight matrices for flow data.
- **Flow-LISA:** Detects Hot-spots (HH) and Cold-spots (LL) of inter-regional interactions.
- **Dynamic Visualization:** Visualizes complex flow patterns using Alluvial plots and LISA cluster maps.

---

## 📂 Repository Structure

```text
├── data/                 # Raw/Processed data descriptions (Data not uploaded for security)
├── notebooks/            # Step-by-step analysis workflows
│   ├── 01_Data_Preprocessing.ipynb    # Data cleaning, monthly aggregation, and merging
│   ├── 02_Spatial_Weighting.ipynb     # KNN/Distance-band weight matrix construction
│   ├── 03_Flow_LISA_Analysis.ipynb    # Computation of Flow-LISA indices
│   └── 04_Visualization.ipynb         # Generation of LISA maps and Alluvial plots
├── .gitignore            # Rules to exclude large data files and checkpoints
└── requirements.txt      # List of required Python libraries
