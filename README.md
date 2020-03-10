# Goalie Analysis

### Description
Hockey goalies are often measured by statistics such as Goals Against Average (goals allowed per 60 minutes played) and Save Percentage (saves divided by total shots faced). These stats have some diagnostic ability regarding the goalie's skill, but they do not take into account the difficulty of the shots faced. Therefore, it's plausible that a goalie, despite worse GAA and SV%, may be playing with more skill than a goalie with better conventional statistics. For instance, the former goalie may be facing dramatically more difficult shots if playing on a team with poor defense. This would bias the goalie's GAA and SV% higher. Therefore, determining goalie performance should be more complex than a simple analysis of GAA, etc.

With this motivation in mind, an Expected Goals model was developed to determine the probability of a goal, given an "average" goalie for the 2019-20 season, for every shot taken.

### The Model
A gradient boosting model, calibrated to produce probabilities, was selected after cross-validation analysis suggested relatively robust performance against a test dataset. For more information on model development, see the following: [Model Development](https://github.com/jpicca/goalieAnalysis/blob/master/modelDevelopment.ipynb)

### Live Version
Once per week, a shell script is run to gather the latest game data and update the model. This model is then used to predict goal probabilities for all shots taken so far this season. Thereafter, total expected and allowed goals are calculated for every goalie that has played in the league during the 2019-20 season.

These numbers are used to make two visualizations: 
- A grid of 5 ft x 5 ft spacing that displays a goalie's relative strengths/weaknesses in terms of shot location.
- A scatterplot that illustrates a goalie's performance vs expected and compares it to other goalies in the league.

### Front End
The front-end is built on a python-flask framework delivered by an AWS EC2 instance running an Apache server with wsgi enabled. D3.js is utilized to update the grid, while the scatterplot is created from matplotlib.

Begin to type a goalie's name in the input form and then choose a goalie from the returned list. Then see how your favorite goalie is actually doing this season!

[Live Version](http://www.joeypicca.info/FlaskApp/goalieAnalysis/)

![Front End Example](https://github.com/jpicca/goalieAnalysis/blob/master/screenshot.jpg)
