import json
import numpy as np
import requests

# Load the goalie list json
with open('./data/goalies.json', 'r') as file:
    baseDict = json.load(file)

# Loop through the dictionary and grab TOI data from NHL API

per60Dict = {}

for value in baseDict.values():
    url = f'https://statsapi.web.nhl.com/api/v1/people/{value}/stats?stats=statsSingleSeason&season=20192020'
    
    print(f'Getting TOI data for {value}...')
    response = requests.get(url)
    
    timeList = response.json()['stats'][0]['splits'][0]['stat']['timeOnIce'].split(':')
    minOnIce = int(timeList[0]) + int(timeList[1])/60
    
    per60 = np.round(minOnIce/60,2)
    
    # Get goalie's team
    url = f'https://statsapi.web.nhl.com/api/v1/people/{value}'
    response = requests.get(url).json()
    team = response['people'][0]['currentTeam']['name'].split(' ')[-1]
    
    per60Dict[value] = {'games': per60, 'currTeam': team}

# Save the updated dict to a json file
with open('./data/goalieTime.json','w') as file:
    json.dump(per60Dict, file)