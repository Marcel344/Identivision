from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from os import path
import time
import os
import urllib.request
import ssl
from PyQt5.QtCore import QThread, pyqtSignal


ssl._create_default_https_context = ssl._create_unverified_context

class FBWebScraperThread(QThread):

    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        QThread.__init__(self)

    # run method gets called when we start the thread
    def run(self):
        if (path.isdir('profilepics')):
            print("profilepics folder already exists !")
        else:
            os.mkdir('profilepics')

        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver2 = webdriver.Chrome(ChromeDriverManager().install())

        names=[] #List to store names
        profiles=[]
        driver.get("https://www.facebook.com/pg/AUST.Lebanon/reviews/?referrer=page_recommendations_see_all&ref=page_internal")

        SCROLL_PAUSE_TIME = 4

        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        content = driver.page_source
        soup = BeautifulSoup(content)
        
        for a in soup.findAll('a',attrs={'class':'_5pb8 o_c3pynyi2g _8o _8s lfloat _ohe'}):
            name=a.attrs.get('title')
            if (name!= None):
                names.append(name)
                self.signal.emit(name)
                profileLink = a.attrs.get("href")
                driver2.get(profileLink)
                content2 = driver2.page_source
                soup2 = BeautifulSoup(content2)
                img = soup2.find('img', attrs={'class':'_11kf img'})
                if (img != None):
                    urllib.request.urlretrieve(img.attrs.get("src"), "profilepics/"+name+".jpg")
                df = pd.DataFrame({'Name':names}) 
                df.to_csv('names.csv', index=False, encoding='utf-8')

        driver2.close()


from pynput.mouse import Controller

class IGWebScraperThread(QThread):

    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        QThread.__init__(self)

    # run method gets called when we start the thread
    def run(self):

        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get("https://www.instagram.com/accounts/login/?hl=en&next=%2Faust_lebanon%2F&source=desktop_nav")
        time.sleep(5)
        driver.find_element_by_name("username").send_keys("9_silverbeat_9")
        driver.find_element_by_name("password").send_keys("1Chocomax1")
        driver.find_element_by_css_selector("button[type='submit']").click()
        time.sleep(3)
        driver.find_element_by_css_selector("a.-nal3").click()
        time.sleep(2)

        SCROLL_PAUSE_TIME = 1.2

        # Get scroll height
        mouse = Controller()

        counter = 0
        mouse.position = (666, 433)

        while counter<100:
            print("Watch out ! Taking controls of mouse")
            if (counter<10):
                mouse.scroll(0, -1000)
                time.sleep(SCROLL_PAUSE_TIME+0.5)
                mouse.scroll(0, 1000)

            mouse.scroll(0, -1000)
            time.sleep(SCROLL_PAUSE_TIME)
            counter = counter+1

        content = driver.page_source
        soup = BeautifulSoup(content)

        names = []
        profileLinks = []
        driver2 = webdriver.Chrome(ChromeDriverManager().install())
        ssl._create_default_https_context = ssl._create_unverified_context

        for a in soup.findAll('div',attrs={'class':'d7ByH'}):
            name = a.find('a')
            profileLinks.append(name.attrs.get("href"))
            driver2.get("https://www.instagram.com"+name.attrs.get("href"))
            content2 = driver2.page_source
            soup2 = BeautifulSoup(content2)
            img = soup2.find('img', attrs={'class':'_6q-tv'})
            if (img != None):
                urllib.request.urlretrieve(img.attrs.get("src"), "profilepics/"+name.attrs.get("title")+".jpg")
                self.signal.emit(name.attrs.get("title"))
                names.append(name.attrs.get("title"))


        df = pd.DataFrame({'Name':names,'href':profileLinks}) 
        df.to_csv('instaFollowers.csv', index=False, encoding='utf-8')