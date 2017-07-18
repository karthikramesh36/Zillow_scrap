from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import requests,re,time,pandas,string

""" validating input"""
def enterInput():
    attempt=0
    state=area=text=""
    while attempt < 20:
        attempt+=1
        if state == "":
            state=input("Enter the State in 2 alphabets")
        if area =="":
            area=input("Enter the Area name")
        if not re.match("^[a-zA-Z]{2,2}$", state):
            """raise Exception("Invalid state")"""
            state=""
            print("Try again !, wrong state format")
        else:
            print("State Accepted",state)
            attempt+=10
        if area.isnumeric():
            """raise Exception("Invalid area")"""
            area=""
            print("area",area)
            print("Try again !, wrong area format")
        else:
            print("Area accepted",area)
            attempt+=10

    text=area + "," + state
    return text
"""getting the homepage"""
driver = webdriver.Firefox()
driver.get("https://www.zillow.com")
title=driver.title
if "Zillow" not in title:
    raise ValueError("Wrong page")

"""shifting from home page through user input"""
driver.find_element_by_id("citystatezip").click()
driver.implicitly_wait(10)
"""userinput=enterInput()"""
userinput="los angeles, CA"
driver.find_element_by_id("citystatezip").send_keys(Keys.DELETE)
driver.implicitly_wait(1)
driver.find_element_by_id("citystatezip").send_keys(userinput)
driver.find_element_by_id("citystatezip").send_keys(Keys.RETURN)
driver.implicitly_wait(10)


"""when webpage shows results for undesired/incorrect user input"""
choice='n'
while choice == 'y':
    try:
        errorelement = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "zsg-notification-bar-close")))
        choice = input("Exact User area not to be found in Zillow database, to try again press y or any key to continue.. ")
        choice= choice.lower()
        if choice =='y':
            userinput=enterInput()
        else:
            print("Going Ahead with the Available broad results ...")
    except WebDriverException:
        print("no error message dislpayed")
        choice='n'


"""extracting data from webpage into dict"""
""" while loop controls the number of pages upto which data is required"""
L=[]
i=0
while (i < 15):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.implicitly_wait(10)
    print(driver.title)
    time.sleep(10)
    currentURL = driver.current_url
    print("current url",currentURL)
    pageSOURCE = requests.get(currentURL)
    print("page source",pageSOURCE)
    html = pageSOURCE.content
    soup = BeautifulSoup(html, "html.parser")
    all=soup.find_all("div",{"class":"zsg-photo-card-caption"})
    print ("total items",all)

    for item in all:
        d={}
        d["Status"] =item.find_all("span",{"class":"zsg-photo-card-status"})[0].text
        d["Address"] = item.find_all("span",{"class":"zsg-photo-card-address"})[0].text
        try:
            d["Cost"] = item.find("span",{"class":"zsg-photo-card-price"}).text
        except:
            d["Cost"] = None
        info= item.find("span",{"class":"zsg-photo-card-info"}).text
        fornow=re.split("·", info)
        try:
            if 'bds' in fornow[0]:
                d["Beds"]=(fornow[0])
        except:
            d["Beds"]= None
        try:
            if 'ba' in fornow[1]:
                d["Baths"]=(fornow[1])
        except:
            d["Baths"]= None
        try:
            if 'sqft' in fornow[2]:
                d["Sq.Ft"]=(fornow[2])
        except:
            d["Sq,Ft"]= None
        L.append(d)






    """Shifting through pages"""

    pageShift=driver.find_element_by_class_name("zsg-pagination-next")
    pages=pageShift.find_element_by_tag_name("a")
    driver.implicitly_wait(10)
    pages.click()
    driver.implicitly_wait(10)
    i+=1


"""storing the web data from dict to dataframe"""
df=pandas.DataFrame(L)
print(df)
df.to_csv("Output.csv")
