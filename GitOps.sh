#!/bin/bash

IMAGE_TAG=$1
# This shell script for update remote git repo
git add Kubernetes/Flask-Deloyment.yaml
git commit -m "Update HiveBox's imageTag: ${IMAGE_TAG}"
git push origin main

# Sync HiveBox app with ArgoCD
argocd app sync hivebox