# Backend Engineer's Guide

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)](#contributing)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/djeada/Backend-Engineers-Guide/pulls)

A comprehensive collection of backend engineering notes, covering essential topics such as API design, databases, deployment strategies, distributed systems, networking, performance optimization, security best practices, and more. This repository serves as both a personal knowledge base and a community resource for backend engineers at all experience levels.

<img width="1536" height="1024" alt="backend_notes" src="https://github.com/user-attachments/assets/b1a1a790-aa63-448d-840d-aa01b4055cdc" />

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Notes](#notes)
  - [API Design](#api-design)
  - [Network Communications](#network-communications)
  - [Web Servers](#web-servers)
  - [Databases](#databases)
  - [Caching](#caching)
  - [Data Processing](#data-processing)
  - [Data Formats](#data-formats)
  - [Security](#security)
  - [Deployment](#deployment)
  - [Distributed Systems](#distributed-systems)
- [Scripts](#scripts)
- [Projects](#projects)
- [References](#references)
- [Contributing](#contributing)
- [License](#license)

## Overview

This guide is designed to provide practical insights and real-world examples for backend engineers. Each topic is organized into its own Markdown file within the `notes` directory, making it easy to navigate and reference specific areas of interest.

**Key Features:**

- **Comprehensive Coverage** – Spans the full backend engineering landscape from API design to distributed systems
- **Practical Focus** – Emphasizes real-world applications and industry best practices
- **Regularly Updated** – Content is continuously refined to reflect current technologies and methodologies
- **Community-Driven** – Open to contributions and feedback from the developer community

## Getting Started

### Prerequisites

- Basic understanding of programming concepts
- Familiarity with command-line interfaces
- A text editor or IDE for viewing Markdown files (VS Code, Obsidian, or any Markdown viewer recommended)

### Quick Start

Clone the repository to your local machine:

```bash
git clone https://github.com/djeada/Backend-Engineers-Guide.git
cd Backend-Engineers-Guide/notes
```

Browse the topics by navigating through the `notes` directory, or view the content directly on GitHub.

### How to Use This Guide

1. **Sequential Learning** – Start from API Design and progress through each section for a structured learning path
2. **Reference Guide** – Jump directly to specific topics when you need quick answers
3. **Deep Dives** – Explore the references section for additional resources on topics that interest you

## Notes

### API Design

| Topic | Description | Link |
|-------|-------------|------|
| API Communication Protocols | Introduction to API design principles and patterns | [📖 Read](notes/01_api_design/01_api_communication_protocols.md) |
| REST | RESTful API architecture and best practices | [📖 Read](notes/01_api_design/02_rest.md) |
| GraphQL | Query language for APIs with flexible data fetching | [📖 Read](notes/01_api_design/03_graphql.md) |
| gRPC | High-performance RPC framework using Protocol Buffers | [📖 Read](notes/01_api_design/04_grpc.md) |
| Stateful vs Stateless | State management patterns in API design | [📖 Read](notes/01_api_design/05_state_management.md) |
| Data Transmission | Methods and protocols for data exchange | [📖 Read](notes/01_api_design/06_data_transmission.md) |

---

### Network Communications

| Topic | Description | Link |
|-------|-------------|------|
| Network Communications | Fundamentals of network communication | [📖 Read](notes/02_network_communications/01_network_communications.md) |
| TCP vs UDP | Comparison of transport layer protocols | [📖 Read](notes/02_network_communications/02_tcp_and_udp.md) |
| HTTP Protocol | Hypertext Transfer Protocol deep dive | [📖 Read](notes/02_network_communications/03_http_protocol.md) |
| WebSockets | Real-time bidirectional communication | [📖 Read](notes/02_network_communications/04_web_sockets.md) |
| Metrics and Analysis | Network performance monitoring, analysis, and modern observability tools (Prometheus, Grafana, Jaeger, Perf, ClickHouse, and more) | [📖 Read](notes/02_network_communications/05_metrics_and_analysis.md) |

---

### Web Servers

| Topic | Description | Link |
|-------|-------------|------|
| Web Server Overview | Introduction to web server architecture | [📖 Read](notes/03_server_technologies/01_web_server_overview.md) |
| Static & Dynamic Content | Serving different types of web content | [📖 Read](notes/03_server_technologies/02_static_dynamic_content.md) |
| Tomcat | Apache Tomcat servlet container | [📖 Read](notes/03_server_technologies/03_tomcat.md) |
| Apache | Apache HTTP Server configuration and usage | [📖 Read](notes/03_server_technologies/04_apache.md) |
| Nginx | High-performance web server and reverse proxy | [📖 Read](notes/03_server_technologies/05_nginx.md) |
| Forward Proxies | Client-side proxy servers | [📖 Read](notes/03_server_technologies/06_forward_proxies.md) |
| Reverse Proxies | Server-side proxy patterns | [📖 Read](notes/03_server_technologies/07_reverse_proxies.md) |
| Load Balancing | Traffic distribution strategies | [📖 Read](notes/03_server_technologies/08_load_balancing.md) |

---

### Databases

| Topic | Description | Link |
|-------|-------------|------|
| Types of Databases | Overview of database categories and use cases | [📖 Read](notes/04_databases/01_types_of_databases.md) |
| Transactions | ACID properties and transaction management | [📖 Read](notes/04_databases/02_transactions.md) |
| Indexes | Database indexing strategies for performance | [📖 Read](notes/04_databases/03_indexes.md) |
| Isolation Levels | Concurrency control and isolation | [📖 Read](notes/04_databases/04_isolation_levels.md) |
| Data Warehousing | Analytics and data warehouse design | [📖 Read](notes/04_databases/05_data_warehousing.md) |
| Replication | Database replication strategies | [📖 Read](notes/04_databases/06_replication.md) |
| Halloween Problem | Classic database update anomaly | [📖 Read](notes/04_databases/07_halloween_problem.md) |

---

### Caching

| Topic | Description | Link |
|-------|-------------|------|
| Caching Strategies | Cache patterns and eviction policies | [📖 Read](notes/05_caching/01_caching_strategies.md) |
| Redis | In-memory data store for caching | [📖 Read](notes/05_caching/02_redis.md) |
| Content Delivery Networks | CDN architecture and implementation | [📖 Read](notes/05_caching/03_content_delivery_networks.md) |
| Database Caching | Query and result caching techniques | [📖 Read](notes/05_caching/04_database_caching.md) |

---

### Data Processing

| Topic | Description | Link |
|-------|-------------|------|
| Pub/Sub vs Queue | Messaging pattern comparison | [📖 Read](notes/06_data_processing/01_pub_sub_vs_queue.md) |
| Messaging System Integration | Integrating message brokers | [📖 Read](notes/06_data_processing/02_messaging_system_integration.md) |
| Batch Processing | Large-scale batch data processing | [📖 Read](notes/06_data_processing/03_batch_processing.md) |
| Stream Processing | Real-time data stream processing | [📖 Read](notes/06_data_processing/04_stream_processing.md) |
| ETL and ELT Pipelines | Extract-Transform-Load patterns, data quality, and incremental loading | [📖 Read](notes/06_data_processing/05_etl_and_pipelines.md) |
| Lambda and Kappa Architecture | Batch + streaming hybrid vs stream-only data architectures | [📖 Read](notes/06_data_processing/06_lambda_and_kappa_architecture.md) |
| Workflow Orchestration | DAG-based pipeline scheduling, retries, and observability | [📖 Read](notes/06_data_processing/07_workflow_orchestration.md) |

---

### Data Formats

| Topic | Description | Link |
|-------|-------------|------|
| Protocol Buffers | Google's language-neutral serialization format | [📖 Read](notes/07_data_formats/01_protocol_buffers.md) |
| XML | Extensible Markup Language | [📖 Read](notes/07_data_formats/02_xml.md) |
| JSON | JavaScript Object Notation | [📖 Read](notes/07_data_formats/03_json.md) |
| YAML | YAML Ain't Markup Language | [📖 Read](notes/07_data_formats/04_yaml.md) |

---

### Security

| Topic | Description | Link |
|-------|-------------|------|
| Authentication | Auth mechanisms and implementation | [📖 Read](notes/08_security/01_auth.md) |
| TLS | Transport Layer Security | [📖 Read](notes/08_security/02_tls.md) |
| Security Vulnerabilities | Common vulnerabilities and mitigations | [📖 Read](notes/08_security/03_security_vulnerabilities.md) |
| Security Best Practices | Industry security standards and measures | [📖 Read](notes/08_security/04_security_best_practices_and_measures.md) |
| Third-Party Cookies | Cookie security and privacy concerns | [📖 Read](notes/08_security/05_third_party_cookies_vulnerabilities.md) |
| Secure Containers | Container image hardening, runtime security, and network isolation | [📖 Read](notes/08_security/06_secure_containers.md) |
| Credentials Management | Managing and supplying secrets safely in production | [📖 Read](notes/08_security/07_credentials_management.md) |
| Supply Chain Attacks | Dependency confusion, typosquatting, SBOM, and artefact signing | [📖 Read](notes/08_security/08_supply_chain_attacks.md) |

---

### Deployment

| Topic | Description | Link |
|-------|-------------|------|
| CentOS on DigitalOcean | Server deployment on DigitalOcean | [📖 Read](notes/09_deployment/01_centos_digital_ocean.md) |
| Static Python Website | Deploying Python websites to Netlify | [📖 Read](notes/09_deployment/02_static_python_website_netlify.md) |
| Docker | Containerisation fundamentals, Dockerfile best practices, Compose, and security | [📖 Read](notes/09_deployment/03_docker.md) |
| Kubernetes | Container orchestration, core objects, autoscaling, and storage | [📖 Read](notes/09_deployment/04_kubernetes.md) |
| CI/CD Pipelines | Continuous integration and delivery with GitHub Actions and GitLab CI | [📖 Read](notes/09_deployment/05_ci_cd.md) |
| Deployment Strategies | Rolling, Blue-Green, Canary, Feature Flags, and strategy selection guide | [📖 Read](notes/09_deployment/06_deployment_strategies.md) |
| Infrastructure as Code | Terraform and Ansible for reproducible, version-controlled infrastructure | [📖 Read](notes/09_deployment/07_infrastructure_as_code.md) |

---

### Distributed Systems

| Topic | Description | Link |
|-------|-------------|------|
| Coordination Services | Distributed coordination and consensus | [📖 Read](notes/10_distributed_systems/01_coordination_services.md) |
| Gossip Protocol | Decentralized information dissemination | [📖 Read](notes/10_distributed_systems/02_gossip_protocol.md) |
| Linearizability | Strong consistency guarantees | [📖 Read](notes/10_distributed_systems/03_linearizability.md) |
| Concurrent Writes | Handling write conflicts | [📖 Read](notes/10_distributed_systems/04_concurrent_writes.md) |
| Operational Transform | Collaborative editing algorithms | [📖 Read](notes/10_distributed_systems/05_operational_transform.md) |
| Algorithms Summary | Overview of distributed system algorithms | [📖 Read](notes/10_distributed_systems/06_algorithms_summary.md) |
| Optimistic vs Pessimistic Locking | Concurrency control strategies | [📖 Read](notes/10_distributed_systems/07_optimistic_vs_pessimistic_locking.md) |

## Scripts

The [`scripts/`](scripts/) directory contains small, self-contained Python scripts that bring the topics above to life with runnable demos. Every script uses only the Python standard library.

| Directory | Script | Topic |
|-----------|--------|-------|
| `api_design/` | [`rest_api_example.py`](scripts/api_design/rest_api_example.py) | Minimal REST API server with CRUD endpoints |
| `api_design/` | [`graphql_example.py`](scripts/api_design/graphql_example.py) | GraphQL-like query engine with field selection |
| `network_communications/` | [`tcp_udp_example.py`](scripts/network_communications/tcp_udp_example.py) | TCP vs UDP echo server/client comparison |
| `network_communications/` | [`http_request_example.py`](scripts/network_communications/http_request_example.py) | HTTP methods, headers, and content types |
| `databases/` | [`transaction_example.py`](scripts/databases/transaction_example.py) | SQLite transactions and ACID properties |
| `databases/` | [`index_example.py`](scripts/databases/index_example.py) | Index performance and EXPLAIN QUERY PLAN |
| `caching/` | [`lru_cache_example.py`](scripts/caching/lru_cache_example.py) | LRU cache implementation and eviction |
| `caching/` | [`cache_strategies_example.py`](scripts/caching/cache_strategies_example.py) | Write-through, write-back, and cache-aside patterns |
| `data_formats/` | [`format_conversion.py`](scripts/data_formats/format_conversion.py) | JSON, XML, and YAML conversion |
| `data_formats/` | [`protocol_buffer_example.py`](scripts/data_formats/protocol_buffer_example.py) | Protocol-buffer-like binary serialization |
| `data_processing/` | [`pub_sub_example.py`](scripts/data_processing/pub_sub_example.py) | In-process publish/subscribe broker |
| `data_processing/` | [`batch_processing_example.py`](scripts/data_processing/batch_processing_example.py) | Batch processing pipeline with configurable batches |
| `data_processing/` | [`stream_processing_example.py`](scripts/data_processing/stream_processing_example.py) | Tumbling/sliding windows and alert-style stream processing |
| `data_processing/` | [`dead_letter_queue_example.py`](scripts/data_processing/dead_letter_queue_example.py) | Dead-letter queue with retry limits and poison-message routing |
| `data_processing/` | [`etl_pipeline_example.py`](scripts/data_processing/etl_pipeline_example.py) | ETL pipeline with incremental extraction, transform, and upsert load |
| `data_processing/` | [`workflow_orchestration_example.py`](scripts/data_processing/workflow_orchestration_example.py) | DAG orchestrator with topological sort, parallel waves, retries, and backfill |
| `security/` | [`hashing_example.py`](scripts/security/hashing_example.py) | Password hashing, token generation |
| `security/` | [`jwt_example.py`](scripts/security/jwt_example.py) | JWT-like token creation and verification |
| `distributed_systems/` | [`gossip_protocol_example.py`](scripts/distributed_systems/gossip_protocol_example.py) | Gossip protocol cluster simulation |
| `distributed_systems/` | [`vector_clock_example.py`](scripts/distributed_systems/vector_clock_example.py) | Vector clock causality tracking |
| `server_technologies/` | [`load_balancer_example.py`](scripts/server_technologies/load_balancer_example.py) | Load balancing strategy simulation |
| `server_technologies/` | [`reverse_proxy_example.py`](scripts/server_technologies/reverse_proxy_example.py) | Reverse proxy routing by path prefix |
| `deployment/` | [`health_check_example.py`](scripts/deployment/health_check_example.py) | Health-check and readiness endpoints |
| `deployment/` | [`rolling_deploy_example.py`](scripts/deployment/rolling_deploy_example.py) | Rolling deployment simulation |

See the [scripts README](scripts/README.md) for prerequisites and usage instructions.

## Projects

The [`projects/`](projects/) directory contains guided labs that combine notes, scripts, and longer walkthroughs into focused backend engineering exercises.

| Project | Focus | Link |
|---------|-------|------|
| API Reliability Lab | API versioning, idempotency, and webhook verification | [📖 Open](projects/api_reliability_lab/README.md) |
| Network Resilience Lab | TCP/UDP trade-offs, HTTP request flow, DNS caching, and circuit breakers | [📖 Open](projects/network_resilience_lab/README.md) |
| Security Controls Lab | Password hashing, JWT verification, encryption concepts, and rate limiting | [📖 Open](projects/security_controls_lab/README.md) |
| Data Interchange Lab | JSON/XML/YAML conversion and Protocol Buffers-style binary serialization | [📖 Open](projects/data_interchange_lab/README.md) |
| Request Pipeline Lab | Middleware composition for logging, auth, tracing, and CORS | [📖 Open](projects/request_pipeline_lab/README.md) |
| Cluster Membership Lab | Gossip propagation and eventual consistency in distributed clusters | [📖 Open](projects/cluster_membership_lab/README.md) |
| Database Reliability Lab | Transactions, schema evolution, indexes, and connection pooling | [📖 Open](projects/database_reliability_lab/README.md) |
| Cache Patterns Lab | LRU eviction, TTL expiration, and cache write strategies | [📖 Open](projects/cache_patterns_lab/README.md) |
| Messaging Reliability Lab | Pub/sub, batch processing, stream processing, and dead-letter queues | [📖 Open](projects/messaging_reliability_lab/README.md) |
| Distributed Coordination Lab | Leader election, vector clocks, quorums, and consistent hashing | [📖 Open](projects/distributed_coordination_lab/README.md) |
| Grafana Alert Test Environment | Multi-service lab for Grafana alerting, Prometheus metrics, and notification policies | [📖 Open](projects/grafana_test_setup/README.md) |
| Reverse Proxy Lab | Path-based routing and load-balancing strategies using standard-library demos | [📖 Open](projects/reverse_proxy_lab/README.md) |
| Deployment Rollout Lab | Rolling deploys, canary releases, and readiness checks | [📖 Open](projects/deployment_rollout_lab/README.md) |

See the [projects README](projects/README.md) for the full project index.

## References

### 📚 Books

| Title | Author(s) | Link |
|-------|-----------|------|
| *Designing Data-Intensive Applications* | Martin Kleppmann | [Amazon](https://amzn.to/4iX2sU6) |
| *Building Microservices* | Sam Newman | [Amazon](https://amzn.to/4i9MvJg) |
| *Clean Architecture* | Robert C. Martin | [Amazon](https://amzn.to/4lp7ZEU) |
| *Domain-Driven Design* | Eric Evans | [Amazon](https://amzn.to/4iYQ6Lx) |
| *Release It!* | Michael T. Nygard | [Amazon](https://amzn.to/4jf34UW) |
| *The Art of Scalability* | Martin L. Abbott, Michael T. Fisher | [Amazon](https://amzn.to/422qAyR) |
| *Microservices Patterns* | Chris Richardson | [Amazon](https://amzn.to/4jqgbD1) |
| *Continuous Delivery* | Jez Humble, David Farley | [Amazon](https://amzn.to/3RDoxep) |
| *Site Reliability Engineering* | Betsy Beyer et al. | [Amazon](https://amzn.to/4i8cOiZ) |

### 🎓 Online Courses and Resources

| Resource | Platform |
|----------|----------|
| [Node.js Tutorial for Beginners](https://www.thenetninja.co.uk/courses/node-js-tutorial-for-beginners) | The Net Ninja |
| [The Complete Node.js Developer Course](https://www.udemy.com/course/the-complete-nodejs-developer-course-2/) | Udemy |
| [Building Scalable Java Microservices with Spring Boot](https://www.coursera.org/learn/google-cloud-java-spring) | Coursera |
| [Microservices Architecture](https://www.edx.org/course/microservices-architecture) | edX |
| [Backend Development with Python](https://www.pluralsight.com/courses/backend-development-with-python) | Pluralsight |
| [Node.js and Express](https://www.freecodecamp.org/news/tag/nodejs/) | FreeCodeCamp |
| [Building Web APIs with ASP.NET Core](https://docs.microsoft.com/en-us/learn/modules/build-web-api-aspnet-core/) | Microsoft Learn |
| [Community Tutorials](https://www.digitalocean.com/community/tutorials) | DigitalOcean |
| [REST API Tutorial](https://restfulapi.net/) | RESTful API |
| [Learning Center](https://learning.postman.com/) | Postman |

## Contributing

We welcome contributions from the community! Here's how you can help:

### Ways to Contribute

- **Report Issues** – Found an error or have a suggestion? [Open an issue](https://github.com/djeada/Backend-Engineers-Guide/issues)
- **Improve Content** – Fix typos, clarify explanations, or add examples
- **Add New Topics** – Have expertise in an area not yet covered? We'd love your input
- **Share Resources** – Know of great learning materials? Add them to the references

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature-name`)
3. Make your changes following the existing formatting conventions
4. Commit your changes (`git commit -m 'Add: brief description of changes'`)
5. Push to your branch (`git push origin feature/your-feature-name`)
6. Open a Pull Request

For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>⭐ If you find this guide helpful, please consider giving it a star!</strong>
</p>
