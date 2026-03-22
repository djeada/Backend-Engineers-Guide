
## Deploying CentOS VM on Digital Ocean

Digital Ocean provides cloud-based virtual machines called Droplets that let you deploy and manage CentOS servers. The overall flow looks like this:

```
 +-------------+         SSH (port 22)         +----------------------+
 |             | ---------------------------->  |                      |
 | Local       |                                |  Digital Ocean       |
 | Machine     |                                |  Droplet (CentOS)   |
 |             | <----------------------------  |                      |
 +-------------+        Response               +----------------------+
                                                    |    |    |
                                                    |    |    |
                                                +---+  +---+  +---+
                                                |Web|  |DB |  |App|
                                                +---+  +---+  +---+
                                               :80/443  :5432  :8080
```

- **Local** is your development machine where you write code and manage deployments.
- **Droplet** is the CentOS virtual machine running in a Digital Ocean datacenter.
- **Services** such as a web server, database, and application run inside the droplet.

### Step 1: Sign Up and Log In

- **Navigate** to [digitalocean.com](https://www.digitalocean.com/) and create an account.
- **Verify** your email address and add a payment method.
- **Log** in to the Digital Ocean dashboard.

### Step 2: Generate an SSH Key

- **Open** a terminal on your local machine and generate a key pair:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

- **Accept** the default file location (`~/.ssh/id_ed25519`) or specify a custom path.
- **Copy** the public key so it can be added to Digital Ocean:

```bash
cat ~/.ssh/id_ed25519.pub
```

- **Paste** the public key into the Digital Ocean dashboard under **Settings → Security → SSH Keys**.

### Step 3: Create a New Droplet

- **Click** "Create" and select "Droplets" from the dropdown.
- **Choose** CentOS as the distribution and pick the desired version (e.g., CentOS Stream 9).
- **Select** a droplet size based on your workload (CPU, RAM, and storage).
- **Pick** a datacenter region closest to your target audience to minimize latency.
- **Enable** options like monitoring, automatic backups, and private networking as needed.
- **Assign** a meaningful hostname (e.g., `prod-api-01`) and click "Create Droplet."

### Step 4: Initial Server Access

- **Note** the public IP address shown in the dashboard after the droplet is provisioned.
- **Connect** to the droplet over SSH:

```bash
ssh root@YOUR_DROPLET_IP
```

- **Confirm** the fingerprint on the first connection and you will land in a root shell.

### Step 5: Create a Non-Root User

- **Add** a new user and grant it sudo privileges:

```bash
adduser deploy
passwd deploy
usermod -aG wheel deploy
```

- **Copy** your SSH key to the new user so you can log in without a password:

```bash
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy
```

- **Test** the new user by opening a separate terminal and running `ssh deploy@YOUR_DROPLET_IP`.

### Step 6: Update Packages and Configure Firewall

- **Update** all installed packages to their latest versions:

```bash
sudo dnf update -y
```

- **Install** common tools you will need:

```bash
sudo dnf install -y vim git curl wget
```

- **Enable** the firewall and allow only the ports your services require:

```bash
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

### Step 7: Install and Configure Services

- **Install** a web server such as Nginx:

```bash
sudo dnf install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

- **Verify** the server is running by visiting `http://YOUR_DROPLET_IP` in a browser.
- **Deploy** your application code by cloning a repository or using `scp`:

```bash
git clone https://github.com/your-org/your-app.git /var/www/your-app
```

- **Configure** Nginx to reverse-proxy traffic to your application on its internal port.

### Step 8: Secure SSH Access

- **Disable** root login and password authentication by editing `/etc/ssh/sshd_config`:

```
PermitRootLogin no
PasswordAuthentication no
```

- **Restart** the SSH daemon to apply changes:

```bash
sudo systemctl restart sshd
```

- **Confirm** that you can still log in with your non-root user before closing the root session.

### Post-Deployment

#### Monitoring

- **Enable** the Digital Ocean monitoring agent during droplet creation or install it manually:

```bash
curl -sSL https://repos.insights.digitalocean.com/install.sh | sudo bash
```

- **Set** up alerts in the dashboard for CPU, memory, and disk usage thresholds.
- **Consider** tools like `htop`, `journalctl`, or Prometheus for deeper insight into resource usage.

#### Backups

- **Turn** on weekly backups in the Digital Ocean dashboard (adds 20% to the droplet cost).
- **Schedule** application-level backups for databases and uploaded files:

```bash
pg_dump mydb > /backups/mydb_$(date +%F).sql
```

- **Store** critical backups off-site using Digital Ocean Spaces or another object storage provider.

#### Security Hardening

- **Install** and enable automatic security updates:

```bash
sudo dnf install -y dnf-automatic
sudo systemctl enable --now dnf-automatic-install.timer
```

- **Run** `sudo dnf needs-restarting -r` periodically to check if a reboot is required after updates.
- **Use** Fail2Ban to protect against brute-force SSH attempts:

```bash
sudo dnf install -y epel-release
sudo dnf install -y fail2ban
sudo systemctl enable --now fail2ban
```

- **Review** open ports regularly with `sudo firewall-cmd --list-all` and remove any that are no longer needed.
