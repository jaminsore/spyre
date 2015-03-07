from spyre import server

import pandas as pd
import numpy as np
from bokeh.resources import INLINE
from bokeh.resources import CDN
from bokeh.embed import components

from bokeh.sampledata import us_counties, unemployment
from bokeh.models import HoverTool
from bokeh.plotting import *
from collections import OrderedDict


def load_data():
	colors = np.array(["#F1EEF6", "#D4B9DA", "#C994C7", 
					   "#DF65B0", "#DD1C77", "#980043"])

	data = pd.DataFrame(us_counties.data).T
	data['rate'] = pd.Series(unemployment.data)
	data.dropna(subset=['rate'], inplace=True)

	data['idx'] = (data['rate'] // 2).astype('i8')
	data.loc[data['idx'] > 5, 'idx'] = 5
	data['color'] = colors[data['idx'].values]

	data['mlong'] = data['lons'].map(np.mean)
	data['mlats'] = data['lats'].map(np.mean)

	mask = (data.mlong > -130) & (data.mlong < -65) &\
		   (data.mlats > 25) & (data.mlats < 50)
		
	data = data[mask]
	return data


def make_options(data):
	options = [{"label": "all", "value":"all"}]
	states = pd.unique(data['state'].dropna())
	states.sort()
	states_opts = [{"label": x.upper(), "value":x} for x in states.tolist()]
	options.extend(states_opts)
	return options


class UnemploymentApp(server.App):
	
	title = "US Unemployment"

	controls = [{"control_type" : "hidden",
				 "label" : "get historical stock prices",
				 "control_id" : "update_data" 
				}]

	outputs = [{"output_type" : "html",
				"output_id" : "html_id",
				 "control_id" : "update_data",
				 "on_page_load" : True}]
	
	data = load_data()
	
	inputs = [{	"input_type":'dropdown',
				"label": 'State',
				"options" : make_options(data),
				"variable_name": 'state', 
				"action_id": "update_data"
			}]
	
	
	def __init__(self, custom_js=INLINE.js_raw[0], custom_css=INLINE.css_raw[0]):
		server.App.__init__(self, custom_css=custom_css, custom_js=custom_js)
	
	
	def html_id(self, state, **params):
		if state=='all':
			data = self.data
		else:
			data = self.data[self.data['state']==state]

		TOOLS="pan,wheel_zoom,box_zoom,reset,hover,previewsave,resize"

		fig = figure(title=state.upper()+" Unemployment 2009", tools=TOOLS)
		fig.patches(data['lons'], data['lats'], fill_color=data['color'], fill_alpha=0.7,  line_color="white", line_width=0.5, )

		hover = fig.select(dict(type=HoverTool))
		hover.tooltips = OrderedDict([
		    ("index", "$index")
		])

		script, div = components(fig, CDN)
		html = "%s\n%s"%(script, div)
		return html

app = UnemploymentApp()

app.launch(port=9097)