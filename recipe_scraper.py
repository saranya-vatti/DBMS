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

datafile = "G:\\Courses\\Spring 18\DBMS\\Assignments\\data.csv"

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

def appendToFile(file, content):
    try:
        print("Writing : " + content + " to file")
        file.write(content.encode('utf8').replace(b'\n',b'\r\n'))
    except Exception as e:
        log_error(e, "appendToFile")
        
def parseRecipePage(url):
    row=list()
    try:
        req = urllib2.Request(url, headers={"User-Agent" : "Magic Browser"})
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response.read(), "html.parser")
        recipename=soup.find_all(class_="recipe-summary__h1")[0].get_text()
        row.append(recipename )
        chef=soup.find_all(class_="submitter__name")[0].get_text()
        row.append(chef)
        prep=soup.select("time[itemprop='prepTime']")[0].get_text()
        row.append(prep)
        cookTime=soup.select("time[itemprop='cookTime']")[0].get_text()
        row.append(cookTime)
        total=soup.select("time[itemprop='totalTime']")[0].get_text()
        row.append(total)
        instructions=soup.select("[itemprop='recipeInstructions']")[0].get_text().strip()
        row.append(instructions)
        row.append(url)
        rating=soup.select("[class='rating-stars']")[0]['data-ratingstars']
        row.append(rating)
        calories=soup.find_all(class_="calorie-count")[0].get_text()
        row.append(calories)
    except Exception as e:
        log_error(e, "parseRecipePage: " + url)
    return row

i=0
sitemapurl="http://dish.allrecipes.com/faq-sitemap/"
req = urllib2.Request(sitemapurl, headers={"User-Agent" : "Magic Browser"})
response = urllib2.urlopen(req)
soup = BeautifulSoup(response.read(), "html.parser")
aArr=soup.find_all("a", href=True)
try:
    csvwriter = csv.writer(open(datafile, 'wb'))
    csvwriter.writerow(['name','chef','prep','cooktime','total','instructions','link','rating','calories'])
except Exception as e:
    log_error(e, "createFile")
for aitem in aArr:
    href=aitem['href']
    if(href.startswith("http://allrecipes.com/recipes/")):
        req = urllib2.Request(href, headers={"User-Agent" : "Magic Browser"})
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response.read(), "html.parser")
        recipeArr=soup.select("#fixedGridSection a[href]")
        recipe_set=set()
        for rec in recipeArr:
            if "/recipe/" in rec['href']:
                if rec['href'].startswith("/"):
                    href="http://allrecipes.com" + rec['href']
                else:
                    href=rec['href']
                recipe_set.add(href)
        for url in recipe_set:
            row=parseRecipePage(url)
            print("Appending row " + ''.join(row) + " to file")
            csvwriter.writerow(row)
file.close()
    
