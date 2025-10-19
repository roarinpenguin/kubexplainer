"""
Rule-based explanation engine for Kubernetes YAML fields.
Maps field paths to human-readable explanations.
"""

from typing import Dict, Any, List, Optional
import re

# Comprehensive explanation dictionary
FIELD_EXPLANATIONS = {
    # Metadata
    "metadata": "Contains metadata about the Kubernetes object, including its name, namespace, labels, and annotations.",
    "metadata.name": "The unique name of this resource within its namespace. Must be a valid DNS subdomain name.",
    "metadata.namespace": "The namespace in which this resource exists. Namespaces provide scope for resource names and enable resource quotas and access control.",
    "metadata.labels": "Key-value pairs for identifying, selecting, and grouping Kubernetes objects. Used by selectors in Services, ReplicaSets, and more.",
    "metadata.annotations": "Non-identifying metadata stored as key-value pairs. Used for storing arbitrary information like build info, monitoring configs, or tool-specific data.",
    "metadata.creationTimestamp": "Timestamp when this resource was created in the cluster. Set automatically by Kubernetes.",
    "metadata.resourceVersion": "An opaque value representing the internal version of this object. Used for optimistic concurrency control.",
    "metadata.uid": "A unique identifier for this object across the entire cluster. Generated automatically.",
    
    # Common spec fields
    "spec": "Defines the desired state and behavior of this resource. The actual specification varies by resource type.",
    "spec.replicas": "Defines the desired number of pod replicas. The ReplicaSet controller ensures this many pods are running at all times.",
    "spec.selector": "Defines how to identify pods that belong to this resource. Must match the pod template labels.",
    "spec.selector.matchLabels": "Key-value pairs that must all match for a pod to be selected. This is an AND operation across all labels.",
    "spec.selector.matchExpressions": "More complex label selection criteria using set-based operators like In, NotIn, Exists, and DoesNotExist.",
    
    # Pod Template
    "spec.template": "Defines the pod template used to create new pods. Contains metadata and spec for the pods.",
    "spec.template.metadata": "Metadata for pods created from this template, including labels that must match the selector.",
    "spec.template.metadata.labels": "Labels applied to all pods created from this template. Must match the parent resource's selector.",
    "spec.template.spec": "The specification for pods created from this template, defining containers, volumes, and pod-level settings.",
    
    # Containers
    "spec.template.spec.containers": "List of containers to run in each pod. At least one container is required.",
    "spec.containers": "List of containers to run in this pod. Each container runs as an isolated process within the pod's namespace.",
    "containers[].name": "The name of this container within the pod. Must be unique within the pod and follow DNS label rules.",
    "containers[].image": "The Docker/OCI container image to run. Format: [registry/]repository[:tag|@digest]. If no tag is specified, 'latest' is assumed.",
    "containers[].imagePullPolicy": "Determines when the kubelet pulls the image. Options: Always (always pull), IfNotPresent (pull if not cached), Never (never pull, use cached only).",
    "containers[].command": "The container's entrypoint command array. Overrides the Docker image's ENTRYPOINT. If not provided, the image's ENTRYPOINT is used.",
    "containers[].args": "Arguments passed to the container's command. Overrides the Docker image's CMD. Combined with 'command' if both are specified.",
    "containers[].env": "Environment variables to set in the container. Can be specified directly or sourced from ConfigMaps, Secrets, or other sources.",
    "containers[].ports": "List of ports to expose from the container. Primarily informational - doesn't prevent the container from binding to additional ports.",
    "containers[].resources": "Compute resource requirements and limits for this container. Affects scheduling and runtime behavior.",
    "containers[].volumeMounts": "Paths in the container's filesystem where volumes should be mounted.",
    "containers[].livenessProbe": "Health check to determine if the container is running. If it fails repeatedly, the container is restarted.",
    "containers[].readinessProbe": "Health check to determine if the container is ready to serve traffic. Failed probes remove the pod from service endpoints.",
    "containers[].startupProbe": "Health check for slow-starting containers. Disables liveness/readiness probes until it succeeds, preventing premature restarts.",
    "containers[].securityContext": "Security settings for this container, such as running as a specific user, capabilities, or read-only filesystem.",
    
    # Container resources
    "containers[].resources.requests": "Minimum resources guaranteed to this container. Used by the scheduler to place pods on nodes with sufficient capacity.",
    "containers[].resources.limits": "Maximum resources this container can use. Container will be throttled (CPU) or killed (memory) if limits are exceeded.",
    "containers[].resources.requests.cpu": "Minimum CPU units guaranteed. Specified in cores (e.g., '500m' = 0.5 cores). Used for scheduling.",
    "containers[].resources.requests.memory": "Minimum memory guaranteed. Specified in bytes (e.g., '256Mi', '1Gi'). Used for scheduling.",
    "containers[].resources.limits.cpu": "Maximum CPU units allowed. Container is throttled if it tries to exceed this. Specified in cores.",
    "containers[].resources.limits.memory": "Maximum memory allowed. Container is killed (OOMKilled) if it exceeds this limit. Specified in bytes.",
    
    # Container ports
    "containers[].ports[].containerPort": "The port number this container listens on. Must be between 1-65535.",
    "containers[].ports[].protocol": "The network protocol for this port. Options: TCP (default), UDP, or SCTP.",
    "containers[].ports[].name": "Optional name for this port. Can be referenced by Services and useful for service discovery.",
    "containers[].ports[].hostPort": "Port number on the host to forward to this container port. Limits pod scheduling to nodes where the port is available.",
    
    # Environment variables
    "containers[].env[].name": "The name of the environment variable as it appears in the container.",
    "containers[].env[].value": "The literal string value of the environment variable.",
    "containers[].env[].valueFrom": "Source for the environment variable's value, such as a ConfigMap, Secret, or field reference.",
    "containers[].env[].valueFrom.configMapKeyRef": "Populates the environment variable from a key in a ConfigMap.",
    "containers[].env[].valueFrom.secretKeyRef": "Populates the environment variable from a key in a Secret. The value is kept confidential.",
    "containers[].env[].valueFrom.fieldRef": "Populates the environment variable from a pod field like metadata.name or status.podIP.",
    
    # Volumes
    "spec.volumes": "List of volumes that can be mounted by containers in this pod. Defines storage sources.",
    "volumes[].name": "The name of this volume. Must be unique within the pod and referenced by container volumeMounts.",
    "volumes[].emptyDir": "A temporary directory that shares a pod's lifetime. Starts empty and is deleted when the pod is removed.",
    "volumes[].hostPath": "Mounts a file or directory from the host node's filesystem. Useful for system-level operations but not portable.",
    "volumes[].configMap": "Mounts a ConfigMap as files. Each key becomes a file, and its value becomes the file content.",
    "volumes[].secret": "Mounts a Secret as files. Each key becomes a file with base64-decoded content. Used for sensitive data.",
    "volumes[].persistentVolumeClaim": "Mounts a PersistentVolumeClaim, providing persistent storage that survives pod restarts and rescheduling.",
    
    # Volume mounts
    "containers[].volumeMounts[].name": "The name of the volume to mount. Must match a volume defined in spec.volumes.",
    "containers[].volumeMounts[].mountPath": "The absolute path in the container where the volume should be mounted.",
    "containers[].volumeMounts[].readOnly": "If true, the volume is mounted as read-only. Default is false (read-write).",
    "containers[].volumeMounts[].subPath": "A specific file or subdirectory within the volume to mount, rather than the entire volume.",
    
    # Probes
    "livenessProbe.httpGet": "Performs an HTTP GET request to check container health. Success is any status code between 200-399.",
    "readinessProbe.httpGet": "Performs an HTTP GET request to check if the container is ready for traffic.",
    "livenessProbe.exec": "Executes a command inside the container. Exit code 0 indicates success.",
    "readinessProbe.exec": "Executes a command to check readiness. Exit code 0 means the container is ready.",
    "livenessProbe.tcpSocket": "Attempts to open a TCP connection to the specified port. Success means the port is open.",
    "readinessProbe.tcpSocket": "Checks readiness by attempting a TCP connection to the specified port.",
    "livenessProbe.initialDelaySeconds": "Number of seconds to wait after the container starts before performing the first probe.",
    "livenessProbe.periodSeconds": "How often (in seconds) to perform the probe. Default is 10 seconds.",
    "livenessProbe.timeoutSeconds": "Number of seconds after which the probe times out. Default is 1 second.",
    "livenessProbe.successThreshold": "Minimum consecutive successes for the probe to be considered successful after a failure. Default is 1.",
    "livenessProbe.failureThreshold": "Number of consecutive failures before the container is restarted (liveness) or marked unready (readiness). Default is 3.",
    
    # Service
    "spec.type": "Determines how the Service is exposed. Options: ClusterIP (internal only), NodePort (exposed on each node), LoadBalancer (cloud load balancer), ExternalName (DNS alias).",
    "spec.clusterIP": "The internal IP address assigned to this Service. Automatically assigned by Kubernetes unless explicitly set or set to 'None' for headless services.",
    "spec.ports": "List of ports that are exposed by this Service. Each port maps a Service port to a target port on the pods.",
    "spec.ports[].port": "The port that this Service listens on. Other services and pods connect to this port.",
    "spec.ports[].targetPort": "The port on the pod to forward traffic to. Can be a number or a named port from the pod's port list.",
    "spec.ports[].nodePort": "For NodePort or LoadBalancer Services, the port exposed on every node. Must be in the range 30000-32767.",
    "spec.ports[].protocol": "The protocol for this Service port. Usually TCP or UDP.",
    "spec.sessionAffinity": "Whether to enable session affinity. 'ClientIP' routes requests from the same client IP to the same pod. Default is 'None'.",
    "spec.externalTrafficPolicy": "Controls how external traffic is routed. 'Cluster' (default) allows any node to handle traffic. 'Local' preserves client IPs but requires local pods.",
    
    # Deployment specific
    "spec.strategy": "Defines how pods are replaced during updates. Options: RollingUpdate (gradual replacement) or Recreate (all pods killed before new ones start).",
    "spec.strategy.type": "The deployment strategy type: RollingUpdate or Recreate.",
    "spec.strategy.rollingUpdate": "Parameters for a rolling update strategy.",
    "spec.strategy.rollingUpdate.maxSurge": "Maximum number of pods that can be created above the desired replica count during an update. Can be a number or percentage.",
    "spec.strategy.rollingUpdate.maxUnavailable": "Maximum number of pods that can be unavailable during an update. Can be a number or percentage.",
    "spec.revisionHistoryLimit": "Number of old ReplicaSets to retain for rollback purposes. Default is 10.",
    "spec.progressDeadlineSeconds": "Maximum time in seconds for a deployment to make progress before it's considered failed. Default is 600 seconds.",
    "spec.minReadySeconds": "Minimum number of seconds a newly created pod should be ready before it's considered available. Used to prevent flapping.",
    
    # Ingress
    "spec.rules": "List of host and path-based routing rules for this Ingress. Defines how external requests are routed to Services.",
    "spec.rules[].host": "The fully qualified domain name for this rule. Requests to this hostname follow these routing rules.",
    "spec.rules[].http": "HTTP-specific routing rules for this host.",
    "spec.rules[].http.paths": "List of path-based routing rules. Requests matching a path are forwarded to the specified backend.",
    "spec.rules[].http.paths[].path": "URL path prefix to match. Requests starting with this path are routed to the backend.",
    "spec.rules[].http.paths[].pathType": "How to interpret the path. Options: Exact (exact match), Prefix (path prefix), ImplementationSpecific.",
    "spec.rules[].http.paths[].backend": "The Service to route matching requests to.",
    "spec.rules[].http.paths[].backend.service": "Specifies the Service backend for this path.",
    "spec.rules[].http.paths[].backend.service.name": "The name of the Service to route traffic to.",
    "spec.rules[].http.paths[].backend.service.port": "The port on the Service to forward traffic to.",
    "spec.tls": "TLS/HTTPS configuration for this Ingress. Defines certificates and which hosts use HTTPS.",
    "spec.tls[].hosts": "List of hosts that should use this TLS certificate.",
    "spec.tls[].secretName": "Name of the Secret containing the TLS certificate and private key.",
    
    # ConfigMap
    "data": "Key-value pairs of configuration data. Each key is a filename or variable name, and each value is the content.",
    "binaryData": "Binary data stored as base64-encoded strings. Used for non-UTF8 data like images or compiled binaries.",
    
    # Secret
    "type": "The type of Secret. Common types: Opaque (arbitrary data), kubernetes.io/tls (TLS certificate), kubernetes.io/dockerconfigjson (Docker registry auth).",
    "stringData": "Key-value pairs of secret data in plain text. Automatically base64-encoded when stored. Useful for creating Secrets declaratively.",
    
    # PersistentVolumeClaim
    "spec.accessModes": "How the volume can be mounted. Options: ReadWriteOnce (single node read-write), ReadOnlyMany (multiple nodes read-only), ReadWriteMany (multiple nodes read-write).",
    "spec.resources": "Resource requirements for the persistent volume, primarily storage capacity.",
    "spec.resources.requests.storage": "The amount of storage requested. Format: '1Gi', '500Mi', '1Ti', etc.",
    "spec.storageClassName": "The name of the StorageClass to use. Determines the type of storage (SSD, HDD, etc.) and the provisioner.",
    "spec.volumeMode": "Defines whether the volume is a filesystem (default) or a raw block device.",
    
    # StatefulSet
    "spec.serviceName": "The name of the Service that governs this StatefulSet. Used for network identity of the pods.",
    "spec.podManagementPolicy": "How pods are created and scaled. 'OrderedReady' (default) creates pods sequentially. 'Parallel' creates all pods simultaneously.",
    "spec.volumeClaimTemplates": "Templates for PersistentVolumeClaims. Each pod gets its own persistent volume based on these templates.",
    
    # DaemonSet
    "spec.updateStrategy": "How DaemonSet pods are updated. 'RollingUpdate' updates pods gradually. 'OnDelete' updates only when pods are manually deleted.",
    
    # Job
    "spec.completions": "The desired number of successfully completed pods. Job continues until this many pods have succeeded.",
    "spec.parallelism": "Maximum number of pods that can run in parallel. Controls job concurrency.",
    "spec.backoffLimit": "Number of retries before considering the Job as failed. Default is 6.",
    "spec.activeDeadlineSeconds": "Maximum duration in seconds that the Job can run. Job is terminated if it exceeds this time.",
    
    # CronJob
    "spec.schedule": "Cron schedule for running the Job. Format: 'minute hour day month weekday' (e.g., '0 0 * * *' for daily at midnight).",
    "spec.jobTemplate": "Template for the Job to be created on each schedule run.",
    "spec.successfulJobsHistoryLimit": "Number of successful Job history entries to keep. Default is 3.",
    "spec.failedJobsHistoryLimit": "Number of failed Job history entries to keep. Default is 1.",
    "spec.concurrencyPolicy": "How to handle concurrent Job executions. Options: Allow, Forbid, Replace.",
    
    # Status (read-only)
    "status": "The current observed state of this resource. Automatically managed by Kubernetes controllers.",
    "status.phase": "High-level summary of where the resource is in its lifecycle.",
    "status.conditions": "Detailed list of conditions representing the status of different aspects of the resource.",
    "status.replicas": "The actual number of pod replicas currently running.",
    "status.readyReplicas": "The number of pod replicas that are ready to serve traffic.",
    "status.availableReplicas": "The number of pod replicas that are available (ready for at least minReadySeconds).",
}

