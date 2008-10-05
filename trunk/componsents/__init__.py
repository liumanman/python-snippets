# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
#       __init__.py
#       
#       Copyright 2008 Jason Lee <huacnlee@gmail.com>
#       http://huacn.blogbus.com
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from django.utils import simplejson

class ExecuteState():
	"""
	summary:
		返回值对象,用于返回执行状态		
	"""	
	# 是否执行成功,默认是 True 成功，因为经过长期使用发现 True 用得较多
	success = True
	# 提示消息
	message = ""
	# 导致不成功的标志，错误是由谁引起的
	mark = ""
	# 导致不成功的对象 [object 类型]
	owner = None	
	
	def json(self):
		"""
		summary:
			得到本对象的JSON格式的字符串
		"""
		return simplejson.encode(str(obj2dict(self)))
	


def obj2dict(obj):
	"""
	summary:
		将object转换成dict类型	
	"""
	memberlist = [m for m in dir(obj)]
	_dict = {}
	for m in memberlist:
		if m[0] != "_" and not callable(m):
			_dict[m] = getattr(obj,m)
	
	return _dict
	

if __name__ == "__main__":
	s = ExecuteState()
	s.success = False
	s.message = "成功"
	s.mark = "none"
	print s.json()


