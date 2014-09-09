# -*- coding: UTF-8 -*-
import os,urllib,urllib2,re,MySQLdb,time,getpass

notes = []
newurl = raw_input('Note List Url:')
notes.append(newurl)
mydb = raw_input('Database Name:')
mypasswd = getpass.getpass('Mysql Passwd:')

p_url = re.compile('''<a title=".+?href="(.*?)".+?</a>''')
p_prev = re.compile('''<link rel="prev" href="(.*?)"/>''')

a_title = re.compile('''<div class="note-header note-header-container">.+?<h1>(.*?)</h1>.+?<div>''',re.DOTALL)
a_time = re.compile('''<span class="pl">20(.*?)</span>''')
a_content = re.compile('''<div class="note" id="link-report">(.*?)</div>''')
a_author = re.compile('''<img width="48" height="48" src=".+?" alt="(.*?)">''')

def getpage(url):
    time.sleep(3)
    print 'start page: ',url
    req = urllib2.Request(url)
    req.add_header("User-Agent","Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20100101 Firefox/21.0")
    req.add_header("If-None-Match","c1858c2845ca9501136ca83d624f8d4d")
    u = urllib2.urlopen(req).read()
    return u

def getprevpos(content,pattern):
    r = pattern.findall(content)
    for x in r: 
        #print 'find prev: ',x
        return x
def get_article(content,pattern):
    aurls = pattern.findall(content)
    for aurl in aurls[::-1]: 
        #print 'article url: ',aurl
        save_article(aurl)

def save_article(url):
    connection = MySQLdb.connect(host='127.0.0.1', user='root', passwd=mypasswd, db=mydb,charset='utf8')
    cursor = connection.cursor()
    isexist = cursor.execute("SELECT url FROM `collect_douban` where url = '"+url+"'")
    connection.close()
    if isexist:
        print 'exist'
    else:
        page_content = getpage(url)
        title = a_title.findall(page_content)[0].strip()
        created = '20' + a_time.findall(page_content)[0]
        content = a_content.findall(page_content)[0]
        author = a_author.findall(page_content)[0]

        timeArray = time.strptime(created, "%Y-%m-%d %H:%M:%S")
        timestamp = int(time.mktime(timeArray))

        insert_db(title,content,author,timestamp,url)

def insert_db(title,content,author,timestamp,url):
    connection = MySQLdb.connect(host='127.0.0.1', user='root', passwd=mypasswd, db=mydb,charset='utf8')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO collect_douban(`url`,`title`,`type`,`content`,`author`,`status`,`created`)VALUES(%s,%s,%s,%s,%s,%s,%s)", (url,title,'note',content,author,'0',timestamp))
    connection.close()
def main():
    for note in notes:
        url = note
        while(True):
            listcontent = getpage(url)
            get_article(listcontent,p_url)
            prev_url = getprevpos(listcontent,p_prev)
            if prev_url is None:
                break
            else:
                url = prev_url

if __name__ == '__main__':
    main()
