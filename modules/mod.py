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
import json

dynamicalGreen_file_columns = ["omega_Re", "omega_Im", "Re(G(z))", "Im(G(z))"]
supported_lattice_dict = {"chain": 1, "ladder": 2}

#Since the template of the Standard.in file changes according to what kind of lattice we run (for instance the chain has one dimension L and one exchange J, the ladder has two of each), we create a json file containing all the templates in the form of dict,
#in ./modules/templates.json
#We will have to manually add the template for new lattice we wish to implement in this program. The function returns input_file_syntax which contains the template for the chosen lattice
def get_lattice_syntax():

	try:
		os.chdir("./PrepareData")
	#If the directory does not exist we create it
	except:
		os.mkdir("./PrepareData")
		os.chdir("./PrepareData")
		os.system("cat ../modules/standard_template.def > Standard.in")
	finally:
		os.chdir("..")

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

def get_dimensions():

	lattice, lattice_num, input_file_syntax = get_lattice_syntax()

	if lattice.lower() == "chain":
		try:
			with open("./PrepareData/Standard.in", "r") as f:
				input_file = f.read()

			site_number = input_file.splitlines()[input_file_syntax["L"]].split("=")[1].replace(" ", "")
			return int(site_number), 1
		except:
			return 1, 1

	elif lattice.lower() == "ladder":
		try:
			with open("./PrepareData/Standard.in", "r") as f:
				input_file = f.read()

			length = input_file.splitlines()[input_file_syntax["L"]].split("=")[1].replace(" ", "")
			width = input_file.splitlines()[input_file_syntax["W"]].split("=")[1].replace(" ", "")

			return int(length), int(width)
		except:
			return 1, 1

	elif lattice_num < 0:
		return 1, 1


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

def fetch_settings():

	values_to_set = []

	try:
		with open("./modules/settings.def") as f:
			settings_file = f.read()

	except FileNotFoundError as fnf_error:
		print(fnf_error)
		print("Using the standard HPhi settings instead")

	settings = settings_file.splitlines()
	settings = filter_comments(settings)
	for line in settings:
		values_to_set.append([int(x) for x in line.split() if x.isdigit()][0])

	return values_to_set

def clear_workspace(length):

	os.system("rm -Rf kx0*")

	os.chdir("./PrepareData")

	os.system("rm -R output calcmod.def coulombinter.def exchange.def geometry.dat greenone.def greentwo.def hund.def lattice.gp locspn.def modpara.def namelist.def pair.def 2> /dev/null")
	
	os.chdir("..")

def run_Hphi(i, length):

	lattice, lattice_num, input_file_syntax = get_lattice_syntax()
	
	os.system("rsync -a --exclude='./PrepareData/std_job.out' --exclude='./PrepareData/Standard.in' PrepareData/ kx{0}".format(i/length, '.3f'))
	#TODO: Ma perchè se ho formattato con .3f rsync mi copia ancora le cartelle chiamandole con float a 3000 cifre decimali?? Che problemi ha?	
	os.system("./modules/writepair {0} {1} {2} > ./kx{0}/pair.def".format(i/length, length, lattice_num, '.3f'))
	os.chdir("./kx{0}".format(i/length, '.3f'))
	os.system("../HPhi -e namelist.def > kx{0}_job.out".format(i/length, '.3f'))
	os.chdir("..")

def generate_plot(i, df, length):
	
	os.chdir("./kx{0}".format(i/length, '.3f'))
	temp_df = pd.read_csv("./output/zvo_DynamicalGreen.dat", header = None, index_col=False, names = dynamicalGreen_file_columns, sep = ' ')
	
	min_val = temp_df[temp_df['Im(G(z))']==temp_df['Im(G(z))'].min()].iloc[0]
	df_colormap = temp_df[['omega_Re', 'Im(G(z))']].copy()
	
	df_colormap['kx'] = [i/length]*temp_df.shape[0]
	
	#TODO: Perchè se metto sort=False o sort=True in questo append, non funziona più nulla
	df = df.append(min_val)
	os.chdir("..")	
	return df, df_colormap

