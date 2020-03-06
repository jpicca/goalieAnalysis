import matplotlib.pyplot as plt
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.image as mpimg
import pandas as pd
import json

with open('./data/goalieTime.json', 'r') as file:
    baseDict = json.load(file)

df = pd.read_csv('./data/dataToFilter.csv')

fig,ax = plt.subplots(figsize=(15,9))
plt.plot([0,4],[0,4],linestyle='dashed',linewidth=1)

avgExp, avgGAA = 2.8, 2.8

for goalie in baseDict.keys():
    img=mpimg.imread(f'./static/teamLogos/{baseDict[goalie]["currTeam"]}.png')
    
    goalieDF = df[(df['goalie'] == int(goalie))].reset_index(drop=True)
    allowedDF = df[(df['goalie'] == int(goalie)) & (df['target'] == 1)].reset_index(drop=True)
                     
    expectedGoals = goalieDF['goalProb'].sum()/baseDict[goalie]['games']
    allowedGoals = allowedDF['target'].sum()/baseDict[goalie]['games']
                     
    ax.imshow(img,extent=(expectedGoals-0.05,expectedGoals+0.05,allowedGoals-0.05,allowedGoals+0.05),alpha=0.25)
    ax.set_xlim([avgExp-0.75,avgExp+0.75])
    ax.set_xlabel('Expected Goals Against Average')
    ax.set_ylim([avgGAA-0.75,avgGAA+0.75])
    ax.set_ylabel('Goals Against Average')

    fig2,ax2 = plt.subplots(figsize=(15,9))
    ax2.imshow(img,extent=(expectedGoals-0.1,expectedGoals+0.1,allowedGoals-0.1,allowedGoals+0.1))
    ax2.set_xlim([avgExp-0.75,avgExp+0.75])
    ax2.set_ylim([avgGAA-0.75,avgGAA+0.75])
    ax2.set_xlabel('Expected Goals Against Average')
    ax2.set_ylabel('Goals Against Average')
    fig2.tight_layout()
    fig2.savefig(f'./static/images/{goalie}',ax=ax2,dpi=100,transparent=True)
    plt.close(fig2)

fig.tight_layout()             
fig.savefig('./static/images/allTeams.png',ax=ax,dpi=100)

