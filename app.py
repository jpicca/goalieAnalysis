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

file = open('./data/goalies.json')
openedFile = file.read()
goalieDict = json.loads(openedFile)

#################################################
# load dataframe
#################################################

df = pd.read_csv('./data/playLibrary_v2.csv')

@app.route("/")
def welcome():
    return (
        "Hopefully this fucking works"
    )

@app.route("/api/v1.0/goalies/<goalieID>")
def goalieAnalysis(goalieID):
    
    goalieDF = df[df['goalie'] == int(goalieID)]
    
    # Create grid object
    G = createGrid()
    totalGrid = np.zeros(G.tx.shape)

    points = G.grid_points(goalieDF['x'], goalieDF['y'])  # Run the Gridder!

    # Grid shot points for that game
    for point in points:
        totalGrid[point] += 1
    
    return jsonify(totalGrid.flatten().tolist())

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

