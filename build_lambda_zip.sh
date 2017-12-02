#!/usr/bin/env bash

# Build anniversary.py into a zip file to deploy to AWS Lambda
thisdir="$(cd $(dirname "$0"); pwd)"
mkdir $thisdir/build
mkdir $thisdir/dist
cp -p $thisdir/anniversary.py $thisdir/build/
cd $thisdir/build
zip $thisdir/dist/anniversary.zip *
