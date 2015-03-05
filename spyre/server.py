import matplotlib
matplotlib.use('Agg')

import os
import json
import jinja2

try:
	import io
except ImportError:
	import StringIO as io

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

try:
	
	from . import model
except (ImportError, SystemError):
	import model

try:
	from . import View
except ImportError:
	import view as View
except SystemError:
	import View

import cherrypy
from cherrypy.lib.static import serve_file
from cherrypy.lib.static import serve_fileobj

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

templateLoader = jinja2.FileSystemLoader( searchpath=ROOT_DIR )
templateEnv = jinja2.Environment( loader=templateLoader )


class Root(object):
	
	def __init__(self, app_instance):
# 		app_instance = App
		self._app = app_instance


	@cherrypy.expose
	def index(self):
		v = View.View()
		template = jinja2.Template(v.getHTML())
		return template.render( self._app.templateVars )


	@cherrypy.expose
	def plot(self, **args):
		args = self.clean_args(args)
		p = self._app.getPlot(args)
		d = model.Plot()
		buffer = d.getPlotPath(p)
		cherrypy.response.headers['Content-Type'] = 'image/png'
		return buffer.getvalue()


	@cherrypy.expose
	def image(self, **args):
		args = self.clean_args(args)
		img = self._app.getImage(args)
		d = model.Image()
		buffer = d.getImagePath(img)
		cherrypy.response.headers['Content-Type'] = 'image/jpg'
		return buffer.getvalue()


	@cherrypy.expose
	def data(self, **args):
		args = self.clean_args(args)
		data = self._app.getJsonData(args)
		cherrypy.response.headers['Content-Type'] = 'application/json'
		return json.dumps({'data':data,'args':args})


	@cherrypy.expose
	def table(self, **args):
		args = self.clean_args(args)
		df = self._app.getTable(args)
		html = df.to_html(index=False, escape=False)
		for i, col in enumerate(df.columns):
			html = html.replace('<th>{}'.format(col),'<th><a onclick="sortTable({},"table0");"><b>{}</b></a>'.format(i,col))
		html = html.replace('border="1" class="dataframe"','class="sortable" id="sortable"')
		html = html.replace('style="text-align: right;"','')
		cherrypy.response.headers['Content-Type'] = 'text/html'
		return html


	@cherrypy.expose
	def html(self, **args):
		args = self.clean_args(args)
		html = self._app.getHTML(args)
		cherrypy.response.headers['Content-Type'] = 'text/html'
		return html


	@cherrypy.expose
	def download(self, **args):
		args = self.clean_args(args)
		filepath = self._app.getDownload(args)
		if type(filepath).__name__=="str":
			return serve_file(filepath, "application/x-download", "attachment", name='data.csv')
		if type(filepath).__name__=="instance":
			return serve_fileobj(filepath.getvalue(), "application/x-download", "attachment", name='data.csv')
		else:
			return "error downloading file. filepath must be string of buffer"


	@cherrypy.expose
	def no_output(self, **args):
		args = self.clean_args(args)
		self._app.noOutput(args)
		return ''


	@cherrypy.expose
	def spinning_wheel(self, **args):
		v = View.View()
		buffer = v.getSpinningWheel()
		cherrypy.response.headers['Content-Type'] = 'image/gif'
		return buffer.getvalue()


	def clean_args(self,args):
		for k,v in args.items():
			# turn checkbox group string into a list
			if v.rfind("__list__") == 0:
				tmp = v.split(',')
				if len(tmp)>1:
					args[k] = tmp[1:]
				else:
					args[k] = []
			# convert to a number
			if v.rfind("__float__") == 0:
				args[k] = float(v[9:])
		return args


