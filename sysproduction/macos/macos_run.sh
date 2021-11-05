#!/bin/bash

# shellcheck source=/dev/null
. ~/.profile
cd $PYSYS_CODE || return
source env/bin/activate

IN=$1
array=(${IN//./ })
size=${#array[@]}
last_index=$((size-1))
log_file=${array[last_index]//_/$'-'}
#echo "${log_file}"

#python $SCRIPT_PATH/run.py $1 >> $ECHO_PATH/$2_`date +"%Y-%m-%d_%H%M%S"`.log
python $SCRIPT_PATH/run.py $1 >> $ECHO_PATH/$log_file.log