# Resource type descriptions
RESOURCE_DESCRIPTIONS = {
    "Deployment": "Manages a replicated set of pods, providing declarative updates and rollback capabilities. Ideal for stateless applications.",
    "Service": "Exposes a set of pods as a network service with a stable IP and DNS name. Enables service discovery and load balancing.",
    "Pod": "The smallest deployable unit in Kubernetes, representing one or more containers that share storage and network resources.",
    "ConfigMap": "Stores non-confidential configuration data as key-value pairs. Allows separating configuration from container images.",
    "Secret": "Stores sensitive data such as passwords, tokens, or keys. Data is base64-encoded and can be encrypted at rest.",
    "Ingress": "Manages external HTTP/HTTPS access to services, providing load balancing, SSL termination, and name-based virtual hosting.",
    "PersistentVolumeClaim": "Requests storage resources from the cluster. Abstracts storage details from applications.",
    "PersistentVolume": "Represents a piece of storage in the cluster. Can be dynamically provisioned or manually created.",
    "StatefulSet": "Manages stateful applications requiring stable network identities, ordered deployment, and persistent storage.",
    "DaemonSet": "Ensures a copy of a pod runs on all (or selected) nodes. Used for node-level services like logging or monitoring.",
    "Job": "Creates one or more pods and ensures a specified number complete successfully. Used for batch processing and one-time tasks.",
    "CronJob": "Runs Jobs on a schedule (cron format). Used for periodic tasks like backups or report generation.",
    "ReplicaSet": "Ensures a specified number of pod replicas are running. Usually managed by Deployments rather than created directly.",
    "Namespace": "Provides scope for resource names and enables multi-tenancy. Resources in one namespace are isolated from others.",
    "ServiceAccount": "Provides an identity for processes running in pods, used for API authentication and authorization.",
    "Role": "Defines permissions within a namespace. Contains rules that represent a set of permissions.",
    "ClusterRole": "Like Role, but cluster-wide. Can grant access to cluster-scoped resources or across all namespaces.",
    "RoleBinding": "Grants permissions defined in a Role to users or ServiceAccounts within a namespace.",
    "ClusterRoleBinding": "Grants permissions defined in a ClusterRole at the cluster level.",
    "HorizontalPodAutoscaler": "Automatically scales the number of pods based on observed CPU/memory utilization or custom metrics.",
    "NetworkPolicy": "Defines how groups of pods can communicate with each other and external endpoints. Provides network segmentation.",
}