class App:

	title = ''
	inputs = [{		"input_type":'text',
					"label": 'Variable', 
					"value" : "Value Here",
					"variable_name": 'var1'}]

	controls = []

	outputs = [{	"output_type" : "plot",
					"output_id" : "plot",
					"control_id" : "button1",
					"on_page_load" : "true"}]
	outputs = []
	inputs = []
	tabs = []
	templateVars = {}
	
	def __init__(self):
		if self.title:
			self.templateVars['title'] = self.title
		if self.controls:
			self.templateVars['controls'] = self.controls
		if self.outputs:
			self.templateVars['outputs'] = self.outputs
		if self.inputs:
			self.templateVars['inputs'] = self.inputs
		if self.tabs:
			self.templateVars['tabs'] = self.tabs
			
		d3 = self.getD3()
		custom_js = self.getCustomJS()
		custom_css = self.getCustomCSS()

		self.templateVars['d3js'] = d3['js']
		self.templateVars['d3css'] = d3['css']
		self.templateVars['custom_js'] = custom_js
		self.templateVars['custom_css'] = custom_css

		v = View.View()
		self.templateVars['js'] = v.getJS()
		self.templateVars['css'] = v.getCSS()
	
	
	def getJsonData(self, params):
		"""turns the DataFrame returned by getData into a dictionary

		arguments:
		the params passed used for table or d3 outputs are forwarded on to getData
		"""
		df = self.getData(params)
		return df.to_dict(outtype='records')

	def getData(self, params):
		"""Override this function

		arguments:
		params (dict)

		returns:
		DataFrame
		"""
		try:
			return eval("self."+str(params['output_id'])+"()")
		except:
			return pd.DataFrame({'name':['Override','getData() method','to generate tables'], 'count':[1,4,3]})

	def getTable(self, params):
		"""Used to create html table. Uses dataframe returned by getData by default
		override to return a different dataframe.

		arguments: params (dict)
		returns: html table
		"""
		return self.getData(params)

	def getDownload(self, params):
		"""Override this function

		arguments: params (dict)
		returns: path to file or buffer to be downloaded (string or buffer)
		"""
		df = self.getData(params)
		buffer = io.StringIO()
		df.to_csv(buffer, index=False)
		filepath = buffer
		return filepath

	def getPlot(self, params):
		"""Override this function

		arguments:
		params (dict)

		returns:
		matplotlib.pyplot figure
		"""
		try:
			return eval("self."+str(params['output_id'])+"()")
		except:
			plt.title("Override getPlot() method to generate figures")
			return plt.gcf()

	def getImage(self, params):
		"""Override this function

		arguments: params (dict)
		returns: matplotlib.image (figure)
		"""
		try:
			return eval("self."+str(params['output_id'])+"()")
		except:
			return np.array([[0,0,0]])

	def getHTML(self, params):
		"""Override this function

		arguments: params (dict)
		returns: html (string)
		"""
		try:
			return eval("self."+str(params['output_id'])+"()")
		except:
			return "<b>Override</b> the getHTML method to insert your own HTML <i>here</i>"

	def noOutput(self, params):
		"""Override this function
		A method for doing stuff that doesn't reququire an output (refreshing data,
			updating variables, etc.)

		arguments:
		params (dict)
		"""
		try:
			return eval("self."+str(params['output_id'])+"()")
		except:
			pass

	def getD3(self):
		return {'css' : '', 'js' : ''}

	def getCustomJS(self):
		"""Override this function

		returns:
		string of javascript to insert on page load
		"""
		return ""

	def getCustomCSS(self):
		"""Override this function

		returns:
		string of css to insert on page load
		"""
		return ""

	def launch(self,host="local",port=8080):
		webapp = Root(self)
		if host!="local":
			cherrypy.server.socket_host = '0.0.0.0'
		cherrypy.server.socket_port = port
		cherrypy.quickstart(webapp)

	def launch_in_notebook(self, port=9095, width=900, height=600):
		"""launch the app within an iframe in ipython notebook"""
		from IPython.lib import backgroundjobs as bg
		from IPython.display import HTML

		jobs = bg.BackgroundJobManager()
		jobs.new(self.launch, kw=dict(port=port))
		return HTML('<iframe src=http://localhost:{} width={} height={}></iframe>'.format(port,width,height))


class Launch(App):
	"""Warning: This class is depricated. Use App instead"""
 
if __name__=='__main__':
	app = App()
	app.launch()
