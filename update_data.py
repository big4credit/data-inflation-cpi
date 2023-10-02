import sys

import requests
import json
import prettytable
import pandas as pd

from pathlib import Path

outputDir = './data'
serieses = ['CUUR0000SA0','CUUR0000SA0L1E']
filenameMap = {'CUUR0000SA0': 'inflation-all-items', 'CUUR0000SA0L1E': 'inflation-core'}

# check data folder exists
outputDir_exists = Path(outputDir).exists()
if not outputDir_exists: 
    print("Exit: data folder does not exist (./data)")
    sys.exit()
else:
    print("Removing CSV files in " + outputDir)

# clean data folder
path = Path(outputDir)
path_list = path.glob("*.csv")
[f.unlink() for f in path_list if f.is_file()]

# get CPI data from BLS site
print("Getting data from BLS website...")
headers = {'Content-type': 'application/json'}
data = json.dumps({"seriesid": serieses,"startyear":"2013", "endyear":"2023"})

p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
json_data = json.loads(p.text)

print("Saving new data...")
for series in json_data['Results']['series']:
    seriesId = series['seriesID']
    print('Series: ' + seriesId)
    df = pd.json_normalize(series, record_path=['data'])
    df['value'] = pd.to_numeric(df['value'])

    df['valueYearAgo'] = df['value'].shift(-12)
    df['valueYearAgo'] = pd.to_numeric(df['valueYearAgo'])
    df['valueYearAgo'].fillna(value=999, inplace=True)

    df['valueMonthAgo'] = df['value'].shift(-1)
    df['valueMonthAgo'] = pd.to_numeric(df['valueMonthAgo'])
    df['valueMonthAgo'].fillna(value=999, inplace=True)


    df['inflationYoYRaw']= df['value'] / df['valueYearAgo']
    df['inflationYoYNorm']= ((df['inflationYoYRaw'] - 1)*100).round(1)

    df['inflationMoMRaw']= df['value'] / df['valueMonthAgo']
    df['inflationMoMNorm']= ((df['inflationMoMRaw'] - 1)*100).round(1)

    df['dateStr'] = df['year'].astype(str) + '-' + df['period'].str[1:]

    df.drop(df.tail(12).index, inplace = True)

    # Save YoY data
    column_names = ['date', 'inflation']  # desired column names in csv
    column_df = ['dateStr', 'inflationYoYNorm'] # column names in corresponding DataFrame
    filename = outputDir + '/' + filenameMap[seriesId] + '-yoy.csv'
    df.to_csv(filename, index=False, header=column_names, columns=column_df)

    # Save MoM data 
    column_names = ['date', 'inflation']  # desired column names in csv
    column_df = ['dateStr', 'inflationMoMNorm'] # column names in corresponding DataFrame
    filename = outputDir + '/' + filenameMap[seriesId] + '-mom.csv'
    df.to_csv(filename, index=False, header=column_names, columns=column_df)

    #print(df)
    #print(df.dtypes)

print("Done!")
