import pandas as pd
import numpy as np
from tqdm.auto import tqdm
import warnings

# Set display options for floating point numbers and ignore warnings
pd.options.display.float_format = '{:.5f}'.format
warnings.filterwarnings(action='ignore')

# 1. Load Preprocessed Datasets
# 'card_month.csv': Monthly credit card transaction flow data
# 'pop_month.csv': Monthly mobile-based floating population flow data
pay = pd.read_csv('./card_month.csv', encoding='cp949')
pm = pd.read_csv('./pop_month.csv', encoding='cp949')

# Define analysis target month
ym = ['202203']

# 2. Merge Card and Population Data for each month
for i in tqdm(ym):
    # Select key columns: O/D codes, coordinates (x, y), and numeric IDs
    pay1 = pay.loc[:, ['O', 'D', 'O_x', 'O_y', 'D_x', 'D_y', 'num_x', 'num_y', 'CODE', 'PAY_' + i]]
    pm1 = pm['POP_' + i]
    
    # Concatenate population flow data to the card flow dataframe
    df_pop = pd.concat([pay1, pm1], axis=1)
    df_pop.to_csv('./pay_pop_' + i + '.csv', encoding='cp949', index=False)

# 3. Define Depopulation Regions in Jeolla Province
# Load administrative code mapping file
code = pd.read_csv('./CODE_2023.01.01.csv', encoding='cp949')

# List of district names (SGG) designated as depopulation regions in Jeolla-do
pop_nm = [
    '고창군', '김제시', '남원시', '무주군', '부안군', '순창군', '임실군', '장수군', '정읍시', '진안군', 
    '강진군', '고흥군', '곡성군', '구례군', '담양군', '보성군', '신안군', '영광군', '영암군', '완도군', 
    '장성군', '장흥군', '진도군', '함평군', '해남군', '화순군'
]

# Extract codes for the defined regions
code_list = []
for i in pop_nm:
    code_list.append(list(code[code['SGG'] == i]['CODE']))

# 4. Filter Inter-regional Flows between Depopulation Regions
for y in tqdm(ym):
    df = pd.read_csv('./pay_pop_month/pay_pop_' + y + '.csv', encoding='cp949')
    df['O'] = df['O'].astype(str)
    df['D'] = df['D'].astype(str)

    # Filter flows where both Origin (O) and Destination (D) are in the Jeolla depopulation list
    # The codes below represent the specific administrative codes for the SGGs listed above
    depop_codes = [
        '35570', '35060', '35050', '35530', '35580', '35560', '35550', '35540', '35040', '35520',
        '36590', '36550', '36520', '36530', '36510', '36560', '36680', '36640', '36610', '36660',
        '36650', '36580', '36670', '36630', '36600', '36570'
    ]
    
    df = df[df['O'].isin(depop_codes) & df['D'].isin(depop_codes)]
    
    # 5. Statistical Normalization (Z-score)
    # Standardizing card payment (PAY) and population (POP) values for spatial association analysis
    df['Zpay_P'] = (df['PAY_' + y] - df['PAY_' + y].mean()) / df['PAY_' + y].std()
    df['Zpop_P'] = (df['POP_' + y] - df['POP_' + y].mean()) / df['POP_' + y].std()
    
    # Drop unnecessary columns and save the regional subset
    df = df.drop(['CODE'], axis=1)
    df.to_csv('./pay_pop_전라도(인구감소지역)_' + y + '.csv', encoding='cp949', index=False)