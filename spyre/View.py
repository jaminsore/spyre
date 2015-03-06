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
		self.JS_PATH = self.ROOT_DIR+'/public/js/'
		self.CSS_PATH = self.ROOT_DIR+'/public/css/'

	def getHTML(self):
		file_path = self.ROOT_DIR+'/view.html'
		f = codecs.open(file_path, 'r', ENCODING)
		return f.read()

	def getJS(self):
		self.JS = ""
		for file in os.listdir(self.JS_PATH):
			if file.find('.js')>0:
				file_path = self.JS_PATH+file
				print(file_path)
				with codecs.open(file_path, 'r', ENCODING) as f:
					self.JS += f.read()
				self.JS += "\n"
		return self.JS

	def getCSS(self):
		self.CSS = ""
		for file in os.listdir(self.CSS_PATH):
			if file.find('.css')>0:
				file_path = self.CSS_PATH+file
				with codecs.open(file_path, 'r', ENCODING) as f:
					self.CSS += f.read()
				self.CSS += "\n"
		return self.CSS

	def getSpinningWheel(self):
		buffer = io.BytesIO()
		f = open(self.ROOT_DIR+'/public/images/loading_wheel.gif','rb')
		buffer.write(f.read())
		f.close()
		return(buffer)
