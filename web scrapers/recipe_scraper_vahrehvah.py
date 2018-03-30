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
    aArr=soup.find(class_="glossaryiteams").find_all("a", href=True)

    for aitem in aArr:
        href=aitem['href']
        log_debug(href)
        parseRecipePage(href)
    #parseRecipePage("https://www.vahrehvah.com/maddur-vada-air-fryer")
    cleanup()
       
def parseRecipePage(url):
    row=list()
    try:
        req = urllib2.Request(url, headers={"User-Agent" : "Magic Browser"})
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response.read(), "html.parser")

        json_text=soup.select("script[type='application/ld+json']")[0].get_text()
        data=json.loads(json_text)
        name = data['name']
        chef = data['author']['name']
        image = data['image']
        desc = data['description']
        rating = data['aggregateRating']['ratingValue']
        num_of_reviews = data['aggregateRating']['ratingCount']
        servings = data['recipeYield']
        calories = data['nutrition']['calories']
        fatContent = data['nutrition']['fatContent']
        proteinContent = data['nutrition']['proteinContent']
        cholesterolContent = data['nutrition']['cholesterolContent']
        sodiumContent = data['nutrition']['sodiumContent']
        #ingredients = data.recipeIngredient
        instructions = data['recipeInstructions'].replace("\r\n\r\n","").strip()
        
        if name in recipeSet:
            return
        log_debug("Name = " + name)
        row.append(name)

        row.append(url)

        log_debug("desc = " + desc)
        row.append(desc)

        log_debug("chef = " + chef)
        row.append(chef)

        try:
            pElemArr = soup.select("div[class='col-md-6 col-lg-6 col-sm-6 col-xs-6'] p")
            for pElem in pElemArr:
                text = pElem.get_text().strip()
                if text.startswith("Prep time : "):
                    prepTime = text.replace("Prep time :","").strip()
                elif text.startswith("Cook time :"):
                    cookTime = text.replace("Cook time :","").strip()
                elif text.startswith("Total time :"):
                    totalTime = text.replace("Total time :","").strip()
        except Exception as e:
            log_error(e, "Error getting prepTime, cookTime, totalTime, chef for " + url)

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
                            csvwriter2.writerow(tmplist) # write to the next row in the ingredients csv file
                        ingredients.append(ingrDict[ingr]) # maintain a list to add comma separated values to the recipe's "ingredients" column
                        log_debug("Mapping is : " + ingr + ", " + str(ingrDict[ingr]))
            except Exception as e:
                log_error(e, "Error trying to parse ingredient: " + ingr)
        ingredientsString = ', '.join(str(x) for x in ingredients)
        log_debug("ingredients = " + ingredientsString)
        row.append(ingredientsString)

        log_debug("instructions = " + instructions)
        row.append(instructions)

        log_debug("rating = " + str(rating))
        row.append(rating)

        log_debug("num_of_reviews = " + str(num_of_reviews))
        row.append(num_of_reviews)

        log_debug("calories = " + str(calories))
        row.append(calories)

        log_debug("servings = " + str(servings))
        row.append(servings)

        log_debug("fatContent = " + str(fatContent))
        row.append(fatContent)

        row.append("NULL")

        log_debug("proteinContent = " + str(proteinContent))
        row.append(proteinContent)

        log_debug("cholesterolContent = " + str(cholesterolContent))
        row.append(cholesterolContent)

        log_debug("sodiumContent = " + str(sodiumContent))
        row.append(sodiumContent)

        log_debug("image = " + image)
        row.append(image)
            
    except Exception as e:
        log_error(e, "parseRecipePage: " + url)
    global csvwriter

    try:
        csvwriter.writerow(row)
        print("Successfully added recipe for " + name)
    except Exception as e:
        log_error(e, "Error while trying to write "+ str(row) + " to file")

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
