import traceback
import sys
import time
import json
import os.path
sys.path.append('..\\PTTCrawlerLibrary')
import PTT
print('Welcome to 準點報時機器人 v 1.0.17.0714')

Board = "Test"
Retry = True

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

def readTimeFile(Time):
    with open(Time.replace(':', '') + '.txt', encoding = 'utf-8-sig') as TimeFile:
        PostContentList = TimeFile.readlines()
    
    PostContentList = [x.strip() for x in PostContentList]
    result = '\r\n'.join(PostContentList)
    return result
    
PTTCrawler = PTT.Crawler(ID, Password, False)
if not PTTCrawler.isLoginSuccess():
    PTTCrawler.Log('Login fail')
else:
    #PTTCrawler.setLogLevel(PTTCrawler.LogLevel_DEBUG)

    First = True
    LastTime = ''
    
    WaitNexMin = False
    StartTime = 0
    
    while Retry:
        try:
            
            while True:
                
                if WaitNexMin:
                    WaitNexMin = False
                    EndTime = time.time()
                    
                    while EndTime - StartTime < 45:
                        time.sleep(45 - (EndTime - StartTime))
                        EndTime = time.time()
                    
                ErrorCode, Time = PTTCrawler.getTime()
                if ErrorCode != PTTCrawler.Success:
                    PTTCrawler.Log('Get time error')
                    continue
                if len(Time) < 5:
                    Time = '0' + Time
                if LastTime != Time:
                    LastTime = Time
                    if First:
                        First = False
                        PTTCrawler.Log('Start detect PTT time')
                        continue
                    break
            StartTime = time.time()
            WaitNexMin = True
            
            PTTCrawler.Log('Ptt time: ' + Time + '!')

            PostContent = PTTCrawler.readPostFile(Time.replace(':', '') + '.txt')
            if PostContent == None:
                continue
            
            ErrorCode = PTTCrawler.post(Board, '準點報時 ' + Time, PostContent, 2, 0)
            if ErrorCode == PTTCrawler.Success:
                PTTCrawler.Log('Post in ' + Board + ' success')
                PTTCrawler.Log(PostContent)
            elif ErrorCode == PTTCrawler.NoPermission:
                PTTCrawler.Log('發文權限不足')
            else:
                PTTCrawler.Log('Post in Test fail')
            
        except KeyboardInterrupt:
            '''
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            '''
            PTTCrawler.Log('Interrupted by user')
            PTTCrawler.logout()
            sys.exit()
        except EOFError:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            Retry = True
            break
        except ConnectionAbortedError:
            Retry = True
            break
        except Exception:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            Retry = True
            break