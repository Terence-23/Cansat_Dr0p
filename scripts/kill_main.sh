#!/bin/sh
ps -aux |grep -v grep | grep new_main.py| awk '{print sudo kill }'|sh
