# HPhi_dispersionrelations
This is part of my master thesis, conducted at ESRF (Grenoble).

Script to generate dispersion relations using the program HPhi.

Make sure you have HPhi (https://github.com/issp-center-dev/HPhi) installed in the same directory where the script main.sh is located. 
For now the program only works for the chain, ladder and square lattice. You can specify the parameters (number of sites, exchange interaction, magnetic field along z) in ./PrepareData/Standard.in, following the syntax for the standard mode input file given on P.26 of the HPhi manual.

After running the script, you will find one output directory for each k-value, containing the Dynamical Green's Functions. A colormap of the resulting single-magnon dispersion relation will appear on screen. The color represents the intensity, and as usual the value of K is on the x-axis while the energy (in meV) is on the y-axis.

Tested using HPhi version 3.2.0
