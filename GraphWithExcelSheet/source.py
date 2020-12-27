import numpy as np
import matplotlib.pyplot as plt
import zipfile
import re

def get_sheetdata(stPath):
	with zipfile.ZipFile(stPath, 'r') as zip:
		with zip.open('xl/worksheets/sheet1.xml') as f:
			return f.read().decode('utf-8')

def get_textdata(stPath):
	with zipfile.ZipFile(stPath, 'r') as zip:
		with zip.open('xl/sharedStrings.xml') as f:
			return f.read().decode('utf-8')

def get_column_AB(strData):
	data_list = [m for m in re.findall("<c[^>]*?r=\"(.*?)\"[^>]*?>(.*?)</c>", strData)]
	data_list = [[f[0], re.findall("<v>(.*?)</v>", f[1])[0]] for f in data_list]

	# Extract A,B Column and Convert String Data to Float
	data_list_A = np.array([[float(f[0][1:]), float(f[1])] for f in data_list if f[0][0] == "A"])
	data_list_B = np.array([[float(f[0][1:]), float(f[1])] for f in data_list if f[0][0] == "B"])

	# Sort Data and Marge A with B
	data_list_A = np.array(sorted(data_list_A, key=lambda x: x[0])).transpose(1, 0)[1]
	data_list_B = np.array(sorted(data_list_B, key=lambda x: x[0])).transpose(1, 0)[1]

	return (data_list_A, data_list_B)

def get_text(strData):
	return [m for m in re.findall("<t>(.*?)</t>", strData)]

def main():
	# Reading Data
	strData = get_sheetdata("Data.xlsx")
	strText = get_textdata("Data.xlsx")

	# Extract Data
	(data_list_A, data_list_B) = get_column_AB(strData)
	data_text = get_text(strText)

	# Get X,Y Axis String and Remove Header from Data
	strXaxis = data_text[int(data_list_A[0])]
	strYaxis = data_text[int(data_list_B[0])]
	data_list_A = data_list_A[1:]
	data_list_B = data_list_B[1:]

	# Initialization of plt
	fig = plt.figure()
	axs = [fig.add_subplot(111)]
	axs[0].set_xlabel(strXaxis)
	axs[0].set_ylabel(strYaxis)
	axs[0].set_xlim([np.min(data_list_A), np.max(data_list_A)])
	axs[0].set_ylim([np.min(data_list_B), np.max(data_list_B)])
	axs[0].plot(data_list_A, data_list_B, c="blue")

	plt.show()

main()
