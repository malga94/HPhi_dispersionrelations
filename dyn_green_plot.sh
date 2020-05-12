#!/bin/bash

gnuplot -e "set terminal png size 400,300; set output 'prova.png';"

for dirname in kx*/; do
	var=$var"'$dirname/output/zvo_DynamicalGreen.dat' using 1:4 title 'Dyn_G$dirname', "
done 

gnuplot -e "plot $var; pause -10"
