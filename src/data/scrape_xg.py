from selenium import webdriver
from seleniumrequests import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import sys
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

#LOGIN
#Uses login.txt file to enter FFS members area
login_file = open("login.txt", "r")
details = login_file.readlines()
payload = {"username" : details[0].strip(), "password" : details[1].strip()}
driver = Chrome(ChromeDriverManager().install())
response = driver.request('POST', 'https://members.fantasyfootballscout.co.uk/', data = payload)

#LOAD DF
#Opens private stats table webpage on given url. Table columns: Team, G, GC, xGC, xG. Selects values for gameweek given in sys arg
driver.get('https://members.fantasyfootballscout.co.uk/my-stats-tables/view/48423/')
try:
    element = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME,'fgameweek')))
finally:
    select_gw = Select(element)
    select_gw.select_by_value(sys.argv[1])
    driver.find_element_by_name('filter').click()

#SCRAPE DATA
#Use beautiful soup to scrape data from private stats page, create raw csv
page_source = driver.page_source
soup = BeautifulSoup(page_source, "lxml")
column_range = [i for i in range(0,5)]
heading = "Team,G,GC,xGC,xG"
CURR_GW = sys.argv[1]
fileName = "../../data/raw/gw/gw_"+str(CURR_GW)
table = soup.find_all('table')[0]
file_name = open(fileName, 'w')
file_name.write(heading)
#iterates through rows, columns, scrapes data in csv format
for row in table.find_all('tr'):
    currentCopyLocation = 0
    columnIndex = 0
    columns = row.find_all('td')
    for column in columns:
        if(currentCopyLocation > len(column_range)):
            break
        if columnIndex == 0:
            file_name.write(column.get_text().strip().split("\n")[0].strip()+",")
            currentCopyLocation+=1
        elif( columnIndex == column_range[currentCopyLocation]):
            if(currentCopyLocation == len(column_range)-1):
                file_name.write(column.get_text().strip())
            else:
                file_name.write(column.get_text().strip()+",")
            currentCopyLocation+=1
        columnIndex+=1
    file_name.write("\n")

#Close file and driver
file_name.close()
driver.quit()

#CLEAN GW DATA
fixtures = pd.read_csv('../../data/interim/2021.csv')
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

#Read in raw data as pandas dataframe
dgw = []
gw=pd.read_csv("../../data/raw/gw/gw_"+str(CURR_GW))
gw_fixtures = fixtures.loc[fixtures["GW"]==int(CURR_GW)]

#Check for presence of DGW, add DGW teams + week to print array. Drop dgw teams from fixtures, ammend data manually.
team_list = pd.DataFrame(np.concatenate([gw_fixtures["Home"].values,gw_fixtures["Away"].values]))
dgw.append((team_list[team_list.duplicated()].values+str(CURR_GW)).tolist())
gw_fixtures = gw_fixtures.drop_duplicates("Home")
gw_fixtures = gw_fixtures.drop_duplicates("Away")

#Map opposition team name, opposition team id, home team id to gw
gw["Opp"]= (gw["Team"].map(gw_fixtures.set_index("Home")["Away"]).fillna("")+gw["Team"].map(gw_fixtures.set_index("Away")["Home"]).fillna(""))
gw["Team_id"]=gw["Team"].map(id_dict)
gw["Opp_id"]=gw["Opp"].map(id_dict)

#Save gw
gw.to_csv("../../data/interim/gw_clean/gw_clean_"+str(CURR_GW)+".csv", index=False)
#Print dgw items to notify team+week that require manual editing
if len(dgw)>0:
    print("Double gameweeks:", dgw)