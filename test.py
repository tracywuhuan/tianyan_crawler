#!/usr/bin/env python
# coding:utf-8
from selenium import webdriver
import time
import re
import sys
import sqlite3
import traceback
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.by import By

def driver_open():
    binary = FirefoxBinary('/Applications/IBM Firefox.app/Contents/MacOS/firefox-bin')
    browser = webdriver.Firefox(firefox_binary=binary)
    return browser

def get_content(driver, url):
    driver.get(url)
    # 等待5秒，更据动态网页加载耗时自定义
    time.sleep(10)
    # 获取网页内容
    content = driver.page_source.encode('utf-8')
    #driver.close()
    soup = BeautifulSoup(content, 'lxml')
    return soup


def get_basic_info(dbname,soup,companyname,companylink):

    
    try:
        zcsjHTML = soup.select('.baseInfo_model2017')[0]
        zcsj = ""
        jyzt = ""
        zcdz = ""
        basicinfostr = ""
        for idx, tr in enumerate(zcsjHTML.find_all('tr')):
            if idx != 0:
                tds = tr.find_all('td')
                zcsj = tds[2].find_all('div')[0].contents[0]
        print u'注册时间：' + zcsj

        jyztHTML = soup.select('.baseInfo_model2017')[0]
        for idx, tr in enumerate(jyztHTML.find_all('tr')):
            if idx != 0:
                tds = tr.find_all('td')
                jyzt = tds[3].find_all('div')[0].contents[0]
        print u'经营状态：' + jyzt

        zcdzHTML = soup.select('.base2017')[0]
        for idx, tr in enumerate(zcdzHTML.find_all('tr')):
            if idx == 4:
                zcdz = tr.find_all('td')[0].select('.ng-binding')[0].contents[0]
                #zcdz =  tds[0].find_all('div > span')[0].contents[0]
        print u'注册地址：' + zcdz
        with sqlite3.connect(dbname) as c:
            c.text_factory = str
            c.execute("INSERT INTO Companybasicinfo VALUES ('%s','%s','%s','%s','%s')" % (companyname,companylink,zcsj,jyzt,zcdz))
    except Exception as e:
        pass
    


#对外投资
def get_dytz(dytzdbname,companyname,driver):


    try:
        pages = driver.find_element_by_xpath("//div[contains(@class,'out-investment-container')]/div[contains(@class,'company_pager')]/ul")
    except Exception as e:
        try:
            #不需要翻页直接读
            trs = driver.find_element_by_xpath("//div[contains(@class,'out-investment-container')]/div/table/tbody").find_elements_by_class_name("ng-scope")
            for tr in trs:
                tds = tr.find_elements_by_class_name("ng-binding")
                if(len(tds) >= 7):
                    with sqlite3.connect(dytzdbname) as c:
                        c.text_factory = str
                        c.execute("INSERT INTO Companydytz VALUES ('%s','%s','%s','%s','%s','%s','%s','%s')" % (companyname,tds[0].text,tds[1].text,tds[2].text,tds[3].text,tds[4].text,tds[5].text,tds[6].text))
        except Exception as e:
            pass

    else:
        try:
            #需要翻页
            currentpage = 1#当前页
            while 1:
                total = driver.find_element_by_xpath("//div[contains(@class,'out-investment-container')]/div[contains(@class,'company_pager')]/div")

                totalpages = re.sub(r'[^\x00-\x7f]', ' ', total.text)#共几页
                if(currentpage > int(totalpages)):
                    break

                #读取表格内容
                trs = driver.find_element_by_xpath("//div[contains(@class,'out-investment-container')]/div/table/tbody").find_elements_by_class_name("ng-scope")
                for tr in trs:
                    tds = tr.find_elements_by_class_name("ng-binding")
                    if(len(tds) >= 7):
                        with sqlite3.connect(dytzdbname) as c:
                            c.text_factory = str
                            c.execute("INSERT INTO Companydytz VALUES ('%s','%s','%s','%s','%s','%s','%s','%s')" % (companyname,tds[0].text,tds[1].text,tds[2].text,tds[3].text,tds[4].text,tds[5].text,tds[6].text))

                #下一页
                nextpagelink = pages.find_element_by_link_text(">")          
                #element = driver.find_element_by_xpath("//div[contains(@class,'company_pager')]/ul/li["+str(len(pages))+"]/a[contains(@ng-click,'selectPage')]")
                driver.execute_script("arguments[0].click();", nextpagelink)
                time.sleep(5)
                currentpage+=1
                    #pages = driver.find_element_by_xpath("//div[contains(@class,'company_pager')]/ul").find_elements_by_class_name("ng-scope")#重新计算多少页（网站的bug）
        except Exception as e:
            pass


