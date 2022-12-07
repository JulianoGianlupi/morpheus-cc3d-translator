from cc3d.cpp.PlayerPython import *
from cc3d import CompuCellSetup
from cc3d.core.PySteppables import *
import numpy as np



global boundary2
boundary2 = 0.0

global boundary
boundary = 0.0

global b
b = 0.0

global b2
b2 = 0.0

class exampleSteppable(SteppableBasePy):

	def __init__(self, frequency=1):
		SteppableBasePy.__init__(self,frequency)

		self.track_cell_level_scalar_attribute(field_name='niegbors', attribute_name='b')

	def start(self):
		"""
		Called before MCS=0 while building the initial simulation
		"""
		pass

	def step(self, mcs):
		"""
		Called every frequency MCS while executing the simulation
		:param mcs: current Monte Carlo step
		"""



		for cell in self.cell_list_by_type(self.CT1):
			boundary = 0
			b = 0
			b2 = 0
			for neighbor, common_surface_area in self.get_cell_neighbor_data_list(cell):
				if neighbor and neighbor.type == self.CT2:
					boundary += common_surface_area
				if neighbor and neighbor.type == self.CT2:
					b += 1
				cell.dict['b']=b
				if neighbor and neighbor.type == self.CT2:
					b2 += common_surface_area

		for cell in self.cell_list_by_type(self.CT2):
			b = 0
			b2 = 0
			for neighbor, common_surface_area in self.get_cell_neighbor_data_list(cell):
				if neighbor and neighbor.type == self.CT1:
					b += 1
				cell.dict['b']=b
				if neighbor and neighbor.type == self.CT1:
					b2 += common_surface_area


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


