#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 13:21:55 2019

@author: fmalgarini
"""

import os
import re
import sys
import time, datetime
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from modules.mod import get_energy, get_exchange, modify_modpara, modify_calcmod, modify_locspn, add_interall_to_namelist, run_Hphi, generate_plot, get_dimensions, fetch_settings, read_kpath, output_hamiltonian
from modules.color_map_modules import plot_colormap

dynamicalGreen_file_columns = ["omega_Re", "omega_Im", "Re(G(z))", "Im(G(z))"]
color_map_columns = ["kx", "omega_Re", "Im(G(z))"]

#These two functions momentarily disable print; I use them when ignore_warnings in the settings is set to 1, in which case warning messages will not be printed. Remember to always enable after
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__

def write_to_log(time_elapsed, num_kvals, lattice_num, nOmega, nSites, log_length):
	if log_length != 0:
		i = -1
		with open('./log.def', 'r') as f:
			for i, l in enumerate(f):
				pass
			if i > log_length:
				#Removing oldest 3 lines (corresponding to 1 run) when the file becomes too large. The '' after the -i option in sed avoids the creation of a backup file, but I think it might only work on OSX: I will have to check this, and in case modify it
				os.system("""sed -i '' -e '1,3d' log.def""")

	with open('./log.def', 'a') as f:
		f.write("Date: {0}\nLattice: {1}, Nsites: {2}, Kvalues: {3}, NOmega: {4}\nElapsed time (seconds): {5}\n\n".format(datetime.datetime.now(), lattice_num, nSites, num_kvals, nOmega, time_elapsed))

def plot(lattice_num, x_kpath, y_kpath, length, width, num_kvals, nOmega, gs_energy, do_we_plot, do_we_show):

	#We define the dataframe which will contain the dynamical Green function (DGF for short); our aim is to plot the k values against the real frequencies column of this dataframe
	df = pd.DataFrame(columns = dynamicalGreen_file_columns)
	df_colormap = pd.DataFrame(columns = color_map_columns)

	#Preparing the df to contain the correct information to be plotted. We want the value of the real part of the frequency for which the imaginary part of the DGF is minimum

	if lattice_num == 3:
		for i in range(len(x_kpath)):
			df = generate_plot(x_kpath[i]/width, y_kpath[i]/length, df, length)

	else:
		for i in range(0, length):
			df = generate_plot(i/length, 0, df, length)

	df = df.append(df.iloc[0], sort = False)

	#Let us append the k_values to df as index, because i want them in the dispersion_relation.def file for plotting.
	if lattice_num < 3:
		e = pd.Series([x/length for x in x_kpath])
		e = e.append(pd.Series([1]))
		#Rescale the k vector to the more usual (0,2pi) instead of (0,1)
		e = e.mul(2*math.pi)
	else:
		e = pd.Series([(x/length,y/width) for x,y in zip(x_kpath, y_kpath)])
		e = e.append(pd.Series([(x_kpath[0]/length, y_kpath[0]/width)]))

	df = df.set_index(e)
	#It is customary to plot the dispersion relation choosing the GS energy as the zero point energy. HPhi uses the GS energy it calculates as lowest energy for the dispersion relations, so I sum it to omega
	df["omega_Re"] = df["omega_Re"] - gs_energy #remember that gs_energy < 0!!

	df.to_csv("./Dispersion_relation.def", columns = ["omega_Re", "Im(G(z))"], index_label="Kx", sep=' ')
	#Prepare the plot of the K values versus the real parts of the frequency omega
	if do_we_plot != 0:
		plt.plot(np.linspace(0, 1, num_kvals+1), list(df.iloc[:,0]))
		plt.savefig("./dispersion_plot", format = 'pdf')
		if do_we_show:
			plt.show()

 	#Currently not working for square lattice (the whole colormap program has to be rewritten anyways)
	plot_colormap(lattice_num, length, width, x_kpath, y_kpath, nOmega, do_we_plot, do_we_show)

def main():

	if sys.argv[1] == "-h":
		print("Program that uses HPhi to calculate and plot the magnon dispersion relation for your system. Options:\n0: Prepares every file and directory for the calculation of the dispersion relation, but does run HPhi\n1: Like 0, but also runs HPhi and outputs the dispersion relation (this is probably what you need)\n-h: display this help text")
		exit()
	try:
		run = int(sys.argv[1])
	except ValueError:
		print("Invalid option. Use option -h for help menu")
		exit()
	except Exception as e:
		print("Unexpected error:{0}", str(e))
		exit()

	start = time.time()
	settings_values, settings_keys = fetch_settings()
	if settings_values:
		settings = dict(zip(settings_keys, settings_values))

		try:
			#Using standard values if one of the settings is missing
			try:
				ignore_warnings = settings["ignore_warnings"]
			except KeyError:
				ignore_warnings = 0

			if ignore_warnings:
				blockPrint()

			try:
				nOmega = settings["NOmega"]
			except KeyError:
				print("nOmega is not specified in settings; using default value of 100")
				nOmega = 100

			try:
				max_omega = settings["max_omega"]
			except KeyError:
				print("The maximum frequency max_omega for which to compute the Dynamical Green functions is not specified in settings; using default value of 7")
				max_omega = 7

			try:
				DM_interaction = settings["DM"]
			except KeyError:
				print("DM_interaction is not specified in settings; using default value of 0")
				DM_interaction = 0

			try:
				S = settings["2S"]
			except KeyError:
				print("2S is not specified in settings; using default value of 2S=1")
				S = 1

			try:
				anisotropy = settings["anisotropy"]
			except KeyError:
				print("Anisotropy is not specified in settings: defaulting to 0 (isotropic Heisenberg Hamiltonian)")
				anisotropy = 0

			try:
				output_ham = settings["Output_Hamiltonian"]
			except KeyError:
				print("Output_Hamiltonian is not specified in settings; using default value of 0 (not outputting Hamiltonian matrix)")
				output_ham = 0

			try:
				do_we_plot = settings["plot"]
			except KeyError:
				print("Plot is not specified in settings; the plot of the dispersion relation will be shown at the end of the calculation. Set plot = 0 in settings to avoid showing the plot")
				do_we_plot = 1

			try:
				do_we_show = settings["show_plot"]
			except KeyError:
				do_we_show = 1
				
			try:
				log_length = settings["log_file_length"]
			except KeyError:
				log_length = 100

			enablePrint()
			
		except:
			print("The syntax of the settings file is not correct. Please refer to the manual, or download the template from github for reference")
			exit()

		finally:
			enablePrint()

	else:
		#Using standard values instead
		nOmega = 200
		max_omega = 7
		DM_interaction = 0
		S = 1
		anisotropy = 0
		output_ham = 0
		do_we_plot = 1
		log_length = 100
		do_we_show = 1
		ignore_warnings = 0

	gs_energy = get_energy()
	length, width, lattice_num = get_dimensions(0)
	x_kpath, y_kpath = read_kpath(length, width, lattice_num)
	num_kvals = len(x_kpath)
	
	if run == True:

		if output_ham:
			if length*width > 12 and not ignore_warnings:
				print("Warning: the system is very large and will take a long time for exact diagonalization. If you want to run it anyway, please set ignore_warnings = 1 in the settings. ")
			else:
				output_hamiltonian(length, width, lattice_num)

		if S != 1:
			modify_locspn(S)

		if DM_interaction != 0 or S != 1:
			J_list = get_exchange()
			print("Adding InterAll file")
			os.system("./modules/write_interall {0} {1} {2} {3} {4} {5} {6} > ./PrepareData/InterAll.def".format(length, width, lattice_num, DM_interaction, S, float(J_list[0]), float(J_list[1])))
			#When 2S!=1 we must use InterAll instead of the usual exchange.def, Hund.def and CoulombInter.def. Thus, the three latter files have to be removed from namelist.def, so that only InterAll.def is used
			add_interall_to_namelist(S)

		if anisotropy != 0:
			print("Adding anisotropy")
			J_list = get_exchange()
			#Changing coulombinter and hund files to include the anisotropy (they govern the SzSz part of the Heisenberg Hamiltonian)
			#NB:Still have to write most interactions for the ladder
			os.system("./modules/write_anisotropy {0} {1} {2} {3} {4} {5} {6} {7} {8} {9} > ./PrepareData/coulombinter.def".format(length, width, lattice_num, float(J_list[0]), float(J_list[1]), float(J_list[2]), float(J_list[3]), float(J_list[4]), anisotropy, 0))
			os.system("./modules/write_anisotropy {0} {1} {2} {3} {4} {5} {6} {7} {8} {9} > ./PrepareData/hund.def".format(length, width, lattice_num, float(J_list[0]), float(J_list[1]), float(J_list[2]), float(J_list[3]), float(J_list[4]), anisotropy, 1))

		#Necessary modifications to the input files to compute the DGF: read the HPhi manual for more details
		modify_modpara(gs_energy, max_omega, nOmega)
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

	
	end = time.time()
	time_elapsed = end-start
	write_to_log(time_elapsed, num_kvals, lattice_num, nOmega, length*width, log_length)

	plot(lattice_num, x_kpath, y_kpath, length, width, num_kvals, nOmega, gs_energy, do_we_plot, do_we_show)

if __name__ == '__main__':
	main()
