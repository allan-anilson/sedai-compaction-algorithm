from kubernetes import client, config
import subprocess

# Load kube config
config.load_kube_config()

v1 = client.CoreV1Api()

# Define resource thresholds
CPU_OVER_THRESHOLD = 5  # Percentage
MEMORY_OVER_THRESHOLD = 5  # Percentage
CPU_UNDER_THRESHOLD = 3  # Percentage
MEMORY_UNDER_THRESHOLD = 3  # Percentage

# Get node metrics
def get_node_metrics():
    output = subprocess.run(["kubectl", "top", "nodes"], capture_output=True, text=True)
    lines = output.stdout.split("\n")[1:]  # Skip header
    nodes = {}

    for line in lines:
        if line.strip():
            parts = line.split()
            node_name = parts[0]
            cpu_usage = int(parts[1].strip("m")) / 1000  # Convert millicores to cores
            memory_usage = int(parts[3].strip("Mi"))  # Already in MiB

            nodes[node_name] = {"cpu": cpu_usage, "memory": memory_usage}

    return nodes

# Classify nodes
def classify_nodes():
    nodes = get_node_metrics()
    overutilized = []
    underutilized = []

    for node, metrics in nodes.items():
        # Get node capacity
        node_obj = v1.read_node(node)
        allocatable = node_obj.status.allocatable

        try:
            total_cpu = float(allocatable["cpu"])  # Directly use cores
            total_memory = int(allocatable["memory"].strip("Ki")) / 1024  # Convert to MiB
        except Exception as e:
            print(f"Error parsing node resources for {node}: {e}")
            continue

        cpu_percent = (metrics["cpu"] / total_cpu) * 100
        memory_percent = (metrics["memory"] / total_memory) * 100

        print(f"Node: {node}, CPU: {cpu_percent:.2f}%, Memory: {memory_percent:.2f}%")  # Debug output

        if cpu_percent > CPU_OVER_THRESHOLD or memory_percent > MEMORY_OVER_THRESHOLD:
            overutilized.append(node)
        elif cpu_percent < CPU_UNDER_THRESHOLD and memory_percent < MEMORY_UNDER_THRESHOLD:
            underutilized.append(node)

    return overutilized, underutilized

# Drain a node
def drain_node(node):
    print(f"Draining node: {node}")
    subprocess.run(["kubectl", "cordon", node], text=True)
    subprocess.run(["kubectl", "drain", node, "--ignore-daemonsets", "--delete-emptydir-data"], text=True)

# Main reshuffling logic
def reshuffle():
    overutilized, underutilized = classify_nodes()

    if not underutilized:
        print("No underutilized nodes available. Skipping reshuffling.")
        return

    for node in overutilized:
        if underutilized:
            drain_node(node)
        else:
            print(f"Keeping {node} active to ensure scheduling capacity.")

# Run reshuffling
reshuffle()

