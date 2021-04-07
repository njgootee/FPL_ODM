import pandas as pd
import numpy as np
import sys

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
odm_model(CURR_COMPL_GW)