#!/bin/bash

. ~/.profile
cd $PYSYS_CODE
source env/bin/activate

python $SCRIPT_PATH/run.py $1 >> $ECHO_PATH/$2_`date +"%Y-%m-%d_%H%M%S"`.log
