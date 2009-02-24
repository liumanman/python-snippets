from distutils.core import setup
import py2exe

setup(
	console = [{
		'script':"flickwall.py",
		'icon_resources': [(0, "flickwall.ico")],
	}],	
	data_files = ['readme.txt','searchlist.txt','proxy.txt'],
	version = "0.1.0",
	options = {"py2exe":
		{
			"unbuffered" : True,
			"compressed": 1,
			"optimize": 2,
			"bundle_files": 1,
			"dist_dir" : "bin"
		}
	},
	zipfile = None,
)
