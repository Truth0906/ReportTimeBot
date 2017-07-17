import traceback
import sys
import time
import json
import os.path
sys.path.append('..\\PTTCrawlerLibrary')
import PTT
print('Welcome to 準點報時機器人 v 1.0.17.0717')

Board = "Test"

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

PTTCrawler = PTT.Crawler(ID, Password, False)

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

if not PTTCrawler.isLoginSuccess():
    PTTCrawler.Log('Login fail')
else:
    #PTTCrawler.setLogLevel(PTTCrawler.LogLevel_DEBUG)

    First = True
    LastTime = ''
    
    while True:
    
        try:
        
            ErrorCode, Time = PTTCrawler.getTime()
            if ErrorCode != PTTCrawler.Success:
                PTTCrawler.Log('取得時間失敗')
                sys.exit()
            
            FileData, NextTimeString = readNextMinFile(Time)
            if FileData != None:
                FileDataList = FileData.split('\r\n')
                
                Title = FileDataList[0]
                
                Content = '\r\n'.join(FileDataList[1:])
                
                Title = Title.replace('{TIME}', NextTimeString)
                Content = Content.replace('{TIME}', NextTimeString)
                
                PTTCrawler.Log('偵測到報時檔案，將在一分鐘後在 ' + Board + ' 發文')
                
            if First:
                PTTCrawler.Log('成功啟動! 與 PTT 同步時間中')
                LastTime = Time
            else:
                time.sleep(50)
            
            while LastTime == Time:
                ErrorCode, Time = PTTCrawler.getTime()
                if ErrorCode != PTTCrawler.Success:
                    PTTCrawler.Log('取得時間失敗')
                    sys.exit()
            LastTime = Time
            if First:
                First = False
                PTTCrawler.Log('成功同步')
            
            PTTCrawler.Log(Time)
            
            if FileData == None:
                continue
            
            ErrorCode = PTTCrawler.post(Board, Title, Content, 2, 0)
            if ErrorCode == PTTCrawler.Success:
                PTTCrawler.Log('在 ' + Board + ' 板發文成功')
            elif ErrorCode == PTTCrawler.NoPermission:
                PTTCrawler.Log('發文權限不足')
            else:
                PTTCrawler.Log('在  ' + Board + ' 板發文失敗') 
        except KeyboardInterrupt:
            
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