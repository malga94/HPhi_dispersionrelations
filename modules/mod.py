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
import datetime

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

	try:
		lattice = inputfile.splitlines()[2].split("=")[1].replace('"', '').replace(" ", "")
	except:
		print("Error: lattice not specified. Using standard template")
		copy = "cp modules/standard_template.def ./PrepareData/Standard.in"
		os.system(copy)
		lattice = "chain"

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

#This function looks at the output file in every kx directory (see next function) and determines if the program was interrupted while running, in which case the parts of the previous run which completed correctly will be kept
def did_it_run(dir):

	os.chdir("{0}".format(dir))
	files_list = os.listdir()
	for fi in files_list:
		#The output file has this name by default, and shoudln't be changed
		if fi[0:2] == "kx" and fi[-7:] == "job.out":
			output_file = fi

	try:
		with open("./" + output_file, 'r') as f:
			output_file_contents = f.read()
	except FileNotFoundError:
		return False

	os.chdir("..")

	#Would like to find a better way: when a run completes correctly, the output file ends with a newline. Of course that might happen even if it is interrupted (altough generally it does not), so this is not a great line
	try:
		if output_file_contents[-1] == '\n':
			return True
	#It means that the file was empty; this happens for instance if the calculation gets terminated by the user with ctrl+c in the shell
	except IndexError:
		return False
	except Exception as e:
		print("Error: {0}".format(str(e)))

	return False

#Function to determine if last run was interrupted before finishing properly
def run_interrupted():

	#Listing all directories that start with kx, which are the ones created in the previous run
	dgf_dirs = []
	ls = os.listdir()
	for dir in ls:
		if dir[0:2] == "kx":
			dgf_dirs.append(dir)

	for dir in dgf_dirs:
		if not did_it_run(dir):
			#Remove the half-run which didn't complete
			os.system("rm -Rf {0}".format(dir))
			return True

	return False

def modify_modpara(gs_energy, max_omega, nOmega):

	os.chdir("./PrepareData")
	sed_command_for_DGF = "sed -e 's/OmegaOrg.*/OmegaIm        0.5/' modpara.def | sed 's/NOmega.*/NOmega         {0}/' | sed 's/OmegaMax.*/OmegaMax       {1}/' | sed 's/OmegaMin.*/OmegaMin       {2}/g' > modpara.def.tmp && mv modpara.def.tmp modpara.def".format(nOmega, max_omega, gs_energy)
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

def get_exchange():

	lattice, lattice_num, input_file_syntax = get_lattice_syntax()

	with open("./PrepareData/Standard.in", "r") as f:
		input_file = f.read()

	if lattice_num == 1:

		try:
			J = input_file.splitlines()[input_file_syntax["J"]].split("=")[1].replace(" ", "")
		except IndexError:
			print("Warning: J not specified for the chain lattice. Are you sure you don't want nearest-neighbour exchange?")
			J = 0
		try:
			Jdash = input_file.splitlines()[input_file_syntax["J'"]].split("=")[1].replace(" ", "")
		except IndexError:
			print("Warning: J' not specified for the chain lattice. Defaulting to 0 (only NN exchange)")
			Jdash = 0
		except Exception as e:
			print("Error: {0}".format(str(e)))
			print("Using J' = 0")

		if J == 0 and Jdash == 0:
			print("Error: you have not specified any exchange interaction. Please check instructions on how to write the input file")
			exit()

		return [J, Jdash, 0, 0, 0]

	if lattice_num == 2:

		#Code for getting J0
		try:
			J0 = input_file.splitlines()[input_file_syntax["J0"]].split("=")[1].replace(" ", "")
		except IndexError:
			print("Warning: J0 (vertical coupling, along the rungs) not specified for ladder. Defaulting to 0")
			J0 = 0

		#Code for getting J1
		try:
			J1 = input_file.splitlines()[input_file_syntax["J1"]].split("=")[1].replace(" ", "")
		except IndexError:
			print("Warning: J1 (horizontal coupling) not specified for ladder. Defaulting to 0")
			J1 = 0
		except Exception as e:
			print("Error: {0}".format(str(e)))
			print("Using J1 = 0")

		#Code for getting J2
		try:
			J2 = input_file.splitlines()[input_file_syntax["J2"]].split("=")[1].replace(" ", "")
		except IndexError:
			print("Warning: J2 (diagonal coupling) not specified for ladder. Defaulting to 0")
			J2 = 0
		except Exception as e:
			print("Error: {0}".format(str(e)))
			print("Using J2 = 0")

		#Code for getting J1'
		try:
			J1dash = input_file.splitlines()[input_file_syntax["J1'"]].split("=")[1].replace(" ", "")
		except IndexError:
			print("Warning: J1' (next-nearest neighbour coupling) not specified for ladder. Defaulting to 0")
			J1dash = 0
		except Exception as e:
			print("Error: {0}".format(str(e)))
			print("Using J1' = 0")

		#Code for getting J2'
		try:
			J2dash = input_file.splitlines()[input_file_syntax["J2'"]].split("=")[1].replace(" ", "")
		except IndexError:
			print("Warning: J2' not specified for ladder. Defaulting to 0")
			J2dash = 0
		except Exception as e:
			print("Error: {0}".format(str(e)))
			print("Using J2' = 0")

		return [J0, J1, J2, J1dash, J2dash]

	if lattice_num == 3:
		#TODO: It should be possible to specify only J (instead of both J0 and J1) in the common case where the vertical and
		#horizontal NN exchange couplings have the same value

		#Code for getting J0
		try:
			J0 = input_file.splitlines()[input_file_syntax["J0"]].split("=")[1].replace(" ", "")
		except IndexError:
			print("Warning: J0 (horizontal coupling) not specified for square lattice. Defaulting to 0")
			J0 = 0

		#Code for getting J1
		try:
			J1 = input_file.splitlines()[input_file_syntax["J1"]].split("=")[1].replace(" ", "")
		except IndexError:
			print("Warning: J1 (vertical coupling) not specified for square lattice. Defaulting to 0")
			J1 = 0
		except Exception as e:
			print("Error: {0}".format(str(e)))
			print("Using J1 = 0")

		#Code for getting J'
		try:
			Jdash = input_file.splitlines()[input_file_syntax["J'"]].split("=")[1].replace(" ", "")
		except IndexError:
			print("Warning: J' (diagonal coupling) not specified for square lattice. Defaulting to 0")
			Jdash = 0
		except Exception as e:
			print("Error: {0}".format(str(e)))
			print("Using J' = 0")

		try:
			Jdashdash = input_file.splitlines()[input_file_syntax["J''"]].split("=")[1].replace(" ", "")
		except IndexError:
			print("Warning: J'' (second nearest neighbour coupling) not specified for square lattice. Defaulting to 0")
			Jdashdash = 0
		except Exception as e:
			print("Error: {0}".format(str(e)))
			print("Using J'' = 0")

		return [J0, J1, Jdash, Jdashdash, 0]

