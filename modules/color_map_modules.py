#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 13:21:55 2019

@author: fmalgarini
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

dynamicalGreen_file_columns = ["omega_Re", "omega_Im", "Re(G(z))", "Im(G(z))"]

def prepare_color_file(nsite):

	try:
		f = open("./colorplot.def", "w")
		f.write('')
	except:
		pass

	for i in range(0, nsite):
		os.system("cat ./kx{0}ky{1}/output/zvo_DynamicalGreen.dat >> ./colorplot.def".format(i/nsite, 0))

def prepare_list_to_plot(nsite, nOmega):

	#TODO: Ma che cavolo è sta roba? 
	with open("./colorplot.def", "r") as f:
		df = pd.read_csv(f, sep = ' ', error_bad_lines=False, header = None, names = dynamicalGreen_file_columns, index_col = False)
	
	Z = []

	vals = [nOmega*i for i in range(0, nsite)]
	for val in vals:
		Y = df[['Im(G(z))']].loc[val:val+499].values
		Y = [y[0] for y in Y]
		Z.append(Y)

	Y = df[['Im(G(z))']].loc[:nOmega-1].values
	Y = [y[0] for y in Y]
	
	Z.append(Y)
	return Z

def turn_around_listoflists(Z):

	lista_temp = []
	lista_vera = []

	for i in range(len(Z[0])):
		for element in Z:
			lista_temp.append(element[i])

		lista_vera.append(lista_temp)
		lista_temp = []

	return lista_vera

def plot_colormap(nsite, nOmega):

	prepare_color_file(nsite)

	Z = prepare_list_to_plot(nsite, nOmega)

	ZTranspose = turn_around_listoflists(Z)
	
	plt.pcolor(ZTranspose)
	# print(np.linspace(-2.5, 3, 10))
	# plt.yticks(np.linspace(0, 500, 20), np.linspace(-2.50, 7, 20))
	# plt.xticks(np.arange(0, len(Z.columns), 1), Z.columns)
	
	plt.show()





