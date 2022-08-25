#!/bin/zsh

. ~/.zprofile
cd $PYSYS_CODE || return
for f in site/reports/*_report; do mv "$f" "$f.txt"; done
git add site/*
git add site/reports/*
git commit -m "updating site"
git subtree push --prefix site origin gh-pages

