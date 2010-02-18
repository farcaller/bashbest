#!/usr/bin/env python
# Bash Best
# http://github.com/farcaller/bashbest
#
# Copyright (c) 2010 Vladimir Pouzanov <farcaller@gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import re, datetime, urllib, plistlib, sys, os
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
        v['id'] = k
        l.append(v)
    return sorted(l, key=itemgetter('rate'), reverse=True)
    

if __name__ == '__main__':
    if sys.argv[1] == 'fetch':
        s,e,f = sys.argv[2:]
        if os.path.isfile(f):
            d = plistlib.readPlist(f)
        else:
            d = None
        q = fetch_quotes(int(s),int(e), d)
        plistlib.writePlist(q, f)
    elif sys.argv[1] == 'sort':
        d = plistlib.readPlist(sys.argv[2])
        l = resort_quotes(d)
        for i in l:
            print "** ID %7s ** RATE %s ** %s **" % (i['id'], i['rate'], i['date'])
            print i['quote'].encode('utf8')
