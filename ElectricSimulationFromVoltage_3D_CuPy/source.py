import numpy as np
import cupy as cp
import time
import glob
import csv
import re
import pandas as pd
from sympy import Q

class ElectricFieldClass:
	def __init__(self,LENGTH_X,LENGTH_Y,LENGTH_Z,PITCH,VOLTS,charges):
		self.LENGTH_X = LENGTH_X
		self.LENGTH_Y = LENGTH_Y
		self.LENGTH_Z = LENGTH_Z
		self.PITCH = PITCH
		self.charges = charges
		self.EPARAM = cp.hstack([VOLTS, charges])
		self.canvas_electric_field = cp.zeros((LENGTH_X,LENGTH_Y,LENGTH_Z,3), cp.double)
		self.canvas_electric_voltage = cp.zeros((LENGTH_X,LENGTH_Y,LENGTH_Z), cp.double)
		self.canvas_electric_voltage_prev = cp.zeros((LENGTH_X,LENGTH_Y,LENGTH_Z), cp.double)
		epsilon = 8.85418782e-12
		self.k = 1 / (4*cp.pi*epsilon)

		ar = cp.stack(cp.meshgrid(cp.arange(LENGTH_Z), cp.arange(LENGTH_Y), cp.arange(LENGTH_X)), axis=-1).transpose(3,0,1,2)
		self.Fxyz = cp.array([ar[2],ar[0],ar[1]]).transpose(1,2,3,0)

	def calc_electric_field_per_pixel(self, target_pos, origin_pos, q):
		r_vec = (cp.array(target_pos) - cp.array(origin_pos))*self.PITCH
		r_norm = cp.linalg.norm(r_vec)

		if(r_norm == 0):
			return cp.array([0,0,0])
		E =  self.k * q / (r_norm**3) * r_vec
		return E
		
	def calc_electric_field(self, range_z = []):
		if range_z == []:
			range_z = range(self.LENGTH_Z)
		self.canvas_electric_field = cp.zeros((self.LENGTH_X,self.LENGTH_Y,self.LENGTH_Z,3), cp.double)
		for charge in self.EPARAM:
			Qx = cp.full((self.LENGTH_Z,self.LENGTH_Y,self.LENGTH_X),charge[0])
			Qy = cp.full((self.LENGTH_Z,self.LENGTH_Y,self.LENGTH_X),charge[1])
			Qz = cp.full((self.LENGTH_Z,self.LENGTH_Y,self.LENGTH_X),charge[2])
			Qxyz = cp.asarray([Qx,Qy,Qz]).transpose(1,2,3,0)
			Q = charge[4]

			r_vec = self.Fxyz - Qxyz
			r_vec_T2 = (r_vec**2).transpose(3,0,1,2)
			r_norm = cp.sqrt(r_vec_T2[0]+r_vec_T2[1]+r_vec_T2[2])
			r_norm[int(charge[2])][int(charge[1])][int(charge[0])] = np.inf #to avoid error

			Ex = self.k * Q / (r_norm**3) * r_vec.transpose(3,0,1,2)[0]
			Ey = self.k * Q / (r_norm**3) * r_vec.transpose(3,0,1,2)[1]
			Ez = self.k * Q / (r_norm**3) * r_vec.transpose(3,0,1,2)[2]
			self.canvas_electric_field += cp.asarray([Ex,Ey,Ez]).transpose(1,2,3,0)

	def calc_electric_voltage(self, range_z = []):
		if range_z == []:
			range_z = range(self.LENGTH_Z)

		canvas_electric_field_T = self.canvas_electric_field.transpose(3,2,0,1)
		canvas_electric_voltage_T = self.canvas_electric_voltage.transpose(2,0,1)
		canvas_electric_voltage_T[0] = -canvas_electric_field_T[0][0] * self.PITCH

		for i in cp.arange(self.LENGTH_X)[1:]:
			canvas_electric_voltage_T[i] = canvas_electric_voltage_T[i-1] - (canvas_electric_field_T[0][i] + canvas_electric_field_T[0][i-1])*0.5 * self.PITCH
		
		self.canvas_electric_voltage = canvas_electric_voltage_T.transpose(1,2,0)

	def calc_electric_charges(self):
		for charge in self.EPARAM:
			volt_current = self.canvas_electric_voltage[int(charge[2])][int(charge[1])][int(charge[0])]
			volt_prev = self.canvas_electric_voltage_prev[int(charge[2])][int(charge[1])][int(charge[0])]
			if (volt_current - volt_prev) == 0:
				continue

			step = charge[5] * (charge[3] - volt_current)/(volt_current - volt_prev)
			if step == 0:
				continue
		
			charge[4] += step
			charge[5] = step
		self.charges = self.EPARAM.transpose(1,0)[4:6].transpose(1,0)
		self.canvas_electric_voltage_prev = self.canvas_electric_voltage.copy()

	def error_rate(self):
		volts_taget = cp.array(self.EPARAM).transpose(1,0)[3]
		volts_current = cp.array([self.canvas_electric_voltage[int(charge[2])][int(charge[1])][int(charge[0])] for charge in self.EPARAM])
		error_rate = cp.asnumpy(volts_current - volts_taget)
		return [np.max(error_rate),np.min(error_rate),np.average(np.abs(error_rate))]

	def train(self):
		self.calc_electric_charges()
		self.calc_electric_field()
		self.calc_electric_voltage()
	
