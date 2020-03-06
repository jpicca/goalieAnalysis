import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

checkedGames = []
playType, shooter, goalie, shooterTeamScore, goalieTeamScore = [],[],[],[],[]
shooterHomeAway = [] # Is the goalie playing at home or not?
x,y = [],[]
periodList,shotType = [],[] # Adjust for defending side (make x positive for attacking zone)
periodTime = []
manPowerList = []
isOT = []

shooterDict, goalieDict = {},{}

# Grab the last date from when this code was last run
with open('./data/lastDate.txt', 'r') as file:
    startDate = file.readline()

# Add a day to the start date, since we read in the last day for which we grabbed data
startDate = (datetime.strptime(startDate,'%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
endDate = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

### Need to eventually create loop to check games for every team, setting up the checkedGames list beforehand
teamIdList = [1,2,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,28,29,30,52,53,54]
#### **** For testing *** 
#teamIdList = [1]

def timeConvert(time,period):
    seconds = int(time.split(':')[0])*60 + int(time.split(':')[1]) + (period-1)*1200
    return seconds

def getPlays(playList):
    
    # loop through plays for each game
    # We store the index in case we need to get the previous score for a goal play
    
    # We need to know if it's Vegas playing at home -- for some reason VGK home games
    # don't report a rinkside per period. So we need to adjust for that on the fly
    vegasHome = False;
    
    if (metaData['teams']['home']['id'] == 54):
        vegasHome = True;
    
    penalties = {'home':[],'away':[]}
    numOnIce = {'home':5,'away':5}
    
    for idx,play in enumerate(playList):
        
        try:
            
            # If we've entered shootout territory, break the play loop since we don't care about these data
            if (play['about']['period'] == 5):
                
                break
                
                  
            if ((play['result']['eventTypeId'] == 'PENALTY')): 
                if ((play['result']['penaltyMinutes'] < 10) 
                    & (play['result']['secondaryType'] != 'Fighting')):

                    #Need to check if home or away penalty

                    penTeamLoc = homeAwayDict[play['team']['id']]
                    penaltyTime = play['about']['periodTime']
                    penaltyPeriod = play['about']['period']

                    expirationTime = timeConvert(penaltyTime,penaltyPeriod) + (play['result']['penaltyMinutes'])*60

                    # if penalty only 2 min
                    if (play['result']['penaltyMinutes'] == 2):

                        # the second position of the appended tuple indicates if it's a major penalty or not
                        penalties[penTeamLoc].append((expirationTime,False))
                        
                        '''if (playList[idx-1]['result']['eventTypeId'] == 'PENALTY'):
                            
                            if ((playList[idx-1]['about']['periodTime'] == play['about']['periodTime']) &
                               (playList[idx-1]['players'][0]['player']['id'] == play['players'][0]['player']['id'])):
                            
                                penalties[penTeamLoc].append((expirationTime+120,False))'''
                        
                        numOnIce[penTeamLoc] -= 1

                    # if penalty 4 min
                    if (play['result']['penaltyMinutes'] == 4):

                        # Add the second penalty for a double minor, but only subtract one skater
                        additionalPenalty = timeConvert(penaltyTime,penaltyPeriod) + 120
                        penalties[penTeamLoc].append((additionalPenalty,False))
                        penalties[penTeamLoc].append((expirationTime,False))

                        numOnIce[penTeamLoc] -= 1

                    # if penalty 5 min
                    if (play['result']['penaltyMinutes'] == 5):

                        # Set boolean to True (is penalty major? True)
                        penalties[penTeamLoc].append((expirationTime,True))

                        numOnIce[penTeamLoc] -= 1

                    #homePenalties.append([play['about']['periodTime'],play['about']['period']])
                    
            if ((play['result']['eventTypeId'] == 'GOAL') | (play['result']['eventTypeId'] == 'SHOT')):
                
                thisPlay = play['result']['eventTypeId']
                
                # A little empty net logic
                if (thisPlay == 'GOAL'):
                    if (play['result']['emptyNet'] == True):
                        
                        # We don't want to append empty-net goal data at this time
                        continue
                
                # We try appending shotType first -- in the weird case of an awarded goal,
                # there is no shot type, in which case an error is caught and we go to the next play
                # Therefore, we need to test this first before trying to append anything else
                shotType.append(play['result']['secondaryType'])
                
                playType.append(thisPlay)
                
                period = play['about']['period']
                periodList.append(period)
                
                currentTime = timeConvert(play['about']['periodTime'], period)
                               
                periodTime.append(currentTime)
                
                #print(f'Before check home {numOnIce["home"]}')
                
                # Check if penalties have expired
                if (len(penalties['home']) > 0):
                    
                    for i,penalty in enumerate(penalties['home']):

                        if (currentTime > penalty[0]):
                            #print('before home')
                            #print(numOnIce['home'])
                            #del penalties['home'][i]
                            numOnIce['home'] += 1
                            #print('after home')
                            #print(numOnIce['home'])
                    penalties["home"] = [x for x in penalties["home"] if currentTime < x[0]]        
                    
                    #print(f'Home: {penalties["home"]}')
                
                #print(f'Before check away {numOnIce["away"]}')
                          
                if (len(penalties['away']) > 0):
                    for i,penalty in enumerate(penalties['away']):
                    
                        if (currentTime > penalty[0]):
                            #print('before away')
                            #print(numOnIce['away'])
                            #del penalties['away'][i]
                            numOnIce['away'] += 1
                            #print('after away')
                            #print(numOnIce['away'])
                    penalties["away"] = [x for x in penalties["away"] if currentTime < x[0]]
                          
                    #print(f'Away: {penalties["away"]}')
                
                # Add dummy variable for OT
                if (period == 4):
                    
                    isOT.append(1)
                    
                else:
                    
                    isOT.append(0)
                
                ####################################
                #### Perform x coord adjustment ####
                ####################################         
                
                # Get the location of the shooting/scoring team 
                shootingTeamLoc = homeAwayDict[play['team']['id']]
                
                if (shootingTeamLoc == 'home'):
                    goalieLoc = 'away'
                else:
                    goalieLoc = 'home'
                    
                manPowerList.append(numOnIce[shootingTeamLoc] - numOnIce[goalieLoc])
                
                # Use that location to determine if we need to adjust x
                try:
                    if vegasHome:
                        # Vegas needs its x reversed in the 1st and 3rd
                        if (((period == 1) | (period == 3)) & (shootingTeamLoc == 'home')):
                            x.append(play['coordinates']['x']*-1)
                        # Opposing team needs its x reversed in 2nd and OT
                        elif (((period == 2) | (period == 4)) & (shootingTeamLoc == 'away')):
                            x.append(play['coordinates']['x']*-1)
                        else:
                            x.append(play['coordinates']['x'])
                    # If VGK isn't the home team, we can continue as normal
                    else:
                        rinkside = periods[period-1][shootingTeamLoc]['rinkSide']
                        if (rinkside == 'right'):
                            x.append(play['coordinates']['x']*-1)
                        else:
                            x.append(play['coordinates']['x'])
                except Exception as e:
                    print(str(e),period,idx)
                
                #### --------------------------- ####
                
                # Append y coordinate
                y.append(play['coordinates']['y'])
                
                # Append shooter home/away
                shooterHomeAway.append(shootingTeamLoc)
                
                # Append shooterID and add shooter to dictionary
                # Shooter will always be the first element of the player list, regardless of goal or shot
                shooterID = play['players'][0]['player']['id']
                shooterDict[shooterID] = play['players'][0]['player']['fullName']
                
                if (thisPlay == 'SHOT'):
                    
                    goalieID = play['players'][1]['player']['id']
                    goalieDict[goalieID] = play['players'][1]['player']['fullName']
                      
                    shooterTeamScore.append(play['about']['goals'][shootingTeamLoc])
                    goalieTeamScore.append(play['about']['goals'][goalieLoc])
                
                else:
                    
                    goalieID = play['players'][-1]['player']['id']
                    goalieDict[goalieID] = play['players'][-1]['player']['fullName']
                      
                    shooterTeamScore.append(playList[idx-1]['about']['goals'][shootingTeamLoc])
                    goalieTeamScore.append(playList[idx-1]['about']['goals'][goalieLoc])
                      
                    # Logic to boost numOnIce after a power-play goal
                      
                    if (play['result']['strength']['code'] == 'PPG'):
                          
                          #print('Power Play Goal!')
                          majorUpOne = False
                          
                          # Loop through penalties in effect on the shorthanded team
                          for specPen in penalties[goalieLoc]:
                              
                              # If a major was in effect and the shorthanded team was only down 1 person
                              if ((specPen[1] == True) & (numOnIce[shootingTeamLoc] - numOnIce[goalieLoc] == 1)):
                                  
                                  # Set to True for later and don't do anything -- major continues
                                  majorUpOne = True
                      
                                  break
                      
                          # Otherwise, we need to add 1 back to the shorthanded team and remove the penalty
                          if (not majorUpOne):
                      
                              numOnIce[goalieLoc] += 1
                      
                              for idx,specPen in enumerate(penalties[goalieLoc]):
                              
                                  if (specPen[1] == False):
                                      
                                      del penalties[goalieLoc][idx]
                                      
                                  
                    
                shooter.append(shooterID)
                goalie.append(goalieID)

        # Stoppage plays don't have the above properties so we have to catch those errors
        except(KeyError):
            
            pass
            #print("stoppage or some nonsense")

for team in teamIdList:

    url = 'https://statsapi.web.nhl.com/api/v1/schedule?'

    params = {
        'teamId': team,
        'startDate': startDate,
        #'startDate': '2019-10-01',
        'endDate': endDate
    }

    response = requests.get(url, params)
    
    print(f'Checking games for team {team}')
    for idx,game in enumerate(response.json()['dates']):
        #print(game['games'][0]['link'])

        gameID = game['games'][0]['gamePk']

        # As we look through more and more teams, we'll start running into duplicate games that we've already
        # scraped. If so, move to the next game
        if gameID in checkedGames:
            continue
        else:
            checkedGames.append(gameID)

        # Get game endpoints and request data
        gameEndpoint = game['games'][0]['link']
        game_url = "https://statsapi.web.nhl.com" + gameEndpoint

        print(f'Grabbing: {game_url}')
        gameResponse = requests.get(game_url)

        if (gameResponse.status_code == 200):

            # Get various json data if the game response is valid
            playList = gameResponse.json()['liveData']['plays']['allPlays']
            boxScore = gameResponse.json()['liveData']['boxscore']
            metaData = gameResponse.json()['gameData']
            periods = gameResponse.json()['liveData']['linescore']['periods']

        # Get the home/away for each team, to use in our x adjustment

        homeAwayDict = {}
        homeAwayDict[metaData['teams']['away']['id']] = 'away'
        homeAwayDict[metaData['teams']['home']['id']] = 'home'

        # Get plays

        getPlays(playList)


# After the for loop, create a dataframe
playsDF = pd.DataFrame({'play':playType, 'shooter':shooter, 'goalie':goalie, 
                        'shooterTeamScore':shooterTeamScore,'goalieTeamScore':goalieTeamScore,
                        'shooterHomeAway':shooterHomeAway,'period':periodList, 'time':periodTime,
                        'x': x, 'y': y, 'shotType':shotType, 'manAdvantageDiff': manPowerList})

# Combine original dataframe with this new dataframe, unless an original doesn't exist,
# in which case, save the new dataframe as is

try:
    print('Reading base play file...')
    baseDF = pd.read_csv('./data/playLibrary_v2.csv')
    joinedDF = pd.concat([baseDF,playsDF])
    joinedDF.to_csv('./data/playLibrary_v2.csv',index=False)
    
except:
    print('A base play file does not appear to exist.')
    print('*'*10)
    print('Saving play dataframe to make a base play file...')
    playsDF.to_csv('./data/playLibrary_v2.csv',index=False)

# Update goalie json
# Load prior json
with open('./data/goalies.json', 'r') as file:
    baseDict = json.load(file)

# Loop through goalies and add any new ones to the dict
for goalie in goalieDict:
    baseDict[goalieDict[goalie]] = str(goalie)

# Save the updated dict to a json file
with open('./data/goalies.json','w') as file:
    json.dump(baseDict, file)

# Write enddate to a text file so we know where to start with next write
with open('./data/lastDate.txt', 'w') as file:
    file.write(endDate)