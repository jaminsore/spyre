from spyre import server

import skimage
from skimage import data, filter, io

class ImageEditor(server.App):
	title = "Image Editor"
	inputs = [{	"input_type": "slider",
					"variable_name": "sigma",
					"label": "sigma",
					"value": 0.1,
					"max": 10,
					"step":0.1,
					"action_id":"getImage"},
				{"input_type": "slider",
					"variable_name": "red",
					"label": "red",
					"value": 1,
					"max": 1,
					"step":0.1,
					"action_id":"getImage"},
				{"input_type": "slider",
					"variable_name": "green",
					"label": "green",
					"value": 1,
					"max": 1,
					"step":0.1,
					"action_id":"getImage"},
				{"input_type": "slider",
					"variable_name": "blue",
					"label": "blue",
					"value": 1,
					"max": 1,
					"step":0.1,
					"action_id":"getImage"}]

	controls = [{"control_type":"hidden",
					"control_id":"render",
					"label":"render"}]

	outputs = [{"output_type":"image",
					"output_id":"getImage",
					"control_id":"render",
					"on_page_load":True}]

	def getImage(self, sigma, red, green, blue, **params):
		image = data.coffee()
		new_image = filter.gaussian_filter(image, sigma=sigma, multichannel=True)
		new_image[:,:,0] = red*new_image[:,:,0]
		new_image[:,:,1] = green*new_image[:,:,1]
		new_image[:,:,2] = blue*new_image[:,:,2]
		return new_image


app = ImageEditor()
app.launch(port=9000)