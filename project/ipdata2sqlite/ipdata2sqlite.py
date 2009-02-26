# -*- coding: utf-8 -*-
#!/usr/bin/python
import sqlite3,os,traceback
import re



# ####################################
# config
# ####################################
SQLITE_DB_PATH = './ipdata.sqlite'
IPDATA_TEXT_PATH = './ipdata.txt'
AREA_TEXT_PATH = './areas.txt'
CHARSET = 'gb2312'

# ####################################
# common function
# ####################################
def _bin2int(s):
	r = 0
	for i in range(0,len(s)):
		r += ord(s[i])*pow(256,i)
	return r

def _bin2ip(s):
	return "%d.%d.%d.%d" % ( ord(s[3]),ord(s[2]),ord(s[1]),ord(s[0]))

def _int2ip(i):
	return "%d.%d.%d.%d" % (i/(256*256*256), (i%(256*256*256))/(256*256),(i%(256*256))/(256), i%256)

def _ip2int(ip):
	m = re.match('^(\d+)\.(\d+)\.(\d+)\.(\d+)$',ip)
	if not m:
		return 0
	else:
		return int(m.group(1))*256*256*256+int(m.group(2))*256*256+int(m.group(3))*256+int(m.group(4));

def _out_log(msg,type=1):
	if type == 1:
		print 'info:  %s' % msg
	else:
		print 'error: %s' % msg


# ####################################
# generate db
# ####################################
def gen_db():
	ipdata_text  = raw_input('Type the IPData text database file path:')
	area_text  = raw_input('Type the Area text database file path:')
	if len(ipdata_text) == 0:
		ipdata_text = IPDATA_TEXT_PATH
	if len(area_text) == 0:
		area_text = AREA_TEXT_PATH
		
	conn = sqlite3.connect(SQLITE_DB_PATH)
	cur = conn.cursor()
	
	
	# drop old table		
	_out_log('Dropping the old data...')
	try:
		cur.execute('DROP TABLE "main"."address"')
	except:
		_out_log(str(traceback),0)
		
	
	cur.execute('''CREATE  TABLE "main"."address" 
	("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , 
	"start" INTEGER NOT NULL , 
	"end" INTEGER NOT NULL , 
	"province" VARCHAR NOT NULL , 
	"city" VARCHAR NOT NULL , 
	"location" VARCHAR,
	"area_id" INTEGER NOT NULL ,
	"area_type" INTEGER NOT NULL, 
	"parent_id" INTEGER NOT NULL, 
	"ip_start" VARCHAR NOT NULL,
	"ip_end" VARCHAR NOT NULL )
	''')
	
	
	# ###############################
	# import data from text to db
	# ###############################
	_out_log('Text database loading...')
	
	# update areas ip_start & ip_end
	# load areas.txt db
	f = open(area_text,'r')
	txt = f.read()
	f.close()
	areas = txt.split('\n')
	
	# load ipdata.txt db	
	f = open(ipdata_text,'r')
	txt = f.read()
	f.close()
	iplines = txt.split('\n')
	
	# convert & save to sqlite database
	line_count = 0
	for ipline in iplines:
		line_count += 1
		
		# if line_count == 1000:break
		
		try:
			i_id,start,end,province,city = ipline.split('|')			
			area_id,area_type,parent_id = -1,-1,-1
		except:
			_out_log('line %s convert error.%s' % (line_count,str(traceback)),2)
			continue
		
		# convert to real IP address
		ip_start,ip_end = _int2ip(int(float(start))),_int2ip(int(float(end)))
		
		_out_log('Insert <%s|%s> line:%s' % (province,city,line_count))
		
		# get ytrip areaid & areatype
		for area in areas:
			a_id,a_name,a_slug,a_parent,a_type = area.split('|')
			if province == a_name and (a_name.find(city) == -1 or city.find(a_name) == -1):
				area_id,area_type,parent_id = a_id,a_type,a_parent
				break
				
		for area in areas:
			a_id,a_name,a_slug,a_parent,a_type = area.split('|')
			if a_name.find(city) != -1 or city.find(a_name) != -1:
				area_id,area_type,parent_id = a_id,a_type,a_parent
				break		
				
		try:
			cur.execute('''INSERT INTO "main"."address" 
			("start","end","province","city","location","area_id","area_type","parent_id","ip_start","ip_end") 
			VALUES (%s,%s,"%s","%s","%s","%s",%s,%s,"%s","%s")
			''' % (start,end,province.decode(CHARSET),city.decode(CHARSET),'',area_id,area_type,parent_id,ip_start,ip_end))
		except:
			_out_log(str(traceback),0)
	# save db
	conn.commit()
	cur.close()
			

	_out_log('Gernate done.Record count:%s' % line_count)
	
