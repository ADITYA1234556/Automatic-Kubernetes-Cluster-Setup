import boto3
import paramiko
import time

# Define your AWS and instance configuration
AWS_REGION = 'eu-west-3'  # Change to your desired region
INSTANCE_TYPE = 't3.medium'  # Choose instance type
KEY_NAME = 'OWNKEYADI2'  # Ensure your key is in AWS and accessible
SECURITY_GROUP_IDS = 'sg-027d5850ec69e6c09'  # Replace with your security group
SUBNET_ID = 'subnet-00de9af047920c590'  # Replace with your subnet
AMI_ID = 'ami-07db896e164bc4476'  # Replace with your desired AMI (e.g., Amazon Linux 2)
BASH_SCRIPT_PATH = 'script.sh'  # Replace with your script path

# Boto3 EC2 client
ec2 = boto3.client('ec2', region_name=AWS_REGION)


key_path = 'E:/ITC/new_key.pem'

try:
    private_key = paramiko.RSAKey.from_private_key_file(key_path)
    print("Key loaded successfully")
except Exception as e:
    print(f"Failed to load key: {e}")

#CREATE AN EC2 AND GET ITS INSTANCE ID
def create_ec2(count):
    #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/run_instances.html
    instances = ec2.run_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        MaxCount=count,
        MinCount=count,
        Monitoring={
            'Enabled': True
        },
        SecurityGroupIds=[SECURITY_GROUP_IDS],
        SubnetId=SUBNET_ID,
        KeyName=KEY_NAME,
        TagSpecifications=[
            {
                'ResourceType': 'instance',  # Specifies that we're tagging EC2 instances
                'Tags': [
                    {'Key': 'Name', 'Value': 'MyK8sClusterInstance'},
                    {'Key': 'Environment', 'Value': 'Development'},
                ]
            }
        ]
    )
    instances_ids = [instance['InstanceId'] for instance in instances['Instances']]
    print(f"Created instances: {instances_ids}")
    print(instances_ids)
    return instances_ids

#wait for the previous function to create EC2 and pass the instance ID to get the instances public IP
def wait_for_instance_create(instance_ids):
    #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/instance/wait_until_running.html
    ec2_resource = boto3.resource('ec2', region_name=AWS_REGION)
    print(f"Received instance IDs: {instance_ids}")
    instances = []
    for instance_identity in instance_ids:
        if instance_identity.startswith("i-"):
            instance = ec2_resource.Instance(instance_identity)
            print(f"Waiting for instance {instance_identity} to start")
            instance.wait_until_running()
            instance.reload()
            print(f"Instance {instance_identity} is running with public IP {instance.public_ip_address}")
            instances.append(instance)
        else:
            print(f"Invalid instance ID format: {instance_identity}")
    print(instances)
    return instances

