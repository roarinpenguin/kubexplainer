"""
YAML parsing and validation service for Kubernetes manifests.
"""

from ruamel.yaml import YAML
from typing import List, Dict, Any, Tuple, Optional
import io

class YAMLService:
    """Service for parsing and validating Kubernetes YAML manifests."""
    
    def __init__(self):
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
    
    def parse(self, content: str) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Parse YAML content into structured documents.
        
        Args:
            content: YAML string content
            
        Returns:
            Tuple of (success, parsed_documents, error_message)
        """
        try:
            documents = []
            stream = io.StringIO(content)
            
            # Parse all YAML documents (supports multi-doc YAML with ---)
            for doc in self.yaml.load_all(stream):
                if doc is not None:
                    documents.append(dict(doc))
            
            if not documents:
                return False, [], "No valid YAML documents found"
            
            return True, documents, ""
        
        except Exception as e:
            return False, [], f"YAML parsing error: {str(e)}"
    
    def extract_resources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract Kubernetes resources from parsed YAML documents.
        
        Args:
            documents: List of parsed YAML documents
            
        Returns:
            List of resource dictionaries with metadata
        """
        resources = []
        
        for doc in documents:
            if not isinstance(doc, dict):
                continue
            
            kind = doc.get("kind")
            api_version = doc.get("apiVersion")
            
            if not kind or not api_version:
                continue
            
            metadata = doc.get("metadata", {})
            name = metadata.get("name")
            namespace = metadata.get("namespace")
            
            resources.append({
                "kind": kind,
                "api_version": api_version,
                "name": name,
                "namespace": namespace,
                "content": doc
            })
        
        return resources
    
    def validate_structure(self, resources: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate Kubernetes resource structure.
        
        Args:
            resources: List of resource dictionaries
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        for resource in resources:
            kind = resource.get("kind")
            content = resource.get("content", {})
            name = resource.get("name", "unnamed")
            
            # Check required fields
            if not kind:
                issues.append({
                    "severity": "error",
                    "path": "kind",
                    "message": "Missing required field 'kind'",
                    "suggestion": "Specify the resource type (e.g., Deployment, Service, Pod)"
                })
            
            if not resource.get("api_version"):
                issues.append({
                    "severity": "error",
                    "path": "apiVersion",
                    "message": f"Missing required field 'apiVersion' in {kind}",
                    "suggestion": "Add apiVersion field (e.g., 'apps/v1', 'v1')"
                })
            
            metadata = content.get("metadata", {})
            if not metadata.get("name"):
                issues.append({
                    "severity": "error",
                    "path": "metadata.name",
                    "message": f"Missing required field 'metadata.name' in {kind}",
                    "suggestion": "Every resource must have a name"
                })
            
            # Resource-specific validation
            if kind == "Deployment":
                issues.extend(self._validate_deployment(content, name))
            elif kind == "Service":
                issues.extend(self._validate_service(content, name))
            elif kind == "Pod":
                issues.extend(self._validate_pod(content, name))
            elif kind == "Ingress":
                issues.extend(self._validate_ingress(content, name))
            
            # Check for deprecated API versions
            deprecated = self._check_deprecated_api(kind, resource.get("api_version"))
            if deprecated:
                issues.append(deprecated)
        
        is_valid = not any(issue["severity"] == "error" for issue in issues)
        return is_valid, issues
    
    def _validate_deployment(self, content: Dict, name: str) -> List[Dict]:
        """Validate Deployment-specific requirements."""
        issues = []
        spec = content.get("spec", {})
        
        if not spec:
            issues.append({
                "severity": "error",
                "path": "spec",
                "message": f"Deployment '{name}' missing spec field",
                "suggestion": "Add spec with selector, replicas, and template"
            })
            return issues
        
        if "selector" not in spec:
            issues.append({
                "severity": "error",
                "path": "spec.selector",
                "message": f"Deployment '{name}' missing selector",
                "suggestion": "Add spec.selector.matchLabels to select pods"
            })
        
        if "template" not in spec:
            issues.append({
                "severity": "error",
                "path": "spec.template",
                "message": f"Deployment '{name}' missing pod template",
                "suggestion": "Add spec.template with pod specification"
            })
        else:
            # Validate template
            template = spec["template"]
            template_spec = template.get("spec", {})
            
            if not template_spec.get("containers"):
                issues.append({
                    "severity": "error",
                    "path": "spec.template.spec.containers",
                    "message": f"Deployment '{name}' has no containers defined",
                    "suggestion": "Add at least one container in spec.template.spec.containers"
                })
            
            # Check selector matches template labels
            selector_labels = spec.get("selector", {}).get("matchLabels", {})
            template_labels = template.get("metadata", {}).get("labels", {})
            
            if selector_labels and template_labels:
                for key, value in selector_labels.items():
                    if template_labels.get(key) != value:
                        issues.append({
                            "severity": "warning",
                            "path": "spec.selector.matchLabels",
                            "message": f"Selector label '{key}' doesn't match template labels",
                            "suggestion": "Ensure selector.matchLabels match template.metadata.labels"
                        })
        
        return issues
    
    def _validate_service(self, content: Dict, name: str) -> List[Dict]:
        """Validate Service-specific requirements."""
        issues = []
        spec = content.get("spec", {})
        
        if not spec:
            issues.append({
                "severity": "error",
                "path": "spec",
                "message": f"Service '{name}' missing spec field",
                "suggestion": "Add spec with selector and ports"
            })
            return issues
        
        if not spec.get("selector") and spec.get("type") != "ExternalName":
            issues.append({
                "severity": "warning",
                "path": "spec.selector",
                "message": f"Service '{name}' missing selector",
                "suggestion": "Add spec.selector to route traffic to matching pods"
            })
        
        if not spec.get("ports"):
            issues.append({
                "severity": "error",
                "path": "spec.ports",
                "message": f"Service '{name}' has no ports defined",
                "suggestion": "Add at least one port in spec.ports"
            })
        
        return issues
    
    def _validate_pod(self, content: Dict, name: str) -> List[Dict]:
        """Validate Pod-specific requirements."""
        issues = []
        spec = content.get("spec", {})
        
        if not spec:
            issues.append({
                "severity": "error",
                "path": "spec",
                "message": f"Pod '{name}' missing spec field",
                "suggestion": "Add spec with containers"
            })
            return issues
        
        containers = spec.get("containers", [])
        if not containers:
            issues.append({
                "severity": "error",
                "path": "spec.containers",
                "message": f"Pod '{name}' has no containers defined",
                "suggestion": "Add at least one container in spec.containers"
            })
        
        for idx, container in enumerate(containers):
            if not container.get("name"):
                issues.append({
                    "severity": "error",
                    "path": f"spec.containers[{idx}].name",
                    "message": f"Container at index {idx} missing name",
                    "suggestion": "Every container must have a unique name"
                })
            
            if not container.get("image"):
                issues.append({
                    "severity": "error",
                    "path": f"spec.containers[{idx}].image",
                    "message": f"Container '{container.get('name', idx)}' missing image",
                    "suggestion": "Specify the container image to run"
                })
        
        return issues
    
    def _validate_ingress(self, content: Dict, name: str) -> List[Dict]:
        """Validate Ingress-specific requirements."""
        issues = []
        spec = content.get("spec", {})
        
        if not spec:
            issues.append({
                "severity": "error",
                "path": "spec",
                "message": f"Ingress '{name}' missing spec field",
                "suggestion": "Add spec with rules"
            })
            return issues
        
        rules = spec.get("rules", [])
        if not rules and not spec.get("defaultBackend"):
            issues.append({
                "severity": "warning",
                "path": "spec.rules",
                "message": f"Ingress '{name}' has no rules or defaultBackend",
                "suggestion": "Add routing rules or a default backend"
            })
        
        return issues
    
    def _check_deprecated_api(self, kind: str, api_version: str) -> Optional[Dict]:
        """Check for deprecated API versions."""
        deprecated_apis = {
            ("Deployment", "extensions/v1beta1"): ("apps/v1", "1.16"),
            ("Deployment", "apps/v1beta1"): ("apps/v1", "1.16"),
            ("Deployment", "apps/v1beta2"): ("apps/v1", "1.16"),
            ("StatefulSet", "apps/v1beta1"): ("apps/v1", "1.16"),
            ("StatefulSet", "apps/v1beta2"): ("apps/v1", "1.16"),
            ("DaemonSet", "extensions/v1beta1"): ("apps/v1", "1.16"),
            ("DaemonSet", "apps/v1beta2"): ("apps/v1", "1.16"),
            ("ReplicaSet", "extensions/v1beta1"): ("apps/v1", "1.16"),
            ("Ingress", "extensions/v1beta1"): ("networking.k8s.io/v1", "1.22"),
            ("Ingress", "networking.k8s.io/v1beta1"): ("networking.k8s.io/v1", "1.22"),
        }
        
        key = (kind, api_version)
        if key in deprecated_apis:
            new_version, removed_in = deprecated_apis[key]
            return {
                "severity": "warning",
                "path": "apiVersion",
                "message": f"{kind} API version '{api_version}' is deprecated",
                "suggestion": f"Use '{new_version}' instead (removed in Kubernetes {removed_in})"
            }
        
        return None
    
    def generate_yaml(self, resource_type: str, config: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        Generate YAML for a Kubernetes resource.
        
        Args:
            resource_type: Type of resource (deployment, service, etc.)
            config: Configuration parameters
            
        Returns:
            Tuple of (success, yaml_content, error_message)
        """
        try:
            if resource_type == "deployment":
                content = self._generate_deployment(config)
            elif resource_type == "service":
                content = self._generate_service(config)
            elif resource_type == "ingress":
                content = self._generate_ingress(config)
            elif resource_type == "configmap":
                content = self._generate_configmap(config)
            else:
                return False, "", f"Unknown resource type: {resource_type}"
            
            # Convert to YAML string
            stream = io.StringIO()
            self.yaml.dump(content, stream)
            yaml_str = stream.getvalue()
            
            return True, yaml_str, ""
        
        except Exception as e:
            return False, "", f"Generation error: {str(e)}"
    
    def _generate_deployment(self, config: Dict) -> Dict:
        """Generate a Deployment manifest."""
        name = config.get("name", "my-deployment")
        image = config.get("image", "nginx:latest")
        replicas = config.get("replicas", 3)
        port = config.get("port", 80)
        
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": name,
                "labels": {
                    "app": name
                }
            },
            "spec": {
                "replicas": replicas,
                "selector": {
                    "matchLabels": {
                        "app": name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": name
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": name,
                            "image": image,
                            "ports": [{
                                "containerPort": port
                            }]
                        }]
                    }
                }
            }
        }
    
    def _generate_service(self, config: Dict) -> Dict:
        """Generate a Service manifest."""
        name = config.get("name", "my-service")
        app_label = config.get("app", name)
        port = config.get("port", 80)
        target_port = config.get("targetPort", port)
        service_type = config.get("type", "ClusterIP")
        
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": name
            },
            "spec": {
                "selector": {
                    "app": app_label
                },
                "type": service_type,
                "ports": [{
                    "port": port,
                    "targetPort": target_port,
                    "protocol": "TCP"
                }]
            }
        }
    
    def _generate_ingress(self, config: Dict) -> Dict:
        """Generate an Ingress manifest."""
        name = config.get("name", "my-ingress")
        host = config.get("host", "example.com")
        service_name = config.get("serviceName", "my-service")
        service_port = config.get("servicePort", 80)
        path = config.get("path", "/")
        
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": name
            },
            "spec": {
                "rules": [{
                    "host": host,
                    "http": {
                        "paths": [{
                            "path": path,
                            "pathType": "Prefix",
                            "backend": {
                                "service": {
                                    "name": service_name,
                                    "port": {
                                        "number": service_port
                                    }
                                }
                            }
                        }]
                    }
                }]
            }
        }
    
    def _generate_configmap(self, config: Dict) -> Dict:
        """Generate a ConfigMap manifest."""
        name = config.get("name", "my-config")
        data = config.get("data", {"key": "value"})
        
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": name
            },
            "data": data
        }
