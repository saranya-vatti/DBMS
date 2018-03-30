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

datafilename = "G:\\Courses\\Spring 18\\DBMS\\dbms-repo\\DBMS\\data\\data_recipeland.csv"
ingredientfilename = "G:\\Courses\\Spring 18\\DBMS\\dbms-repo\\DBMS\\data\\ingr.csv"
ingrDict=dict()
recipeUrlSet=set()
recipeExistingUrlSet=set()
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
        recipeExistingUrlSet.add(r["link"])
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

tag=""
recipeListUrlSet=set()
def main():
    sitemapurl="https://recipeland.com/recipes/categories/browse"
    req = urllib2.Request(sitemapurl, headers={"User-Agent" : "Magic Browser"})
    response = urllib2.urlopen(req)
    soup = BeautifulSoup(response.read(), "html.parser")
    aArr=soup.select("div[id='yield']")[0].find_all("div", recursive=False)[5].find_all("a")
    for aElem in aArr:
        href=aElem['href']
        tag=aElem.contents[0]
        if href not in recipeListUrlSet and href.startswith("https://recipeland.com/recipes/for/"):
            recipeListUrlSet.add(href)
            req2 = urllib2.Request(href, headers={"User-Agent" : "Magic Browser"})
            response2 = urllib2.urlopen(req2)
            soup2 = BeautifulSoup(response2.read(), "html.parser")
            showing = soup2.select("p[class='c tiny']")[0].get_text()
            digArr = re.findall(r'\d+', showing)
            firstPage = digArr[1]
            total = digArr[2]
            numPages = math.ceil((int(total)/int(firstPage)))
            for pageNum in range (1,numPages):
                href2 = href + "?page=" + str(pageNum)
                req3 = urllib2.Request(href2, headers={"User-Agent" : "Magic Browser"})
                response3 = urllib2.urlopen(req3)
                soup3 = BeautifulSoup(response3.read(), "html.parser")
                aArr2 = soup3.select(".recipe_list a")
                for aElem2 in aArr2:
                    href3 = aElem2['href']
                    if href3.startswith("https://recipeland.com/recipe") and href3 not in recipeUrlSet:
                        recipeUrlSet.add(href3)
    for url in recipeUrlSet:
        parseRecipePage(url)
        cleanup()
       
