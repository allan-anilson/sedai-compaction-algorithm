# sedai-compaction-algorithm
Compact Feature for Resource Reshuffling in Kubernetes

This project aims to develop a compact feature within Kubernetes that optimizes resource utilization by reshuffling workloads across nodes.
The feature will utilize drain and cordon commands to systematically evict pods from underutilized nodes, facilitating efficient resource consolidation.
By cordoning nodes, new pods are prevented from scheduling on specific nodes during reshuffling, streamlining the compaction process.
Taints and tolerations will be applied to control pod placements, ensuring that critical workloads, such as Deployments, StatefulSets, and Jobs, are managed appropriately, maintaining stability and continuity.
For complex workloads like StatefulSets and Jobs, specific logic will account for the need for persistent storage and ordered restarts, minimizing disruption during compaction.
This approach will reduce resource fragmentation, enhance node utilization, and improve overall cost-efficiency.

