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

def prepare_color_file(lattice_num, length, width, x_kpath, y_kpath):

	try:
		f = open("./colorplot.def", "w")
		f.write('')
	except:
		print("Warning: could not produce colorplot. Please give writing permissions to the program (either run it as administrator on windows, or chmod -R 664 foldername on Unix)")

	if lattice_num == 3:
		for i in range(len(x_kpath)):
			os.system("cat ./kx{0}ky{1}/output/zvo_DynamicalGreen.dat >> ./colorplot.def".format(x_kpath[i]/width, y_kpath[i]/length))

	else:
		for i in range(0, length):
			os.system("cat ./kx{0}ky{1}/output/zvo_DynamicalGreen.dat >> ./colorplot.def".format(i/length, 0))
		os.system("cat ./kx{0}ky{1}/output/zvo_DynamicalGreen.dat >> ./colorplot.def".format(0/length, 0))

def prepare_list_to_plot(nkpoints, nOmega):
	#Produces a list of lists of length N_k, where N_k is the total number of k-points in which we calculate the dispersion relation
	#Each list inside is of length NOmega, and contains all the values of Im[G(z)] for that specific k-point, for varying omega
	with open("./colorplot.def", "r") as f:
		df = pd.read_csv(f, sep = ' ', error_bad_lines=False, header = None, names = dynamicalGreen_file_columns, index_col = False)

	Z = []

	vals = [nOmega*i for i in range(0, nkpoints+1)]
	for val in vals:
		Y = df[['Im(G(z))']].loc[val:val+499].values
		#next line simply because loc returns a list of one element instead of simply a number, so that Y is a list of lists. I want Y to be just a list
		Y = [y[0] for y in Y]
		Z.append(Y)

	return Z

def turn_around_listoflists(Z):

	#Instead of K_n lists of NOmega elements, what we really need for the plot is NOmega lists of K_n elements
	#This function takes the list of lists creeated by the previous function, unpacks it and groups it by
	#equal omega instead of equal K-points.
	lista_temp = []
	lista_vera = []

	for i in range(len(Z[0])):
		for element in Z:
			lista_temp.append(element[i])

		lista_vera.append(lista_temp)
		lista_temp = []

	return lista_vera

def plot_colormap(lattice_num, length, width, x_kpath, y_kpath, nOmega):

	prepare_color_file(lattice_num, length, width, x_kpath, y_kpath)

	if lattice_num != 3:
		num_k_points = length
	else:
		#Minus one because differently from the chain and ladder, here we don't append the first point to the
		#end of the lists for symmetry (in the chain we always finish with K=2pi which gives exactly the same
		#values of Im[G(z)] as k=0)
		num_k_points = len(x_kpath)-1
	Z = prepare_list_to_plot(num_k_points, nOmega)

	ZTranspose = turn_around_listoflists(Z)

	plt.pcolor(ZTranspose)
	# print(np.linspace(-2.5, 3, 10))
	# plt.yticks(np.linspace(0, 500, 20), np.linspace(-2.50, 7, 20))
	# plt.xticks(np.arange(0, len(Z.columns), 1), Z.columns)

	plt.show()
