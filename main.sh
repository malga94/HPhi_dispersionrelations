#!/bin/bash

if [ "$1" == "-h" ] ; then
    echo "A very simple bash script to avoid having to run the two python programs separately each time. Running this without options will save the magnon dispersion relation for your system in a file, and plot it"
    exit 0
fi

python3 prepare_dir.py 0
python3 runhphi.py 1