def add_interall_to_namelist(S):

	os.system("""echo "InterAll InterAll.def" >> ./PrepareData/namelist.def""")
	if S != 1:
		os.chdir("./PrepareData")
		use_only_interall = "sed -e 's/Exchange.*//' namelist.def | sed -e 's/CoulombInter.*//' | sed -e 's/Hund.*//' | awk 'NF' > temp.def"
		os.system(use_only_interall)
		os.system("mv temp.def namelist.def")
		os.system("../HPhi -e namelist.def > exp_job.out")
		os.chdir("..")

def output_hamiltonian(length, width, lattice_num):

	try:
		os.system("gcc -o ./modules/print_hamiltonian ./modules/print_hamiltonian.c")
	except IOError:
		print("Warning: could not compile 'print_hamiltonian.c'. Hamiltonian matrix will not be printed. Try to compile the c program manually. ")
	except Exception as e:
		print("Error: {0}".format(str(e)))

	os.system("cp -R PrepareData full_diag_PrepareData")

	os.chdir("./full_diag_PrepareData")

	with open("./Standard.in", "a+") as f:
		f.write("""HamIO="Out" """)

	os.system("sed -e 's/method = \"Lanczos\"/method = \"Full Diag\"/' Standard.in > temp.def")
	os.system("mv temp.def Standard.in")

	os.system("../HPhi -s Standard.in > ../PrepareData/output_ham_std_job.out")
	os.system("../modules/print_hamiltonian")
	os.system("cp ./output/zvo_Ham.dat ../Hamiltonian.dat")
	os.chdir("..")
	os.system("rm -Rf full_diag_PrepareData")

	current_time = datetime.datetime.now()
	lattice = '?'
	for key in supported_lattice_dict.keys():
		if supported_lattice_dict[key] == lattice_num:
			lattice = key

	with open ("./output_ham.dat", "a+") as f:
		f.write("\nHamiltonian for run on {0}, for the L={1}, W={2} {3}\n".format(current_time, length, width, lattice))

def check_order():
	return True
	#Here the aim is to write a function that checks that in the input file Standard.in, the parameters
	#are given in the same order specified by the templates. If not, it changes the file accordingly

def addwidth_to_standard(line_for_width, input_file_syntax):
	#The aim is to have a function that adds the line specified by "line" in the correct position
	#in the file Standard.in, as given by the templates

	for key in input_file_syntax.keys():
		if key == 'W':
			linenum = input_file_syntax[key]

	with open("./PrepareData/Standard.in", 'r') as f:
		data = f.readlines()

	oldlines = []
	newlines = []
	for line in data:
		oldlines.append(line)

	for line in oldlines[0:linenum]:
		line = line.replace("\n","").replace("[","").replace("]","")
		newlines.append(line)

	newlines.append(line_for_width)

	for line in oldlines[linenum:]:
		line = line.replace("\n","").replace("[","").replace("]","")
		newlines.append(line)

	with open("./PrepareData/Standard.in", 'w+') as f:
		f.write('\n'.join(newlines))

