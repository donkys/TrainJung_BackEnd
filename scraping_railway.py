import sqlite3
import bs4
import requests
import json
import os
import time

import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

line_bot_api = LineBotApi('NPsaa2HVsAgdPyNpJ9VApz8QIvPWyipteTJ0X6Jd9mD+1iPV7Vd50L06BzPDrQSdGTl3t3D/9QqV0QsVXCxDmvrCXW8dIKWyoe+ey5PZpPGSYJGEoGoeCEES1Ad2gOjTJ1DnNYRdmMPjmt/Wx4tFrgdB04t89/1O/w1cDnyilFU=')


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
        addTrain.append({"id":row[0], "name": row[1], "time" : row[2]})
    
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

def _getInfoStation(id: int):
    cursor = __conn.execute('''SELECT id, station_name FROM StationOUT WHERE ''' + str(id) + ''' == id ''')
    string = []
    for row in cursor:
        row = list(row)
        string.append({"id" : str(row[0]) , "name" : str(row[1])})

    return string

def _getInfoName(id: int):
    cursor = __conn.execute('''SELECT id, station_name FROM StationOUT WHERE ''' + str(id) + ''' == id ''')
    string = []
    for row in cursor:
        row = list(row)
        string.append(str(row[1]))

    return string[0]

def _updatetime(idStation: int, numberTrain: int, time: str):
    # print("UPDATE StationOUT SET Train_" + str(numberTrain) + " = \"" + time +"\" WHERE id == "+ str(idStation))
    try:
        __conn.execute("UPDATE StationOUT SET Train_" + str(numberTrain) + " = \"" + time +"\" WHERE id == "+ str(idStation))
        __conn.commit()
    except sqlite3.Error as error:
        return {"id":"-1", "err": error}
    
    # message = "ตอนนี้รถไฟ หมายเลข :"+str(trainNumber) + "\n ปรับเวลาเป็น : "+time + + _getInfoName(idStation)
    _pushLineNotify(message)
    
    return {"id":0, "message":"Update "+ str(idStation) + ", Train_" + str(numberTrain) +" to " + str(time)+" Success"}

def _addStatus(idStation: int,trainNumber:int , onTime: bool, ms: str):
    status = ""
    message = ""
    if onTime:
        message = "ตอนนี้รถไฟ หมายเลข :"+str(trainNumber) + " \nมีสถานะ : On Time\n" + "มีรายละเอียด : " + ms + "\nแจ้งจากสถานี : " + _getInfoName(idStation)
    else: 
        message = "ตอนนี้รถไฟ หมายเลข :"+str(trainNumber) + " มีสถานะ : Delay\n" + "มีรายละเอียด : " + ms + "\nแจ้งจากสถานี : " + _getInfoName(idStation)  
    _pushLineNotify(message)
        
    return {"idStation":idStation, "Train":trainNumber, "Status":status, "Problem":message}

def _pushNotify(idStation: int, numberTrain: int, time: str, topic:str, message:str):
    #push notify function
    print("Notification : " + Station + " Train No." + numberTrain + " Change to " + numberTrain)

    return {"topic":topic + "[" + str(idStation) + "" + str(numberTrain) + "" + str(time) + "]", "Message":message}

def _pushLineNotify(str):
    try:
        line_bot_api.push_message('Udf4ee11552c59cd4a32cbc311fd0d744', TextSendMessage(text=str))
    except LineBotApiError as e:
        print(e)

def _home():
    with open('./Home.json', encoding="utf8") as json_file:
        data = json.load(json_file)
        return data
    return {"id":-1, "err":"can't open file"}

def _getNameTrain():
    with open('./nameoftrain.json', encoding="utf8") as json_file:
        data = json.load(json_file)
        return data    
    return {"id":-1, "err":"can't open file"}

# print(_getNameTrain())
# __createTable("StationOUT")
# _dataInsertOUT()
# __conn.close()

# _home()