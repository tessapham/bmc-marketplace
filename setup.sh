#!/bin/bash
# Author: Xinyi Wang
# Description: shell script for database setup
# Instruction to use:
# to set permission: chmod 755 setup
# to run: ./setup.sh

python -m flask db init
flask db migrate -m "users table"
flask db upgrade
flask db migrate -m "posts table"
flask db upgrade
flask db migrate -m "interested table"
flask db upgrade
