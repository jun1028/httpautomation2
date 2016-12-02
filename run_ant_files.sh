#!/bin/bash

THISDIR=/home/water/httpautomation

export PYTHONPATH=$PYTHONPATH:$THISDIR:$THISDIR/src

echo "start Python"

ant  -f $THISDIR/antxml/build-py.xml -Dtestcase.filename=testcases -Dtestrunner.filename=FilesRunner.py

