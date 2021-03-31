# Offense-Defense Model Applied to EPL
This repository applies the 'Offense-Defense Model' to the English Premier League 2020/2021 season. The Offense-Defense Model is described in ["Offense-Defense Approach to Ranking
Team Sports"](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.141.5694&rep=rep1&type=pdf) (Govan, Langville, Meyer). 
The objective of this application is to create weekly ratings of EPL teams' offensive and defensive form. 
These ratings could be useful to compare to subjective opinions of EPL teams, make predictions on game outcomes and inform Fantasy Premier League players on teams to invest in and avoid.

## Data
ODM was originally applied to American football and basketball games, which are typically high scoring. 
In contrast, football (soccer) games typically feature few goals and frequently a team will score 0. This is problematic in the context of applying the ODM model to football for two reasons:
1. A team scoring 0 in a game is equivalent to the team not playing (see data matrix *A* in ODM)
2. The uncommon and discreet nature of goals in a game makes them a poor indicator of offensive/defensive performance (luck and fleeting moments of brilliance/ineptitude can have a significant influence)

### Solution: xG
Expected goals, or xG is a statistical measurement used to more accurately evaluate football performance. 
The xG of a shot is representative of the probability of the shot leading to a goal, and is based on historical data of very similar shots. 
xG of every scoring opportunity can be summized to provide the overall xG scoreline of a game, as illustrated by the example below:
Measure | Liverpool FC | Leeds United
--------|--------------|-------------
Goals | 4 | 3
xG | 3.15 | 0.27

The validity of xG as an indicator for football performance is somewhat contested, however it is widely supported by those invested in statistical and objective football analysis.

### Source disclaimer
xG and other data for this application was sourced from the members area of [Fantasy Football Scout](https://www.fantasyfootballscout.co.uk/), which requires a paid subscription to access.
This repository **does not** reproduce or provide free access to this paid content. To run/modify the provided scripts and pull data from FFS, a user is required to input their paid account details.

## Run Instructions
Dependent on python 3.8, selenium, Beautiful Soup 4, Pandas and NumPy
1. Pull data from FFS
    1. Input login details to *login.txt*
    2. Run scrape_fixtures.py with following CLA:
    ```
    python scrape_fixtures.py <last_completed_gw_number>
    ```
    3. In scrape.py edit private stats table link to personal stats table with columns: Team, G, GC, xGC, xG and filtered by arbitrary gameweek.
    4. Run scrape.py for each completed gameweek with following CLA:
    ```
    python scrape.py <gw_number>
    ```
 2. Clean data, perform odm model, generate weekly ratings tables (offense_scores.csv and defense_scores.csv)
    1. Run odm.py with following CLA (may take few minutes):
    ```
    python odm.py <last_completed_gw_number>
    ```
 
