# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import datetime

import pymysql
import requests
import time
from bs4 import BeautifulSoup


#全局变量 数据库用
dbhost ='localhost'
dbuser = 'root'
dbpass = 'root'
dbname = 'stock'
db = pymysql.connect(host=dbhost, user=dbuser, password=dbpass, database=dbname)

# 得到所有的股票代码
def getStockCode():
    cursor =db.cursor()
    # ①股票代码   ②公司名称    ③东证1or2部   ④1or2的代码   ⑤行业种类  ⑥公司规模
    cursor.execute("select * from stockname;")
    dataTable =cursor.fetchall()
    return dataTable


#开始处理程序
def StartProcess(codeList):

    #有多少数量就处理多少次
    for data in codeList:

        stockCode=str(data[0])

        baseURL ='https://finance.yahoo.co.jp/quote/'

        URL =baseURL + stockCode

        print (URL)
        strhtml = requests.get(URL)
        soup = BeautifulSoup(strhtml.text,'lxml')
        data = soup.select('#referenc > div > ul > li> dl > dd')

        infolist = []  # 这里保存了所有需要的情报

        for item in data:
            result={
                'title':item.get_text()
            }
            temp = str(result.values())
            tempNumber1 = temp.find('[')
            tempNumber2 = temp.find(']') + 1
            temp = temp[tempNumber1:tempNumber2]
            infolist.append(temp)

        # 股票代码
        code =stockCode

        #今日价格以及时间
        parenthesesLocation = infolist[8].find('(')
        todayPrice = int(infolist[8][2:parenthesesLocation].replace(',',''))/100
        today = datetime.datetime.now()

        #今年最高价格及时间
        tempHighPrice =infolist[10].replace('更新','')
        parenthesesLocationLeft = tempHighPrice.find('(')
        parenthesesLocationRight =tempHighPrice.find(')')
        if ',' in tempHighPrice[2:parenthesesLocationLeft]:
            highPrice = int(tempHighPrice[2:parenthesesLocationLeft].replace(',',''))
        else:
            highPrice = int(tempHighPrice[2:parenthesesLocationLeft])
        highPriceDate = tempHighPrice[parenthesesLocationLeft+1:parenthesesLocationRight]

        #今年最低价格及时间
        tempLowPrice =infolist[11].replace('更新','')
        parenthesesLocationLeft = tempLowPrice.find('(')
        parenthesesLocationRight =tempLowPrice.find(')')
        if ',' in tempLowPrice[2:parenthesesLocationLeft]:
            lowPrice = int(tempLowPrice[2:parenthesesLocationLeft].replace(',',''))
        else:
            lowPrice = int(tempLowPrice[2:parenthesesLocationLeft])
        lowPriceDate = tempLowPrice[parenthesesLocationLeft+1:parenthesesLocationRight]

        #股票分红率
        parenthesesLocationLeft = infolist[2].find('\'')
        parenthesesLocationRight = infolist[2].find('%')
        dividend = infolist[2][2:parenthesesLocationRight]

        #执行存储过程
        InsertIntoDatabase(code, todayPrice, today, highPrice, highPriceDate, lowPrice, lowPriceDate,
                           dividend)



#存储方法
def InsertIntoDatabase(code,todayprice,today,highPrice,highPriceDate,lowPrice,lowPriceDate,dividend):

    today = "'" + str(today) + "'"
    highPriceDate = "'" + highPriceDate + "'"
    lowPriceDate = "'" + lowPriceDate + "'"

    cursor = db.cursor()
    sqlstr ="insert into record (code,todayPrice,today,highPrice,highPriceDate,lowPrice,lowPriceDate,dividend)" \
            " values ({0},{1},{2},{3},{4},{5},{6},{7}) ;".format(code,todayprice,today,highPrice,highPriceDate,lowPrice,lowPriceDate,dividend)

    try:
        cursor.execute(sqlstr)
        db.commit()
    except:
        db.rollback()


if __name__ == '__main__':

    stockCode =getStockCode()  #得到股票名称的数据

    infoList = StartProcess(stockCode)   #传入方法

    print(" <!!!  MISSION COMPLETE  !!!>")





