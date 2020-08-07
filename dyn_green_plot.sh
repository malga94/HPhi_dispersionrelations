#!/bin/bash

if [ "$1" == "-h" ] ; then
    echo "A script that plots every Dynamical Green Function in the same gnuplot window. Curves are labelled by their value of K"
    exit 0
fi

gnuplot -e "set terminal png size 400,300; set output 'prova.png';"

for dirname in kx*/; do
	var=$var"'$dirname/output/zvo_DynamicalGreen.dat' using 1:4 title 'Dyn_G$dirname', "
done 

gnuplot -e "plot $var; pause -10"
