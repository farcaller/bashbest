#!/usr/bin/env python

from objc import *
from Foundation import *
import re, datetime

RX_DATE = r'.*(\d{4,4}-\d{2,2}-\d{2,2}).*(\d{2,2}:\d{2,2}).*'

def fetch_quote(i):
	if type(i) == int:
		u = NSURL.URLWithString_('http://bash.org.ru/quote/%d' % (i, ))
	else:
		u = NSURL.URLWithString_(i)
	doc,err = NSXMLDocument.alloc().initWithContentsOfURL_options_error_(u, NSXMLDocumentTidyHTML, None)
	if err and err.domain() != u'NSXMLParserErrorDomain':
		raise Exception(err)
	else:
		root = doc.rootElement()
		n, err = root.nodesForXPath_error_("/html/body/div[@id='page']/div[@id='quotes']/div[1]/div[2]", None)
		quote = u""
		for sn in n[0].children():
			if sn.kind() == 7:
				quote += sn.stringValue()
			elif sn.kind() == 2 and sn.name() == 'br':
				quote += '\n'
		#quote = quote.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
		n, err = root.nodesForXPath_error_("/html/body/div[@id='page']/div[@id='quotes']/div[1]/div[1]/span", None)
		rate = int(str(n[0].children()[0]))
		n, err = root.nodesForXPath_error_("/html/body/div[@id='page']/div[@id='quotes']/div[1]/div[1]", None)
		dt, hr = RX_DATE.match(n[0].stringValue()).groups()
		return i, rate, quote, dt, hr

def fetch_quotes(start, end, known=None):
	l = {}
	if known:
		l = known
	
	for i in range(start,end+1):
		if str(i) in l: continue
		
		print "fetching %d..." % (i, )
		try:
			i, r, q, d, h = fetch_quote(i)
		except:
			print "   failed :("
			continue
		yy,mo,da = d.split('-')
		hr,mi = h.split(':')
		dt = datetime.datetime(yy,mo,da,hr,mi)
		l[str(i)] = dict(rate=r, quote=q, date=dt)
	
	return l

def resort_quotes(d):
	from operator import itemgetter
	l = []
	for k,v in d.iteritems():
		l.append(v)
	return sorted(l, key=itemgetter('rate'), reverse=True)
	

if __name__ == '__main__':
	import sys, plistlib
	if sys.argv[1] == 'fetch':
		s,e,f = sys.argv[2:]
		q = fetch_quotes(int(s),int(e))
		d, e = NSPropertyListSerialization.dataFromPropertyList_format_errorDescription_(q, NSPropertyListXMLFormat_v1_0, None)
		d.writeToFile_atomically_(f, YES)
	elif sys.argv[1] == 'sort':
		d = plistlib.readPlist(sys.argv[2])
		l = resort_quotes(d)
		for i in l:
			print i['quote'].encode('utf8')
