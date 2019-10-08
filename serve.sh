#!/usr/bin/env bash

MY_DIR="$( cd "$(dirname "$0")" ; pwd -P )"

LISTEN_HOST=0.0.0.0
LISTEN_PORT=5000
PYTHON=${MY_DIR}/venv/bin/python
LD_LIBRARY_PATH=${MY_DIR}/ir/pigpio
GPIO_PIN=25

export LISTEN_HOST; export LISTEN_PORT; export LD_LIBRARY_PATH; export GPIO_PIN;

cd ${MY_DIR}
${PYTHON} -m ir.serve
