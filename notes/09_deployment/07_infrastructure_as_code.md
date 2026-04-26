
## Infrastructure as Code

Infrastructure as Code (IaC) is the practice of defining and managing infrastructure (servers, networks, databases, load balancers) through machine-readable configuration files instead of manual processes or ad-hoc scripts. Changes are committed to version control, reviewed, and applied automatically, giving infrastructure the same reproducibility and auditability as application code.

```
  Developer writes HCL / YAML
          |
          | git push / PR
          v
  +-----------------+     plan      +-----------------+
  |  IaC Config     | ────────────► |  Execution Plan |
  |  (Terraform,    |               |  (diff: what    |
  |   Ansible,      |               |   will change)  |
  |   Pulumi)       | ──── apply ──► +-----------------+
  +-----------------+                       |
                                            | provisions
                                            v
                                    +-----------------+
                                    |  Cloud / On-Prem|
                                    |  Infrastructure |
                                    +-----------------+
```

### Key Benefits

- **Reproducibility** – any environment can be recreated identically from the same configuration.
- **Version control** – infrastructure changes are tracked, reviewable, and revertible.
- **Automation** – eliminates manual, error-prone console clicks.
- **Consistency** – development, staging, and production environments are defined by the same code.
- **Documentation** – the configuration files are the authoritative description of the system.

### Terraform

Terraform by HashiCorp is a declarative IaC tool. You describe the desired end state of your infrastructure in HashiCorp Configuration Language (HCL), and Terraform calculates the changes required to reach that state.

#### Providers

A provider is a plugin that knows how to talk to a specific API (AWS, GCP, Azure, Kubernetes, GitHub, etc.).

```hcl
terraform {
  required_version = ">= 1.7"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state in S3 so the team shares the same state file
  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}
```

#### Variables and Outputs

```hcl
variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

output "web_server_ip" {
  value       = aws_instance.web.public_ip
  description = "Public IP of the web server"
}
```

#### Resources

```hcl
# VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = { Name = "main-vpc" }
}

# Public subnet
resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = true
}

# Security group
resource "aws_security_group" "web" {
  name   = "web-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 instance
resource "aws_instance" "web" {
  ami                    = "ami-0c55b159cbfafe1f0"
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.web.id]

  tags = { Name = "web-server" }
}
```

#### Core Workflow

```bash
# Initialise – download providers and configure backend
terraform init

# Preview changes without making them
terraform plan -out=tfplan

# Apply the saved plan
terraform apply tfplan

# Destroy all managed resources
terraform destroy
```

#### Modules

Modules are reusable, composable units of Terraform configuration.

```hcl
# Using the official AWS VPC module
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"

  name             = "prod-vpc"
  cidr             = "10.0.0.0/16"
  azs              = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets   = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  enable_nat_gateway = true
}
```

#### State Management

Terraform keeps track of what it has created in a **state file** (`terraform.tfstate`). For team use, store state remotely (S3 + DynamoDB for locking, Terraform Cloud, GitLab-managed state) so that:

- Multiple team members can apply changes safely.
- State is not lost if a local machine is replaced.
- Sensitive values in state are encrypted at rest.

### Ansible

Ansible is a configuration management and provisioning tool. It connects to servers over SSH and executes tasks described in **playbooks** (YAML files). Unlike Terraform, Ansible is procedural — it executes tasks in order — though idempotent tasks produce the same result when re-run.

#### Inventory

An inventory lists the servers Ansible manages.

```ini
# inventory/hosts.ini
[web]
web-01 ansible_host=203.0.113.10
web-02 ansible_host=203.0.113.11

[db]
db-01 ansible_host=203.0.113.20

[all:vars]
ansible_user=deploy
ansible_ssh_private_key_file=~/.ssh/id_ed25519
```

#### Playbook

```yaml
# playbooks/deploy_web.yml
---
- name: Deploy web application
  hosts: web
  become: true   # sudo

  vars:
    app_version: "1.2.3"
    app_dir: /opt/myapp

  tasks:
    - name: Install system packages
      ansible.builtin.package:
        name: [git, python3, python3-pip]
        state: present

    - name: Create app directory
      ansible.builtin.file:
        path: "{{ app_dir }}"
        state: directory
        owner: deploy
        mode: "0755"

    - name: Clone application repository
      ansible.builtin.git:
        repo: https://github.com/myorg/myapp.git
        dest: "{{ app_dir }}"
        version: "v{{ app_version }}"
        force: true

    - name: Install Python dependencies
      ansible.builtin.pip:
        requirements: "{{ app_dir }}/requirements.txt"
        virtualenv: "{{ app_dir }}/venv"

    - name: Copy systemd unit file
      ansible.builtin.template:
        src: templates/myapp.service.j2
        dest: /etc/systemd/system/myapp.service
      notify: Restart myapp

    - name: Enable and start service
      ansible.builtin.systemd:
        name: myapp
        enabled: true
        state: started

  handlers:
    - name: Restart myapp
      ansible.builtin.systemd:
        name: myapp
        state: restarted
        daemon_reload: true
```

```bash
# Run the playbook
ansible-playbook -i inventory/hosts.ini playbooks/deploy_web.yml

# Dry run (check mode) – shows what would change
ansible-playbook -i inventory/hosts.ini playbooks/deploy_web.yml --check

# Limit to a specific host
ansible-playbook -i inventory/hosts.ini playbooks/deploy_web.yml --limit web-01
```

#### Roles

Roles are reusable, structured units of Ansible automation.

```
roles/
  nginx/
    tasks/main.yml
    handlers/main.yml
    templates/nginx.conf.j2
    defaults/main.yml
    meta/main.yml
```

```yaml
# playbooks/site.yml – using roles
- name: Configure web servers
  hosts: web
  roles:
    - common
    - nginx
    - myapp
```

### Terraform vs Ansible

| Dimension | Terraform | Ansible |
|-----------|-----------|---------|
| Primary use | Provisioning cloud resources | Configuring and deploying software |
| Paradigm | Declarative (desired state) | Procedural (ordered tasks, idempotent) |
| State | Maintains state file | Stateless (idempotent tasks) |
| Language | HCL | YAML |
| Agent | Agentless (API calls) | Agentless (SSH) |
| Strength | Cloud infrastructure lifecycle | Server configuration, application deployment |

They are complementary: use Terraform to provision the servers, then Ansible to configure them.

### IaC Best Practices

- **Version control everything** – treat IaC the same as application code with PRs and code reviews.
- **Use remote state** (Terraform) with locking to prevent concurrent modifications.
- **Separate environments** into distinct state files or workspaces to isolate blast radius.
- **Never hardcode secrets** – use Vault, AWS Secrets Manager, or environment variables.
- **Use modules and roles** to avoid duplication and enforce consistency.
- **Run plan/check before apply** – review diffs in CI before merging infrastructure changes.
- **Tag all resources** with environment, owner, and project for cost attribution and auditing.
- **Test infrastructure code** with tools like Terratest (Go) or Molecule (Ansible).
