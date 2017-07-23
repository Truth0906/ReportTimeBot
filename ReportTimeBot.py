import traceback
import sys
import time
import json
import os.path
from time import gmtime, strftime
sys.path.append('..\\PTTCrawlerLibrary')
import PTT
import threading
import requests
from bs4 import BeautifulSoup

print('Welcome to 準點報時機器人 v 1.0.17.0723')

Board = "Wanted"
#Board = "Test"
# If you want to automatically login define Account.txt
# {"ID":"YourID", "Password":"YourPW"}
try:
    with open('Account.txt', encoding = 'utf-8-sig') as AccountFile:
        Account = json.load(AccountFile)
        ID = Account['ID']
        Password = Account['Password']
    print('Auto ID password mode')
except FileNotFoundError:
    ID = input('Input ID: ')
    Password = getpass.getpass('Input password: ')

def Log(InputMessage, ends='\r\n'):
    TotalMessage = "[" + strftime("%Y-%m-%d %H:%M:%S") + "] " + InputMessage
    print(TotalMessage.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding), end=ends)

def clearTag(String):
    String = str(String)
    
    String = String.replace('<BR>', '\r\n')
    String = String[:String.find('更新時間:')]
    
    while '<' in String and '>' in String:
        String = String.replace(String[String.find('<') : String.find('>') + 1], '')
    
    while String.endswith('\r') or String.endswith('\n') or String.endswith(' '):
        String = String[: len(String) - 1]
    
    return String

def getweather():
    result = ''
    TargetURLList=['http://www.cwb.gov.tw/V7/forecast/taiwan/Hsinchu_City.htm'
                   #, 'http://www.cwb.gov.tw/V7/forecast/taiwan/Taichung_City.htm'
                   ]
    LocationList=['新竹', '台中']
    
    for i in range(len(TargetURLList)):

        TargetUrl = TargetURLList[i]
        
        res=requests.get(
            url=TargetUrl,
            timeout=3
        )
        res.encoding = 'utf-8-sig'
        
        WebUrl = res.text[res.text.find('readTXT(\'/V7/forecast/taiwan/Data'):]
        WebUrl = WebUrl[:WebUrl.find('txt') + 3]
        WebUrl = 'http://www.cwb.gov.tw/' + WebUrl[10:]
        
        res=requests.get(
            url=WebUrl,
            timeout=3
        )
        res.encoding = 'utf-8-sig'
        
        Temp = LocationList[i] + '地區:\r\n\r\n'
        Temp += clearTag(res.text)
        result += Temp
        
    return result
    
PTTCrawler = PTT.Crawler(ID, Password, False)

Time = ''
LastTime = ''

Running = True

def readNextMinFile(Time):
    
    MinTemp = int(Time[3:]) + 1
    HourTemp = int(Time[:2])
    
    if MinTemp >= 60:
        MinTemp = MinTemp % 60
        HourTemp = (HourTemp + 1) % 24
    
    StringHour = str(HourTemp)
    if len(StringHour) == 1:
        StringHour = '0' + StringHour
    
    StringMin = str(MinTemp)
    if len(StringMin) == 1:
        StringMin = '0' + StringMin
    
    NextTime = StringHour + StringMin
    
    return PTTCrawler.readPostFile(NextTime + '.txt') , StringHour + ':' + StringMin

def showTime():

    while Running:
        Log('PTT 時間: ' + Time, '\r')
        time.sleep(1)
        
if not PTTCrawler.isLoginSuccess():
    PTTCrawler.Log('Login fail')
else:
    #PTTCrawler.setLogLevel(PTTCrawler.LogLevel_DEBUG)

    First = True
    Init = False
    
    while True:
        Init = False
        try:
            ErrorCode, Time = PTTCrawler.getTime()
            if ErrorCode != PTTCrawler.Success:
                PTTCrawler.Log('取得時間失敗，初始化所有狀態')
                First = True
                LastTime = ''
                continue
            
            FileData, NextTimeString = readNextMinFile(Time)
            if FileData != None:
                FileDataList = FileData.split('\r\n')
                
                Title = FileDataList[0]
                
                Content = '\r\n'.join(FileDataList[1:])
                
                Title = Title.replace('{TIME}', NextTimeString)
                Content = Content.replace('{TIME}', NextTimeString).replace('{WEATHER}', getweather())
                
                PTTCrawler.Log('偵測到報時檔案，將在一分鐘後在 ' + Board + ' 發文')
                
            if First:
                PTTCrawler.Log('成功啟動! 與 PTT 同步時間中')
                LastTime = Time
            else:
                # Wait 50 sec
                StartTime = time.time()
                EndTime = 0
                
                while EndTime - StartTime < 50:
                    time.sleep(1)
                    ErrorCode, Time = PTTCrawler.getTime()
                    EndTime = time.time()
                    
            while LastTime == Time:
                ErrorCode, Time = PTTCrawler.getTime()
                if ErrorCode != PTTCrawler.Success:
                    PTTCrawler.Log('取得時間失敗，初始化所有狀態')
                    First = True
                    LastTime = ''
                    Init = True
                    break
            if Init:
                continue
            
            LastTime = Time
            if First:
                First = False
                PTTCrawler.Log('成功同步')
                
                threading.Thread(target = showTime).start()
                
            if FileData != None:
                ErrorCode = PTTCrawler.post(Board, Title, Content, 2, 0)
                if ErrorCode == PTTCrawler.Success:
                    PTTCrawler.Log(Time + ' 在 ' + Board + ' 板發文成功')
                elif ErrorCode == PTTCrawler.NoPermission:
                    PTTCrawler.Log('發文權限不足')
                else:
                    PTTCrawler.Log(Time + ' 在  ' + Board + ' 板發文失敗')
            
        except KeyboardInterrupt:
            # CTRL + C
            Running = False
            PTTCrawler.Log('使用者中斷')
            PTTCrawler.logout()
            sys.exit()
        except EOFError:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            Running = True
            break
        except ConnectionAbortedError:
            Running = True
            break
        except Exception:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            Running = True
            break