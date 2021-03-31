from selenium import webdriver
from seleniumrequests import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import sys
from bs4 import BeautifulSoup

#LOGIN
#Uses login.txt file to enter FFS members area
login_file = open("login.txt", "r")
details = login_file.readlines()
payload = {"username" : details[0].strip(), "password" : details[1].strip()}
driver = Chrome()
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
#Use beautiful soup to scrape data from private stats page, create csv
page_source = driver.page_source
soup = BeautifulSoup(page_source, "lxml")
column_range = [i for i in range(0,5)]
heading = "Team,G,GC,xGC,xG"
fileName = "gw_data\\gw_"+sys.argv[1]
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