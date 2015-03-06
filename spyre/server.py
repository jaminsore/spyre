from __future__ import absolute_import, division, print_function
import matplotlib
matplotlib.use('Agg')

import os
import json
import jinja2

import io


import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from functools import wraps
from . import model
from . import View


import cherrypy
from cherrypy.lib.static import serve_file
from cherrypy.lib.static import serve_fileobj
from tempfile import TemporaryFile

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

templateLoader = jinja2.FileSystemLoader( searchpath=ROOT_DIR )
templateEnv = jinja2.Environment( loader=templateLoader )

def clean_kwargs(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		for k, v in kwargs.items():
			if v.startswith('__list__'):
				kwargs[k] = v.split(',')[1:]
			if v.startswith('__float__'):
				kwargs[k] = float(v[9:])
		return f(*args, **kwargs)
	return wrapper

class Root(object):
	
	def __init__(self, app_instance):
# 		app_instance = App
		self._app = app_instance


	@cherrypy.expose
	def index(self):
		html = self._app.view.getHTML()
		template = jinja2.Template(html)
		try:
			return template.render( self._app.templateVars )
		except UnicodeDecodeError:
			print (html)
			raise


	@cherrypy.expose
	@clean_kwargs
	def plot(self, output_id, **kwargs):
		p = getattr(self._app, output_id)(**kwargs)
		d = model.Plot()
		buffer = d.getPlotPath(p)
		cherrypy.response.headers['Content-Type'] = 'image/png'
		return buffer.getvalue()


	@cherrypy.expose
	@clean_kwargs
	def image(self, output_id, **kwargs):
		img = getattr(self._app, output_id)(**kwargs)
		d = model.Image()
		buffer = d.getImagePath(img)
		cherrypy.response.headers['Content-Type'] = 'image/jpg'
		return buffer.getvalue()


	@cherrypy.expose
	@clean_kwargs
	def data(self, ouput_id, **kwargs):
		data = getattr(self._app, output_id)(**kwargs)
		cherrypy.response.headers['Content-Type'] = 'application/json'
		return json.dumps({'data':data,'args':kwargs})


	@cherrypy.expose
	@clean_kwargs
	def table(self, output_id, **kwargs):
		df = getattr(self._app, output_id)(**kwargs)
		html = df.to_html(index=False, escape=False)
		for i, col in enumerate(df.columns):
			html = html.replace('<th>{}'.format(col),'<th><a onclick="sortTable({},"table0");"><b>{}</b></a>'.format(i,col))
		html = html.replace('border="1" class="dataframe"','class="sortable" id="sortable"')
		html = html.replace('style="text-align: right;"','')
		cherrypy.response.headers['Content-Type'] = 'text/html'
		return html


	@cherrypy.expose
	@clean_kwargs
	def html(self, output_id, **kwargs):
		html = getattr(self._app, output_id)(**kwargs)
		cherrypy.response.headers['Content-Type'] = 'text/html'
		return html


	@cherrypy.expose
	@clean_kwargs
	def download(self, output_id, **kwargs):
		filepath = getattr(self._app, output_id)(**kwargs)
		content_type, disposition = "application/x-download", "attachment"
		if isinstance(filepath, tuple):
			filepath, name = filepath
		else:
			name = None
		if isinstance(filepath, str):
			return serve_file(filepath, content_type, disposition, 
							  name=name)
		elif isinstance(filepath, (io.BytesIO, io.StringIO)):
			if isinstance(filepath, io.StringIO):
				mode = 'w+'
			else:
				mode = 'w+b'
			f = TemporaryFile(mode)
			f.write(filepath.getvalue())
			f.seek(0)
			return serve_fileobj(f, content_type, disposition, name=name)
		elif hasattr(filepath, 'read'):
			return server_fileobj(filepath, content_type, disposition, 
								  name=name)
		else:
			raise TypeError('"%s" must return string or buffer'
							% output_id)

	@cherrypy.expose
	def no_output(self, output_id, **kwargs):
		getattr(self._app, output_id)(**kwargs)
		return ''


	@cherrypy.expose
	def spinning_wheel(self, **kwargs):
		buffer = self._app.view.getSpinningWheel()
		cherrypy.response.headers['Content-Type'] = 'image/gif'
		return buffer.getvalue()


class App:
	'''\
	`spyre` application base class
	
	
	..  example ::
	
		import matplotlib.pyplot as plt
		import numpy as np
		
		class(App):
			outputs = [{'output_type' : 'plot',
						'output_id' : plot_method',
						'on_page_load' : True}]
						
			def plot_method(self, **params):
				"plots a sign wave on page load"
				fig, ax = plt.subplots(1, 1)
				x = np.linspace(0, np.pi / 2)
				ax.plot(x, np.sin(x))
				return fig
	'''
	title = ''
	inputs = [{}]

	controls = []

	outputs = [{}]
	outputs = []
	inputs = []
	tabs = []
	templateVars = {}
	
	def __init__(self, d3=None, custom_js='', custom_css='', view=View.View()):
		'''
		Parameters
		----------
			d3 : dict
				dictionary of with `'js'` and `'css'` keys
			custom_js : string
				custom JavaScript
			custom_css : string
				custom cascading style sheet CSS
			view : View.View instance
		'''
				
		if d3 is None:
			d3 = {'css' : '', 'js':''}
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
			
		self.templateVars['d3js'] = d3['js']
		self.templateVars['d3css'] = d3['css']
		self.templateVars['custom_js'] = custom_js
		self.templateVars['custom_css'] = custom_css

		self.templateVars['js'] = view.getJS()
		self.templateVars['css'] = view.getCSS()
		self.view = view
		
	
	def launch(self,host="local",port=8080):
		'''\
		Overried this method to csutomize launch behavior
		'''
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
 

