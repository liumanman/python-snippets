import os,sys,urllib2

PROXY_INFO = {
	'user' : 'hs.li' ,
	'pass' : 'huacnlee' ,
	'host' : '172.28.10.204' ,
	'port' : 8080
}

def load_url(url):	
	proxy_support = urllib2 . ProxyHandler ( { 'http' : \
	'http://%(user)s:%(pass)s@%(host)s:%(port)d' % PROXY_INFO } ) 
	opener = urllib2.build_opener(proxy_support,urllib2.HTTPHandler)
	urllib2 . install_opener(opener) 
	src = urllib2.urlopen(url)
	return src.read()
	
if __name__=='__main__':
	print load_url("http://www.google.com")