#INSTALL KUBERNETES ON A NODE USING SSH AND A PROVIDED SCRIPT
def setup_kubenernetes(instance, script_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private_key = paramiko.RSAKey.from_private_key_file('E:/ITC/new_key.pem')

    try:
        # Retry connecting until the instance is ready
        while True:
            try:
                ssh.connect(instance.public_ip_address, username='ubuntu', pkey=private_key)
                print(f"Connected to instance {instance.id}")
                break
            except paramiko.ssh_exception.NoValidConnectionsError:
                print(f"Retrying connection to {instance.public_ip_address}...")
                time.sleep(10)

        with open(script_path, "r") as file:
            commands = file.readlines()
        for line in commands:
            if line.strip() == "" or line.strip().startswith("#"):
                continue

            print(f"Executing command on {instance.id}: {line.strip()}")
            stdin, stdout, stderr = ssh.exec_command(line.strip())
            stdout_output = stdout.read().decode()
            stderr_output = stderr.read().decode()
            if stderr_output:
                print(f"Error executing command on instance {instance.id}: {stderr_output}")
            else:
                print(f"Output from instance {instance.id}: {stdout_output}")

        print(f"Completed setup on {instance.id}")
    finally:
        ssh.close()

# FUNCTION TO EXECUTE AFTER K8S INSTALLATION ON MASTER NODE
def setup_master_after_install(ssh, is_root=False):
    """Setup the kubernetes user and kubeconfig."""
    if is_root:
        ssh.exec_command("export KUBECONFIG=/etc/kubernetes/admin.conf")
    else:
        # Setup for non-root user
        ssh.exec_command("mkdir -p $HOME/.kube")
        ssh.exec_command("sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config")
        ssh.exec_command("sudo chown $(id -u):$(id -g) $HOME/.kube/config")
    print("Kubernetes user configuration completed.")

#APPLY POD NETWORK WITH WEAVE
def apply_pod_network(ssh, pod_network_cidr="10.244.0.0/16"):
    """Apply the pod network configuration to the cluster."""
    # Example: Apply Flannel CNI (you can replace with other network options like Calico)
    flannel_yaml = "https://reweave.azurewebsites.net/k8s/v1.29/net.yaml"
    ssh.exec_command(f"kubectl apply -f {flannel_yaml}")
    print(f"Pod network with CIDR {pod_network_cidr} applied.")

#FUNCTION TO EXECUTE AFTER K8S INSTALLATION ON WORKER NODE
def setup_kubernetes_worker(ssh, join_command):
    """Run the join command on worker nodes to join the Kubernetes cluster."""
    print(join_command)
    stdin, stdout, stderr = ssh.exec_command(join_command)
    output = stdout.read().decode()
    print(output)
    if "kubelet is already running" in output:
        print("Worker node already joined.")
    else:
        print("Worker node joined successfully.")

def initialize_cluster(master_instance, worker_instances):
    """Initialize the Kubernetes cluster and join worker nodes."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private_key = paramiko.RSAKey.from_private_key_file('E:/ITC/new_key.pem')

    try:
        # Connect to the master node and initialize the cluster
        ssh.connect(master_instance.public_ip_address, username='ubuntu', pkey=private_key)
        print("Initializing Kubernetes cluster on master node...")
        # Run kubeadm init to initialize the cluster
        stdin, stdout, stderr = ssh.exec_command("sudo kubeadm init --pod-network-cidr=10.244.0.0/16")
        output_init = stdout.read().decode().strip()
        error_init = stderr.read().decode().strip()

        if error_init:
            print(f"Error during kubeadm init: {error_init}")
        print(f"kubeadm init output: {output_init}")

        # Now create the token and get the join command
        stdin, stdout, stderr = ssh.exec_command("sudo kubeadm token create --print-join-command")
        output_command = stdout.read().decode().strip()
        error_command = stderr.read().decode().strip()

        if error_command:
            print(f"Error during token creation: {error_command}")
            return

        if output_command:
            join_command = "sudo " + output_command
            print(f"Join command: {join_command}")
            # Configure the Kubernetes user on the master node
            setup_master_after_install(ssh)

            # Apply the pod network to the cluster
            apply_pod_network(ssh)
            print("Joining worker nodes to the cluster...")
            for worker in worker_instances:
                worker_ssh = paramiko.SSHClient()
                worker_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                worker_ssh.connect(worker.public_ip_address, username='ubuntu', pkey=private_key)
                # Passing the join command as part of the setup script for worker nodes
                setup_kubernetes_worker(worker_ssh, join_command=join_command)
                worker_ssh.close()
        else:
            print("Error: Could not retrieve join command from master initialization output.")
    finally:
        ssh.close()

# Main execution
if __name__ == "__main__":
    # Create master node
    master_instance_ids = create_ec2(count=1) #returns a list of instance ids take only the fist value to pass as string
    master_instances = wait_for_instance_create(master_instance_ids)
    master_instance = master_instances[0]
    setup_kubenernetes(master_instance, BASH_SCRIPT_PATH)

    # Create worker nodes
    worker_instance_ids = create_ec2(count=2)  # Change count as needed
    worker_instances = wait_for_instance_create(worker_instance_ids)
    for worker in worker_instances:
        setup_kubenernetes(worker, BASH_SCRIPT_PATH)

    # Initialize Kubernetes cluster and join workers
    initialize_cluster(master_instance, worker_instances)