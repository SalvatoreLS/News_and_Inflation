#!/bin/bash

# IF PYTHON3 IS INSTALLED

pip_version='pip'

if [ /usr/bin/python3 ]; then
  echo "Python3 is installed"
  pip_version="pip3"
fi

$pip_version install $(cat requirements.txt | tr '\n' ' ')

playwright install

exit 0
