#!/bin/bash
for ((i=1; i<=30; i++))
do 
 echo "Load=$1 Alg=$2"
 ./cli_rsrc_alloc_sim.py 5 20 10 $1 -C 0.0067 -w 8 -p 40 -q 0.5 -L $2 -F
done
#`

