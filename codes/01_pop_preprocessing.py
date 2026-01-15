import pandas as pd
import numpy as np
from tqdm.auto import tqdm
import warnings

# Ignore warnings for cleaner output
warnings.filterwarnings(action='ignore')

# 1. Generate a list of year-month strings (YYYYMM) from 2018 to 2022
ym = []
month = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
for i in range(2018, 2023):
    for j in month:
        ym.append(str(i) + j)

# 2. Process population flow data for each year-month
ps_list = []
for y in tqdm(ym):
    print(f'Processing data for: {y}')
    
    # Load administrative code mapping and raw population flow data
    code = pd.read_csv('./CODE_2023.01.01.csv', encoding='cp949')
    pop = pd.read_csv('./성연령최종파일_' + y + '.csv', sep='|', encoding='utf-8').loc[:, ['home_GU_CODE', 'dst_HCODE', 'POP']]

    # Preprocess administrative codes (converting to 5-digit standard)
    code['CODE_AD_2'] = (code['CODE_AD'] / 100000).astype(int)
    df_code = code[['CODE', 'CODE_AD_2']]

    # Extract 5-digit destination code from 'dst_HCODE'
    a = pop['dst_HCODE'].astype(str).tolist()
    dst_code = [c[:5] for c in a]
    pop['D'] = dst_code
    pop['D'] = pop['D'].astype(int)
    
    # Rename and correct specific origin code (e.g., handling administrative changes)
    pop = pop.rename(columns={'home_GU_CODE': 'O'})
    pop['O'] = pop['O'].replace(28170, 28177)

    # Merge population data with administrative codes for both Origin (O) and Destination (D)
    df_code1 = pd.merge(pop, df_code, left_on='O', right_on='CODE_AD_2', how='left')
    df_code2 = pd.merge(df_code1, df_code, left_on='D', right_on='CODE_AD_2', how='left')

    # Create a unique Origin-Destination (OD) pair key by concatenating codes
    df_pop = df_code2[['CODE_x', 'CODE_y', 'POP']]
    df_pop['CODE'] = df_pop['CODE_x'].astype(str) + df_pop['CODE_y'].astype(str)
    df_pop = df_pop[['CODE', 'POP']]

    # Aggregate population by OD pair
    pop_sum = df_pop.groupby('CODE')['POP'].sum()
    ps = pd.DataFrame()
    ps['CODE'] = pop_sum.index.tolist()
    ps['POP_' + y] = pop_sum.tolist()

    ps_list.append(ps)

# 3. Final data integration: Merge monthly results into a single master OD matrix
# Load master OD coordinate/number file
od_xy = pd.read_csv('./od_xy_num_0716.csv', encoding='cp949')

df_pop_sum = od_xy        
for i in tqdm(range(len(ps_list))):
    od_xy['CODE'] = od_xy['CODE'].astype(str)
    # Successively merge monthly population columns and fill missing values with 0
    df_pop_sum = df_pop_sum.merge(ps_list[i], on='CODE', how='left').fillna(0)

# 4. Save the finalized time-series population flow dataset
df_pop_sum.to_csv('./pop_month.csv', encoding='cp949', index=False)