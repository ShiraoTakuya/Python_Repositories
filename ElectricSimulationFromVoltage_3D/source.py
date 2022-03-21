import cv2
import numpy as np
import time
import glob
import csv
import re
import pandas as pd

class ElectricFieldClass:
	def __init__(self,LENGTH_X,LENGTH_Y,LENGTH_Z,PITCH,VOLTS,charges):
		self.LENGTH_X = LENGTH_X
		self.LENGTH_Y = LENGTH_Y
		self.LENGTH_Z = LENGTH_Z
		self.PITCH = PITCH
		self.charges = charges
		self.EPARAM = np.hstack([VOLTS, charges])
		self.canvas_electric_field = np.zeros((LENGTH_X,LENGTH_Y,LENGTH_Z,3), np.double)
		self.canvas_electric_voltage = np.zeros((LENGTH_X,LENGTH_Y,LENGTH_Z), np.double)
		self.canvas_electric_voltage_prev = np.zeros((LENGTH_X,LENGTH_Y,LENGTH_Z), np.double)
		epsilon = 8.85418782e-12
		self.k = 1 / (4*np.pi*epsilon)

	def calc_electric_field_per_pixel(self, target_pos, origin_pos, q):
		r_vec = (np.array(target_pos) - np.array(origin_pos))*self.PITCH
		r_norm = np.linalg.norm(r_vec)

		if(r_norm == 0):
			return np.array([0,0,0])
		E =  self.k * q / (r_norm**3) * r_vec
		return E

	def calc_electric_field(self, range_z = []):
		if range_z == []:
			range_z = range(self.LENGTH_Z)
		self.canvas_electric_field = np.zeros((self.LENGTH_X,self.LENGTH_Y,self.LENGTH_Z,3), np.double)
		for charge in self.EPARAM:
			for z in range_z:
				for y in range(self.LENGTH_Y):
					for x in range(self.LENGTH_X):
						self.canvas_electric_field[z][y][x] += self.calc_electric_field_per_pixel([x,y,z],charge[0:3],charge[4])

	def calc_electric_field_fast(self):
		self.canvas_electric_field = np.zeros((self.LENGTH_X,self.LENGTH_Y,self.LENGTH_Z,3), np.double)

		yzs = np.array([self.EPARAM.transpose(1,0)[1],self.EPARAM.transpose(1,0)[2]]).transpose(1,0) #array of y,z
		yzs = pd.DataFrame(yzs).drop_duplicates().values
		xs_max = {}
		for yz in yzs:
			y = int(yz[0])
			z = int(yz[1])
			key = str(y)+"_"+str(z)
			xs_max[key] = np.max([charge[0] for charge in filter(lambda x: [int(x[1]),int(x[2])] == [int(yz[0]),int(yz[1])], self.EPARAM)])

		for charge in self.EPARAM:
			for yz in yzs:
				y = int(yz[0])
				z = int(yz[1])
				key = str(y)+"_"+str(z)
				for x in range(int(xs_max[key]+1)):
					self.canvas_electric_field[z][y][x] += self.calc_electric_field_per_pixel([x,y,z],charge[0:3],charge[4])

	def calc_electric_voltage(self, range_z = []):
		if range_z == []:
			range_z = range(self.LENGTH_Z)
		for z in range_z:
			for y in range(self.LENGTH_Y):
				self.canvas_electric_voltage[z][y][0] = -self.canvas_electric_field[z][y][0][0] * self.PITCH
		for z in range_z:
			for y in range(self.LENGTH_Y):
				for x in range(self.LENGTH_X)[1:]:
					self.canvas_electric_voltage[z][y][x] = self.canvas_electric_voltage[z][y][x-1] - (self.canvas_electric_field[z][y][x][0] + self.canvas_electric_field[z][y][x-1][0])*0.5 * self.PITCH

	def calc_electric_voltage_fast(self):
		yzs = np.array([self.EPARAM.transpose(1,0)[1],self.EPARAM.transpose(1,0)[2]]).transpose(1,0) #array of y,z
		yzs = pd.DataFrame(yzs).drop_duplicates().values
		xs_max = {}
		for yz in yzs:
			y = int(yz[0])
			z = int(yz[1])
			key = str(y)+"_"+str(z)
			xs_max[key] = np.max([charge[0] for charge in filter(lambda x: [int(x[1]),int(x[2])] == [int(yz[0]),int(yz[1])], self.EPARAM)])

		for charge in self.EPARAM:
			for yz in yzs:
				y = int(yz[0])
				z = int(yz[1])
				key = str(y)+"_"+str(z)
				self.canvas_electric_voltage[z][y][0] = -self.canvas_electric_field[z][y][0][0] * self.PITCH
				for x in range(int(xs_max[key])+1)[1:]:
					self.canvas_electric_voltage[z][y][x] = self.canvas_electric_voltage[z][y][x-1] - (self.canvas_electric_field[z][y][x][0] + self.canvas_electric_field[z][y][x-1][0])*0.5 * self.PITCH

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
		self.charges = self.EPARAM.transpose(1,0)[4:6]
		self.canvas_electric_voltage_prev = self.canvas_electric_voltage.copy()

	def error_rate(self):
		volts_taget = np.array(self.EPARAM).transpose(1,0)[3]
		volts_current = np.array([self.canvas_electric_voltage[int(charge[2])][int(charge[1])][int(charge[0])] for charge in self.EPARAM])
		error_rate = volts_current - volts_taget
		return [np.max(error_rate),np.min(error_rate),np.average(np.abs(error_rate))]

	def train(self):
		self.calc_electric_charges()
		self.calc_electric_field_fast()
		self.calc_electric_voltage_fast()
	
	def prepare(self, range_z = []):
		self.calc_electric_field(range_z)
		self.calc_electric_voltage(range_z)

