#! /usr/bin/env bash

cd ~/harbor-macro/harbor-macro.gitlab.io/
git add public/reports/*.txt
git commit -m "Updating reports"

git push origin

exit 0;