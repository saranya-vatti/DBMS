try:
    import urllib.request as urllib2
except:
    import urllib2
import bs4
from bs4 import BeautifulSoup
import re
import json
import os
import time
import urllib
import shutil
import csv

datafile = "G:\\Courses\\Spring 18\DBMS\\Assignments\\data_vahrehvah.csv"

LOG_LEVELS = {
    "DEBUG" : 100,
    "INFO" : 200,
    "ERROR" : 300,
    "NONE" : 400
}
LOGLVL=LOG_LEVELS["ERROR"]

def log_error(exception, location):
    if(LOGLVL <= LOG_LEVELS["ERROR"]):
        print("Exception encountered : " + str(type(exception)) + " in " + location)
        print("Exception : " + str(exception))

def log_info(string):
    if(LOGLVL <= LOG_LEVELS["INFO"]):
        print(string)

def log_debug(string):
    if(LOGLVL <= LOG_LEVELS["DEBUG"]):
        print(string)
       
def parseRecipePage(url):
    row=list()
    try:
        req = urllib2.Request(url, headers={"User-Agent" : "Magic Browser"})
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response.read(), "html.parser")
        name=soup.select("h3[class='non-printable']")[0].get_text()
        row.append(name)
        desc=soup.find_all(class_="preparation_p2")[0].get_text()
        row.append(desc.replace("\"\"", "\"").strip())
        chef="Vahchef"
        row.append(chef)
        prepTime=soup.select("td")[2].get_text().strip().replace("Prep time","")
        row.append(prepTime)
        cookTime=soup.select("td")[3].get_text().strip().replace("Cook time","")
        row.append(cookTime)
        total=soup.select("td")[4].get_text().strip().replace("Total time","")
        row.append(total)
        instructions=soup.select("[itemprop='recipeInstructions']")[0].get_text().strip()
        row.append(instructions)
        row.append(url)
        rating=soup.select("[class='rating-stars']")[0]['data-ratingstars']
        row.append(rating)
        num_of_reviews=soup.find_all(class_="review-count")[0].get_text()
        row.append(num_of_reviews.replace(" reviews", ""))
        calories=soup.find_all(class_="calorie-count")[0].get_text()
        row.append(calories.replace(" cals", ""))
        ### WHY THE HELL IS THIS NOT WORKING
        servings=soup.find_all(class_="servings-count")[0].get_text().replace(" servings", "").strip()
        row.append(servings)
        ### ???
        fatContent=soup.select("span[itemprop='fatContent']")[0].get_text()
        row.append(fatContent)
        carbohydrateContent=soup.select("span[itemprop='carbohydrateContent']")[0].get_text()
        row.append(carbohydrateContent)
        proteinContent=soup.select("span[itemprop='proteinContent']")[0].get_text()
        row.append(proteinContent)
        cholesterolContent=soup.select("span[itemprop='cholesterolContent']")[0].get_text()
        row.append(cholesterolContent)
        sodiumContent=soup.select("span[itemprop='sodiumContent']")[0].get_text()
        row.append(sodiumContent)
    except Exception as e:
        log_error(e, "parseRecipePage: " + url)
    return row

i=0
sitemapurl="https://www.vahrehvah.com/allrecipes"
req = urllib2.Request(sitemapurl, headers={"User-Agent" : "Magic Browser"})
response = urllib2.urlopen(req)
soup = BeautifulSoup(response.read(), "html.parser")
aArr=soup.find_all("a", href=True)
try:
    csvwriter = csv.writer(open(datafile, 'w'), delimiter=',')
    csvwriter.writerow(['name','desc','chef','prepTime','cooktime','total','instructions','link','rating','num_of_reviews','calories','servings','fat','carb','protein','cholesterol','sodium'])
except Exception as e:
    log_error(e, "createFile")
for aitem in aArr:
    href=aitem['href']
    if(href.startswith("https://www.vahrehvah.com/")):
        try:
            row=parseRecipePage(href)
            csvwriter.writerow(row)
            print("Successfully added recipe for " + row[0])
        except Exception as e:
            log_error(e, "Error while trying to write "+ row + " to file")
file.close()
    
