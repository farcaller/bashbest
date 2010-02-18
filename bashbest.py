#!/usr/bin/env python

import re, datetime, urllib, plistlib, sys
from lxml import etree

RX_DATE = re.compile(r'.*(\d{4,4}-\d{2,2}-\d{2,2}).*(\d{2,2}:\d{2,2}).*')

def fetch_quote(i):
    if type(i) == int:
        u = 'http://bash.org.ru/quote/%d' % (i, )
    else:
        u = i
    
    data = urllib.urlopen(u).read()
    html = etree.HTML(data)
    
    div = html.xpath("/html/body/div[@id='page']/div[@id='quotes']/div[1]/div[2]")[0]
    quote_text = ''.join([div.text,]+['\n'+br.tail for br in div.getchildren()]+[div.tail,])
    rate = int(html.xpath("/html/body/div[@id='page']/div[@id='quotes']/div[1]/div[1]/span")[0].text)
    date = RX_DATE.search(html.xpath("/html/body/div[@id='page']/div[@id='quotes']/div[1]/div[1]/a[4]")[0].tail.strip()).groups()
    yy,mo,da = date[0].split('-')
    hr,mi = date[1].split(':')
    return dict(quote=quote_text, rate=rate, date=datetime.datetime(int(yy),int(mo),int(da),int(hr),int(mi)))

def fetch_quotes(start, end, known=None):
    l = {}
    if known:
        l = known
    
    for i in range(start,end+1):
        if str(i) in l: continue
        
        print "fetching %d..." % (i, )
        try:
            quote = fetch_quote(i)
        except:
            print "   failed :("
            continue
        l[str(i)] = quote
    
    return l

def resort_quotes(d):
    from operator import itemgetter
    l = []
    for k,v in d.iteritems():
        l.append(v)
    return sorted(l, key=itemgetter('rate'), reverse=True)
    

if __name__ == '__main__':
    if sys.argv[1] == 'fetch':
        s,e,f = sys.argv[2:]
        q = fetch_quotes(int(s),int(e))
        plistlib.writePlist(q, f)
    elif sys.argv[1] == 'sort':
        d = plistlib.readPlist(sys.argv[2])
        l = resort_quotes(d)
        for i in l:
            print i['quote'].encode('utf8')
