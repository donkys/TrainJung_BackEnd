import sqlite3
import bs4
import requests
import json
import os
import time

import math
from datetime import datetime
from dateutil.relativedelta import relativedelta

#create a data structure
__conn = sqlite3.connect('./database/railwaythai.db')
__c = __conn.cursor()

_data = requests.get(
    'https://ttsview.railway.co.th/SRT_Schedule2022.php?ln=th&line=3&trip='+'1')

# Scraping web
def _setScraping():
    return bs4.BeautifulSoup(_data.text, "html.parser")

__soup = _setScraping()

def _getStation():
    e = []
    for c in __soup.find_all('td', {'class': 'style31'}):
        a = c.find('a', {'style': 'color:black; text-decorate:none;'})
        if (a is not None):
            e.append(a.text.strip())
    return e


def _getNumberTrain():
    e = []
    a = []
    temp = []

    for c in __soup.find_all('span', {'class': 'HeadTable'}):
        a = c.find('a', {'style': 'color:black; text-decorate:none;'})
        if (a is not None):
            e.append(a.text.strip())

    return e


def _getTimeStation(numTrain):
    a = []
    temp = []
    count = 0

    for c in __soup.find_all('td', {'class': 'style3'}):
        count += 1
        temp.append(c.text.strip())

        if count % numTrain == 0:
            a.append(temp)
            temp = []

    return a
            

def _dataInsertOUT():
    stationCount = 0
    station = _getStation()
    time = _getTimeStation(13)
    __c.execute("DELETE FROM StationOUT")

    for i in range(len(time)):
        __c.execute("INSERT INTO StationOUT VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                    ((i+1), station[i], time[i][0], time[i][1], time[i][2],
                                    time[i][3], time[i][4], time[i][5], time[i][6], time[i][7], 
                                    time[i][8], time[i][9], time[i][10], 
                                    time[i][11], time[i][12]))
    __conn.commit()

def _dataInsertIN():
    stationCount = 0
    station = _getStation()
    time = _getTimeStation(15)
    __c.execute("DELETE FROM StationIN")

    for i in range(len(time)):
        __c.execute("INSERT INTO StationIN VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                    ((i+1), station[i], time[i][0], time[i][1], time[i][2],
                                    time[i][3], time[i][4], time[i][5], time[i][6], time[i][7], 
                                    time[i][8], time[i][9], time[i][10], 
                                    time[i][11], time[i][12], time[i][13], time[i][14]))

    __conn.commit()


def __createTable(nameTable):
    str = 'CREATE TABLE IF NOT EXISTS ' + nameTable + '( id INTEGER PRIMARY KEY AUTOINCREMENT, station_name TEXT,'

    for num in _getNumberTrain():
        str += "Train_" + num + " TEXT,"
    str = str[:len(str)-1] + ");"

    __c.execute(str)

# ---------------------------------------------------------------------------------------

def _getTrain():

    #Connect Database
    cursor = __conn.execute("SELECT * FROM StationOUT")

    addTrain = []
    for row in cursor:
        addTrain.append({"id" : row[0], "name":row[1], "Time" : row[2:len(row)]})
    
    return addTrain

def _getTrainNumber():
    number = _getNumberTrain()
    train = []

    for t in number:
        cursor = __conn.execute('''SELECT Train_''' + str(t) + ''' FROM StationOUT''')
        addTrain = []
        for row in cursor:
            addTrain.append(row[0])    
        train.append({"number":t, "Time" : addTrain})
    return train

def _getTrainByID(numberTrain):
    cursor = __conn.execute('''SELECT id, station_name, Train_''' + str(numberTrain) + ''' FROM StationOUT WHERE Train_''' + str(numberTrain) + ''' != "" ''')
    addTrain = []
    for row in cursor:
        addTrain.append({row[0] : row[1],"Time" : row[2]})
    
    return addTrain


def _getStationAtoB(idA : int, idB : int):
    number = _getNumberTrain()
    train = []

    for t in number:
        cursor = __conn.execute("SELECT Train_" + str(t) + " \
            FROM StationOUT WHERE id >= "+str(idA)+" AND id <= "+ str(idB))
        addTrain = []
        count = 0
        
        for row in cursor:
            addTrain.append({"id" : count + idA, "time" : row[0]}) 
            count+=1

        if addTrain[0]['time'] != '':    
            if  addTrain[len(addTrain)-1]["time"] != '':
                train.append({"number":t, "Time" : addTrain})
                
    return train

def _getTableTrainByIDAtoB(number : int, idA : int, idB : int):
    train = []
    cursor = __conn.execute("SELECT Train_" + str(number) + " \
        FROM StationOUT WHERE id >= "+str(idA)+" AND id <= "+ str(idB))
    addTrain = []
    count = 0
    
    for row in cursor:
        addTrain.append({"id" : count + idA, "time" : row[0]}) 
        count+=1

    if addTrain[0]['time'] != '':    
        if  addTrain[len(addTrain)-1]["time"] != '':
                train.append({"number":number, "Time" : addTrain})
        else: return {"id":-1, "err":"dont't have time destination Train"}
    else: return {"id":-1, "err":"dont't have time Start Train"}

    return train

def _getTableTrainByID(numberTrain:int, ):
    cursor = __conn.execute('''SELECT id, station_name, Train_''' + str(numberTrain) + ''' FROM StationOUT WHERE Train_''' + str(numberTrain) + ''' != "" ''')
    addTrain = []

    for row in cursor:
        e = datetime.strptime(row[2], "%H:%M") - relativedelta(seconds=1)
        addTrain.append({"id":int(row[0]), "name":row[1], "Arr" : e.strftime("%H:%M"), "Dep":row[2]})
    
    return addTrain



# __createTable("StationOUT")
# _dataInsertOUT()
# __conn.close()

