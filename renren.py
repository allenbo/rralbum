#!/usr/bin/python
#coding=utf-8
import sys
import urllib2
import urllib
import re
import cookielib

reload(sys)
sys.setdefaultencoding('utf-8')

""" function to deal with personal shared album"""

def get_raw_img_url_from_data(data):
    match = re.findall('large:\'([^\']*)\'', data)
    if match:
        raw_url = set(match)
    else:
        raw_url = set()
    return raw_url

def download_img_from_url(url, filename) :
    req = urllib2.Request(url)
    fd = opener.open(req)
    total_try = 5
    cur_try = 0
    while cur_try < total_try:
        try:
            data = fd.read()
            open(filename, "wb").write(data)
        except:
            print 'From', url, 'download file', filename,'faild, try again'
            cur_try += 1
        else:
            break
        

def url_get_photo_count(data):
    match = re.search('(\d+)张照片', data)
    if match: return int(match.group(1))
    else:
        return 0
        
def get_url_from_ajax_return(data):
    link_str = data.split('"largeUrl":"')[1:]
    link = set()
    for s in link_str:
        link.add(s.split('"')[0].replace('\\',''))
    return link

def get_url_from_ajax(url, photo_number):
    cur_num = 0
    ajax_call = 1
    raw_url = set()
    global opener
    while cur_num < photo_number:
        ajax_link = url + '/bypage/ajax?curPage=' + str(ajax_call*3) +'&pagenum=3'
        fd = opener.open(ajax_link)
        extend = get_url_from_ajax_return(fd.read())
        raw_url |= extend
        ajax_call += 1
        cur_num += len(extend)
    return raw_url

""" function to deal with public page shared album """

def get_real_url_from_public_shared_album(data, url):
    datas = []
    datas.append(data)
    curpage = 0

    while datas[curpage].find('下一页') != -1:
        curpage += 1
        req = urllib2.Request(album_url+'?curpage='+str(curpage))
        try:
            fd = opener.open(req)
        except:
            print 'Url ' + album_url + '?curpage='+str(curpage) + 'open error'
            sys.exit(0)
        datas.append(fd.read())
        print 'find a another next page ' + str(curpage)
        
    prefix = album_url[album_url.find('/')+len('//page.renren.com'):album_url.rfind('/')+1]
    prefix = prefix.replace('album', 'photo')
    restr = 'a href=\"'+prefix+'(\d+)\"'
    url_contains_real_url = []
    for d in datas:
        match = re.findall(restr,d)
        if match:
            url_contains_real_url.extend(match)
    prefix = url[:url.rfind('/')].replace('album', 'photo')
    urls = [prefix + '/' + x for x in url_contains_real_url]
    
    real_urls = set()
    for url in urls:
        req = urllib2.Request(url) 
        try:
            fd = opener.open(req)
        except:
            print 'Url ' + url + 'open error'
            sys.exit(0)
        data = fd.read()
        
        real_urls.add(data.split('\"largeurl\":\"')[1].split('\"')[0].replace('\\', ''))
    return real_urls

        

header = {'Host':'www.renren.com', 'User-Agent':'Mozilla/5.0 (X11;Ubuntu;Linux i686,rv:10.02)\
        Gecko/20100101 Firefox 10.0.2', 'Accept':'text/html,application/xhtml+xml,\
        application/xml;q=0.9,*/*;q=0.8', 'Accept-Language':'en-us,en;q=0.5',\
        'Connection':'keep-alive'}

cookiesjar = cookielib.CookieJar()
cookiehandler = urllib2.HTTPCookieProcessor(cookiesjar)
opener = urllib2.build_opener(cookiehandler)

opener.open('http://www.renren.com')
post_data = { 'email':'*******',\
        'password':'*****',\
        'icode':'',\
        'origURL':'http://www.renren.com/indexcon',\
        'domain':'renren.com',\
        'key_id':'1',\
        'captcha_tpye':'web_login',\
        '_rtk':'91cdffe3'}

req = urllib2.Request('http://www.renren.com/PLogin.do', headers = header, data = urllib.urlencode(post_data))

try:
    fd = opener.open(req)
except urllib2.HTTPError, e:
    print e
    sys.exit(0)

print 'Login in successfully'
print 'Please input the album address you wan to download:'
raw_album_url = raw_input()


if raw_album_url.find('curPage') != -1:
    album_url = raw_album_url.split('?')[0]
else:
    album_url = raw_album_url

req =urllib2.Request(album_url)
try:
    fd = opener.open(req)
except urllib2.HTTPError, e:
    print 'Url '+album_url+' open error'
    sys.exit(0)
data = fd.read()
raw_url = set()
if album_url.find('page.renren.com') != -1: #download from public shared album
    raw_url = get_real_url_from_public_shared_album(data, album_url)
else:
    photo_count = url_get_photo_count(data)
    print 'There are', photo_count, 'to download'
    #print data
    raw_url = get_raw_img_url_from_data(data)

    if not raw_url:
       print "There are no image link in this url, please check the url you enter"
       sys.exit(1)

    if len(raw_url) < photo_count:
        raw_url |= get_url_from_ajax(album_url, photo_count - len(raw_url))

count = 0
for url in raw_url:
    filename = url[url.rfind('_')+1:]
    download_img_from_url(url, filename)
    print filename, "finished"
    count = count + 1
    if count % 20 == 0:
        print count, 'File finished ===='
print 'All file finished'