def read_ini(path, parameter):
	return re.search(parameter+"(.*)", open(path).read())[1]

def csv_write(path, arr):
	np.savetxt(path, np.array(arr), delimiter=",")

def csv_read(path):
	return np.loadtxt(path, delimiter=",")

def standization(ar):
	ar_no_bias = ar - np.nanmin(ar)
	return np.asarray(ar_no_bias/np.nanmax(ar_no_bias) * 255, np.uint8)

def main():
	LENGTH_X = int(read_ini("SET.INI", "LENGTH_X="))
	LENGTH_Y = int(read_ini("SET.INI", "LENGTH_Y="))
	LENGTH_Z = int(read_ini("SET.INI", "LENGTH_Z="))
	PITCH = float(read_ini("SET.INI", "PITCH="))
	VOLTS = csv_read("SET_VOLTS.csv")

	charges = []
	if glob.glob("data\\charges_*.csv") == []:
		charges = np.array([[1,1] for x in VOLTS])
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
			ElectricFieldInstance.prepare(CUTTING_Z)

			Es_std_3d = standization([ElectricFieldInstance.canvas_electric_field[z] for z in CUTTING_Z])
			Es_std_3d = dict([z_E for z_E in zip(*[CUTTING_Z,Es_std_3d])])
			Vs_std_3d = standization([ElectricFieldInstance.canvas_electric_voltage[z] for z in CUTTING_Z])
			Vs_std_3d = dict([z_V for z_V in zip(*[CUTTING_Z,Vs_std_3d])])
			for z in CUTTING_Z:
				Es_std = Es_std_3d[z].transpose(2,0,1)
				Vs_std = Vs_std_3d[z]
				Es = ElectricFieldInstance.canvas_electric_field[z].transpose(2,0,1)
				Vs = ElectricFieldInstance.canvas_electric_voltage[z]
				cv2.imwrite(f"data\\canvas_electric_field_Xvec_z{z:04d}_{count:04d}.png", Es_std[0])
				cv2.imwrite(f"data\\canvas_electric_field_Yvec_z{z:04d}_{count:04d}.png", Es_std[1])
				cv2.imwrite(f"data\\canvas_electric_field_Zvec_z{z:04d}_{count:04d}.png", Es_std[2])
				cv2.imwrite(f"data\\canvas_electric_voltage_z{z:04d}_{count:04d}.png", Vs_std)
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
