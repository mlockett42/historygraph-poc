Readme
======

This file is a place holder for the livewire python (3rd attempt)

Installation
------------

Under Ubuntu

Checkout the historygraph libary
git clone https://github.com/mlockett42/historygraph.git

Checkout the historygraph-poc library
git clone https://github.com/mlockett42/historygraph-poc.git

Link the historygraph library into the correct place
cd ~/historygraph-poc
ln -s ../historygraph/historygraph historygraph


sudo apt-get install libssl-dev libffi-dev

Use these insstructions to get python qt4 / pyside to work in virtual env

Create the virtual environment

virtualenv .
source bin/activate
pip install pip --upgrade
pip install urllib3[secure]
pip install -r requirements.txt


pyside will take a long time to install.

Running Tests
-------------

To run the unittests (TDD) run ./unittests

To run the BDD functional tests 
from the livewirepy directory
source bin/activate
export PYTHONPATH=$PWD
cd tests
lettuce