def read_ini(path, parameter):
	return re.search(parameter+"(.*)", open(path).read())[1]

def csv_write(path, arr):
	np.savetxt(path, cp.asnumpy(arr), delimiter=",")

def csv_read(path):
	return cp.asarray(np.loadtxt(path, delimiter=","))

def standization(ar):
	ar_no_bias = ar - cp.nanmin(ar)
	return cp.asarray(ar_no_bias/cp.nanmax(ar_no_bias) * 255, cp.uint8)

def main():
	LENGTH_X = int(read_ini("SET.INI", "LENGTH_X="))
	LENGTH_Y = int(read_ini("SET.INI", "LENGTH_Y="))
	LENGTH_Z = int(read_ini("SET.INI", "LENGTH_Z="))
	PITCH = float(read_ini("SET.INI", "PITCH="))
	VOLTS = csv_read("SET_VOLTS.csv")

	charges = []
	if glob.glob("data\\charges_*.csv") == []:
		charges = cp.array([[1,1] for x in VOLTS])
	else:
		charges = csv_read(glob.glob("data\\charges_*.csv")[-1])
	ElectricFieldInstance = ElectricFieldClass(LENGTH_X,LENGTH_Y,LENGTH_Z,PITCH,VOLTS,charges)

	print("Calculating...")
	LOOP_LIMIT = int(read_ini("SET.INI", "LOOP_LIMIT="))
	SAVE_PERIOD = int(read_ini("SET.INI", "SAVE_PERIOD="))
	CUTTING_Z = eval(read_ini("SET.INI", "CUTTING_Z="))

	count = 0
	if glob.glob("data\\charges_*.csv") == []:
		count = 1
	else:
		count = int(glob.glob("data\\charges_*.csv")[-1][13:17])+1
	while True:
		if(count > LOOP_LIMIT):
			break

		ElectricFieldInstance.train()

		if (count % SAVE_PERIOD) == 0:
			Es_std_3d = standization(cp.asarray([ElectricFieldInstance.canvas_electric_field[z] for z in CUTTING_Z]))
			Es_std_3d = dict([z_E for z_E in zip(*[CUTTING_Z,Es_std_3d])])
			Vs_std_3d = standization(cp.asarray([ElectricFieldInstance.canvas_electric_voltage[z] for z in CUTTING_Z]))
			Vs_std_3d = dict([z_V for z_V in zip(*[CUTTING_Z,Vs_std_3d])])
			for z in CUTTING_Z:
				Es_std = Es_std_3d[z].transpose(2,0,1)
				Vs_std = Vs_std_3d[z]
				Es = ElectricFieldInstance.canvas_electric_field[z].transpose(2,0,1)
				Vs = ElectricFieldInstance.canvas_electric_voltage[z]
				csv_write(f"data\\canvas_electric_field_Xvec_z{z:04d}_{count:04d}.csv", Es[0])
				csv_write(f"data\\canvas_electric_field_Yvec_z{z:04d}_{count:04d}.csv", Es[1])
				csv_write(f"data\\canvas_electric_field_Zvec_z{z:04d}_{count:04d}.csv", Es[2])
				csv_write(f"data\\canvas_electric_voltage_z{z:04d}_{count:04d}.csv", Vs)
				csv_write(f"data\\charges_{count:04d}.csv", ElectricFieldInstance.charges)

		print(f"Results: {count:04d}")
		error_rate = ElectricFieldInstance.error_rate()
		print(f"Error Max: {error_rate[0]*100:.2f} V")
		print(f"Error Min: {error_rate[1]*100:.2f} V")
		print(f"Error AbsAve: {error_rate[2]*100:.2f} V")

		count += 1

	print("Finished")
	
main()
