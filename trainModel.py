import pandas as pd
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import math

# Read in Data

df = pd.read_csv('./data/playLibrary_v2.csv')

###
### Data Prep
###

# Set up features
df['scoreDiff'] = df['shooterTeamScore'] - df['goalieTeamScore']
df['isOT'] = (df['period']/4).apply(lambda x: math.floor(x))
df['distance'] = ((89 - df['x'])*(89 - df['x']) + (df['y']*df['y']))**(0.5)
df['angle'] = (df['y']/df['distance']).apply(lambda x: math.asin(x)*180/math.pi)
df['shooterIsHome'] = pd.get_dummies(df['shooterHomeAway'],drop_first=True)
df = df.join(pd.get_dummies(df['shotType'],drop_first=True))
df = df.join(pd.get_dummies(df['shooter']))
df['target'] = pd.get_dummies(df['play'])['GOAL']

###
### Model Training
###

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import GradientBoostingClassifier as GBC

X = df.drop(columns=['target','period','shotType','shooterHomeAway','goalie','shooter','play'])
y = df['target']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
trainX, testX, trainy, testy = train_test_split(X_scaled, y, test_size=0.5, random_state=2)

# Instantiate model
model = GBC(random_state=2)
calibrated = CalibratedClassifierCV(model, cv=5)

# Fit model to our data (this takes a little while)
print('Fitting model to data... hang tight for a little while')
calibrated.fit(trainX, trainy)

###
### Persisting model and scaler
###

from joblib import dump
from datetime import datetime

print('Saving new model and associated scaler')

today = datetime.now().strftime('%d%m%Y')

dump(calibrated, f'./models/gbGoalie_{today}.joblib')
dump(scaler, './models/scaler.bin')