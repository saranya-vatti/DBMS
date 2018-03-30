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
import math

datafilenameInput = "G:\\Courses\\Spring 18\\DBMS\\dbms-repo\\DBMS\\data\\data.csv"
datafilenameOutput = "G:\\Courses\\Spring 18\\DBMS\\dbms-repo\\DBMS\\data\\data_allrecipes.csv"
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

datafileInput=open(datafilenameInput)
datafileOutput=open(datafilenameOutput, 'a', newline='')
def main():
    try:
        csvreader = csv.DictReader(datafileInput)
        csvwriter = csv.writer(datafileOutput)
        for r in csvreader:
            row=list()
            row.append(r["name"])
            row.append(r["link"])
            row.append(r["desc"])
            row.append(r["chef"])
            row.append(r["prepTime"])
            row.append(r["cooktime"])
            row.append(r["total"])
            row.append(r["ingredients"])
            row.append(r["instructions"])
            row.append(r["rating"])
            row.append(r["num_of_reviews"])
            row.append(r["calories"])
            row.append(r["servings"])
            row.append(r["fat"])
            row.append(r["carb"])
            row.append(r["protein"])
            row.append(r["cholesterol"])
            row.append(r["sodium"])
            href=r["link"]
            req = urllib2.Request(href, headers={"User-Agent" : "Magic Browser"})
            response = urllib2.urlopen(req)
            soup = BeautifulSoup(response.read(), "html.parser")

            try:
                imageLink=soup.select("meta[property='og:image']")[0]['content'].strip()
                log_debug("imageLink = " + imageLink)
                row.append(imageLink)
            except Exception as e:
                log_info("No imageLink for " + r["name"])
                row.append("NULL")

            try:
                metaArr=soup.select("meta[itemprop='recipeCategory']")
                keywordsArr=[]
                for metaElem in metaArr:
                    keywordsArr.append(metaElem['content'].strip())
                keywords=", ".join(keywordsArr)
                log_debug("keywords = " + keywords)
                row.append(keywords)
            except Exception as e:
                log_info("No keywords for " + href)
                row.append("NULL")
                
            
            try:
                csvwriter.writerow(row)
                log_info("Successfully added recipe for " + r["name"])
            except Exception as e:
                log_error(e, "Error while trying to write "+ (row) + " to file")

        datafileInput.close()
        datafileOutput.close()
    except Exception as e:
        log_error(e, "Error in reading datafile")

def cleanup():
    global datafileInput
    global datafileOutput
    datafileInput.close()
    datafileOutput.close()
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        cleanup()
