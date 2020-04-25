#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 13:21:55 2019

@author: fmalgarini
"""

import os
import subprocess
import re
import numpy as np
import pandas as pd
import json

dynamicalGreen_file_columns = ["omega_Re", "omega_Im", "Re(G(z))", "Im(G(z))"]
supported_lattice_dict = {"chain": 1, "ladder": 2, "square": 3}

#Since the template of the Standard.in file changes according to what kind of lattice we run (for instance the chain has one dimension L and one exchange J, the ladder has two of each), we create a json file containing all the templates in the form of dict,
#in ./modules/templates.json
#We will have to manually add the template for new lattice we wish to implement in this program. The function returns input_file_syntax which contains the template for the chosen lattice
def get_lattice_syntax():

	try:
		with open("./PrepareData/Standard.in", "r") as f:
			inputfile = f.read()
	except:
		return "None", -1, 0

	lattice = inputfile.splitlines()[2].split("=")[1].replace('"', '').replace(" ", "")

	for l in supported_lattice_dict.keys():
		if not lattice.find(l) == -1:
			lattice = l
			lattice_num = supported_lattice_dict[l]

	if not lattice in supported_lattice_dict.keys():
		print("Error: the lattice specified in the generate_inputfile script is not supported. Please choose from the following: {0}".format(supported_lattice_dict.keys()))
		exit()

	with open("./modules/templates.json", "r") as f:
		templates = json.load(f)
		input_file_syntax = templates[lattice]

	return lattice, lattice_num, input_file_syntax

def modify_modpara(gs_energy, nOmega):

	os.chdir("./PrepareData")
	sed_command_for_DGF = "sed -e 's/OmegaOrg.*/OmegaIm        0.5/' modpara.def | sed 's/NOmega.*/NOmega         {0}/' | sed 's/OmegaMax.*/OmegaMax       7/' | sed 's/OmegaMin.*/OmegaMin       {1}/g' > modpara.def.tmp && mv modpara.def.tmp modpara.def".format(nOmega, gs_energy)
	os.system(sed_command_for_DGF)
	os.chdir("..")

def modify_calcmod():

	os.chdir("./PrepareData")
	sed_command_for_DGF = "sed -e 's/CalcSpec.*/CalcSpec   1/' calcmod.def | sed 's/InputEigenVec.*/InputEigenVec    1/' | sed 's/OutputEigenVec.*/OutputEigenVec    0/' > calcmod.def.tmp && mv calcmod.def.tmp calcmod.def"
	os.system(sed_command_for_DGF)
	os.chdir("..")

def modify_locspn(S):
	spin_file = []
	os.chdir("./PrepareData")
	#I allowed myself to hardcode the 5 and 6 in head and tail commands because the HPhi manual explicitally states that the header of locspn.def is always 5 lines. Could break if HPhi standards for input files change; rewrite this part
	get_header = "head -n5 locspn.def > temp.def"
	change_spin = "tail -n +6 locspn.def | awk '{ $2=%d; print $0 }' >> temp.def" % S
	os.system(get_header)
	os.system(change_spin)
	os.system("mv temp.def locspn.def")
	os.chdir("..")

def get_exchange(lattice_num):

	grep_command_NN = "cat PrepareData/Standard.in | grep 'J'"
	J_line = subprocess.check_output([grep_command_NN], shell=True)
	exchange = int(J_line.decode("utf-8").split()[2])
	return exchange

def add_interall_to_namelist(S):

	os.system("""echo "InterAll InterAll.def" >> ./PrepareData/namelist.def""")
	if S != 1:
		os.chdir("./PrepareData")
		use_only_interall = "sed -e 's/Exchange.*//' namelist.def | sed -e 's/CoulombInter.*//' | sed -e 's/Hund.*//' | awk 'NF' > temp.def"
		os.system(use_only_interall)
		os.system("mv temp.def namelist.def")
		os.system("rm temp.def")
		os.system("../HPhi -e namelist.def > exp_job.out")
		os.chdir("..")

def get_dimensions():

	lattice, lattice_num, input_file_syntax = get_lattice_syntax()

	if lattice.lower() == "chain":
		try:
			with open("./PrepareData/Standard.in", "r") as f:
				input_file = f.read()

			site_number = input_file.splitlines()[input_file_syntax["L"]].split("=")[1].replace(" ", "")
			return int(site_number), 1, lattice_num
		except:
			print("Could not find the length of the chain in the input file. Please add the relevant line to Standard.in")
			exit()

	elif lattice.lower() == "ladder" or lattice.lower() == "square":
		try:
			with open("./PrepareData/Standard.in", "r") as f:
				input_file = f.read()

			length = input_file.splitlines()[input_file_syntax["L"]].split("=")[1].replace(" ", "")
			width = input_file.splitlines()[input_file_syntax["W"]].split("=")[1].replace(" ", "")

			return int(length), int(width), lattice_num
		except:
			print("Could not find the length/width of the system in the input file. Please add the relevant line to Standard.in")
			exit()

def get_energy():

	try:
		with open("./PrepareData/output/zvo_energy.dat", "r") as f:
			energy_file = f.read()

	except FileNotFoundError as fnf_error:
		print(fnf_error)
		print("This is most likely because the standard mode did not run correctly: check the file ./PrepareData/std_job.out to see if something went wrong")
		exit()

	except Exception as e:
		print(str(e))
		exit()

	energy = energy_file.splitlines()[0].split(" ")[2]

	return float(energy)

def filter_comments(settings):

	filter_emptylines = [x for x in settings if x.strip()]
	filter_comments = []

	for line in filter_emptylines:
		if line[0] == "#":
			continue
		else:
			filter_comments.append(line)

	return filter_comments

def isfloat(x):

	try:
		a = float(x)
		return True
	except ValueError:
		return False

def fetch_settings():

	values_to_set = []
	keys_to_set = []

	try:
		with open("./modules/settings.def") as f:
			settings_file = f.read()

	except FileNotFoundError as fnf_error:
		print(fnf_error)
		print("Using the standard HPhi settings instead")
		return False

	settings = settings_file.splitlines()
	settings = filter_comments(settings)

	for line in settings:
		keys_to_set.append(line.split()[0])
		try:
			values_to_set.append([float(x) for x in line.split() if isfloat(x.lstrip('-'))][0])
		except Exception as e:
			print(str(e))
			print("\nThis is because in the ./modules/settings.def file all lines should specify a number, not a string or anything else")

	return values_to_set, keys_to_set

def read_kpath(length, width):
	#A function to read the kpath document, which tells the program on which k-path to compute the dispersion relation for the square lattice.
	#The syntax of the file is the following: the first line is a header, and from the second line onwards there is a pair of integer values separated by a comma, which represent a point in real space. These values are the coordinates of a given site,
	#where the site indexes start from (0,0). Each new line represents a new point. The "k-path" can be as long as the user wants (in other words the file can have as many lines as one wants) and if the coordinates specified exceed the dimensions of
	#the square lattice, they will be "folded" back to a valid coordinate with the % operator

	x_kpath = []
	y_kpath = []

	try:
		with open("./modules/kpath.def") as f:
			kpath_file = f.read()

	except FileNotFoundError as fnf_error:
		print(fnf_error)
		print("Working on horizontal k-path with Ky = 0")
		for i in range(0, width):
			x_kpath.append(i)
		return x_kpath, [0]*length

	points = kpath_file.splitlines()

	for i in range(1, len(points)):
		x_coord = int(points[i].split(",")[0])
		y_coord = int(points[i].split(",")[1])

		if x_coord >= width:
			x_coord = x_coord%width

		if y_coord >= length:
			y_coord = y_coord%width

		x_kpath.append(x_coord)
		y_kpath.append(y_coord)

	return x_kpath, y_kpath

def clear_workspace():

	os.system("rm -Rf kx0*")

	os.chdir("./PrepareData")

	os.system("rm -R output calcmod.def coulombinter.def exchange.def geometry.dat greenone.def greentwo.def hund.def lattice.gp locspn.def modpara.def namelist.def pair.def InterAll.def 2> /dev/null")

	os.chdir("..")

def run_Hphi(length, width, kx, ky):

	lattice, lattice_num, input_file_syntax = get_lattice_syntax()

	os.system("rsync -a --exclude='./PrepareData/std_job.out' --exclude='./PrepareData/Standard.in' PrepareData/ kx{0}ky{1}".format(kx, ky, '.3f'))
	#TODO: Ma perchè se ho formattato con .3f rsync mi copia ancora le cartelle chiamandole con float a 3000 cifre decimali?? Che problemi ha?
	os.system("./modules/writepair {0} {1} {2} {3} {4} > ./kx{0}ky{1}/pair.def".format(kx, ky, length, width, lattice_num, '.3f'))
	os.chdir("./kx{0}ky{1}".format(kx, ky, '.3f'))
	os.system("../HPhi -e namelist.def > kx{0}ky{1}_job.out".format(kx, ky, '.3f'))
	os.chdir("..")

def generate_plot(kx, ky, df, length):

	os.chdir("./kx{0}ky{1}".format(kx, ky, '.3f'))
	temp_df = pd.read_csv("./output/zvo_DynamicalGreen.dat", header = None, index_col=False, names = dynamicalGreen_file_columns, sep = ' ')

	min_val = temp_df[temp_df['Im(G(z))']==temp_df['Im(G(z))'].min()].iloc[0]
	df_colormap = temp_df[['omega_Re', 'Im(G(z))']].copy()

	df_colormap['kx'] = [kx]*temp_df.shape[0]

	#TODO: Perchè se metto sort=False o sort=True in questo append, non funziona più nulla
	df = df.append(min_val)
	#TODO: Sto scemo di df così contiene anche un indice, che è il numero della riga di zvo_DynamicalGreen in cui c'è il minimo. Va levato perchè il file dispersion_relation.def in cui metto questo df diventa incasinato
	os.chdir("..")
	return df, df_colormap
