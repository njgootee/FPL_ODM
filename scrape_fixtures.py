from selenium import webdriver
from seleniumrequests import Chrome
from bs4 import BeautifulSoup
import sys

#LOGIN
#Uses login.txt file to enter FFS members area
login_file = open("login.txt", "r")
details = login_file.readlines()
payload = {"username" : details[0].strip(), "password" : details[1].strip()}
driver = Chrome()
response = driver.request('POST', 'https://members.fantasyfootballscout.co.uk/', data = payload)

#LOAD DF
#Opens matches page in members area
driver.get('https://members.fantasyfootballscout.co.uk/matches/')

#SCRAPE
#Use beautiful soup to scrape data from matches page, create csv
page_source = driver.page_source
soup = BeautifulSoup(page_source, "lxml")
column_range = [i for i in range(0,3)]
heading = "GW,Home,Score,Away"
fileName = "fixtures\\2021.csv"
#Latest completed gw given in sys arg
gw=int(sys.argv[1])
tables = soup.find_all('table')
file_name = open(fileName, 'w')
file_name.write(heading)
#iterates through rows, columns, scrapes data in csv format
for table in tables:
    for row in table.find_all('tr'):
        currentCopyLocation = 0
        columnIndex = 0
        columns = row.find_all('td')
        for column in columns:
            if(currentCopyLocation > len(column_range)):
                break
            if columnIndex == 0:
                file_name.write(str(gw)+",")
                file_name.write(column.get_text().strip()+",")
                currentCopyLocation+=1
            elif( columnIndex == column_range[currentCopyLocation]):
                if(currentCopyLocation == len(column_range)-1):
                    file_name.write(column.get_text().strip())
                else:
                    file_name.write("".join(column.get_text().split())+",")
                currentCopyLocation+=1
            columnIndex+=1
        file_name.write("\n")
    gw-=1

#Close file and driver
file_name.close()
driver.quit()