#招聘
def get_zp(zpdbname,companyname,driver):

    try:
        zp = driver.find_element_by_xpath("//div[@id='nav-main-recruitCount']/..")
        pages = driver.find_element_by_xpath("//div[@id='nav-main-recruitCount']/../div[2]/div[contains(@class,'company_pager')]/ul")
        '''
        pages = zp[0].find_elements_by_Tag_Name("div")[2].find_element_by_xpath("//div[contains(@class,'company_pager')]/ul")
        '''
    except Exception as e:
        try:
            #不需要翻页直接读
            trs = driver.find_element_by_xpath("//div[@id='nav-main-recruitCount']/../div[2]/div/table/tbody").find_elements_by_class_name("ng-scope")
            for tr in trs:
                tds = tr.find_elements_by_class_name("ng-binding")
                if(len(tds) >= 6):
                    with sqlite3.connect(zpdbname) as c:
                        c.text_factory = str
                        c.execute("INSERT INTO Companyzp VALUES ('%s','%s','%s','%s','%s','%s','%s')" % (companyname,tds[0].text,tds[1].text,tds[2].text,tds[3].text,tds[4].text,tds[5].text))
        except Exception as e:
            pass
        
    else:
        try:
            #需要翻页
            currentpage = 1#当前页
            while 1:

                total = driver.find_element_by_xpath("//div[@id='nav-main-recruitCount']/../div[2]/div[contains(@class,'company_pager')]/div")

                totalpages = re.sub(r'[^\x00-\x7f]', ' ', total.text)#共几页
                if(currentpage > int(totalpages)):
                    break

                #读取表格内容
                trs = driver.find_element_by_xpath("//div[@id='nav-main-recruitCount']/../div[2]/div/table/tbody").find_elements_by_class_name("ng-scope")
                for tr in trs:
                    tds = tr.find_elements_by_class_name("ng-binding")
                    if(len(tds) >= 6):
                        with sqlite3.connect(zpdbname) as c:
                            c.text_factory = str
                            c.execute("INSERT INTO Companyzp VALUES ('%s','%s','%s','%s','%s','%s','%s')" % (companyname,tds[0].text,tds[1].text,tds[2].text,tds[3].text,tds[4].text,tds[5].text))

                #下一页
                nextpagelink = pages.find_element_by_link_text(">")          
                #element = driver.find_element_by_xpath("//div[contains(@class,'company_pager')]/ul/li["+str(len(pages))+"]/a[contains(@ng-click,'selectPage')]")
                driver.execute_script("arguments[0].click();", nextpagelink)
                time.sleep(5)
                currentpage+=1
                    #pages = driver.find_element_by_xpath("//div[contains(@class,'company_pager')]/ul").find_elements_by_class_name("ng-scope")#重新计算多少页（网站的bug）
        except Exception as e:
            pass

