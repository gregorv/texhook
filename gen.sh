#!/bin/bash

cd /var/www/praktikum/repo
git pull --rebase > /dev/null
cd ..
./gen.py $(ls repo/*/*/*.tex)
