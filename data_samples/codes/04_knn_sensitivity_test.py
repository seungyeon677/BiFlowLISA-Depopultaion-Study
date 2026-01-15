import pandas as pd
import numpy as np
from tqdm.auto import tqdm
from libpysal.weights import KNN
import seaborn as sns
import matplotlib.pyplot as plt
import warnings

# Set display options and ignore warnings
pd.options.display.float_format = '{:.5f}'.format
warnings.filterwarnings(action='ignore')

# Define analysis target month
ym = ['202203']

# 1. Sensitivity Analysis for Spatial Weights: KNN 1 to 10
for knn in tqdm(range(1, 11), desc="KNN Sensitivity Loop"):
    shp_path = './bnd_sigungu_00_2022_2022_2Q.shp'
    
    # Create KNN spatial weight matrix from shapefile
    knnW = KNN.from_shapefile(shp_path, k=knn)
    Wknnmatrix, ids = knnW.full()
    p_array = Wknnmatrix

    # Set self-adjacency (Diagonal elements to 1)
    for i in range(len(p_array)):
        p_array[i][i] = 1

    for y in tqdm(ym, desc="Monthly Loop"):
        # Load standardized flow data (Subsetted for Jeolla depopulation regions)
        od = pd.read_csv('./pay_pop_' + '전라도(인구감소지역)' + '_' + y + '.csv', encoding='cp949')
        print("Data loading finished")

        # Convert columns to lists for faster iteration
        O = list(od.loc[:, 'num_x'])
        D = list(od.loc[:, 'num_y'])
        Zpay = list(od.loc[:, 'Zpay_P'])
        Zpop = list(od.loc[:, 'Zpop_P'])
        idx = od.index
        print("Listing finished")

        # 2. Compute Spatial Lag: x = Population, y = Card Payment
        # This calculates the weighted average of 'y' flows in the neighborhood of 'x' flows
        pop_x = []
        for i in range(len(idx)):
            pay_y_neighbors = []
            for j in range(len(idx)):
                # Adjacency between Origin nodes AND Destination nodes
                dist_o = p_array[O[i]-1][O[j]-1]
                dist_d = p_array[D[i]-1][D[j]-1]

                # If either Origin or Destination is adjacent, consider as neighbor flow
                if (dist_o == 1) | (dist_d == 1):
                    zp = Zpay[j]
                else:
                    zp = 0.0
                pay_y_neighbors.append(zp)
            pop_x.append(sum(pay_y_neighbors))

        # 3. Compute Spatial Lag: x = Card Payment, y = Population
        pay_x = []
        for k in range(len(idx)):
            pop_y_neighbors = []
            for f in range(len(idx)):
                dist_o = p_array[O[k]-1][O[f]-1]
                dist_d = p_array[D[k]-1][D[f]-1]

                if (dist_o == 1) | (dist_d == 1):
                    zp = Zpop[f]
                else:
                    zp = 0.0
                pop_y_neighbors.append(zp)
            pay_x.append(sum(pop_y_neighbors))

        # Store lag values
        od['PAYlag'] = pay_x
        od['POPlag'] = pop_x
        
        # 4. Calculate Bivariate Flow Statistics (BiFl)
        # BiFl indicators based on standardized values and spatial lags
        od['BiFl_PAY'] = (od['Zpay_P'] * od['PAYlag']) / od['Zpay_P']**2
        od['BiFl_POP'] = (od['Zpop_P'] * od['POPlag']) / od['Zpop_P']**2

        # Standardize BiFl scores for significance testing
        od['BiFl_PAYsig'] = (od['BiFl_PAY'] - od['BiFl_PAY'].mean()) / od['BiFl_PAY'].std()
        od['BiFl_POPsig'] = (od['BiFl_POP'] - od['BiFl_POP'].mean()) / od['BiFl_POP'].std()

        # 5. Cluster Categorization (HH, HL, LH, LL)
        # Type A: Population (x) vs Card Payment Lag (y)
        od['value_P'] = 'NS' # Default to Non-Significant
        for i in idx:
            if (od['Zpop_P'][i] >= 0):
                od['value_P'][i] = 'HH' if (od['PAYlag'][i] >= 0) else 'HL'
            else:
                od['value_P'][i] = 'LH' if (od['PAYlag'][i] >= 0) else 'LL'

        # Filter by Statistical Significance (Z-score threshold: 2.58 for 99% confidence)
        od['value_P2'] = 'NS'
        for i in idx:
            if abs(od['BiFl_POPsig'][i]) >= 2.58:
                od['value_P2'][i] = od['value_P'][i]

        # Type B: Card Payment (x) vs Population Lag (y)
        od['value_Y'] = 'NS'
        for i in idx:
            if (od['Zpay_P'][i] >= 0):
                od['value_Y'][i] = 'HH' if (od['POPlag'][i] >= 0) else 'HL'
            else:
                od['value_Y'][i] = 'LH' if (od['POPlag'][i] >= 0) else 'LL'

        od['value_Y2'] = 'NS'
        for i in idx:
            if abs(od['BiFl_PAYsig'][i]) >= 2.58:
                od['value_Y2'][i] = od['value_Y'][i]

        # 6. Export Final Results for Visualization
        output_name = f'./KNN{knn}_BiFl_PAY_POP_Jeolla_Depop_{y}.csv'
        od.to_csv(output_name, encoding='cp949', index=False)
        print(f"Results saved for KNN={knn}")
        

