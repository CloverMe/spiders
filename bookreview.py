# -*- coding: UTF-8 -*-
import os,urllib,urllib2,re,MySQLdb,time,getpass

tags = []
newtag = raw_input('Tag Url:')
tags.append(newtag)
mydb = raw_input('Database Name:')
mypasswd = getpass.getpass('Mysql Passwd:')
page = raw_input('Start Page:')

b_url = re.compile('''<a class="nbg" href="(.*?)"''')

b_name = re.compile('''<span property="v:itemreviewed">(.*?)</span>''')
b_isbn = re.compile('''<span class="pl">ISBN:</span>(.*?)<br/>''')
b_img = re.compile('''<a class="nbg".+?href="(.*?)"''',re.DOTALL)
b_author = re.compile('''作者</span>:.+?">(.*?)</a>''',re.DOTALL)

c_url = re.compile('''<a class="pl" href="(.*?)">''')

c_title = re.compile('''<h1>(.*?)</h1>''')
c_content = re.compile('''<span property="v:description" class="">(.*?)</span>''')
c_author = re.compile('''<span property="v:reviewer">(.*?)</span>''')
c_time = re.compile('''class="mn">(.*?)</span>''')
c_avatar = re.compile('''<img class="pil " src="(.*?)">''')

def getpage(url):
    time.sleep(2)
    print 'Page: ',url
    req = urllib2.Request(url)
    req.add_header("User-Agent","Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20100101 Firefox/21.0")
    req.add_header("If-None-Match","c1858c2845ca9501136ca83d624f8d4d")
    u = urllib2.urlopen(req).read()
    return u

def get_book(book_url):
    book_content_source = getpage(book_url) #book page source
    book_name = b_name.findall(book_content_source)[0].strip()
    book_img = b_img.findall(book_content_source)[0].strip()
    
    isbn = b_isbn.findall(book_content_source)
    if not isbn:
        print 'no isbn'
        return
    book_isbn = isbn[0].strip()
  
    author = b_author.findall(book_content_source)
    if not author:
        print 'no author'
        return
    book_author = author[0].strip()
    
    comment = c_url.findall(book_content_source)
    if not comment:
        print 'no comment'
        return
    comment_url = comment[0]
    
    if is_exist(comment_url):
        print 'exist'
    else:
        get_comment(book_name,book_isbn,book_img,book_author,comment_url)
    
def get_comment(book_name,book_isbn,book_img,book_author,comment_url):
    comment_content_source = getpage(comment_url)
    comment_title = c_title.findall(comment_content_source)[0].strip()
    comment_content = c_content.findall(comment_content_source)[0].strip()
    comment_author = c_author.findall(comment_content_source)[0].strip()
    comment_time = c_time.findall(comment_content_source)[0].strip()
    comment_avatar = c_avatar.findall(comment_content_source)[0]
    save_comment(book_name,book_isbn,book_img,book_author,comment_url,comment_title,comment_content,comment_author,comment_time,comment_avatar)
    
def save_comment(book_name,book_isbn,book_img,book_author,comment_url,comment_title,comment_content,comment_author,comment_time,comment_avatar):    
    timeArray = time.strptime(comment_time, "%Y-%m-%d %H:%M:%S")
    timestamp = int(time.mktime(timeArray))
    author_avatar = comment_avatar.replace('icon/u','icon/ul')#replace big avatar

    #print book_name,book_isbn,book_img,book_author,comment_url,comment_title,comment_author,comment_time,comment_avatar;
    
    connection = MySQLdb.connect(host='127.0.0.1', user='root', passwd=mypasswd, db=mydb,charset='utf8')
    cursor = connection.cursor()
    cursor.execute("INSERT INTO collect_bookreview(`url`,`title`,`type`,`img`,`content`,`author`,`author_avatar`,`book_name`,`book_author`,`book_isbn`,`status`,`created`)\
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (comment_url,comment_title,'bookreview',book_img,comment_content,comment_author,author_avatar,book_name,book_author,book_isbn,'0',timestamp))
    connection.close()
      
def is_exist(comment_url):
    connection = MySQLdb.connect(host='127.0.0.1', user='root', passwd=mypasswd, db=mydb,charset='utf8')
    cursor = connection.cursor()
    isexist = cursor.execute("SELECT url FROM `collect_bookreview` where url = '"+comment_url+"'")
    connection.close()
    if isexist:
        return True
    else:
        return False
    
def main():
    for tag in tags:
        print tag
        i = int(page)
        while(i < 1000):
            url = tag + '?start='+str(i) + '&type=T'
            list_content_source = getpage(url) #list page source
            book_urls = b_url.findall(list_content_source)
            for book_url in book_urls: 
                get_book(book_url)
            i = i + 20

if __name__ == '__main__':
    main()
