from __future__ import print_function, absolute_import, division
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import io
import numpy as np

def get_plot_path(plt_obj):
	buffer = io.BytesIO()
	if isinstance(plt_obj, plt.Figure):
		plt_obj.savefig(buffer,format='png',bbox_inches='tight')
	else:
		raise TypeError('"plt_obj" must be %s' % type(plt.Figure))
	plt.close('all')
	return buffer


def get_image_path(img_obj):
	buffer = io.BytesIO()
	mpimg.imsave(buffer,img_obj)
	shape = np.shape(img_obj)
	if ((len(shape) == 3 and shape[-1] != 3 and shape[-1] !=4)  or
		   (len(shape) < 2 or len(shape) > 3)):
		raise TypeError('"img_obj" must be an MxN (luminance),'
						 'MxNx3 (RGB) or MxNx4 (RGBA) array, %s received' 
						 % str(shape))
	mpimg.imsave(buffer,img_obj)
	return buffer
