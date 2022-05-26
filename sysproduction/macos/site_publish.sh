#!/bin/bash

. ~/.profile
cd $PYSYS_CODE || return
git add site/*
git add site/reports/*
git commit -m "updating site"
git subtree push --prefix site origin gh-pages

