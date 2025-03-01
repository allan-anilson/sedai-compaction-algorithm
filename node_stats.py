from kubernetes import client, config
import requests

def get_node_stats():
    # Load kube config
    config.load_kube_config()
    v1 = client.CoreV1Api()
    
    # Fetch all nodes
    nodes = v1.list_node().items
    
    print("Node Resource Usage:")
    for node in nodes:
        node_name = node.metadata.name

        # Get node conditions (e.g., Ready status)
        conditions = {cond.type: cond.status for cond in node.status.conditions}
        ready_status = conditions.get("Ready", "Unknown")

        # Fetch CPU & Memory usage from Metrics API
        try:
            metrics_api = client.CustomObjectsApi()
            node_metrics = metrics_api.get_cluster_custom_object(
                "metrics.k8s.io", "v1beta1", "nodes", node_name
            )

            cpu_usage = node_metrics["usage"]["cpu"]
            memory_usage = node_metrics["usage"]["memory"]
        except Exception as e:
            cpu_usage = "[Not Available]"
            memory_usage = "[Not Available]"

        print(f"Node: {node_name}, Status: {ready_status}")
        print(f"CPU: {cpu_usage} | Memory: {memory_usage}")
        print("-" * 40)

if __name__ == "__main__":
    get_node_stats()

