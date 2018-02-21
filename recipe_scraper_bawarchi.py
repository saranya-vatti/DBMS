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

datafilename = "G:\\Courses\\Spring 18\\DBMS\\dbms-repo\\DBMS\\data\\data_bawarchi.csv"
ingredientfilename = "G:\\Courses\\Spring 18\\DBMS\\dbms-repo\\DBMS\\data\\ingr.csv"
ingrDict=dict()
recipeSet=set()
recipeUrlSet=set()
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
        recipeUrlSet.add(r["link"])
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
    for index in range(1, 1734):
        try:
            sitemapurl="http://www.bawarchi.com/recipe/" + str(index)
            req = urllib2.Request(sitemapurl, headers={"User-Agent" : "Magic Browser"})
            response = urllib2.urlopen(req)
            soup = BeautifulSoup(response.read(), "html.parser")
            aArr=soup.select("div[itemprop='Recipe'] a")
            recipe_set=set()
            for aElem in aArr:
                href=aElem['href']
                if href not in recipeUrlSet:
                        recipe_set.add(href)
        except Exception as e:
            log_error(e, "No recipes under " + str(index))
    for url in recipe_set:
        parseRecipePage(url)
    cleanup()
       
def parseRecipePage(url):
    row=list()
    try:
        req = urllib2.Request(url, headers={"User-Agent" : "Magic Browser"})
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response.read(), "html.parser")
        
        name=soup.select("meta[itemprop='name']")[0]['content']
        if name in recipeSet:
            return
        row.append(name)

        row.append(url)

        try:
            desc=soup.select("meta[name='description']")[0]['content'].replace("\"\"", "\"").replace("Find the complete instructions on Bawarchi.com","").strip()
            log_debug("desc = " + desc)
            row.append(desc)
        except Exception as e:
            log_info("No description for " + name)
            row.append("NULL")

        try:
            chef=soup.select("meta[name='author']")[0]['content']
            log_debug("chef = " + chef)
            row.append(chef)
        except Exception as e:
            log_info("No chef name found for " + name)
            row.append("NULL")

        try:
            prepTime=soup.select("meta[itemprop='prepTime']")[0]['content'].split("PT")[1]
            log_debug("prepTime = " + prepTime)
            row.append(prepTime)
        except Exception as e:
            log_info("No prepTime for " + name)
            row.append("NULL")

        try:
            cookTime=soup.select("meta[itemprop='cookTime']")[0]['content'].split("PT")[1]
            log_debug("cookTime = " + cookTime)
            row.append(cookTime)
        except Exception as e:
            log_info("No cookTime for " + name)
            row.append("NULL")

        try:    
            totalTime=soup.select("div[class='col-md-3 col-sm-4']")[0].get_text().replace("Total Time:","").strip()
            log_debug("totalTime = " + totalTime)
            row.append(totalTime)
        except Exception as e:
            log_info("No totalTime for " + name)
            row.append("NULL")

        ingrElemArr=soup.select("li[itemprop='ingredients']")
        global ingrCounter
        global csvwriter2
        global ingrDict
        ingredients=list()
        for ingrElem in ingrElemArr:
            ingr=ingrElem.get_text().strip()
            try:
                if ingr not in ingrDict:
                    ingrCounter+=1
                    ingrDict.update({ingr:ingrCounter}) # maintain a dict to make sure ingr are unique across multiple recipes
                    tmplist=list()
                    tmplist.append(ingrCounter) # maintain a list to add to the next row in the ingredients csv file
                    tmplist.append(ingr)
                    csvwriter2.writerow(tmplist) # write to the next row in the ingredients csv file
                ingredients.append(ingrDict[ingr]) # maintain a list to add comma separated values to the recipe's "ingredients" column
            except Exception as e:
                log_error(e, "Error trying to parse ingredient: " + ingr)
        ingrStr=', '.join(str(x) for x in ingredients)
        log_debug("ingrStr = " + ingrStr)
        row.append(ingrStr)

        try:
            instrArr=soup.select("meta[itemprop='recipeInstructions']")[0]['content'].split("., ")
            instructions=""
            for instr in instrArr:
                instructions=instructions+instr.strip() + "\n"
            log_debug("instructions = " + instructions)
            row.append(instructions.strip())
        except Exception as e:
            log_error(e, "No instructions for " + name)
            row.append("NULL")

        try:
            rating=soup.select("meta[itemprop='ratingValue']")[0]['content']
            log_debug("rating = " + rating)
            row.append(rating)
        except Exception as e:
            log_info("No rating for " + name)
            row.append("NULL")

        try:
            num_of_reviews=soup.select("meta[itemprop='ratingCount']")[0]['content']
            log_debug("num_of_reviews = " + num_of_reviews)
            row.append(num_of_reviews)
        except Exception as e:
            log_info("No num_of_reviews for " + name)
            row.append("NULL")

        try:  
            calories=soup.select("span[itemprop='calories']")[0].get_text().replace("calories,", "").strip()
            log_debug("calories = " + calories)
            row.append(calories)
        except Exception as e:
            log_info("No calories for " + name)
            row.append("NULL")

        try:
            servings=soup.select("meta[itemprop='recipeYield']")[0]['content'].strip()
            log_debug("servings = " + servings)
            row.append(servings)
        except Exception as e:
            log_info("No servings for " + name)
            row.append("NULL")

        try:
            fatContent=soup.select("span[itemprop='fatContent']")[0].get_text().replace("fat", "").strip()
            log_debug("fatContent = " + fatContent)
            row.append(fatContent)
        except Exception as e:
            log_info("No fatContent for " + name)
            row.append("NULL")

        try:
            carbohydrateContent=soup.select("span[itemprop='carbohydrateContent']")[0].get_text().strip()
            log_debug("carbohydrateContent = " + carbohydrateContent)
            row.append(carbohydrateContent)
        except Exception as e:
            log_info("No carbohydrateContent for " + name)
            row.append("NULL")

        try:
            proteinContent=soup.select("span[itemprop='proteinContent']")[0].get_text().strip()
            log_debug("proteinContent = " + proteinContent)
            row.append(proteinContent)
        except Exception as e:
            log_info("No proteinContent for " + name)
            row.append("NULL")

        try:
            cholesterolContent=soup.select("span[itemprop='cholesterolContent']")[0].get_text().strip()
            log_debug("cholesterolContent = " + cholesterolContent)
            row.append(cholesterolContent)
        except Exception as e:
            log_info("No cholesterolContent for " + name)
            row.append("NULL")

        try:
            sodiumContent=soup.select("span[itemprop='sodiumContent']")[0].get_text().strip()
            log_debug("sodiumContent = " + sodiumContent)
            row.append(sodiumContent)
        except Exception as e:
            log_info("No sodiumContent for " + name)
            row.append("NULL")

        try:
            image=soup.select("meta[property='og:image']")[0]['content']
            log_debug("image = " + image)
            row.append(image)
        except Exception as e:
            log_info("No image for " + name)
            row.append("NULL")

        try:
            keywords=soup.select("meta[name='keywords']")[0]['content']
            log_debug("keywords = " + keywords)
            row.append(keywords)
        except Exception as e:
            log_info("No keywords for " + name)
            row.append("NULL")
            
    except Exception as e:
        log_error(e, "parseRecipePage: " + url)
    global csvwriter

    try:
        csvwriter.writerow(row)
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
