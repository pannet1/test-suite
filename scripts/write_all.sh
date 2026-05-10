#!/bin/sh
cd ~/test-suite/
git add -A && git commit -m "auto-save" && git push

lbu add /root/test-suite
lbu add /root/.gitconfig

lbu commit -d