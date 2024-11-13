# **Automatic Kubernetes Cluster Setup**

Welcome to the **Automatic Kubernetes Cluster Setup** project! This tool automates the setup of a Kubernetes cluster with minimal intervention, allowing you to quickly and effortlessly get your environment up and running. Whether you're a DevOps engineer, a developer, or just learning Kubernetes, this script simplifies cluster initialization and configuration.

---

## **Table of Contents**
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [How It Works](#how-it-works)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

---

## **Overview**
This project automates the process of setting up a Kubernetes cluster on your machines, including:
- Master and worker node setup
- Token generation for joining worker nodes to the master
- Kubernetes components installation (kubeadm, kubelet, kubectl)
- Configuration of pod network

With this automation, setting up a Kubernetes cluster is no longer a complex task. You can get started with your Kubernetes environment in just a few simple steps!

---

## **Features**
- **Automated Setup**: Full Kubernetes cluster initialization with a single script.
- **Cross-Platform**: Works on various Linux distributions (Ubuntu, Amazon Linux, etc.).
- **Scalable**: Easily add worker nodes to scale your cluster.
- **Customizable**: Customize pod network CIDR, Kubernetes versions, and more.
- **Secure**: Implements best practices for token management and certificate handling.

---

## **Installation**
To get started with the **Automatic Kubernetes Cluster Setup**, follow the steps below:

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/k8s-cluster-setup.git
    cd k8s-cluster-setup
    ```

2. Ensure you have the necessary dependencies installed:
    - SSH Client
    - Python 3.x
    - Kubernetes (kubeadm, kubelet, kubectl)

---

## **How It Works**
The script uses the following steps to initialize the Kubernetes cluster:

1. **Master Node Initialization**: The script configures the master node with `kubeadm init`.
2. **Join Command Generation**: After initializing the master node, the script fetches the join command to connect worker nodes.
3. **Network Setup**: The script configures the pod network using the Weave CNI (or your preferred CNI).
4. **Join Worker Nodes**: Worker nodes are automatically joined to the cluster using the generated join command.

---

## **Usage**
To initialize your Kubernetes cluster:

1. **Run the aws.py python file**:
    ```bash
    python3 aws.py
    ```
Once completed, you'll have a fully functional Kubernetes cluster ready to go!

---

## **Contributing**
We welcome contributions to make this project even better! If you have any ideas, bug fixes, or new features, feel free to submit a pull request.

**How to contribute:**
- Fork the repository.
- Clone your fork to your local machine.
- Create a feature branch.
- Make your changes and commit them.
- Push your changes and create a pull request.

---

## **License**
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

### **Let's Get Kubernetes Up and Running!**

Happy Kubernetes setup! 🚀
