from distutils.core import setup
import py2exe

setup(
	console = ["tmTheme2Intype.py"],
	version = "0.4.1",
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