#专利
def get_zl(zldbname,companyname,driver):

    try:
        zp = driver.find_element_by_xpath("//div[@id='nav-main-patentCount']/..")
        pages = driver.find_element_by_xpath("//div[@id='nav-main-patentCount']/../div[2]/div[contains(@class,'company_pager')]/ul")

    except Exception as e:
        try:
            #不需要翻页直接读
            trs = driver.find_element_by_xpath("//div[@id='nav-main-patentCount']/../div[2]/table/tbody").find_elements_by_class_name("ng-scope")
            for tr in trs:
                tds = tr.find_elements_by_class_name("ng-binding")
                if(len(tds) >= 4):
                    with sqlite3.connect(zldbname) as c:
                        c.text_factory = str
                        c.execute("INSERT INTO Companyzl VALUES ('%s','%s','%s','%s','%s')" % (companyname,tds[0].text,tds[1].text,tds[2].text,tds[3].text))
        except Exception as e:
            pass
 
    else:
        try:
            #需要翻页
            currentpage = 1#当前页
            while 1:

                total = driver.find_element_by_xpath("//div[@id='nav-main-patentCount']/../div[2]/div[contains(@class,'company_pager')]/div")

                totalpages = re.sub(r'[^\x00-\x7f]', ' ', total.text)#共几页
                if(currentpage > int(totalpages)):
                    break

                #读取表格内容
                trs = driver.find_element_by_xpath("//div[@id='nav-main-patentCount']/../div[2]/table/tbody").find_elements_by_class_name("ng-scope")
                for tr in trs:
                    tds = tr.find_elements_by_class_name("ng-binding")
                    if(len(tds) >= 4):
                        with sqlite3.connect(zldbname) as c:
                            c.text_factory = str
                            c.execute("INSERT INTO Companyzl VALUES ('%s','%s','%s','%s','%s')" % (companyname,tds[0].text,tds[1].text,tds[2].text,tds[3].text))

                #下一页
                nextpagelink = pages.find_element_by_link_text(">")          
                #element = driver.find_element_by_xpath("//div[contains(@class,'company_pager')]/ul/li["+str(len(pages))+"]/a[contains(@ng-click,'selectPage')]")
                driver.execute_script("arguments[0].click();", nextpagelink)
                time.sleep(5)
                currentpage+=1
                    #pages = driver.find_element_by_xpath("//div[contains(@class,'company_pager')]/ul").find_elements_by_class_name("ng-scope")#重新计算多少页（网站的bug）
        except Exception as e:
            pass


#著作权
def get_zzq(zzqdbname,companyname,driver):

    try:
        zp = driver.find_element_by_xpath("//div[@id='nav-main-cpoyRCount']/..")
        pages = driver.find_element_by_xpath("//div[@id='nav-main-cpoyRCount']/../div[2]/div[contains(@class,'company_pager')]/ul")
        '''
        pages = zp[0].find_elements_by_Tag_Name("div")[2].find_element_by_xpath("//div[contains(@class,'company_pager')]/ul")
        '''
    except Exception as e:
        try:
            #不需要翻页直接读
            trs = driver.find_element_by_xpath("//div[@id='nav-main-cpoyRCount']/../div[2]/table/tbody").find_elements_by_class_name("ng-scope")
            for tr in trs:
                tds = tr.find_elements_by_class_name("ng-binding")
                if(len(tds) >= 6):
                    with sqlite3.connect(zzqdbname) as c:
                        c.text_factory = str
                        c.execute("INSERT INTO Companyzzq VALUES ('%s','%s','%s','%s','%s','%s','%s')" % (companyname,tds[0].text.decode(),tds[1].text,tds[2].text,tds[3].text,tds[4].text,tds[5].text))
        except Exception as e:
            pass
        
    else:
        try:
            #需要翻页
            currentpage = 1#当前页
            while 1:

                total = driver.find_element_by_xpath("//div[@id='nav-main-cpoyRCount']/../div[2]/div[contains(@class,'company_pager')]/div")

                totalpages = re.sub(r'[^\x00-\x7f]', ' ', total.text)#共几页
                if(currentpage > int(totalpages)):
                    break

                #读取表格内容
                trs = driver.find_element_by_xpath("//div[@id='nav-main-cpoyRCount']/../div[2]/table/tbody").find_elements_by_class_name("ng-scope")
                for tr in trs:
                    tds = tr.find_elements_by_class_name("ng-binding")
                    if(len(tds) >= 6):
                        with sqlite3.connect(zzqdbname) as c:
                            c.text_factory = str
                            c.execute("INSERT INTO Companyzzq VALUES ('%s','%s','%s','%s','%s','%s','%s')" % (companyname,tds[0].text,tds[1].text,tds[2].text,tds[3].text,tds[4].text,tds[5].text))

                #下一页
                nextpagelink = pages.find_element_by_link_text(">")          
                #element = driver.find_element_by_xpath("//div[contains(@class,'company_pager')]/ul/li["+str(len(pages))+"]/a[contains(@ng-click,'selectPage')]")
                driver.execute_script("arguments[0].click();", nextpagelink)
                time.sleep(5)
                currentpage+=1
                    #pages = driver.find_element_by_xpath("//div[contains(@class,'company_pager')]/ul").find_elements_by_class_name("ng-scope")#重新计算多少页（网站的bug）
        except Exception as e:
            traceback.print_exc()


