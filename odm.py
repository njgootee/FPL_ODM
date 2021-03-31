import pandas as pd
import numpy as np
import sys

# FUNCTION TO CLEAN FIXTURES DATA
def clean_fixtures(fixtures):
    team_dict = {
        "Leeds United": "LEE",
        "Southampton" : "SOU",
        "Brighton and Hove Albion" : "BHA",
        "Crystal Palace" : "CRY",
        "Manchester United" : "MUN",
        "Arsenal" : "ARS",
        "Newcastle United" : "NEW",
        "Manchester City" : "MCI",
        "Aston Villa" : "AVL",
        "Leicester City" : "LEI",
        "West Ham United" : "WHU",
        "Tottenham Hotspur" : "TOT",
        "Fulham" : "FUL",
        "Sheffield United" : "SHU",
        "Liverpool" : "LIV",
        "Everton" : "EVE",
        "Burnley" : "BUR",
        "West Bromwich Albion" : "WBA",
        "Chelsea" : "CHE",
        "Wolverhampton Wanderers" : "WOL"
    }
    #Replace home, away team names with 3 truncated names, strip score column to x-y format 
    fixtures["Home"].replace(team_dict, inplace=True)
    fixtures["Away"].replace(team_dict, inplace=True)
    fixtures["Score"]=fixtures["Score"].str[:3]
    #Save/replace
    fixtures.to_csv('fixtures/2021.csv', index = False)

#FUNCTION TO CLEAN GW DATA
def clean_gw(fixtures):
    id_dict = {
        "ARS" : 0,
        "AVL" : 1,
        "BHA" : 2,
        "BUR" : 3,
        "CHE" : 4,
        "CRY" : 5,
        "EVE" : 6,
        "FUL" : 7,
        "LEE" : 8,
        "LEI" : 9,
        "LIV" : 10,
        "MCI" : 11,
        "MUN" : 12,
        "NEW" : 13,
        "SHU" : 14,
        "SOU" : 15,
        "TOT" : 16,
        "WBA" : 17,
        "WHU" : 18,
        "WOL" : 19
    }

    dgw = []
    #iterate through gameweeks
    for i in range(1,26):
        gw=pd.read_csv("gw_data/gw_"+str(i))
        gw_fixtures = fixtures.loc[fixtures["GW"]==i]

        #Check for presence of DGW, add DGW teams + week to print array. Drop dgw teams from fixtures, ammend data manually.
        if(len(gw_fixtures)>10):
            team_list = pd.DataFrame(np.concatenate([gw_fixtures["Home"].values,gw_fixtures["Away"].values]))
            dgw.append((team_list[team_list.duplicated()].values+str(i)).tolist())
            gw_fixtures = gw_fixtures.drop_duplicates("Home")
            gw_fixtures = gw_fixtures.drop_duplicates("Away")

        #Map opposition team name, opposition team id, home team id to gw
        gw["Opp"]= (gw["Team"].map(gw_fixtures.set_index("Home")["Away"]).fillna("")+gw["Team"].map(gw_fixtures.set_index("Away")["Home"]).fillna(""))
        gw["Team_id"]=gw["Team"].map(id_dict)
        gw["Opp_id"]=gw["Opp"].map(id_dict)

        #Save gw
        gw.to_csv("gw_clean/gw_clean_"+str(i)+".csv", index=False)
    #Print dgw items to notify team+week that require manual editing
    print("Double gameweeks:", dgw)

#FUNCTION TO GENERATE RANKINGS
def odm_model(COMPL_GW, GW_RANGE = 6):
    team_list=["ARS","AVL","BHA","BUR","CHE","CRY","EVE","FUL","LEE","LEI","LIV","MCI","MUN","NEW","SHU","SOU","TOT","WBA","WHU","WOL"]
    #Create offense and defense dataframes
    o_df=pd.DataFrame(columns=team_list)
    d_df=pd.DataFrame(columns=team_list)

    #Iterate through gameweeks
    for i in range(GW_RANGE+1,COMPL_GW+2):
        #Create 'A' matrix for gameweek with small perturbation to aid convergence
        A = np.zeros((20,20))+0.001
        #Support for fringe Cases (DGW/BGW that affect sample size)
        support = 0
        if i==19:
            support=-1

        #Add past GW_RANGE (+/- support) weeks xGC data to build 'A' matrix
        for j in range((i-GW_RANGE)+support,i):
            #Open gw file, create temp array size 20,20
            gw=pd.read_csv("gw_clean/gw_clean_"+str(j)+".csv")
            temp_arr = np.zeros((20,20))
            #"Score team j got vs team i" == xGC
            temp_arr[gw["Team_id"],gw["Opp_id"]]=gw["xGC"]*100
            A+=temp_arr

        #ODM MODEL: iteratively update offensive and defensive ratings to convergence
        d = np.ones((20,1))
        for k in range(100000):
            o = np.dot(A.T,(1/d))
            d = np.dot(A,(1/o))
        #Append to offense and defense dataframe
        o_df = o_df.append(pd.DataFrame(o.reshape(1,-1), columns=team_list), ignore_index=True)
        d_df = d_df.append(pd.DataFrame(d.reshape(1,-1), columns=team_list), ignore_index=True)
    
    #Add GW Column to dataframes, save to file
    o_df["GW"] = range(GW_RANGE+1,len(o_df)+GW_RANGE+1)
    d_df["GW"] = range(GW_RANGE+1,len(d_df)+GW_RANGE+1)
    o_df.to_csv('offense_scores.csv', index = False)
    d_df.to_csv('defense_scores.csv', index = False)


# Run
CURR_COMPL_GW = int(sys.argv[1])
fixtures = pd.read_csv('fixtures/2021.csv')
clean_fixtures(fixtures)
clean_gw(fixtures)
odm_model(CURR_COMPL_GW)