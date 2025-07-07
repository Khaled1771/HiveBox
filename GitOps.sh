#!/bin/bash

IMAGE_TAG=$1
# This shell script for update remote git repo
git config user.name "Khaled1771"
git config user.email "khhaledd.77@gmail.com"
git checkout main
git pull origin main
git add -A
git commit -m "Update HiveBox's imageTag: ${IMAGE_TAG}"
git push origin main

# Sync HiveBox app with ArgoCD
argocd app sync hivebox