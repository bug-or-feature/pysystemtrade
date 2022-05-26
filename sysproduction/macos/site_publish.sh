#!/bin/bash

. ~/.profile
cd $PYSYS_CODE || return
git add site/*
git commit "updating site"
git subtree push --prefix site origin gh-pages

