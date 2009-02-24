#-*- coding: UTF-8 -*-
import flickr,image,imagecache
import urllib
from PIL import Image
import os

##### configs ######
SEARCH_LIST_FNAME = './searchlist.txt'
PROXY_FNAME = './proxy.txt'

# proxy
PROXY_INFO = {}
if os.path.exists(PROXY_FNAME):	
	f = open(PROXY_FNAME,'r')	
	s = f.read()	
	if len(s) > 0:
		PROXY_INFO = {'http': s }
	f.close()

print """Flickwall V0.1.0"""

PHOTO_SIZE = 'Large'		# photo size [Medium,Large]
SIZE = None			# cut size
PER_PAGE = 15				# per page size

LICENSES = ['All Rights Reserved','Attribution-NonCommercial-ShareAlike License','Attribution-NonCommercial License','Attribution-NonCommercial-NoDerivs License',
		'Attribution License','Attribution-ShareAlike License','Attribution-NoDerivs License','No known copyright restrictions']
		
DOWNLOAD_RESULT = [u'照片已不存在',u'成功',u'程序异常',u'文件已存在，跳过']

# proxy init
url_opener = urllib.URLopener(PROXY_INFO)
# flickr class proxy init
flickr.init(flickr,PROXY_INFO)

def _out_log(msg):	
	print msg
	
def _down_files(photos,folder=None):
	for p in photos:
		#_out_log(u'id:%s  |  title:%s   ' % (p.id,p.title))
		_out_log(u'正在下载:%s' % p.title)
		_out_log(u'状态:%s' % DOWNLOAD_RESULT[_down_file(p,folder)])

def _down_file(photo,folder=None):
	try:
		url = photo.getURL(PHOTO_SIZE,'source')
	except:
		return 0
	
	if folder == None:
		fpath = './data/photos/'
	else:
		fpath = './data/photos/%s/%s/' % (LICENSES[int(photo.license)],folder)

	if not os.path.exists(fpath):
		os.makedirs(fpath)

	fext = url.split('.')[-1]
	fname = '%s.%s' % (photo.title,fext)
	fsavename = '%s%s' % (fpath,fname)

	
	
	# 检查是否有缓存
	cache_key = photo.id
	
	try:
		im = imagecache.get(cache_key)
		
		# 检查最终文件是否存在
		exist_count = os.path.exists(fsavename)
		
		if (im != None and exist_count):
			return 3
		
		if(im == None):
			if exist_count > 0:
				fname = '%s-%s.%s' % (photo.title,exist_count+1,fext)
				fsavename = '%s%s' % (fpath,fname)
			url_opener.retrieve(url,fsavename)	
			im = Image.open(fsavename)
			imagecache.set(cache_key,im)
					
		if SIZE != None:
			new_size = SIZE
		else:
			new_size = im.size
			
		image.resize_image(im,fsavename,new_size,'flickr')
	except:
		return 2
	return 1
	
def get_favorites(email,per_page=PER_PAGE):
	fuser = flickr.people_findByEmail(email)
	_out_log(u"已经连接用户【%s】的图片收藏列表。" % fuser.username)
	photos = []
	_out_log(u'正在获取收藏列表...')
	try:
		photos = flickr.favorites_getPublicList(fuser.id,per_page)
	except:
		_out_log(u'Flick 服务超时，下载失败.')
		return 
	_out_log(u"收藏列表获取完成。")	
	down_files(photos)
	
		
def get_photos(email,per_page=PER_PAGE):
	fuser = flickr.people_findByEmail(email)
	_out_log(u"已经连接用户【%s】的相片列表。" % fuser.username)
	photos = []
	_out_log(u'正在获取相片列表...')
	try:
		photos = flickr.people_getPublicPhotos(fuser.id,per_page)
	except:
		_out_log(u'Flick 服务超时，下载失败.')
		return 
	_down_files(photos)

def search_photos(text,per_page=PER_PAGE):
	photos = []
	_out_log('Search likes %s photos...' % text)
	try:
		photos = flickr.photos_search(text=text,per_page=per_page)
	except:
		_out_log(u'Flick 服务超时，下载失败.')
		return 
	_out_log(u'找到 %s 张照片。' % len(photos))
	_down_files(photos,text)

# 用户数据
email = 'huacnlee@ymail.com'

def show_menu():	
	print """
MainMenu
1.Get Favorites		2.Get my photos		3.Search photos		0.Exit
	"""
	m = raw_input("Choice menu number:")
	count = raw_input("How many photos do you want get?")
	if m == '1':		
		get_favorites(email,count)
	elif m == '2':		
		get_photos(email,count)
	elif m == '3':
		search_texts = []
		if os.path.exists(SEARCH_LIST_FNAME):
			f = open(SEARCH_LIST_FNAME,'r')
			text = f.read()
			f.close()
			search_texts = text.split('\n')
		else:
			text = raw_input('Type the search keyword(e.g.:chengdu):')		
			search_texts = [text]
		for s in search_texts:
			if s != '':
				search_photos(s,count)
	elif m == '0':
		exit()
	else:
		os.system('cls')
		show_menu()
		return
		
	r = raw_input('Download done.Do you like get anthoer?(Y/N):')
	if str.lower(r) == 'y':
		show_menu()	
	
	
if __name__ == '__main__':	
	if not email:
		email = raw_input("Type your Flickr Username(Email address):")
	show_menu()
	