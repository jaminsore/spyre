from __future__ import print_function, absolute_import, division
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import io

class Plot:
	def getPlotPath(self, plt_obj):
		buffer = io.BytesIO()
		if isinstance(plt_obj, plt.Figure):
			plt_obj.savefig(buffer,format='png',bbox_inches='tight')
		else:
			print("Error: getPlot method must return an pyplot figure object")
		plt.close('all')
		return(buffer)

class Image:
	def getImagePath(self, img_obj):
		buffer = io.BytesIO()
		mpimg.imsave(buffer,img_obj)
		try:
			mpimg.imsave(buffer,img_obj)
		except:
			print("Error: getImage method must return an image object")
		return(buffer)
