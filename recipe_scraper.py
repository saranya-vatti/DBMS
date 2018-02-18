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

datafilename = "G:\\Courses\\Spring 18\\DBMS\\Assignments\\data.csv"
ingredientfilename = "G:\\Courses\\Spring 18\\DBMS\\Assignments\\ingr.csv"
sitemapurl="http://dish.allrecipes.com/faq-sitemap/"
ingrDict=dict()
ingrCounter=0
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
    datafile=open(datafilename, 'w', newline='')
    csvwriter = csv.writer(datafile)
    csvwriter.writerow(['name','desc','chef','prepTime','cooktime','total','ingredients','instructions','link','rating','num_of_reviews','calories','servings','fat','carb','protein','cholesterol','sodium'])
except Exception as e:
    log_error(e, "Error in creating datafile")

try:
    ingredientfile=open(ingredientfilename, 'w', newline='')
    csvwriter2 = csv.writer(ingredientfile)
    csvwriter2.writerow(['id','name'])
except Exception as e:
    log_error(e, "Error in creating ingredientfile")

def main():
    req = urllib2.Request(sitemapurl, headers={"User-Agent" : "Magic Browser"})
    response = urllib2.urlopen(req)
    soup = BeautifulSoup(response.read(), "html.parser")
    aArr=soup.find_all("a", href=True)

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
                try:
                    row=parseRecipePage(url)
                    csvwriter.writerow(row)
                    print("Successfully added recipe for " + row[0])
                except Exception as e:
                    log_error(e, "Error while trying to write "+ row + " to file")
    cleanup()
       
def parseRecipePage(url):
    row=list()
    try:
        req = urllib2.Request(url, headers={"User-Agent" : "Magic Browser"})
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response.read(), "html.parser")
        
        name=soup.find_all(class_="recipe-summary__h1")[0].get_text()
        row.append(name)

        desc=soup.find_all(class_="submitter__description")[0].get_text()
        row.append(desc.replace("\"\"", "\"").strip())

        chef=soup.find_all(class_="submitter__name")[0].get_text()
        row.append(chef)

        prepTime=soup.select("time[itemprop='prepTime']")[0].get_text()
        row.append(prepTime)

        cookTime=soup.select("time[itemprop='cookTime']")[0].get_text()
        row.append(cookTime)

        total=soup.select("time[itemprop='totalTime']")[0].get_text()
        row.append(total)

        ingrElemArr=soup.find_all(class_="checkList__item")
        global ingrCounter
        global csvwriter2
        global ingrDict
        ingredients=list()
        for ingrElem in ingrElemArr:
            try:
                ingr=ingrElem.text.strip()
                if "Add all ingredients to list" not in ingr:
                    if ingr and ingr not in ingrDict:
                        tmplist=list()
                        ingrCounter+=1
                        ingrDict.update({ingr:ingrCounter}) # maintain a dict to make sure ingr are unique across multiple recipes
                        ingredients.append(ingrDict[ingr]) # maintain a list to add comma deparated values to the recipe's "ingredients" column
                        tmplist.append(ingrCounter) # maintain a list to add to the next row in the ingredients csv file
                        tmplist.append(ingr)
                        csvwriter2.writerow(tmplist)
            except Exception as e:
                log_error(e, "Error trying to parse ingredient: " + ingr)
        row.append(','.join(str(x) for x in ingredients))
        
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
