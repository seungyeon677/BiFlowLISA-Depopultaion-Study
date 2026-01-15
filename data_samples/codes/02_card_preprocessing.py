import pandas as pd
import numpy as np
from tqdm.auto import tqdm
import warnings

# Ignore warnings for cleaner output
warnings.filterwarnings(action='ignore')

# 1. Extract specific month data from raw text files (Batch 1)
ym = ['202208']
for i in tqdm(ym):
    data_list = []
    # Read the raw transaction data and filter by date
    with open("./KRILA_SHC_F_202302_202211.txt", encoding='utf-8') as f:
        while True:
            line = f.readline()
            if not line:
                break

            date = line.strip().split('|')[0]  # Extract the date column
            if date.startswith(i):
                data_list.append(line.strip().split('|'))
                
    # Get column headers from a reference file
    file = open("./KRILA_SHC_F_202208_2020.txt", 'r', encoding='utf-8')
    line = file.readline()
    columns = line.strip().split('|')

    # Save filtered data as CSV
    df = pd.DataFrame(data_list, columns=columns)
    df.to_csv('./KRILA_' + i + '.csv', encoding='cp949', index=False)

# 2. Extract monthly data for the year 2020 (Batch 2)
ym = ['202001', '202002', '202003', '202004', '202005', '202006', 
      '202007', '202008', '202009', '202010', '202011', '202012']

for i in tqdm(ym):
    data_list = []
    with open("./KRILA_SHC_F_202208_2020.txt", encoding='utf-8') as f:
        while True:
            line = f.readline()
            if not line:
                break

            date = line.strip().split('|')[0]
            if date.startswith(i):
                data_list.append(line.strip().split('|'))
                
    file = open("./KRILA_SHC_F_202208_2020.txt", 'r', encoding='utf-8')
    line = file.readline()
    columns = line.strip().split('|')
    
    df = pd.DataFrame(data_list, columns=columns)
    df.to_csv('./KRILA_' + i + '.csv', encoding='cp949', index=False)

# 3. Load master OD coordinates and Administrative Code mapping
od_xy = pd.read_csv('./od_xy_num_0716.csv', encoding='cp949')
code = pd.read_csv('./CODE_2023.01.01.csv', encoding='cp949')
code['CODE_AD'] = code['CODE_AD'].astype(str)

# Preprocess administrative codes to a 5-digit format
code_ad = [c[:5] for c in code['CODE_AD'].tolist()]
code['CODE_AD_2'] = code_ad

# Define analysis period for 2022
ym = []
month = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
for i in range(2022, 2023):
    for j in month:
        ym.append(str(i) + j)

# 4. Detailed Data Cleaning and Aggregation by month
cs_list = []
for y in tqdm(ym):
    # Load processed CSV for the month
    card = pd.read_csv('./KRILA_' + y + '.csv', encoding='cp949')
    card['MCT_SSG_CD'] = card['MCT_SSG_CD'].astype(str)
    card['CLNN_CTY_CD'] = card['CLNN_CTY_CD'].astype(str)

    # Filter out E-commerce (ETC) and invalid region codes containing '*'
    card_drop = card[~(card['RY_CD'] == 'ETC')]
    card_df = card_drop[~(card_drop['MCT_SSG_CD'].str.contains('\*'))]
    card_df = card_drop[~(card_drop['CLNN_CTY_CD'].str.contains('\*'))]
    
    card_o = card_df['CLNN_CTY_CD'].tolist()
    card_d = card_df['MCT_SSG_CD'].tolist()

    # Standardization of Region Codes (Handling administrative changes/mergers)
    # e.g., Yeoju-gun -> Yeoju-si, Nam-gu -> Michuhol-gu
    o = []
    for val in card_o:
        if val == '41730': o.append('41670')
        elif val == '44730': o.append('36110')
        elif val == '28170': o.append('28177')
        else: o.append(val)

    d = []
    for val in card_d:
        if val == '41730': d.append('41670')
        elif val == '44730': d.append('36110')
        else: d.append(val)

    card_df['O'] = o
    card_df['D'] = d

    # Group by Origin-Destination and sum the transaction amount (TAMT)
    # TAMT is converted from KRW 1,000 to KRW 1
    card_group = card_df.groupby(['O', 'D'])['TAMT'].sum().reset_index()
    card_group['TAMT'] = card_group['TAMT'] * 1000
    card_group = card_group.rename(columns={'TAMT': 'PAY_' + y})

    # Map administrative codes to standardized codes
    c_merge = pd.merge(card_group, code, left_on='O', right_on='CODE_AD_2', how='left')
    c_merge2 = pd.merge(c_merge, code, left_on='D', right_on='CODE_AD_2', how='left')
    c_merge2 = c_merge2.dropna().reset_index()
    
    # Create a unique OD pair key (CODE)
    c_merge2['CODE'] = c_merge2['CODE_x'].astype(int).astype(str) + c_merge2['CODE_y'].astype(int).astype(str)
    card_m = c_merge2[['CODE', 'PAY_' + y]]

    cs_list.append(card_m)

# 5. Final Integration: Merge all monthly columns into the master OD file
df_card_sum = od_xy        
for i in tqdm(range(len(cs_list))):
    od_xy['CODE'] = od_xy['CODE'].astype(str)
    df_card_sum = df_card_sum.merge(cs_list[i], on='CODE', how='left').fillna(0)
    
# Export final time-series card consumption flow data
df_card_sum.to_csv('./card_month.csv', encoding='cp949', index=False)