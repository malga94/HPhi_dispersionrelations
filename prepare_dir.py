#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 13:21:55 2019

@author: fmalgarini
"""

import os
import re
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from modules.mod import get_dimensions, clear_workspace, run_interrupted

dynamicalGreen_file_columns = ["omega_Re", "omega_Im", "Re(G(z))", "Im(G(z))"]

def main():

	if int(sys.argv[1]) == True:
		clear_workspace()
		exit()
	#Let's create the main directory, where the standard mode will be run and thus the energy and eigenvector of the ground state of the system will be calculated
	try:
		os.chdir("./PrepareData")
	#If the directory does not exist we create it
	except:
		os.mkdir("./PrepareData")
		os.chdir("./PrepareData")
		os.system("cat ../modules/standard_template.def > Standard.in")
	finally:
		os.chdir("..")

	#In case there was already a PrepareData directory, but somehow not a Standard.in file (can happen only if Standard.in is deleted manually)
	files = os.listdir("./PrepareData")
	if "Standard.in" not in files:
		os.chdir("./PrepareData")
		os.system("cat ../modules/standard_template.def > Standard.in")
		os.chdir("..")

	length, width, lattice_num = get_dimensions(1)

	if not run_interrupted():
		#This is the function which clears everything generated by the previous run, allowing us to perform a new run from scratch (except the final plot of course, which is kept). Remember to not call anything important kx0*, or it WILL be deleted!!
		clear_workspace()

	#Trying to compile the c scripts used to generate the pair.def file, interall file and files to treat anisotropy in the Heisenberg Hamiltonian
	try:
		os.system("gcc -o ./modules/writepair ./modules/writepair.c")
	except:
		raise IOError("Error: could not compile 'writepair.c'. Please compile the c program manually before running this script")

	try:
		os.system("gcc -o ./modules/write_interall ./modules/write_interall.c")
	except:
		raise IOError("Error: could not compile 'write_interall.c'. Please compile the c program manually before running this script")

	try:
		os.system("gcc -o ./modules/write_anisotropy ./modules/write_anisotropy.c")
	except:
		raise IOError("Error: could not compile 'write_anisotropy.c'. Please compile the c program manually before running this script")

	#Now we run HPhi in standard mode, to generate the eigenvector (needed for the calculation of the DGF). Also all the input files for expert mode are automatically generated, altough we will need to modify them a bit
	os.chdir("./PrepareData")
	os.system("../HPhi -s Standard.in > std_job.out")
	os.chdir("..")

if __name__ == '__main__':
	main()
