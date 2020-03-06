from flask import Flask, jsonify, Response
from flask_cors import CORS
import pandas as pd
import json
from gridder import Gridder
import numpy as np


#################################################
# Flask Setup
#################################################
app = Flask(__name__)
CORS(app)

#################################################
# goalie info
#################################################

file = open('./data/goalieTime.json')
openedFile = file.read()
goalieTime = json.loads(openedFile)

#################################################
# load dataframe
#################################################

#df = pd.read_csv('./data/playLibrary_v2.csv')
df = pd.read_csv('./data/dataToFilter.csv')
df['x'] = df['x'].apply(lambda x: abs(x))

@app.route("/")
def welcome():
    return (
        "Hopefully this fucking works"
    )

@app.route("/api/v1.0/goalies/<goalieID>")
def goalieAnalysis(goalieID):
    
    goalieDF = df[(df['goalie'] == int(goalieID))].reset_index(drop=True)
    allowedDF = df[(df['goalie'] == int(goalieID)) & (df['target'] == 1)].reset_index(drop=True)
    
    # Create grid object
    G = createGrid()
    expectedGrid = np.zeros(G.tx.shape)
    allowedGrid = np.zeros(G.tx.shape)

    expectedPoints = G.grid_points(goalieDF['x'], goalieDF['y'])  # Run the Gridder!
    allowedPoints = G.grid_points(allowedDF['x'], allowedDF['y']) # Run the Gridder!

    # Grid shot points for that game
    #for point in points:
    #    totalGrid[point] += 1

    # Increment by the goal probability, instead of just by 1
    for idx,point in enumerate(expectedPoints):
        expectedGrid[point] += 1*goalieDF['goalProb'][idx]

    for idx,point in enumerate(allowedPoints):
        allowedGrid[point] += 1

    # Calculate goals per 60 min

    expectedP60 = np.round(np.sum(expectedGrid)/goalieTime[goalieID]['games'],2)
    allowedP60 = np.round(np.sum(allowedGrid)/goalieTime[goalieID]['games'],2)

    diffList = (expectedGrid-allowedGrid).flatten().tolist()
    diffList.append([allowedP60,expectedP60])
    
    return jsonify(diffList)
    
    #return jsonify((expectedGrid-allowedGrid).flatten().tolist())

    #goalieJson = json.loads(goalieDF.to_json(orient='records'))

    #return jsonify(goalieJson)

#################################################
# returning the grid object
#################################################

def createGrid(dx=5,dy=5):

    # Create arrays for gridding
    x_axis = np.arange(-100,100,dx)
    y_axis = np.arange(-42.5,42.5,dy)

    # Create our meshgrid from our arrays
    X, Y = np.meshgrid(x_axis, y_axis)

    # Set up the grid
    G = Gridder(X,Y)

    return G



#################################################
# for testing purposes
#################################################

@app.route("/api/v1.0/goalies/test")
def testFunction():

    return jsonify(1,2,3)

# Run the app if called as the main program
if __name__ == "__main__":
    app.run(debug=True)

