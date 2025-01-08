## 2025 Week 1 Makeover Monday submission by Andrew Staroscik 

# setup 

import pandas as pd
import matplotlib.pyplot as plt

# load data
dfA = pd.read_csv('../data/2025/hpvVaccineCoverage.csv')

# limit to just contry data
dfB = dfA[~dfA['Code'].isna()]

# transform data to a time series
dfC = dfB.pivot(index=['Entity', 'Code'], columns='Year', values=' Proportion who received the final dose of (HPV) vaccine (%)').reset_index()

# simplify the dataframe for chart
colsForChart = ['Entity'] + [year for year in range(2010, 2022 + 1)]
df = dfC[colsForChart]
df.set_index('Entity', inplace=True)

# function to get the first and last year of data for each country
def getFirstLastData(row):
    
    firstY = row[row.notna()].index[0]
    lastY = row[row.notna()].index[-1]
    
    newRow = pd.Series(index=row.index, dtype=float)
    newRow[firstY] = row[firstY]
    newRow[lastY] = row[lastY]
    return newRow

# function to add new column to each row based on delta
def changeType(row):
  realVals = row.dropna()
    
  if len(realVals) >= 2:
    firstV = realVals.iloc[0]
    lastV = realVals.iloc[-1]
  
    deltaOfInterest = 10
    if firstV > int(lastV) + deltaOfInterest:
      return 'down'
    if lastV > int(firstV)+ deltaOfInterest:
      return 'up'
    else: 
      if lastV < 30:
          return 'low'
      if lastV < 70: 
          return 'mid'
      else: 
          return 'high'

# add change type to dataframe
df['changeType'] = df.apply(changeType, axis=1)

# function to set status based on 2022 values
def setCurrentBin(v):
  if v >=70:
    return 'high'
  elif v >= 30:
    return 'mid'
  else: 
    return 'low'

# get rid of the world data and all countries without 2022 data
df.drop('World', inplace=True)
df = df[~df[2022].isna()]
df['current'] = df[2022].apply(setCurrentBin)

# set up a 10 panel figure for the chart
fig, axes = plt.subplots(5, 2, figsize=(15, 18), gridspec_kw={'width_ratios': [1.5, 1]})
fig.subplots_adjust(hspace=0)  

changeTypes = ['high', 'up', 'mid', 'down', 'low']
chartLabels = ['High Rates', 'Increasing Rates', 'Intermediate Rates', 'Decreasing Rates', 'Low Rates']

# custom positioning of country names
yPosAdj = [
  {'high': 0.8, 'mid': 1, 'low': 1}, # high
  {'high': 1, 'mid': 0.625, 'low': 0.25}, # rising
  {'high': 1, 'mid': 0.7, 'low': 1}, # intermediate
  {'high': 1, 'mid': 0.8, 'low': 0.5}, # decreasing
  {'high': 1, 'mid': 1, 'low': 0.5} # low
]

yearCol = [col for col in df.columns if isinstance(col, int)]

# Function to determine text color based on the 2022 value
def get_color(value):
  if value >= 70:
    return '#36b700'
  elif value >= 30:
    return '#8c8c8c'
  else:
    return '#9d2c00'
    
def get_color_level(cur):
  if cur == 'high':
    return '#36b700'
  elif cur == 'mid':
    return '#8c8c8c'
  else:
    return '#9d2c00'
    

for i, change_type in enumerate(changeTypes):
  dfByType = df[df['changeType'] == change_type]
  
  # Left panel  Line charts
  tmpChart = axes[i, 0]
  for entity in dfByType.index:
    rowData = dfByType.loc[entity, yearCol].dropna()
    tmpChart.plot(rowData.index, rowData.values, alpha=0.7, color=get_color(rowData[2022]))
  
  tmpChart.set_title('')
  tmpChart.annotate(chartLabels[i], xy=(2009.5, 105), fontsize=18)

  tmpChart.spines['top'].set_visible(False)
  tmpChart.spines['right'].set_visible(False)

  # Remove x-axis tick labels for all charts except the bottom one
  if i < len(changeTypes) - 1:
    tmpChart.set_xticks([])
  else:
    tmpChart.set_xlabel('Year', fontsize=14)

  tmpChart.set_ylim(0, 115)  
  tmpChart.set_ylabel('')
  tmpChart.tick_params(axis='x', labelsize=14)
  tmpChart.tick_params(axis='y', labelsize=14)
  
  # Right panel: List of entities with colored text
  axTickLab = axes[i, 1]
  axTickLab.axis('off')  

  if dfByType.empty:
    axTickLab.text(
      0.5, 0.5, 'No Countries in bin', fontsize=12, color='gray', ha='center', va='center'
    )
  else:
      
    displayBins = ['high', 'mid', 'low']
    for indx, cRate in enumerate(displayBins):
      dfSubset = dfByType[dfByType['current'] == cRate]

      countries = dfSubset.index.tolist()
      values_2022 = dfSubset[2022].tolist()

      numCols = 4
      splitCountries = [countries[j::numCols] for j in range(numCols)]
      splitVals = [values_2022[j::numCols] for j in range(numCols)]
        
      xPos = [-0.6, -0.175, 0.25, 0.65][:numCols]  # Adjust positions for columns
      max_rows = max(len(split) for split in splitCountries)

      txtAdj = 1
      if i == 0:
        txtAdj = 3

      for col, (colCountries, colVals) in enumerate(zip(splitCountries, splitVals)):
        for row, (country, value) in enumerate(zip(colCountries, colVals)):
          color = get_color_level(cRate)
          axTickLab.text(
            xPos[col], 
            yPosAdj[i][cRate] - (row + txtAdj) * 0.09,  # Adjust vertical spacing
            country,
            fontsize=15,
            color=color,
            ha='center',
            va='top'
          )

rightLegendTop = 0.955

fig.text(0.75, rightLegendTop, 'Country Rates in 2022',fontsize=15,color='black',ha='center')
fig.text(0.75, rightLegendTop - 0.015, 'High',fontsize=14,color=get_color(85),ha='center')
fig.text(0.75, rightLegendTop - 0.03, 'Intermediate',fontsize=14,color=get_color(50),ha='center')
fig.text(0.75, rightLegendTop - 0.045, 'Low',fontsize=14,color=get_color(20),ha='center')
fig.text(0.02, 0.45, 'HPV Vaccination Rates (%)',fontsize=22,color='#232323',ha='center',rotation=90)

fig.text( 0.05, 0.976, 'Patterns in HPV Country Level Vaccination Rates Over Time', fontsize= 25)
fig.text( 0.05, 0.01, 'Source: Our World in Data', fontsize= 10)
fig.text( 0.85, 0.025, 'Andrew Staroscik', fontsize= 18, color='#898989', ha='center')
fig.text( 0.85, 0.015, '#makeovermonday', fontsize= 12, color='#898989', ha='center')

plt.tight_layout(rect=[0.025, 0, 1, 0.975])
plt.savefig('./hpvCountryRates.png', dpi=300)
plt.show()


