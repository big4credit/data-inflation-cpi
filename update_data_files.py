import sys
import pandas as pd
from pathlib import Path

# Series: CUUR0000SA0 - CPI All Items
# https://beta.bls.gov/dataViewer/view/timeseries/CUUR0000SA0

# Series: CUUR0000SA0L1E - CPI Core (all items less food and energy)
# https://beta.bls.gov/dataViewer/view/timeseries/CUUR0000SA0L1E

# Series: CUSR0000SA0 - CPI All Items [seasonally adjusted]
# https://beta.bls.gov/dataViewer/view/timeseries/CUSR0000SA0

# Series: CUSR0000SA0L1E - CPI Core (all items less food and energy) [seasonally adjusted]
# https://beta.bls.gov/dataViewer/view/timeseries/CUSR0000SA0L1E

inputDir = './cpi'
outputDir = './data'
serieses = ['CUUR0000SA0','CUUR0000SA0L1E', 'CUSR0000SA0', 'CUSR0000SA0L1E']
filenameMap = {'CUUR0000SA0': 'inflation-all-items', 'CUUR0000SA0L1E': 'inflation-core', 'CUSR0000SA0': 'inflation-all-items-adj', 'CUSR0000SA0L1E': 'inflation-core-adj'}

# check if output data folder exists
outputDir_exists = Path(outputDir).exists()
if not outputDir_exists:
    print("Exit: output data folder does not exist (./data)")
    sys.exit()

# check if input data folder exists
inputDir_exists = Path(inputDir).exists()
if not inputDir_exists:
    print("Exit: input data folder does not exist (./cpi)")
    sys.exit()

# check if input data files exist
for series in serieses:
    input_filepath = inputDir + '/' + series + '.csv'
    if not Path(input_filepath).exists():
        print('Error: input file does not exist;', series)
        sys.exit(1)

print("Updating inflation data...")
for seriesId in serieses:
    print('Series: ' + seriesId)
    input_filepath = inputDir + '/' + seriesId + '.csv'

    df_orig = pd.read_csv(input_filepath)
    df = df_orig[::-1].reset_index(drop=True)  # reverse dataframe

    df['Value'] = pd.to_numeric(df['Value'])

    df['valueYearAgo'] = df['Value'].shift(-12)
    df['valueYearAgo'] = pd.to_numeric(df['valueYearAgo'])
    df['valueYearAgo'].fillna(value=999, inplace=True)

    df['valueMonthAgo'] = df['Value'].shift(-1)
    df['valueMonthAgo'] = pd.to_numeric(df['valueMonthAgo'])
    df['valueMonthAgo'].fillna(value=999, inplace=True)


    df['inflationYoYRaw']= df['Value'] / df['valueYearAgo']
    df['inflationYoYNorm']= ((df['inflationYoYRaw'] - 1)*100).round(1)

    df['inflationMoMRaw']= df['Value'] / df['valueMonthAgo']
    df['inflationMoMNorm']= ((df['inflationMoMRaw'] - 1)*100).round(1)

    df['dateStr'] = df['Year'].astype(str) + '-' + df['Period'].str[1:]

    df.drop(df.tail(12).index, inplace = True)    

    # Save YoY data
    column_names = ['date', 'inflation']  # desired column names in csv
    column_df = ['dateStr', 'inflationYoYNorm'] # column names in corresponding DataFrame
    filename = outputDir + '/' + filenameMap[seriesId] + '-yoy.csv'
    f_ = Path(filename)
    if f_.exists(): f_.unlink()
    df.to_csv(filename, index=False, header=column_names, columns=column_df)

    # Save MoM data
    column_names = ['date', 'inflation']  # desired column names in csv
    column_df = ['dateStr', 'inflationMoMNorm'] # column names in corresponding DataFrame
    filename = outputDir + '/' + filenameMap[seriesId] + '-mom.csv'
    f_ = Path(filename)
    if f_.exists(): f_.unlink()
    df.to_csv(filename, index=False, header=column_names, columns=column_df)

print("Done!")
