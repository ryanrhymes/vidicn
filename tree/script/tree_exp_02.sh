#!/usr/bin/env bash

CHK=20
CPY=$1
LOG="tree_${CPY}copy_xchunk.txt"

APP1="/cs/fs/home/lxwang/cone/Papers/lxwang/vidicn/code/generate_request.py"
APP2="/cs/fs/home/lxwang/cone/Papers/lxwang/vidicn/code/tree/treestatic_partial_relax.py"
APP3="/cs/fs/home/lxwang/cone/Papers/lxwang/vidicn/code/tree/calculate_performance.py"

for x in `seq 2 2 $CHK`; do
    $APP1 $x > trace_request.$x
done

for x in `seq 2 2 $CHK`; do
    $APP2 $x $CPY
done

rm -rf $LOG

for x in `seq 2 2 $CHK`; do
    $APP3 trace_request.$x tree_modelstatic_partial_relax.sol.${x}.${CPY} tree_modelstatic_partial_relax.chunk.${x}.${CPY} | tail -n 1 >> $LOG
done

for x in `seq 2 2 $CHK`; do echo $x; done > z1
paste -d ' ' z1 $LOG > z2
mv z2 $LOG
rm z1