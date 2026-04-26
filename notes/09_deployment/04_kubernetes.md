
## Kubernetes

Kubernetes (K8s) is an open-source container orchestration platform that automates the deployment, scaling, and management of containerised applications across a cluster of machines.

```
  +----------------------- Kubernetes Cluster -----------------------+
  |                                                                   |
  |   +------------------+      +------------------+                 |
  |   |   Control Plane  |      |   Worker Node 1  |                 |
  |   |                  |      |                  |                 |
  |   | API Server        |      | kubelet          |                 |
  |   | etcd             |      | kube-proxy       |                 |
  |   | Scheduler        |      | Container Runtime|                 |
  |   | Controller Mgr   |      | Pods             |                 |
  |   +------------------+      +------------------+                 |
  |                             +------------------+                 |
  |                             |   Worker Node 2  |                 |
  |                             |  kubelet / Pods  |                 |
  |                             +------------------+                 |
  +-------------------------------------------------------------------+
```

- **Control Plane** – manages the desired state of the cluster (API Server, etcd, Scheduler, Controller Manager).
- **Worker Nodes** – run workloads; each node runs a `kubelet` agent, a `kube-proxy`, and a container runtime.
- **Pod** – the smallest deployable unit; wraps one or more containers that share network and storage.

### Core Objects

#### Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
  labels:
    app: myapp
spec:
  containers:
    - name: myapp
      image: ghcr.io/myorg/myapp:1.0.0
      ports:
        - containerPort: 8000
      resources:
        requests:
          cpu: "100m"
          memory: "128Mi"
        limits:
          cpu: "500m"
          memory: "256Mi"
```

Pods are ephemeral. Use higher-level controllers (Deployment, StatefulSet) for resilience.

#### Deployment

A Deployment manages a ReplicaSet to keep the desired number of Pod replicas running and handles rolling updates.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: myapp
          image: ghcr.io/myorg/myapp:1.0.0
          ports:
            - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 20
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

- **readinessProbe** – gates traffic; a Pod does not receive requests until this passes.
- **livenessProbe** – triggers a container restart if the application becomes unresponsive.
- **maxSurge / maxUnavailable** – controls how many extra/missing Pods are allowed during a rolling update.

#### Service

A Service gives Pods a stable DNS name and IP address, load-balancing across healthy replicas.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-svc
spec:
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP   # ClusterIP (internal), NodePort, or LoadBalancer
```

#### Ingress

An Ingress exposes HTTP/HTTPS routes from outside the cluster to Services.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: myapp-svc
                port:
                  number: 80
```

#### ConfigMap and Secret

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
data:
  LOG_LEVEL: "info"
  MAX_CONNECTIONS: "100"
---
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secrets
type: Opaque
data:
  DATABASE_URL: <base64-encoded-value>
```

Reference them in a Pod spec:

```yaml
envFrom:
  - configMapRef:
      name: myapp-config
  - secretRef:
      name: myapp-secrets
```

### Namespace

Namespaces partition cluster resources between teams or environments:

```bash
kubectl create namespace staging
kubectl -n staging apply -f deployment.yaml
```

### Common kubectl Commands

```bash
# Apply manifests
kubectl apply -f deployment.yaml
kubectl apply -f ./k8s/          # apply all files in a directory

# Inspect resources
kubectl get pods -n staging
kubectl describe pod myapp-abc123 -n staging
kubectl logs myapp-abc123 -n staging --follow

# Execute a command inside a pod
kubectl exec -it myapp-abc123 -n staging -- /bin/sh

# Scale a deployment
kubectl scale deployment myapp --replicas=5 -n staging

# Roll out a new image
kubectl set image deployment/myapp myapp=ghcr.io/myorg/myapp:2.0.0 -n staging

# Watch rollout status
kubectl rollout status deployment/myapp -n staging

# Roll back to the previous revision
kubectl rollout undo deployment/myapp -n staging

# Delete resources
kubectl delete -f deployment.yaml
```

### Horizontal Pod Autoscaler (HPA)

HPA automatically scales the number of Pods based on observed metrics.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Persistent Storage

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard
```

Mount it in a Pod:

```yaml
volumes:
  - name: db-storage
    persistentVolumeClaim:
      claimName: db-pvc
containers:
  - name: db
    volumeMounts:
      - mountPath: /var/lib/postgresql/data
        name: db-storage
```

### StatefulSet

Use a StatefulSet for stateful workloads (databases, message brokers) that need stable network identities and ordered deployment:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16-alpine
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 10Gi
```

### Resource Management and Quality of Service

| QoS Class  | Condition |
|------------|-----------|
| Guaranteed | `requests == limits` for all containers |
| Burstable  | `requests < limits` (or only one is set) |
| BestEffort | No `requests` or `limits` set |

Always set `requests` and `limits` to prevent one Pod from starving others and to help the scheduler place Pods on appropriate nodes.

### Security Best Practices

- **Enable RBAC** and grant only the permissions required (principle of least privilege).
- **Use Network Policies** to restrict traffic between Pods.
- **Avoid running containers as root**; set `securityContext.runAsNonRoot: true`.
- **Read-only root filesystem** – `securityContext.readOnlyRootFilesystem: true`.
- **Store secrets in a secrets manager** (Vault, AWS Secrets Manager) and sync with the Kubernetes Secrets API via an operator.
- **Scan images** for CVEs before pushing to the registry.
- **Keep Kubernetes version up to date** to receive security patches.
