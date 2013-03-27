#!/usr/bin/env bash

CSZ=$1
CHK=$2
CPY=10
LOG="tree_xcopy_${CHK}chunk_csz${CSZ}_topx.txt"

APP1="/cs/fs/home/lxwang/cone/Papers/lxwang/vidicn/code/generate_request.py"
APP2="/cs/fs/home/lxwang/cone/Papers/lxwang/vidicn/code/tree/treestatic_partial_relax.py"
APP3="/cs/fs/home/lxwang/cone/Papers/lxwang/vidicn/code/tree/script/calculate_dde_topx.py"

for x in `seq 1 $CPY`; do
    $APP3 trace_request.$CHK tree_modelstatic_partial_relax.sol.$CHK.$x tree_modelstatic_partial_relax.chunk.$CHK.$x | tail -n 1 >> $LOG
done

for x in `seq 1 $CPY`; do echo $x; done > z1
paste -d ' ' z1 $LOG > z2
mv z2 $LOG
rm z1