# Initialize an empty DataFrame to store aggregated results across different KNN values
c_df1 = pd.DataFrame()

# Loop through KNN values from 1 to 10 for sensitivity analysis
for knn in range(1, 11):
    count = []
    for y in ym:
        # Load the Bivariate Flow-LISA results for the specific KNN and year
        df = pd.read_csv('./KNN' + str(knn) + '_BiFl_PAY_POP_전라도_self_' + y + '.csv', encoding = 'cp949')
        
        # Identify significant flow clusters and create list pairs of [Year, Category]
        # HH: High-High, HL: High-Low, LH: Low-High, LL: Low-Low
        a = [[y, 'HH']] * len(df[df['value_Y2'] == 'HH'])
        b = [[y, 'HL']] * len(df[df['value_Y2'] == 'HL'])
        c = [[y, 'LH']] * len(df[df['value_Y2'] == 'LH'])
        d = [[y, 'LL']] * len(df[df['value_Y2'] == 'LL'])
        
        # Combine all detected significant clusters for the current year
        finish = [a + b + c + d]
        count.append(finish)
        
    # Flatten the list of results for the current KNN value
    cc = []
    for i in range(len(count)):
        if len(count[i][0]) != 0:
            for j in range(len(count[i][0])):
                cc.append(count[i][0][j])
                
    # Create a DataFrame for the current KNN results
    col = ['Year', 'category']
    c_df = pd.DataFrame(cc, columns = col)
    c_df['KNN'] = str(knn)
    
    # Append the current KNN results to the master DataFrame
    c_df1 = pd.concat([c_df1, c_df], axis = 0)

# Reset index for clean plotting
c_df1 = c_df1.reset_index()

# Define standardized colors for LISA clusters (Red, Orange, Green, Blue)
colors = ['#FF0000', '#FFAA00', '#38A800', '#0070FF']
sns.set_palette(sns.color_palette(colors))

# Plotting the stacked histogram to visualize sensitivity to KNN parameter
fig, ax = plt.subplots(figsize = (10, 7))
sns.histplot(x = 'KNN', hue='category', hue_order = ['HH', 'HL', 'LH', 'LL'], edgecolor = 'white', 
             multiple='stack', data=c_df1, alpha = 0.6)

# Set title and labels for the chart
plt.title('Bivariate Flow-LISA Cluster Distribution by KNN (k=1 to 10)')
plt.xlabel('K-Nearest Neighbors (k)')
plt.ylabel('Frequency of Significant Flows')

plt.show()