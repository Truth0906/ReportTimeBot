
"""

"""

import requests
from bs4 import BeautifulSoup

def clearTag(String):
    String = str(String)
    
    String = String.replace('<BR>', '\r\n')
    String = String[:String.find('更新時間:')]
    
    while String.endswith('\r') or String.endswith('\n'):
        String = String[: len(String) - 1]
    
    while '<' in String and '>' in String:
        String = String.replace(String[String.find('<') : String.find('>') + 1], '')
    return String
def getweather():
    result = ''
    TargetURLList=['http://www.cwb.gov.tw/V7/forecast/taiwan/Hsinchu_City.htm',
                   'http://www.cwb.gov.tw/V7/forecast/taiwan/Taichung_City.htm']
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
        Temp += clearTag(res.text) + ''
        result += Temp
        
    return result
    
Weather = getweather()
print(Weather)
