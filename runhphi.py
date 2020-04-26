#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 13:21:55 2019

@author: fmalgarini
"""

import os
import re
import sys
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from modules.mod import get_energy, get_exchange, modify_modpara, modify_calcmod, modify_locspn, add_interall_to_namelist, run_Hphi, generate_plot, get_dimensions, fetch_settings, read_kpath
from modules.color_map_modules import plot_colormap

dynamicalGreen_file_columns = ["omega_Re", "omega_Im", "Re(G(z))", "Im(G(z))"]
color_map_columns = ["kx", "omega_Re", "Im(G(z))"]

def plot(lattice_num, x_kpath, y_kpath, length, width, num_kvals, nOmega, gs_energy):

	#We define the dataframe which will contain the dynamical Green function (DGF for short); our aim is to plot the k values against the real frequencies column of this dataframe
	df = pd.DataFrame(columns = dynamicalGreen_file_columns)
	df_colormap = pd.DataFrame(columns = color_map_columns)

	#Preparing the df to contain the correct information to be plotted. We want the value of the real part of the frequency for which the imaginary part of the DGF is minimum

	if lattice_num == 3:
		for i in range(len(x_kpath)):
			df, df_singlekx_colormap = generate_plot(x_kpath[i]/width, y_kpath[i]/length, df, length)

	else:
		for i in range(0, length):
			df, df_singlekx_colormap = generate_plot(i/length, 0, df, length)
			df_colormap = df_colormap.append(df_singlekx_colormap)

	df_colormap = df_colormap.append(df_colormap.loc[df_colormap["kx"] == 0.0])

	with open("./colorplot.def", "w") as f:
		df_colormap.to_csv(f, sep = ' ')

	df = df.append(df.iloc[0], sort = False)

	#Let us append the k_values to df as index, because i want them in the dispersion_relation.def file for plotting. I need to rewrite it for the square
	e = pd.Series([x/length for x in x_kpath])
	e = e.append(pd.Series([1]))
	#Rescale the k vector to the more usual (0,2pi) instead of (0,1)
	e = e.mul(2*math.pi)

	df = df.set_index(e)
	#It is customary to plot the dispersion relation choosing the GS energy as the zero point energy. HPhi uses the GS energy it calculates as lowest energy for the dispersion relations, so I sum it to omega
	df["omega_Re"] = df["omega_Re"] - gs_energy #remember that gs_energy < 0!!
	df.to_csv("./Dispersion_relation.def", columns = ["omega_Re", "Im(G(z))"], index_label="Kx", sep=' ')
	#Prepare the plot of the K values versus the real parts of the frequency omega
	plt.plot(np.linspace(0, 1, num_kvals+1), list(df.iloc[:,0]))
	plt.savefig("./dispersion_plot", format = 'pdf')
	plt.show()

	if lattice_num != 3: #Currently not working for square lattice (the whole colormap program has to be rewritten anyways)
		plot_colormap(length, nOmega)

def main():

	run = int(sys.argv[1])

	settings_values, settings_keys = fetch_settings()
	if settings_values:
		settings = dict(zip(settings_keys, settings_values))

		try:
			nOmega = settings["NOmega"]
			DM_interaction = settings["DM"]
			S = settings["2S"]
		except KeyError as e:

			#Using standard values if one of the settings is missing
			if str(e) == 'nOmega':
				print("nOmega is not specified in settings; using default value of 100")
				nOmega = 100
			elif str(e) == "'DM_interaction'":
				print("DM_interaction is not specified in settings; using default value of 0")
				DM_interaction = 0
			elif str(e) == "'2S'":
				print("2S is not specified in settings; using default value of 2S=1")
				S = 1
			else:
				print("The syntax of the settings file is not correct. Please refer to the manual, or download the template from github for reference")

	else:
		#Using standard values instead
		nOmega = 100
		DM_interaction = 0
		S = 1

	gs_energy = get_energy()
	length, width, lattice_num = get_dimensions()
	x_kpath, y_kpath = read_kpath(length, width, lattice_num)
	num_kvals = len(x_kpath)

	if run == True:
		J = 0
		if S != 1:
			modify_locspn(S)
			J = get_exchange(lattice_num)

		if DM_interaction != 0 or S != 1:
			print("Adding InterAll file")
			os.system("./modules/write_interall {0} {1} {2} {3} {4} {5} > ./PrepareData/InterAll.def".format(length, width, lattice_num, DM_interaction, S, J))
			#When 2S!=1 we must use InterAll instead of the usual exchange.def, Hund.def and CoulombInter.def. Thus, the three latter files have to be removed from namelist.def, so that only InterAll.def is used
			add_interall_to_namelist(S)

		#Necessary modifications to the input files to compute the DGF: read the HPhi manual for more details
		modify_modpara(gs_energy, nOmega)
		modify_calcmod()

		#For the square I want the user to specify any k-path he wants, so I have to write a function that treats this case
		for i in range(num_kvals):
			if lattice_num == 3:
				print("Computing the dispersion relation for point {0} out of {1}".format(i+1, num_kvals))
				run_Hphi(length, width, x_kpath[i]/width, y_kpath[i]/length)
			else:
				#Running HPhi for N equally spaced values of K between 0 and 1, where N is the number of sites specified
				print("Computing the dispersion relation for K={0}".format(x_kpath[i]/length))
				run_Hphi(length, width, x_kpath[i]/length, 0)

	plot(lattice_num, x_kpath, y_kpath, length, width, num_kvals, nOmega, gs_energy)

if __name__ == '__main__':
	main()