def parseRecipePage(url):
    row=list()
    try:
        req = urllib2.Request(url, headers={"User-Agent" : "Magic Browser"})
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response.read(), "html.parser")
        
        name=soup.select("h1[itemprop='name']")[0].get_text()
        if url in recipeExistingUrlSet:
            return
        log_debug("name = " + name)
        row.append(name)

        row.append(url)

        try:
            desc=soup.select("meta[name='Description']")[0]['content'].replace("\"\"", "\"").strip()
            log_debug("desc = " + desc)
            row.append(desc)
        except Exception as e:
            log_info("No description for " + name)
            row.append("NULL")

        try:
            chef=soup.select("meta[itemprop='author']")[0]['content'].replace(" @ recipeland", "")
            log_debug("chef = " + chef)
            row.append(chef)
        except Exception as e:
            log_info("No chef name found for " + name)
            row.append("NULL")

        try:
            prepTimeContent=soup.select("meta[itemprop='prepTime']")[0]['content'].split("PT")[1]
            hrs=prepTimeContent.split("H")[0]
            prepTime=""
            if hrs!="0":
                prepTime = hrs + " hours"
            mins=prepTimeContent.split("H")[1].split("M")[0]
            prepTime = prepTime + mins + " mins"
            log_debug("prepTime = " + prepTime)
            row.append(prepTime)
        except Exception as e:
            log_info("No prepTime for " + name)
            row.append("NULL")

        try:
            cookTimeContent=soup.select("meta[itemprop='cookTime']")[0]['content'].split("PT")[1]
            hrs=cookTimeContent.split("H")[0]
            cookTime=""
            if hrs!="0":
                cookTime = hrs + " hours"
            mins=cookTimeContent.split("H")[1].split("M")[0]
            cookTime += mins + " mins"
            log_debug("cookTime = " + cookTime)
            row.append(cookTime)
        except Exception as e:
            log_info("No cookTime for " + name)
            row.append("NULL")

        try:    
            totalTimeContent=soup.select("meta[itemprop='totalTime']")[0]['content'].split("PT")[1]
            hrs=totalTimeContent.split("H")[0]
            totalTime=""
            if hrs!="0":
                totalTime = hrs + " hours"
            mins=totalTimeContent.split("H")[1].split("M")[0]
            totalTime += mins + " mins"
            log_debug("totalTime = " + totalTime)
            row.append(totalTime)
        except Exception as e:
            log_info("No totalTime for " + name)
            row.append("NULL")

        ingrElemArr=soup.select("table[id='ingredient_list'] tr")
        global ingrCounter
        global csvwriter2
        global ingrDict
        ingredients=list()
        for ingrElem in ingrElemArr:
            ingr=ingrElem.get_text().replace("\n", " ").replace("  ", " ").strip()
            ingr = ingr.replace("℉", " deg F").replace("℃", " deg C").replace("⅓", "1/3").replace("⅛", "1/8").replace("¼", "1/4")
            ingr = ingr.replace("½", "1/2").replace("¾", "3/4").replace("⅓", "1/3").replace("⅔", "2/3").replace("⅞", "7/8").replace("⅜", "3/8").replace("⅕","1/6")
            if ingr.endswith("*"):
                ingr = ingr[:-1].strip()
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
            instructions=soup.select("div[itemprop='recipeInstructions']")[0].get_text().replace("\n\n", "\n").replace("  ", " ").strip()
            instructions = instructions.replace("℉", " deg F").replace("℃", " deg C").replace("⅓", "1/3").replace("⅛", "1/8").replace("¼", "1/4")
            instructions = instructions.replace("½", "1/2").replace("¾", "3/4").replace("⅓", "1/3").replace("⅔", "2/3").replace("⅞", "7/8").replace("⅜", "3/8").replace("⅕","1/6")
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
            
        servings=soup.select("p[itemprop='recipeYield']")[0].get_text().strip()

        try:
            cals=soup.select("span[itemprop='calories']")[0].get_text().replace("calories,", "").strip()
            calories=str(int(cals) * int(servings))
            log_debug("calories = " + calories)
            row.append(calories)
        except Exception as e:
            log_info("No calories for " + name)
            row.append("NULL")

        try:
            log_debug("servings = " + servings)
            row.append(servings)
        except Exception as e:
            log_info("No servings for " + name)
            row.append("NULL")

        try:
            fatContent=str(int(soup.select("span[itemprop='fatContent']")[0].get_text().strip())*int(servings)) + " g"
            log_debug("fatContent = " + fatContent)
            row.append(fatContent)
        except Exception as e:
            log_info("No fatContent for " + name)
            row.append("NULL")

        try:
            carbohydrateContent=str(int(soup.select("span[itemprop='carbohydrateContent']")[0].get_text().strip())*int(servings)) + " g"
            log_debug("carbohydrateContent = " + carbohydrateContent)
            row.append(carbohydrateContent)
        except Exception as e:
            log_info("No carbohydrateContent for " + name)
            row.append("NULL")

        try:
            proteinContent=str(int(soup.select("span[itemprop='proteinContent']")[0].get_text().strip())*int(servings)) + " g"
            log_debug("proteinContent = " + proteinContent)
            row.append(proteinContent)
        except Exception as e:
            log_info("No proteinContent for " + name)
            row.append("NULL")

        try:
            cholesterolContent=str(int(soup.select("span[itemprop='cholesterolContent']")[0].get_text().strip())*int(servings)) + " mg"
            log_debug("cholesterolContent = " + cholesterolContent)
            row.append(cholesterolContent)
        except Exception as e:
            log_info("No cholesterolContent for " + name)
            row.append("NULL")

        try:
            sodiumContent=str(int(soup.select("span[itemprop='sodiumContent']")[0].get_text().strip())*int(servings)) + " mg"
            log_debug("sodiumContent = " + sodiumContent)
            row.append(sodiumContent)
        except Exception as e:
            log_info("No sodiumContent for " + name)
            row.append("NULL")

        try:
            image=soup.select("meta[itemprop='image']")[0]['content']
            log_debug("image = " + image)
            row.append(image)
        except Exception as e:
            log_info("No image for " + name)
            row.append("NULL")

        global tag
        try:
            keywordArr=[]
            if tag!="":
                keywordArr.append(tag)
            keywordArr.extend(soup.select("div[class='health-facts']")[0].get_text().strip().replace(", ", ",").split(","))
            aArr = soup.select("a[itemprop='recipeCategory']")
            for aElem in aArr:
                keywordArr.append(aElem.get_text().strip())
            keywords=(", ").join(keywordArr)
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
        log_info("Successfully added recipe for " + name)
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
