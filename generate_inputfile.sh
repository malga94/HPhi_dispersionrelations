#!/bin/bash

echo "model = \"SpinGC\"" > ./PrepareData/Standard.in
echo "method = \"Lanczos\"" >> ./PrepareData/Standard.in
echo "lattice = \"chain\"" >> ./PrepareData/Standard.in
echo "L = 12" >> ./PrepareData/Standard.in
echo "J = -1" >> ./PrepareData/Standard.in
echo "h = 0" >> ./PrepareData/Standard.in
echo "EigenvecIO=\"Out\"" >> ./PrepareData/Standard.in
  
