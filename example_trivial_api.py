import sys

import requests
import json
import pandas as pd

seriesId = "CUUR0000SA0"

# get CPI data from BLS site
print("Getting data from BLS website...")
headers = {'Content-type': 'application/json'}
data = json.dumps({"seriesid": [seriesId],"startyear":"2022", "endyear":"2023"})

p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
json_data = json.loads(p.text)

#json_data['Results']['series']

#print('Series: ' + seriesId)
df = pd.json_normalize(json_data['Results']['series'][0], record_path=['data'])
