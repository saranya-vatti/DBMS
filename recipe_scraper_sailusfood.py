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

datafilename = "G:\\Courses\\Spring 18\\DBMS\\dbms-repo\\DBMS\\data\\data_sailusfoos.csv"
ingredientfilename = "G:\\Courses\\Spring 18\\DBMS\\dbms-repo\\DBMS\\data\\ingr.csv"
sitemapurl="http://www.sailusfood.com/categories/all_recipes_blogged_to_date/page/"
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
    '''
    for pagenum in 1..44:
        sitemapurl + pagenum + "/"
        req = urllib2.Request(sitemapurl, headers={"User-Agent" : "Magic Browser"})
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response.read(), "html.parser")
        aArr=soup.find(class_="entry-title").find_all("a", href=True)

        for aitem in aArr:
            href=aitem['href']
            parseRecipePage(href)
    '''
    parseRecipePage("http://www.sailusfood.com/lachha-paratha-recipe/")
    cleanup()
       
def parseRecipePage(url):
    row=list()
    try:
        req = urllib2.Request(url, headers={"User-Agent" : "Magic Browser"})
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response.read(), "html.parser")

        name=soup.select("h1[itemprop='name']")[0].get_text().replace("recipe","").strip()
        if name in recipeSet:
            return
        log_debug("Name = " + name)
        row.append(name)

        row.append(url)

        desc=soup.select("div[class='entry-content'] p")[2].get_text().strip()
        log_debug("desc = " + desc)
        row.append(desc)

        chef="Sailaja Gudivada"
        log_debug("chef = " + chef)
        row.append(chef)


        prepTime=soup.select("time[itemprop='prepTime']")[0].get_text().strip()
        log_debug("prepTime = " + prepTime)
        row.append(prepTime)

        cookTime=soup.select("time[itemprop='cookTime']")[0].get_text().strip()
        log_debug("cookTime = " + cookTime)
        row.append(cookTime)

        totalTime="NULL"
        log_debug("totalTime = " + totalTime)
        row.append(totalTime)

        ingrElemArr=soup.select("span[itemprop='recipeIngredient'")
        global ingrCounter
        global csvwriter2
        global ingrDict
        ingredients=list()
        for ingrElem in ingrElemArr:
            try:
                ingr=ingrElem.get_text()
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

        stepElemArr=soup.select("span[class='step'")
        instructions=""
        for stepElem in stepElemArr:
            instructions=instructions+stepElem.text()+"\n"
        instructions=instructions.strip()
        log_debug("instructions = " + instructions)
        row.append(instructions)

        ratingElemArr=soup.select("div[class='rating-star-icon'")
        rating=0
        for ratingElem in ratingElemArr:
            if(ratingElem['style'].contains(" top left")):
                rating+=1
        log_debug("rating = " + str(rating))
        row.append(rating)

        num_of_reviews=soup.select("div[class='rating-msg'")[0].get_text().replace("Votes","").strip()
        log_debug("num_of_reviews = " + num_of_reviews)
        row.append(num_of_reviews)

        calories="NULL"
        log_debug("calories = " + str(calories))
        row.append(calories)

        servings=soup.select("span[itemprop='recipeYield']")[0].get_text().strip()
        log_debug("servings = " + str(servings))
        row.append(servings)

        fatContent="NULL"
        log_debug("fatContent = " + str(fatContent))
        row.append(fatContent)

        carbContent="NULL"
        log_debug("carbContent = " + str(carbContent))
        row.append("NULL")

        calories="NULL"
        log_debug("proteinContent = " + str(proteinContent))
        row.append(proteinContent)

        calories="NULL"
        log_debug("cholesterolContent = " + str(cholesterolContent))
        row.append(cholesterolContent)

        calories="NULL"
        log_debug("sodiumContent = " + str(sodiumContent))
        row.append(sodiumContent)

        image=soup.select("div[align='center'] a")[0]['href']
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