if __name__ == '__main__':
    url = "http://www.tianyancha.com/company/2314149"
    reload(sys)
    sys.setdefaultencoding('utf-8')
    keywords = ["规划"]#,"景观","建筑","园林"]

    driver = driver_open()
    driver.get("http://www.tianyancha.com/login")
    driver.find_element_by_class_name("pb30").find_element_by_class_name("_input").clear()  
    driver.find_element_by_class_name("pb40").find_element_by_class_name("_input").clear()   
    driver.find_element_by_class_name("pb30").find_element_by_class_name("_input").send_keys("13436952068")
    driver.find_element_by_class_name("pb40").find_element_by_class_name("_input").send_keys("baobao1992")

    driver.find_element_by_class_name("login_btn").click()
    time.sleep(5)
    driver.get("http://www.tianyancha.com")

    zzqdbname = "zzq.db"
    zldbname = "zl.db"
    zpdbname = "zp.db"
    dytzdbname = "dytz.db"
    dbname = "basicinfo.db"

    try:
        with sqlite3.connect(zzqdbname) as c:
            c.execute('''CREATE TABLE Companyzzq(companyName VARCHAR(200),pubTime TEXT,name TEXT,shortName TEXT,regNumber TEXT,classNumer TEXT ,version TEXT)''')
        with sqlite3.connect(zldbname) as c:
            c.execute('''CREATE TABLE Companyzl(companyName VARCHAR(200),pubTime TEXT,pname TEXT, preqNumber TEXT, ppubNumber TEXT)''')
        with sqlite3.connect(zpdbname) as c:
            c.execute('''CREATE TABLE Companyzp(companyName VARCHAR(200),pubTime TEXT,position TEXT,salary TEXT, workEXP VARCHAR(50), number VARCHAR(30),city TEXT)''')
        with sqlite3.connect(dytzdbname) as c:
            c.execute('''CREATE TABLE Companydytz(companyName VARCHAR(200),investedName VARCHAR(200),legalPerson VARCHAR(30), capital VARCHAR(100), amount VARCHAR(100),proportion VARCHAR(20),regTime TEXT, status VARCHAR(100))''')
        with sqlite3.connect(dbname) as c:
            c.execute('''CREATE TABLE Companybasicinfo(companyName VARCHAR(200),companylink VARCHAR(100),regTime TEXT, status VARCHAR(50), regLocation VARCHAR(300))''')
    except Exception as e:
        print e

    try:
        for keyword in keywords:
            file_object = open('companylist_'+ keyword +'.txt','r')
            lines = file_object.readlines()
            count = 0
            for line in lines[16038:]:
                if(count >500 ):
                    driver.quit()
                    time.sleep(100)
                    driver = driver_open()
                    driver.get("http://www.tianyancha.com/login")
                    time.sleep(5)
                    driver.find_element_by_class_name("pb30").find_element_by_class_name("_input").clear()  
                    driver.find_element_by_class_name("pb40").find_element_by_class_name("_input").clear()   
                    driver.find_element_by_class_name("pb30").find_element_by_class_name("_input").send_keys("13436952068")
                    driver.find_element_by_class_name("pb40").find_element_by_class_name("_input").send_keys("baobao1992")

                    driver.find_element_by_class_name("login_btn").click()
                    time.sleep(5)
                    driver.get("http://www.tianyancha.com")
                    count = 0
                companyitem = line.split()
                companyname = companyitem[0]
                companylink = companyitem[1]
                print companyname + " " +companylink

                soup = get_content(driver, companylink)
                print u'----获取基础信息----'
                get_basic_info(dbname,soup,companyname,companylink)
                print u'----获取zzq信息----'
                get_zzq(zzqdbname,companyname,driver)
                print u'----获取zl信息----'
                get_zl(zldbname,companyname,driver)
                print u'----获取zp信息----'
                get_zp(zpdbname,companyname,driver)
                print u'----获取dytz信息----'
                get_dytz(dytzdbname,companyname,driver)
                time.sleep(1)
                count += 1
            file_object.close()
    except Exception as e:
        traceback.print_exc()
    finally:
        driver.quit()
