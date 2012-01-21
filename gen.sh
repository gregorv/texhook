#!/bin/bash

cd /var/www/praktikum/repo
git reset --hard > /dev/null
git pull --rebase > /dev/null
cd ..
./gen.py $(ls repo/*/*/*.tex)
