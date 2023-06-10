#!/bin/python

import glob
import os
import traceback

files = glob.glob('**/*.*', root_dir=os.getcwd(), recursive = True)
# print(files)

python = []
rust = []
cpp = []
data = []
config = []
unclasified = []

for i in files:
    match i.split('.')[-1]:
        case 'py':
            python.append(i)
        case 'cpp':
            cpp.append(i)
        case 'h':
            cpp.append(i)
        case 'out':
            data.append(i)
        case 'rs':
            rust.append(i)
        case 'toml':
            config.append(i)
        case 'json':
            config.append(i)
        case _:
            unclasified.append(i)
    
# print(python)

py_lines = 0
for i in python:
    py_lines += len(open(i).readlines())

cpp_lines = 0
for i in cpp:
    cpp_lines += len(open(i).readlines())
    
data_lines = 0
for i in data:
    print(i)
    try: data_lines += len(open(i).readlines())
    except Exception as e: pass#traceback.print_exc()
    
rust_lines = 0
for i in rust:
    rust_lines += len(open(i).readlines())
    
conf_lines = 0
for i in config:
    conf_lines += len(open(i).readlines())
    
unc_lines = 0
for i in unclasified:
    try: unc_lines += len(open(i).readlines())
    except Exception as e: pass#traceback.print_exc()
    
print(f"Results:\n\
    python: {py_lines}\n\
    cpp: {cpp_lines}\n\
    rust: {rust_lines}\n\
    conf: {conf_lines}\n\
    data: {data_lines}\n\
    unclasified: {unc_lines}\n")