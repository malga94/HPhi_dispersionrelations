#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 13:21:55 2019

@author: fmalgarini
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from modules.mod import get_energy, modify_modpara, modify_calcmod, run_Hphi, generate_plot, get_dimensions, fetch_settings
from modules.color_map_modules import plot_colormap

dynamicalGreen_file_columns = ["omega_Re", "omega_Im", "Re(G(z))", "Im(G(z))"]
color_map_columns = ["kx", "omega_Re", "Im(G(z))"]
settings_keys = ["nOmega"] #Updated list of all the user defined settings which can currently be adjusted in the file ./modules/settings.def

def main():

	#We define the dataframe which will contain the dynamical Green function (DGF for short); our aim is to plot the k values against the real frequencies column of this dataframe
	df = pd.DataFrame(columns = dynamicalGreen_file_columns)
	df_colormap = pd.DataFrame(columns = color_map_columns)

	settings_values = fetch_settings()
	settings = dict(zip(settings_keys, settings_values))
	#TODO: mettere un try except o qualcosa che controlli che keys e values siano due liste della stessa lunghezza
	nOmega = settings["nOmega"] 

	gs_energy = get_energy()
	#Necessary modifications to the input files to compute the DGF: read the HPhi manual for more details
	modify_modpara(gs_energy, nOmega)
	modify_calcmod()

	length, width = get_dimensions()

	#Running HPhi for N equally spaced values of K between 0 and 1, where N is the number of sites specified
	for i in range(0, length):
		run_Hphi(i, length)

	#Preparing the df to contain the correct information to be plotted. We want the value of the real part of the frequency for which the imaginary part of the DGF is minimum
	for i in range(0, length):
		df, df_singlekx_colormap = generate_plot(i, df, length)
		df_colormap = df_colormap.append(df_singlekx_colormap)

	df_colormap = df_colormap.append(df_colormap.loc[df_colormap["kx"] == 0.0])
	
	with open("./colorplot.def", "w") as f:
		df_colormap.to_csv(f, sep = ' ')

	df = df.append(df.iloc[0], sort = False)
	
	df.to_csv("./Dispersion_relation.def")
	#Prepare the plot of the K values versus the real parts of the frequency omega
	plt.plot(np.linspace(0, 1, length+1), list(df.iloc[:,0]))
	plt.show()
	plt.savefig("./plot_dispersion", format = 'pdf')

	plot_colormap(length, nOmega)

if __name__ == '__main__':
	main()