class K8sExplainer:
    """Rule-based explainer for Kubernetes YAML fields."""
    
    def __init__(self):
        self.field_explanations = FIELD_EXPLANATIONS
        self.resource_descriptions = RESOURCE_DESCRIPTIONS
    
    def explain_field(self, path: str, value: Any) -> Optional[str]:
        """
        Get explanation for a specific field path.
        
        Args:
            path: Dot-notation path like "spec.replicas" or "containers[].image"
            value: The actual value at this path
            
        Returns:
            Explanation string or None if not found
        """
        # Direct lookup
        if path in self.field_explanations:
            return self.field_explanations[path]
        
        # Try array notation variations
        # Convert spec.template.spec.containers.0.image to containers[].image
        array_path = re.sub(r'\.\d+\.', '[].', path)
        array_path = re.sub(r'\.\d+$', '[]', array_path)
        
        # Check partial matches
        for key in self.field_explanations:
            if array_path.endswith(key) or key in array_path:
                return self.field_explanations[key]
        
        # Generic fallbacks based on common patterns
        if 'name' in path.lower():
            return "The name identifier for this resource or sub-resource."
        elif 'namespace' in path.lower():
            return "The namespace scope for this resource."
        elif 'label' in path.lower():
            return "Labels are key-value pairs used for identification and selection."
        elif 'annotation' in path.lower():
            return "Annotations store arbitrary non-identifying metadata."
        
        return None
    
    def explain_resource(self, kind: str) -> Optional[str]:
        """Get high-level explanation for a resource type."""
        return self.resource_descriptions.get(kind)
    
    def generate_summary(self, resources: List[Dict[str, Any]]) -> str:
        """Generate a summary of all resources in the manifest."""
        if not resources:
            return "No resources found in the manifest."
        
        summary_parts = ["This Kubernetes manifest contains:"]
        
        for idx, resource in enumerate(resources, 1):
            kind = resource.get("kind", "Unknown")
            name = resource.get("metadata", {}).get("name", "unnamed")
            desc = self.explain_resource(kind)
            
            summary_parts.append(f"\n{idx}. **{kind}** named '{name}'")
            if desc:
                summary_parts.append(f"   - {desc}")
        
        return "\n".join(summary_parts)
    
    def walk_and_explain(self, obj: Any, path: str = "", explanations: List[Dict] = None) -> List[Dict]:
        """
        Recursively walk through the YAML structure and generate explanations.
        
        Args:
            obj: Current object (dict, list, or value)
            path: Current path in dot notation
            explanations: List to accumulate explanations
            
        Returns:
            List of explanation dictionaries
        """
        if explanations is None:
            explanations = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                # Get explanation for this field
                explanation = self.explain_field(current_path, value)
                if explanation:
                    explanations.append({
                        "path": current_path,
                        "value": value if not isinstance(value, (dict, list)) else f"<{type(value).__name__}>",
                        "explanation": explanation,
                        "source": "rule-based"
                    })
                
                # Recurse into nested structures
                if isinstance(value, (dict, list)):
                    self.walk_and_explain(value, current_path, explanations)
        
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                current_path = f"{path}.{idx}" if path else str(idx)
                self.walk_and_explain(item, current_path, explanations)
        
        return explanations
