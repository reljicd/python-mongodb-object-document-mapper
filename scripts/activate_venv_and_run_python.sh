#!/usr/bin/env bash

if [ -z "$1" ]
  then
    echo "No input parameters supplied"
    exit 1
fi

if [ ! -d "venv" ]
then
    python3 -m virtualenv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
else
    source venv/bin/activate
fi

PYTHONPATH=$PYTHONPATH:$(pwd)
export PYTHONPATH

python "$@"