#Here the parameter called is 1 when the function is called from prepare_dir, and 0 if it's called from runhphi.
#The reason is I don't want the warning messages to appear twice
def get_dimensions(called):

	lattice, lattice_num, input_file_syntax = get_lattice_syntax()

	if lattice.lower() == "chain":

		with open("./PrepareData/Standard.in", "r") as f:
			input_file = f.read()

		try:
			site_number = input_file.splitlines()[input_file_syntax["L"]].split("=")[1].replace(" ", "")
			return int(site_number), 1, lattice_num
		except:
			print("Could not find the length of the chain in the input file. Please add the relevant line to Standard.in")
			exit()

	elif lattice.lower() == "ladder" or lattice.lower() == "square":

		with open("./PrepareData/Standard.in", "r") as f:
			input_file = f.read()

		data = input_file.splitlines()
		length = data[input_file_syntax["L"]].split("=")[1].replace(" ", "")

		if data[input_file_syntax["W"]].split("=")[0].replace(" ", "") != 'W':

			if lattice.lower() == "ladder":
				if called:
					print("Warning: you forgot to specify the width W in the input file. Defaulting to 2")
					addwidth_to_standard("W = 2", input_file_syntax)
				width = 2

			elif lattice.lower() == "square":
				if called:
					print("Warning: you forgot to specify the width W in the input file. Defaulting to {0}".format(length))
					addwidth_to_standard("W = {0}".format(length), input_file_syntax)
				width = length
		else:
			width = input_file.splitlines()[input_file_syntax["W"]].split("=")[1].replace(" ", "")

		return int(length), int(width), lattice_num
		# except:
		# 	print("Could not find the length/width of the system in the input file. Please add the relevant line to Standard.in")
		# 	exit()

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
		return False, 0

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

def read_kpath(length, width, lattice_num):
	#A function to read the kpath document, which tells the program on which k-path to compute the dispersion relation for the square lattice.
	#The syntax of the file is the following: the first line is a header, and from the second line onwards there is a pair of integer values separated by a comma, which represent a point in real space. These values are the coordinates of a given site,
	#where the site indexes start from (0,0). Each new line represents a new point. The "k-path" can be as long as the user wants (in other words the file can have as many lines as one wants) and if the coordinates specified exceed the dimensions of
	#the square lattice, they will be "folded" back to a valid coordinate with the % operator

	x_kpath = []
	y_kpath = []

	if lattice_num == 3:
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

	else:
		for i in range(0, length):
			x_kpath.append(i)
		return x_kpath, [0]*length

def clear_workspace():

	os.system("rm -Rf kx0*")

	os.chdir("./PrepareData")

	os.system("rm -R output calcmod.def coulombinter.def exchange.def geometry.dat greenone.def greentwo.def hund.def lattice.gp locspn.def modpara.def namelist.def pair.def InterAll.def trans.def output_ham_std_job.out 2> /dev/null")

	os.chdir("..")

def exist_folder(kx, ky):

	ls = os.listdir()
	folder = "kx{0}ky{1}".format(kx, ky, '.3f')
	if folder in ls:
		print("Directory kx{0}ky{1} already exists. Skipping calculation for kx={0}, ky={1}\n".format(kx, ky))
		return True
	else:
		return False

def run_Hphi(length, width, kx, ky):

	lattice, lattice_num, input_file_syntax = get_lattice_syntax()

	if exist_folder(kx, ky) == False:

		os.system("rsync -a --exclude='./PrepareData/std_job.out' --exclude='./PrepareData/exp_job.out' --exclude='./PrepareData/Standard.in' PrepareData/ kx{0}ky{1}".format(kx, ky, '.3f'))
		#TODO: Ma perchè se ho formattato con .3f rsync mi copia ancora le cartelle chiamandole con float a 3000 cifre decimali?? Che problemi ha?
		os.system("./modules/writepair {0} {1} {2} {3} {4} > ./kx{0}ky{1}/pair.def".format(kx, ky, length, width, lattice_num, '.3f'))
		os.chdir("./kx{0}ky{1}".format(kx, ky, '.3f'))
		os.system("../HPhi -e namelist.def > kx{0}ky{1}_job.out".format(kx, ky, '.3f'))
		os.chdir("..")

def generate_plot(kx, ky, df, length):

	os.chdir("./kx{0}ky{1}".format(kx, ky, '.3f'))
	temp_df = pd.read_csv("./output/zvo_DynamicalGreen.dat", header = None, index_col=False, names = dynamicalGreen_file_columns, sep = ' ')

	min_val = temp_df[temp_df['Im(G(z))']==temp_df['Im(G(z))'].min()].iloc[0]

	df = df.append(min_val, sort=False)

	os.chdir("..")
	return df