def gen_min_db():
	conn = sqlite3.connect(SQLITE_DB_PATH)
	cur = conn.cursor()
	
	# Drop old table
	try:
		cur.execute('DROP TABLE "main"."address_min"')
	except:
		_out_log(str(traceback))
	
	# Create new table
	cur.execute('''CREATE  TABLE "main"."address_min" 
	("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , 
	"start" INTEGER NOT NULL , 
	"end" INTEGER NOT NULL , 
	"province" VARCHAR NOT NULL , 
	"city" VARCHAR NOT NULL , 
	"area_id" INTEGER NOT NULL ,
	"area_type" INTEGER NOT NULL, 
	"parent_id" INTEGER NOT NULL, 
	"ip_start" VARCHAR NOT NULL,
	"ip_end" VARCHAR NOT NULL )
	''')
	
	# group the old areas data
	_out_log('Groupping the old address infos.')
	cur.execute('''SELECT min(start) as start,max(end) as end,province,city,area_id,area_type,parent_id 
	FROM address
	GROUP BY province,city,area_id,area_type,parent_id
	''')
	
	# insert new data to table [address_min]
	cur1 = conn.cursor()
	for row in cur:
		ip_start,ip_end = _int2ip(int(row[0])),_int2ip(int(row[1]))
		_out_log('Insert <%s|%s>' % (row[2],row[3]))
		cur1.execute('''INSERT INTO "main"."address_min" 
			("start","end","province","city","area_id","area_type","parent_id","ip_start","ip_end") 
			VALUES (%s,%s,"%s","%s",%s,%s,%s,"%s","%s")
			''' % (row[0],row[1],row[2],row[3],row[4],row[5],row[6],ip_start,ip_end))
			
	# save db
	conn.commit()
	cur.close()
	cur1.close()

	_out_log('Gernate address_min done.')
	
def gen_area():
	area_text  = raw_input('Type the Area text database file path:')
	if len(area_text) == 0:
		area_text = AREA_TEXT_PATH

	conn = sqlite3.connect(SQLITE_DB_PATH)
	cur = conn.cursor()
	
	# Drop old table
	try:
		cur.execute('DROP TABLE "main"."area"')
	except:
		_out_log(str(traceback))

	# Create new table
	cur.execute('''CREATE  TABLE "main"."area" 
	("id" INTEGER PRIMARY KEY NOT NULL , 	
	"name" VARCHAR NOT NULL , 
	"slug" VARCHAR NOT NULL , 
	"parent_id" INTEGER NOT NULL ,
	"area_type" INTEGER NOT NULL)
	''')
	
	# load areas.txt db
	f = open(area_text,'r')
	txt = f.read()
	f.close()
	areas = txt.split('\n')
	
	for area in areas:
		a_id,a_name,a_slug,a_parent,a_type = area.split('|')		
		_out_log('Insert <%s>' % (a_name))
		try:
			cur.execute('''INSERT INTO "main"."area" 
			("id","name","slug","parent_id","area_type") 
			VALUES (%s,"%s","%s",%s,%s)
			''' % (a_id,a_name.decode(CHARSET),a_slug,a_parent,a_type))
		except:
			_out_log(str(traceback),0)
	
	# save db
	conn.commit()
	cur.close()	
	
	_out_log('Gernate area done.')	

def main():		
	_out_log('''
Menu:
	1.Convert Ipdata.txt to db	
	2.Group Areas  	
	3.Convert Areas.txt to db	
	''')
	m = raw_input('Type the menu id:')
	if(m == "1"):
		gen_db()
	elif m=="2":
		gen_min_db()		
	elif m == '3':
		gen_area()
	else:
		exit()
	
	s = raw_input('Press any key to exit.')
	

if __name__ == '__main__':
	main()