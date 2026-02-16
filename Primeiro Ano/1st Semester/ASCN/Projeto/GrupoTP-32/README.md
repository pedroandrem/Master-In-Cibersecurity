# TP25-26 / GrupoTP-32 Setup Guide

This README provides the steps required for your colleagues to configure and run the project using the repositories **TP25-26** and **GrupoTP-32**.

---

## 📁 Requirements

You must have both repositories:

* **TP25-26**
* **GrupoTP-32**

Both repos should exist in the same parent directory:

```
parent-folder/
├── TP25-26/
└── GrupoTP-32/
```

---

## 📁 GrupoTP-32 Repository Structure

```
GrupoTP-32/
├── airtrail-deploy.yml
├── airtrail-undeploy.yml
├── checkpoints/
├── credentials/
├── docs/
├── gke-cluster-create.yml
├── gke-cluster-destroy.yml
├── inventory/
├── README.md
├── results/
├── roles/
└── test-all.yml
```

---

## 🚀 Initial Setup

Assuming both repos are in the same folder:

### 1. Enter the **TP25-26** folder

```bash
cd TP25-26
```

### 2. Start the VM environment

```bash
cd checkpoint
vagrant up
```

### 3. Copy the GrupoTP-32 repo into the VM

```bash
scp -r ../../GrupoTP-32 vagrant@192.168.56.50:
```

After this, inside the VM, you will have the full working directory.

---

## 🔐 Credentials Setup

Inside `GrupoTP-32/credentials/`, each team member must place their **cred.json** file.

> ⚠️ These files are ignored by Git, so each user must manually place their own credentials.

---

## 🖥️ Accessing the VM

```bash
ssh vagrant@192.168.56.50
```

---

# 📦 Installing Dependencies Inside the VM

## 1. Install **kubectl**

Download kubectl:

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
```

Install kubectl:

```bash
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

If you do **not** have root privileges:

```bash
chmod +x kubectl
mkdir -p ~/.local/bin
mv ./kubectl ~/.local/bin/kubectl
```

Add to PATH:

```bash
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

Verify installation:

```bash
kubectl version --client
```

---

## 2. Install **Google Cloud SDK (gcloud)**

Official installation guide: [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)

### Update system packages

```bash
sudo apt-get update
```

### Install required packages

```bash
sudo apt-get install apt-transport-https ca-certificates gnupg curl sudo
```

### Import Google public key

```bash
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
```

### Add gcloud CLI repository

```bash
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
```

### Install Google Cloud CLI

```bash
sudo apt-get update && sudo apt-get install google-cloud-cli -y
```

### Install kubectl + GKE authentication plugin

```bash
sudo apt-get install kubectl
sudo apt-get install google-cloud-sdk-gke-gcloud-auth-plugin -y
```

### Initialize gcloud

```bash
gcloud init
```

### Install Python dependencies

```bash
pip install requests google-auth kubernetes
```

---

## ☁️ Creating the GKE Cluster with Ansible

Inside GrupoTP-32:

```bash
ansible-playbook gke-cluster-create.yml -i inventory/gcp.yml
```

### Authenticate Kubernetes access

```bash
gcloud container clusters get-credentials ascn-cluster --project=ascn-grupo-tp-32 --zone=us-central1-a
```

---

## 🧪 Running Checkpoint Tests

From the main VM directory:

```bash
./checkpoint.sh -i GrupoTP-32/ -o GrupoTP-32/results/ -c 2
```

---

## ✅ Finished!

Your environment should now be fully operational.

If anything fails, verify:

* Credentials exist in `GrupoTP-32/credentials/`
* gcloud is authenticated
* kubectl is correctly installed
* The cluster has credentials configured
