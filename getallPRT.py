from urllib import request
from bs4 import BeautifulSoup
import re
import sys

date_pattern = re.compile('(\d{4})/(\d{1,2})/(\d{1,2})')
time_pattern = re.compile('(^[\s0-9]{1,2}):([0-9]{2})')
list_pattern = re.compile('(^[\s0-9]{1,2}):([0-9]{2})：　(.+)：　(.+)')
list_pattern2 = re.compile('(^[\s0-9]{1,2}):([0-9]{2})\s+(.+)\s\s+(.+)')

for c in range(1,88):
    url = 'https://herrkf.com/prtonair/page/' + str(c) + '/'
#    url = 'https://herrkf.com/prtonair/2020/01/13/3797/' # Maximum PRT
#    url = 'https://herrkf.com/prtonair/2020/04/26/3843/' # 冒頭にコメントあり
#    url = 'https://herrkf.com/prtonair/2019/02/17/3626/' # 時間の前にスペースあり
#    url = 'https://herrkf.com/prtonair/2013/12/23/2843/' # NHK FMのため除外
#    url = 'https://herrkf.com/prtonair/2012/09/09/2671/' # titleがプレイリスト
#    url = 'https://herrkf.com/prtonair/2011/02/27/2307/' # 冒頭に複数行のコメントあり
#    url = 'https://herrkf.com/prtonair/2011/01/10/2220/' # P=>Div
#    url = 'https://herrkf.com/prtonair/2011/01/09/2207/' # :=>Space
#    url = 'https://herrkf.com/prtonair/2010/09/12/696/'  # div id 3桁

    print(c, file=sys.stderr)

    response = request.urlopen(url)
    soup = BeautifulSoup(response, 'lxml')
    
    prt_indexes = soup.find_all('div',id=re.compile('post-\d{3,4}'))
    for i in prt_indexes:
        prt_title = i.select('h1')[0].text
        if re.match('Maximum Power Rock Today',prt_title):
            prt_max = "1"
            prt_date = date_pattern.search(prt_title)
        elif re.match('Power Rock Today',prt_title):
            prt_max = "0"
            prt_date = date_pattern.search(prt_title)
        else:
            break

        prt_contents = i.select('div.entry-content')[0]

        for t in i.select('br'):
            t.replace_with('\n')
            
        prt_lists = ''

        for c2 in prt_contents.select('p'):
            c3 = c2.get_text(strip=True)
            if time_pattern.search(c3):
                prt_lists += c2.get_text()
                
        for c2 in prt_contents.select('div'):
            c3 = c2.get_text(strip=True)
            if time_pattern.search(c3):
                prt_lists += c2.get_text()
                    
        for t2 in prt_lists.split("\n"):
            if list_pattern.search(t2):
                prt_list = list_pattern.search(t2)
            elif list_pattern2.search(t2):
                prt_list = list_pattern2.search(t2)
            else:
                prt_list = 0
                
            if prt_list != 0: 
                print(prt_max,
                    prt_date.group(1),
                    prt_date.group(2),
                    prt_date.group(3),
                    prt_list.group(1),
                    prt_list.group(2),
                    '"'+prt_list.group(3).strip()+'"',
                    '"'+prt_list.group(4).strip()+'"',
                    sep=',')
