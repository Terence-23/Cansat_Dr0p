#!/bin/sh

python3 src/testGen.py
python3 src/wind.py data/test.data -l debug -o out/test.out