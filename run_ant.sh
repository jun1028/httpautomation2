#!/bin/bash

THISDIR=/home/water/httpautomation

export PYTHONPATH=$PYTHONPATH:$THISDIR:$THISDIR/src

echo "start Python"

ant  -f $THISDIR/antxml/build-py.xml -Dtestcase.filename=testcases/sample1.xlsx -Dtestrunner.filename=Runner.py

