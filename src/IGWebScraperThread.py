from pynput.mouse import Controller
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
import time
import urllib.request
import ssl
from PyQt5.QtCore import QThread, pyqtSignal
import PyQt5
from PyQt5 import uic, QtWidgets
from PyQt5 import Qt


class IGWebScraperThread(QThread):

    signal = pyqtSignal('PyQt_PyObject')
    scanSignal = pyqtSignal(int, name='numOfScans')
    statusSignal = pyqtSignal(str, name='status')

    def __init__(self):
        self.state = True
        self.driver = None
        self.desiredNumOfFollowers = 0
        QThread.__init__(self)

    # run method gets called when we start the thread

    def run(self):

        SCROLL_PAUSE_TIME = 0.8

        counter = 0
        time.sleep(3)

        while self.state and counter < self.desiredNumOfFollowers:
            self.driver.execute_script("document.querySelector('div.isgrP').scrollTop += 100")
            time.sleep(1/3)
            counter = counter+1
            self.scanSignal.emit(counter)

        content = self.driver.page_source
        soup = BeautifulSoup(content)

        names = []
        profileLinks = []
        driver2 = webdriver.Chrome(ChromeDriverManager().install())
        ssl._create_default_https_context = ssl._create_unverified_context

        self.state = True
        self.statusSignal.emit("Scanning profiles")


        for a in soup.findAll('div',attrs={'class':'d7ByH'}):
            if not self.state: 
                break
            if(len(names)>self.desiredNumOfFollowers+1):
                break
            name = a.find('a')
            driver2.get("https://www.instagram.com"+name.attrs.get("href"))
            content2 = driver2.page_source
            soup2 = BeautifulSoup(content2)
            img = soup2.find('img', attrs={'class':'_6q-tv'})
            if (img != None):
                profileLinks.append(name.attrs.get("href"))
                urllib.request.urlretrieve(img.attrs.get("src"), "profilepics/"+name.attrs.get("title")+".jpg")
                self.signal.emit(name.attrs.get("title"))
                names.append(name.attrs.get("title"))
                self.scanSignal.emit(len(names))

        self.statusSignal.emit("Done")


    def stopScraper(self):
        self.state = False

    def setNumOfFollowers(self, val):
        self.desiredNumOfFollowers = val

    def loadWebsite(self):
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get("https://www.instagram.com/accounts/login/?hl=en&next=%2Faust_lebanon%2F&source=desktop_nav")
        time.sleep(5)
        driver.find_element_by_name("username").send_keys("9_silverbeat_9")
        driver.find_element_by_name("password").send_keys("1Chocomax1")
        driver.find_element_by_css_selector("button[type='submit']").click()
        time.sleep(8)
        driver.find_element_by_partial_link_text(" followers").click()
        NumOfFollowers = driver.find_element_by_partial_link_text(" followers").text
        self.driver = driver
        return int(NumOfFollowers.split(" ")[0].replace(",", ""))

#        df = pd.DataFrame({'Name':names,'href':profileLinks})                     
#        df.to_csv('instaFollowers.csv', index=False, encoding='utf-8')

class IGwindow(Qt.QWidget):
    def __init__ (self, thread):
        Qt.QWidget.__init__(self)
        uic.loadUi('instagram.ui', self) 
        self.thread = thread
        buttonStyleSheet = "background-color: #262b29;  border: 1px solid #46fd65; border-radius: 10px; font-size: 12px;color: #46fd65;text-align: center;"
        self.totalNumberOfFollowers = self.thread.loadWebsite()
        self.desiredNumberOfFollowers = self.totalNumberOfFollowers
        self.numOfFollowers.setText(str(self.totalNumberOfFollowers))
        self.numOfScans.setText(str(self.totalNumberOfFollowers))
        self.horizontalSlider.setMinimum(20)
        self.horizontalSlider.setMaximum(self.totalNumberOfFollowers)
        self.horizontalSlider.setTickInterval(10)
        self.horizontalSlider.setSingleStep(10)
        self.horizontalSlider.setValue(self.totalNumberOfFollowers)
        self.horizontalSlider.valueChanged.connect(self.value_changed)
        self.showMinimized()
        time.sleep(1)
        self.showNormal()
        self.startBtn.setStyleSheet(buttonStyleSheet)
        self.stopBtn.setStyleSheet(buttonStyleSheet)
        self.startBtn.clicked.connect(self.runThread)
        self.stopBtn.clicked.connect(self.stopThread)
        self.progressBar.setMaximum(self.totalNumberOfFollowers)
        self.progressBar.setMinimum(0)
        self.progressBar.setValue(0)
        self.thread.scanSignal.connect(self.updatePB)
        self.thread.statusSignal.connect(self.setStatus)
        self.setWindowTitle("Instagram Scraper")

        self.PB_PassBy = 0 #First time we get the PB from the scroll event, next time we get PB from scanning each profile

    def runThread(self): 
        self.statusLabel.setText("Running")
        self.thread.setNumOfFollowers(self.desiredNumberOfFollowers)
        self.thread.start()

    def stopThread(self): 
        self.statusLabel.setText("Stopped")
        self.thread.stopScraper()
    
    def updatePB(self, value):
        self.progressBar.setValue(value)

    def setStatus (self, status):
        self.statusLabel.setText(status)

    def value_changed(self, val):
        self.numOfScans.setText(str(val))
        self.desiredNumberOfFollowers = val
        self.progressBar.setMaximum(val)

