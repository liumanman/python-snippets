# -*- coding: utf-8 -*-
from PIL import Image
import os

_cache_path = './data/cache/image/'

def _get_fname(key):
	return '%s%s' % (_cache_path,key)

def set(key,img):
	fname = _get_fname(key)
	if not os.path.exists(_cache_path):
		os.makedirs(_cache_path)
	img.save(fname,img.format)		

def get(key):
	if exist(key):
		return Image.open(_get_fname(key))
	else:
		return None		

def exist(key):
	return os.path.exists(_get_fname(key))