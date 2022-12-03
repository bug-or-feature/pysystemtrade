#! /usr/bin/env bash

cd ~/harbor-macro/harbor-macro.gitlab.io/
git pull
git -v add public
git commit -m "Updating site"

git push origin

exit 0;
