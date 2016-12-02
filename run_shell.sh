#!/bin/bash

THISDIR=/home/water/httpautomation

export PYTHONPATH=$PYTHONPATH:$THISDIR:$THISDIR/src

echo "start Python"

python $THISDIR/src/runner/Runner.py $THISDIR/testcases/simple1.xlsx
