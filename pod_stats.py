from kubernetes import client, config

def get_pod_stats():
    # Load kube config
    config.load_kube_config()
    
    # Initialize API clients
    v1 = client.CoreV1Api()
    metrics_api = client.CustomObjectsApi()
    
    print("Pod Resource Usage:")
    
    # Fetch all pods across all namespaces
    pods = v1.list_pod_for_all_namespaces().items

    for pod in pods:
        pod_name = pod.metadata.name
        namespace = pod.metadata.namespace
        
        try:
            # Fetch pod metrics
            pod_metrics = metrics_api.get_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods",
                name=pod_name
            )
            
            # Extract CPU & memory usage
            total_cpu = sum(
                int(container["usage"]["cpu"].rstrip("n")) for container in pod_metrics["containers"]
            )
            total_memory = sum(
                int(container["usage"]["memory"].rstrip("Ki")) for container in pod_metrics["containers"]
            )

            print(f"Pod: {pod_name}, Namespace: {namespace}")
            print(f"CPU: {total_cpu} nanocores | Memory: {total_memory} KiB")
        
        except Exception as e:
            print(f"Pod: {pod_name}, Namespace: {namespace}")
            print("CPU: [Not Available] | Memory: [Not Available]")

        print("-" * 40)

if __name__ == "__main__":
    get_pod_stats()

