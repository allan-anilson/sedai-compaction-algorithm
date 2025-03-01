from kubernetes import client, config

def get_node_utilization():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    metrics = client.CustomObjectsApi()
    
    nodes = v1.list_node().items
    underutilized_nodes = []
    overloaded_nodes = []
    
    X, Y = 3, 5  # Utilization thresholds in percentage
    
    print("Node Utilization Analysis:")
    for node in nodes:
        node_name = node.metadata.name
        
        try:
            node_metrics = metrics.get_cluster_custom_object(
                group="metrics.k8s.io", version="v1beta1",
                plural="nodes", name=node_name
            )
            
            usage = node_metrics["usage"]
            cpu_usage_milli = int(usage["cpu"].strip("n")) / 1e6  # Convert to millicores
            mem_usage_mib = int(usage["memory"].strip("Ki")) / 1024  # Convert to MiB
            
            cpu_capacity = int(node.status.capacity["cpu"]) * 1000  # Convert cores to millicores
            mem_capacity = int(node.status.capacity["memory"].strip("Ki")) / 1024  # Convert to MiB
            
            cpu_percent = (cpu_usage_milli / cpu_capacity) * 100
            mem_percent = (mem_usage_mib / mem_capacity) * 100
            
            print(f"Node: {node_name} | CPU: {cpu_percent:.2f}% | Memory: {mem_percent:.2f}%")
            
            if cpu_percent < X and mem_percent < X:
                underutilized_nodes.append(node_name)
            elif cpu_percent > Y or mem_percent > Y:
                overloaded_nodes.append(node_name)
                
        except Exception as e:
            print(f"Warning: Could not fetch metrics for {node_name}: {e}")
            continue
    
    print("\nUnderutilized Nodes (< 3% CPU & Memory):", underutilized_nodes)
    print("Overloaded Nodes (> 5% CPU or Memory):", overloaded_nodes)
    
    return underutilized_nodes, overloaded_nodes

if __name__ == "__main__":
    get_node_utilization()

