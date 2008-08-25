#############################################################
# Summary:
#	This mothod from dglogs http://code.google.com/p/dglogs/
# Author:
#	mydjango <mydjango@gmail.com>
# License:
#	GNU General Public License v2
#############################################################
import md5

def getMD5dir(uid,dir):
	if dir > 16:
		dir = 16
	m_dir = md5.new()
	m_dir.update(str(uid))
	uid_dir = m_dir.hexdigest()
	a = ''
	for i in xrange(0,dir):
		x = i*2
		y = x+2
		a = a  + uid_dir[x:y] + '/'
	return a

if __name__ == '__main__':
	print getMD5dir(2,8)
