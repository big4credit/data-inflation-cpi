import sys
import argparse
from datetime import datetime

import requests
import json
#import prettytable
import pandas as pd
import numpy as np

from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--force", help="force update from BLS website", action="store_true")
args = parser.parse_args()


fileDir = './cpi' # dir with csv files
serieses = ['CUUR0000SA0','CUUR0000SA0L1E', 'CUSR0000SA0', 'CUSR0000SA0L1E']
filenameMap = {'CUUR0000SA0': 'inflation-all-items', 'CUUR0000SA0L1E': 'inflation-core', 'CUSR0000SA0': 'inflation-all-items-adj', 'CUSR0000SA0L1E': 'inflation-core-adj'}

yearEnd = datetime.today().year
yearStart = yearEnd - 5  # we will reuest 5 years of data

# check data folder exists
fileDir_exists = Path(fileDir).exists()
if not fileDir_exists:
    print(f"Exit: data folder does not exist ({fileDir})")
    sys.exit()

# check csv files exist
for seriesId in serieses:
    filename = fileDir + '/' + seriesId + '.csv'
    file_exists = Path(filename).exists()
    if not file_exists:
        print(f"Exit: {filename} - does not exist")
        sys.exit()


# get CPI data from BLS site
print("Getting data from BLS website...")
headers = {'Content-type': 'application/json'}
data = json.dumps({"seriesid": serieses,"startyear": yearStart, "endyear": yearEnd})

p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
json_data = json.loads(p.text)

for series in json_data['Results']['series']:
    seriesId = series['seriesID']
    print('Series: ' + seriesId)
  
    # manipulate BLS dataframe
    df_bls = pd.json_normalize(series, record_path=['data'])
    df_bls = df_bls.drop(columns=['periodName', 'footnotes'])  # drop unnecessary columns
    #df_bls = df_bls.drop(columns=['periodName', 'latest', 'footnotes'])  # drop unnecessary columns
    df_bls['seriesId'] = seriesId  # add column with default value equal seriesId
    df_bls['year'] = df_bls['year'].astype('int')  # convert to int64
    df_bls['value'] = df_bls['value'].astype('float')  # convert to float64

    print("  Reading input data file...")
    input_filepath = fileDir + '/' + seriesId + '.csv'
    df_csv = pd.read_csv(input_filepath)

    # merge dataframes
    df_merged = df_csv.merge(df_bls, on=['seriesId', 'year', 'period'], how='outer')
    df_merged['value'] = df_merged['value_y'].fillna(df_merged['value_x'])

    # cross-check that new number from BLS are not very different
    df_xcheck = df_csv.merge(df_bls, on=['seriesId', 'year', 'period'], how='inner')
    # value_x is CSV
    # value_y is BLS
    df_xcheck['equal'] = np.isclose(df_xcheck['value_x'], df_xcheck['value_y'])

    # Save data to CSV
    if args.force or df_xcheck['equal'].all():  # check if data has been revised by Bureau of Labor Statistics
        Path(input_filepath).unlink()
        column_df = ['seriesId', 'year', 'period', 'value']
        df_merged.to_csv(input_filepath, index=False, columns=column_df)
        print('  Saved.')
    if not df_xcheck['equal'].all():
        print("----- Error !!!!!!!!!!!!!!!-----")
        print("Note: BLS data differs CSV data for the same year/period")
        print(df_xcheck[df_xcheck['equal'] == False])
    else:
        pass

    
