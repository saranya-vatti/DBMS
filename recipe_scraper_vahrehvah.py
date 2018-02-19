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

datafilename = "G:\\Courses\\Spring 18\\DBMS\\dbms-repo\\DBMS\\data\\data_vahrehvah.csv"
ingredientfilename = "G:\\Courses\\Spring 18\\DBMS\\dbms-repo\\DBMS\\data\\ingr.csv"
sitemapurl="https://www.vahrehvah.com/allrecipes"
ingrDict=dict()
recipeSet=set()
LOG_LEVELS = {
    "DEBUG" : 100,
    "INFO" : 200,
    "ERROR" : 300,
    "NONE" : 400
}
LOGLVL=LOG_LEVELS["DEBUG"]

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

try:
    datafile=open(datafilename)
    csvreader = csv.DictReader(datafile)
    for r in csvreader:
        recipeSet.add(r["name"])
    datafile.close()
except Exception as e:
    log_error(e, "Error in reading datafile")

try:
    ingredientfile=open(ingredientfilename)
    csvreader1 = csv.DictReader(ingredientfile)
    for r in csvreader1:
        ingrDict[r["name"]] = r["id"]
        ingrCounter=int(r["id"])
    ingredientfile.close()
except Exception as e:
    log_error(e, "Error in reading ingredientfile")

try:
    datafile=open(datafilename, 'a', newline='')
    csvwriter = csv.writer(datafile)
except Exception as e:
    log_error(e, "Error in creating datafile")

try:
    ingredientfile=open(ingredientfilename, 'a', newline='')
    csvwriter2 = csv.writer(ingredientfile)
except Exception as e:
    log_error(e, "Error in creating ingredientfile")

def main():
    req = urllib2.Request(sitemapurl, headers={"User-Agent" : "Magic Browser"})
    response = urllib2.urlopen(req)
    soup = BeautifulSoup(response.read(), "html.parser")
    #aArr=soup.find_all("a", href=True)

    #for aitem in aArr:
        #href=aitem['href']
        #if(href.startswith("https://www.vahrehvah.com/")):
            #parseRecipePage(url)
    parseRecipePage("https://www.vahrehvah.com/maddur-vada-air-fryer")
    cleanup()
       
def parseRecipePage(url):
    row=list()
    try:
        req = urllib2.Request(url, headers={"User-Agent" : "Magic Browser"})
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response.read(), "html.parser")
        
        name=soup.select("h3[class='non-printable']")[0].get_text()
        if name in recipeSet:
            return
        log_debug("Name = " + name)
        row.append(name)

        row.append(url)

        try:
            desc=soup.find_all(class_="preparation_p2")[0].get_text().replace("\"\"", "\"").strip().replace("\r","").replace("\n\n","\n").replace("\t"," ").replace("  "," ")
            log_debug("desc = " + desc)
            row.append(desc)
        except Exception as e:
            log_error(e, "No description for " + url)
            row.append("NULL")

        try:
            pElemArr = soup.select("div[class='col-md-6 col-lg-6 col-sm-6 col-xs-6'] p")
            for pElem in pElemArr:
                text = pElem.get_text().strip()
                if text.startswith("Prep time : "):
                    prepTime = text.replace("Prep time :","").strip()
                    row.append(prepTime)
                elif text.startswith("Cook time :"):
                    cookTime = text.replace("Cook time :","").strip()
                    row.append(cookTime)
                elif text.startswith("Total time :"):
                    totalTime = text.replace("Total time :","").strip()
                    row.append(totalTime)
                elif text.startswith("Author :"):
                    chef=text.replace("Author :","").strip()
                    row.append(chef)
        except Exception as e:
            log_error(e, "Error getting prepTime, cookTime, totalTime, chef for " + url)

        if chef:
            row.append(chef)
            log_debug("chef = " + chef)
        if prepTime:
            row.append(prepTime)
            log_debug("prepTime = " + prepTime)
        if cookTime:
            row.append(cookTime)
            log_debug("cookTime = " + cookTime)
        if totalTime:
            row.append(totalTime)
            log_debug("totalTime = " + totalTime)

        ingrElemArr=soup.select("td")
        global ingrCounter
        global csvwriter2
        global ingrDict
        ingredients=list()
        for ingrElem in ingrElemArr:
            try:
                ingr=ingrElem.get_text()
                if ingr.startswith("• "):
                    ingr=ingr.replace("• ","")
                    if ingr.endswith("."):
                        ingr=ingr[:-1]
                    if ingr:
                        if ingr not in ingrDict:
                            ingrCounter+=1
                            ingrDict.update({ingr:ingrCounter}) # maintain a dict to make sure ingr are unique across multiple recipes
                            tmplist=list()
                            tmplist.append(ingrCounter) # maintain a list to add to the next row in the ingredients csv file
                            tmplist.append(ingr)
                            #csvwriter2.writerow(tmplist) # write to the next row in the ingredients csv file
                        ingredients.append(ingrDict[ingr]) # maintain a list to add comma separated values to the recipe's "ingredients" column
                        log_debug("Mapping is : " + ingr + ", " + ingrDict[ingr])
            except Exception as e:
                log_error(e, "Error trying to parse ingredient: " + ingr)
        ingredientsString = ', '.join(str(x) for x in ingredients)
        log_debug("ingredients = " + ingredientsString)
        row.append(ingredientsString)
        
        instructions=soup.select("script[type='application/ld+json']")[0].get_text()
        data=json.loads(json_text)
        log_debug("instructions = " + instructions)
        row.append(instructions)

        try:
            rating=5 - len(soup.select("[class='glyphicon glyphicon-star-empty']"))
            log_debug("rating = " + rating)
            row.append(rating)
        except Exception as e:
            log_error(e, "No rating for " + url)
            row.append("NULL")

        try:             
            num_of_reviews=soup.find("span", id="liveratng").get_text().strip()
            log_debug("num_of_reviews = " + num_of_reviews)
            row.append(num_of_reviews)
        except Exception as e:
            log_error(e, "No num_of_reviews for " + url)
            row.append("NULL")

        try:  
            calories=soup.select("[class='glyphicon glyphicon-stats']").get_text().strip().replace(" Cals", "")
            log_debug("calories = " + calories)
            row.append(calories)
        except Exception as e:
            log_error(e, "No calories for " + url)
            row.append("NULL")

        try:
            servings=soup.select("[class='glyphicon glyphicon-star-empty']").get_text().strip()
            log_debug("servings = " + servings)
            row.append(servings)
        except Exception as e:
            log_error(e, "No servings for " + url)
            row.append("NULL")

        fatContent="NULL"
        row.append(fatContent)

        carbohydrateContent="NULL"
        row.append(carbohydrateContent)

        proteinContent="NULL"
        row.append(proteinContent)

        cholesterolContent="NULL"
        row.append(cholesterolContent)

        sodiumContent="NULL"
        row.append(sodiumContent)
            
    except Exception as e:
        log_error(e, "parseRecipePage: " + url)
    global csvwriter

    try:
        #csvwriter.writerow(row)
        print(row)
        print("Successfully added recipe for " + name)
    except Exception as e:
        log_error(e, "Error while trying to write "+ row + " to file")

def cleanup():
    global datafile
    global ingredientfile
    datafile.close()
    ingredientfile.close()
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        cleanup()
