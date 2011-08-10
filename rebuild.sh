#!/bin/sh

mkdir -p html
rm -rf ./html/*
./scrape.py --output-dir html

echo 'Rebuilt nightly site.'
