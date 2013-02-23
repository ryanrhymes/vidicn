#!/usr/bin/env bash

DEG=$1
LVL=$2
CHK=2
CPY=10
LOG="tree_d${DEG}_l${LVL}_xcopy_${CHK}chunk.txt"

APP1="/cs/fs/home/lxwang/cone/Papers/lxwang/vidicn/code/generate_request.py"
APP2="/cs/fs/home/lxwang/cone/Papers/lxwang/vidicn/code/tree/treestatic_partial_relax.py"
APP3="/cs/fs/home/lxwang/cone/Papers/lxwang/vidicn/code/tree/calculate_performance.py"

$APP1 $CHK > trace_request.$CHK

for x in `seq 1 $CPY`; do
    $APP2 $CHK $x $DEG $LVL
done

rm -rf $LOG

for x in `seq 1 $CPY`; do
    $APP3 trace_request.$CHK tree_modelstatic_partial_relax.sol.2.$x tree_modelstatic_partial_relax.chunk.2.$x $DEG $LVL | tail -n 1 >> $LOG
done
