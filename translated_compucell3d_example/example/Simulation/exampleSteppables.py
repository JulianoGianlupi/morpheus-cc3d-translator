from cc3d.cpp.PlayerPython import *
from cc3d import CompuCellSetup
from cc3d.core.PySteppables import *
import numpy as np



'''
Copyright (C) 2022, Juliano Ferrari Gianlupi

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

global boundary
boundary = 0.0

global b
b = 0.0

global b2
b2 = 0.0

class exampleSteppable(SteppableBasePy):

	def __init__(self, frequency=1):
		SteppableBasePy.__init__(self,frequency)

		self.track_cell_level_scalar_attribute(field_name='Inter_type_neighbors', attribute_name='b')
		self.track_cell_level_scalar_attribute(field_name='Inter_type_contact', attribute_name='b2')

	def start(self):
		"""
		Called before MCS=0 while building the initial simulation
		"""
		self.plot_win = self.add_new_plot_window(title='Inter-type common contact area', x_axis_title='MonteCarlo Step (MCS)',  y_axis_title='Area', x_scale_type='linear', y_scale_type='linear', grid=True)
		self.plot_win.add_plot('Area', style='Lines', color='red', size=5)

	def step(self, mcs):
		"""
		Called every frequency MCS while executing the simulation
		:param mcs: current Monte Carlo step
		"""


		boundary = 0

		for cell in self.cell_list_by_type(self.CT1):
			b = 0
			b2 = 0
			for neighbor, common_surface_area in self.get_cell_neighbor_data_list(cell):
				if neighbor and neighbor.type == self.CT2:
					boundary += common_surface_area
				cell.dict['boundary']=boundary
				if neighbor and neighbor.type == self.CT2:
					b += 1
				cell.dict['b']=b
				if neighbor and neighbor.type == self.CT2:
					b2 += common_surface_area
				cell.dict['b2']=b2

		for cell in self.cell_list_by_type(self.CT2):
			b = 0
			b2 = 0
			for neighbor, common_surface_area in self.get_cell_neighbor_data_list(cell):
				if neighbor and neighbor.type == self.CT1:
					b += 1
				cell.dict['b']=b
				if neighbor and neighbor.type == self.CT1:
					b2 += common_surface_area
				cell.dict['b2']=b2

		self.plot_win.add_data_point('Area', mcs, boundary)

	def finish(self):
		"""
		Called after the last MCS to wrap up the simulation. Good place to close files and do post-processing
		"""


		return

	def on_stop(self):
		"""
		Called if the simulation is stopped before the last MCS
		"""
		self.finish()


