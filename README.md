# HiveBox - DevOps End-to-End Hands-On Project

<p align="center">
  <a href="https://devopsroadmap.io/projects/hivebox" style="display: block; padding: .5em 0; text-align: center;">
    <img alt="HiveBox - DevOps End-to-End Hands-On Project" border="0" width="90%" src="https://devopsroadmap.io/img/projects/hivebox-devops-end-to-end-project.png" />
  </a>
</p>

## Acknowledgment

Special thanks to **Eng. [Ahmed AbouZaid](https://github.com/aabouzaid)** for proposing the HiveBox project idea. Their vision and thoughtful design helped shape a meaningful and practical learning experience, combining real-world DevOps concepts with hands-on application. This project wouldn't have been the same without their valuable input.


The project aims to cover the whole Software Development Life Cycle (SDLC). That means each phase will cover all aspects of DevOps, such as planning, coding, containers, testing, continuous integration, continuous delivery, infrastructure, etc.


<br/>
<p align="center">
  <a href="https://devopsroadmap.io/projects/hivebox/" imageanchor="1">
    <img src="https://img.shields.io/badge/Get_Started_Now-559e11?style=for-the-badge&logo=Vercel&logoColor=white" />
  </a><br/>
</p>

---

## Introduction

DevOps end-to-end hands-on project, we will utilize the technology and open-source software to build an API to track the environmental sensor data from openSenseMap, a platform for open sensor data in which everyone can participate.

<p align="center">
  <a href="https://devopsroadmap.io/projects/hivebox/" imageanchor="1">
    <img src="https://devopsroadmap.io/assets/images/hivebox-architecture-a7fe504c22027e87b6f7b188cd57d2d8.png" />
  </a><br/>
</p>

### Note!
I used Jenkins as a Continuous Integration & Continuous Deplymment tool for (CI/CD Pipelines), instead of Github Actions!

---

## Implementation

### Phase 1:  Welcome to the DevOps World
<p align="center">
  <a href="https://devopsroadmap.io/projects/hivebox/" imageanchor="1">
    <img src="https://devopsroadmap.io/assets/images/module-01-overview-e3d852c2bde8272515f2c444221cdbfd.png" />
  </a><br/>
</p>

- [Create GitHub account](https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github) (if you don't have one), then [fork this repository](https://github.com/DevOpsHiveHQ/devops-hands-on-project-hivebox/fork) and start from there.
- [Create GitHub project board](https://docs.github.com/en/issues/planning-and-tracking-with-projects/creating-projects/creating-a-project) for this repository (use `Kanban` template).
- Each phase should be presented as a pull request against the `main` branch. Don’t push directly to the main branch!
- Document as you go. Always assume that someone else will read your project at any phase.
- You can get senseBox IDs by checking the [openSenseMap](https://opensensemap.org/) website. Use 3 senseBox IDs close to each other (you can use the following [5eba5fbad46fb8001b799786](https://opensensemap.org/explore/5eba5fbad46fb8001b799786), [5c21ff8f919bf8001adf2488](https://opensensemap.org/explore/5c21ff8f919bf8001adf2488), and [5ade1acf223bd80019a1011c](https://opensensemap.org/explore/5ade1acf223bd80019a1011c)). Just copy the IDs, you will need them in the next steps.

---

### Phase 2: Basics - DevOps Core

<p align="center">
  <a href="https://devopsroadmap.io/projects/hivebox/" imageanchor="1">
    <img src="https://devopsroadmap.io/assets/images/module-02-overview-22e040ce248a0b72495dbc2cea9f6986.png" />
  </a><br/>
</p>

### 2.1 Tools
- Git
- VS code
- Docker
### 2.2 Steps

- Build a Docker image, run and test it locally.
```sh
docker build -t hivebox-image .
docker run --name hivebox hivebox-image
```
- The output should be: 
```sh
HiveBox App Version: v0.0.1
```
---

### Phase 3: Start - Laying the Base

<p align="center">
  <a href="https://devopsroadmap.io/projects/hivebox/" imageanchor="1">
    <img src="https://devopsroadmap.io/assets/images/module-03-overview-3269b01a0471696a3a1e5a86b4c03a4f.png" />
  </a><br/>
</p>

### 3.1 Tools
- Hadolint and VS Code hadolint extension
- Pylint and VS Code Pylint extension
### 3.2 Code
- Use Conventional Commits for Git commits.
- Familiarize yourself with openSenseMap API.
- Implement the code requirements (Flask) .
- Write unit tests for all endpoints.
### 3.3 Containers
- Apply Best Practices for containers (Resize the Docker image).
```sh
docker rm hivebox   # Remove old container to create the new one
hadolint Dockerfile   # Scan your Dockerfile
docker build -t hivebox-image .
docker run -d --name hivebox -p 5000:5000 hivebox-image
```
### 3.4 Continuous Integration (CI Pipeline)
- Setup Jenkins server and configure it with the env.
- Install all Flask app's packages
- Linting code and Dockerfile.
- Add step to unit tests.
- Building the Docker image.
### 3.5 Testing
- In the CI pipeline, call the /version endpoint and ensure it returns the correct value.
- Access the flask app inside the container from your browser.
```sh
http://localhost:5000/version
http://localhost:5000/temperature
```
---

### Phase 4: Expand - Constructing a Shell

<p align="center">
  <a href="https://devopsroadmap.io/projects/hivebox/" imageanchor="1">
    <img src="https://devopsroadmap.io/assets/images/module-04-overview-b8303bb10b6f537c8c8a00d5aa73f1cc.png" />
  </a><br/>
</p>

### 4.1 Tools
- Kind Cluster
- Kubectl

### 4.2 Code
- The senseBox should be configurable via env vars.
#### Metrics:
- Endpoint: /metrics
- Returns default Prometheus metrics about the app.
- Endpoint: /temperature

### 4.3 Kubernetes Deployment
- KIND Cluster configuration to run with Nginx ingress controller.
- Kubernetes core manifests to deploy the application.

### 4.4 Continuous Integration (CI Pipeline)
- Run code integration tests.
- Run SonarQube for code quality, security, and static analysis (Using SonarCloud).
- Apply Best Practices for CI.

### 4.5 Testing
- Try to acces you flask app inisde kubernetes using NodePort "if ypu don't use ingress"
```sh
kubectl describe node kind-control-plane | grep -i ip   # Output like -> InternalIP:  172.19.0.2 
http://172.19.0.2:<YourNodePort>
```
- Using Nginx ingress controller
```sh
sudo vim /etc/hosts
# Add Your Domain with localhost IP address
127.0.0.1 www.hivebox.com     # Save and Exit -> :wq
#Access your ingress now
http://www.hivebox.com
```
### Tip!
If you want to secure your app with HTTPS protocol, just generate SSL Key and assign with kubernetes secrets in ingress.yml file.

- I will use it later, now just test my flask app! 

---
