import pandas as pd
import numpy as np
import math
from joblib import load
from datetime import datetime

# Read dataset
df = pd.read_csv('./data/playLibrary_v2.csv')

# Create additional features
df['scoreDiff'] = df['shooterTeamScore'] - df['goalieTeamScore']
df['isOT'] = (df['period']/4).apply(lambda x: math.floor(x))
df['distance'] = ((89 - df['x'])*(89 - df['x']) + (df['y']*df['y']))**(0.5)
df['angle'] = (df['y']/df['distance']).apply(lambda x: math.asin(x)*180/math.pi)
df['shooterIsHome'] = pd.get_dummies(df['shooterHomeAway'],drop_first=True)
df = df.join(pd.get_dummies(df['shotType'],drop_first=True))
df = df.join(pd.get_dummies(df['shooter']))
df['target'] = pd.get_dummies(df['play'])['GOAL']

# Drop columns we don't need and set up column
X = df.drop(columns=['target','period','shotType','shooterHomeAway','goalie','shooter','play'])
y = df['target']

# Load scaler & model
scaler = load('./models/scaler.bin')

today = datetime.now().strftime('%d%m%Y')
model = load(f'./models/gbGoalie_{today}.joblib')

print('Model and scaler loaded! Transforming features and making goal predictions...')

# Scale features for modeling
X_scaled = scaler.transform(X)

# Predict goal probabilities
goalProb = np.round(model.predict_proba(X_scaled)[:,1],3)

# Create a dataframe to save and use for gridding/plotting
filtDF = df[['goalie','period','x','y','shotType','target']]

print('Added new goal probs to dataframe -- saving to csv')

# Add our predicted goals to filtDF
filtDF.loc[:,'goalProb'] = goalProb
filtDF.to_csv('./data/dataToFilter.csv',index=False)