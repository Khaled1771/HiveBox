#!/bin/bash
echo "######### Configuring Git Repo #########"
set +x  # Hide sensitive output
IMAGE_TAG=$1
# GIT_USERNAME=${GIT_USER}
# GIT_PASSWORD=${GIT_PASS}
REPO_URL="https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/Khaled1771/HiveBox.git"
# Configure Git
cd /mnt/MyData/Courses/Projects/HiveBox
git config --global --add safe.directory /mnt/MyData/Courses/Projects/HiveBox
git config user.name "Khaled1771"
git config user.email "khhaledd.77@gmail.com"
git remote set-url origin $REPO_URL
set -x  # Show logs in pipeline
echo "######### Git Operations #########"
# This shell script for update remote git repo
git checkout main
git add -A
git commit -m "Update HiveBox's imageTag: ${IMAGE_TAG}" || echo "Nothing to commit"
git pull --rebase origin main       # Deny any conflicts through pulling
git push origin main

# Sync HiveBox app with ArgoCD
# argocd app sync hivebox