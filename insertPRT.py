from urllib import request
from bs4 import BeautifulSoup
import re
import cx_Oracle
import os

# 変数設定
res = []
rows = []

# onairlistの最新日付取得
con=cx_Oracle.connect(user='calbeez',password='.Hondavfr400',dsn='db202008140156_low')
cur = con.cursor()

sql ="select max(year) from  calbeez.onairlist"
cur.execute(sql)
res = cur.fetchone()
maxy = res[0]

sql ="select max(month) from  calbeez.onairlist where year = " +  str(maxy)
cur.execute(sql)
res = cur.fetchone()
maxm = res[0]

sql ="select max(day) from  calbeez.onairlist where year = " +  str(maxy) + " and month = " + str(maxm)
cur.execute(sql)
res = cur.fetchone()
maxd = res[0]

last_date = str(maxy) + "/" + str(maxm) + "/" + str(maxd)

# オンエアリストの正規表現
date_pattern = re.compile('(\d{4})/(\d{1,2})/(\d{1,2})')
time_pattern = re.compile('(^[\s0-9]{1,2}):([0-9]{2})')
list_pattern = re.compile('(^[\s0-9]{1,2}):([0-9]{2})：　(.+)：　(.+)')
list_pattern2 = re.compile('(^[\s0-9]{1,2}):([0-9]{2})\s+(.+)\s\s+(.+)')

# Webスクレイピング
url = 'https://herrkf.com/prtonair/'
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
        exit

    if last_date == prt_date.group(0):
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
            row = (prt_max, prt_date.group(1), 
                   prt_date.group(2), 
                   prt_date.group(3), 
                   prt_list.group(1), 
                   prt_list.group(2), 
                   '"'+prt_list.group(3).strip()+'"',
                   '"'+prt_list.group(4).strip()+'"')
            rows.append(row)

# onairlistへのinsert
if len(rows) != 0:
    try:
        cur.executemany("insert into calbeez.onairlist(maximum, year, month, day, hour, minute, title, artist) values (:1, :2, :3, :4, :5, :6, :7, :8)", rows)
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(error.message)
    else:
        con.commit()
        print(len(rows), " rows inserted.")
    finally:
        cur.close()
        con.close()
else:
    print("On air list is not found.")
