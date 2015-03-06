from __future__ import print_function, absolute_import, division
import os
import codecs
import io
import sys
import matplotlib.image as mpimg
# import imp
# imp.reload(sys)
#sys.setdefaultencoding('utf-8')
ENCODING = 'utf-8'
class View:
	def __init__(self):
		self.ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
		self.JS_PATH = os.path.join(self.ROOT_DIR, 'public', 'js')
		self.CSS_PATH = os.path.join(self.ROOT_DIR, 'public', 'css')

	def getHTML(self):
		file_path = os.path.join(self.ROOT_DIR, 'view.html')
		f = codecs.open(file_path, 'r', ENCODING)
		return f.read()

	def getJS(self):
		js_files = (os.path.join(self.JS_PATH, f) 
					for f in os.listdir(self.JS_PATH) if f.endswith('.js'))

		return self._read_files(js_files)

	def _read_files(self, filename_iter, line_end='\n'):
		try:
			open_files = [codecs.open(f, 'r', ENCODING) for f in filename_iter]
			contents = line_end.join(f.read() for f in open_files)
		finally:
			for open_file in open_files:
				open_file.close()
		return contents

		
	def getCSS(self):
		css_files = (os.path.join(self.CSS_PATH, f) 
					 for f in os.listdir(self.CSS_PATH) if f.endswith('.css'))

		return self._read_files(css_files)

	def getSpinningWheel(self):
		buffer = io.BytesIO()
		path = os.path.join(self.ROOT_DIR, 'public', 'images', 
							'loading_wheel.gif')
		with open(path, 'rb') as f:
			buffer.writelines(f)
		return buffer
	
	
