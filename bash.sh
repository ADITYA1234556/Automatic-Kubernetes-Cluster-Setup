#!/bin/bash

#Prepare System Settings to run Kubernetes

#Load Kernel Modules for Kubernetes Networking creates (or overwrites) a file at /etc/modules-load.d/k8s.conf with two kernel module names: overlay and br_netfilter.
#This file instructs the system to automatically load these modules at boot time. The modules are essential for Kubernetes networking:
#overlay: Required for the overlay network driver, which helps containerized applications on different hosts communicate.
#br_netfilter: Enables packet filtering on bridges, which is crucial for Kubernetes network traffic management between pods.
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

#Load the Kernel Modules Immediately without requiring a system reboot, making them active for the current session.
sudo modprobe overlay
sudo modprobe br_netfilter

#Configure Network Settings for Kubernetes Enabling the following options
#Ensures that IPV4 packets traversing the bridge go through iptables for filtering, which is required for Kubernetes network policies.
#Similar to the previous setting but applies to IPv6 traffic.
#Enables IP forwarding, which is crucial for routing traffic between pods across different nodes in the Kubernetes cluster.
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

#Apply the New Network Configuration
sudo sysctl --system

#List the kernel modules by lsmod to Verify that the Modules are Loaded
lsmod | grep br_netfilter
lsmod | grep overlay

#Verify system settings checks the values of the specific network settings we configured in k8s.conf
#If everything is configured as intended, you should see output confirming that each setting is set to 1
sysctl net.bridge.bridge-nf-call-iptables net.bridge.bridge-nf-call-ip6tables net.ipv4.ip_forward

#Installing CRI-O is better suited for k8s as docker container runtime will also need docker shim to perform as CRI-O also CRI-O has less dependencies

sudo apt-get update -y
sudo apt-get install -y software-properties-common curl apt-transport-https ca-certificates
sudo mkdir -p -m 755 /etc/apt/keyrings
sudo curl -fsSL https://pkgs.k8s.io/addons:/cri-o:/prerelease:/main/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/cri-o-apt-keyring.gpg
sudo echo "deb [signed-by=/etc/apt/keyrings/cri-o-apt-keyring.gpg] https://pkgs.k8s.io/addons:/cri-o:/prerelease:/main/deb/ /" | tee /etc/apt/sources.list.d/cri-o.list

sudo apt-get update -y
sudo apt-get install -y cri-o

sudo systemctl daemon-reload
sudo systemctl enable crio --now
sudo systemctl start crio.service


#Installing Kubeadm, Kubelet & Kubectl#
KUBEVERSION=v1.30
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gpg
sudo mkdir -p -m 755 /etc/apt/keyrings
sudo curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
sudo systemctl enable --now kubelet


#LOGIN TO THE EC2 RUN THESE COMMANDS
#sudo kubeadm init --pod-network-cidr=10.244.0.0/16 #YOU WILL GET A TOKEN RUN THE TOKEN ON WORKER EC2S
#ON THE WORKER NODES ASWELL RUN THIS SCRIPT TO INSTALL
# 1. CRI-O CONTAINER RUNTIME 2. KUBELET, KUBEADM, AND KUBECTL
