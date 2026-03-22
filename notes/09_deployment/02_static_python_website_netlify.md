
## Deploying Static Python Website on Netlify

Netlify allows you to easily deploy and manage static websites. A Python-based static site generator like Pelican, MkDocs, or Frozen-Flask produces HTML files that Netlify serves through its global CDN.

```
 +-----------+      push       +------------+     build      +----------+
 |           | -------------> |            | ------------> |          |
 | Git Repo  |                | Netlify    |               | CDN Edge |
 | (GitHub,  |                | Build Env  |               | Nodes    |
 |  GitLab)  |                | (Python +  |               | (Global) |
 |           | <------------- | pip)       | <------------ |          |
 +-----------+   webhook      +------------+   deploy       +----------+
                                                                |
                                                                |
                                                          +-----+-----+
                                                          |  End Users |
                                                          +-----------+
```

- **Repo** holds your source files, templates, and configuration.
- **Build** is the step where Netlify runs your Python generator to produce static HTML.
- **CDN** distributes the output globally so users hit the closest edge node.

### Steps to Deploy

1. **Create** a Git repository containing your static Python website code and a `requirements.txt`:

```
# requirements.txt
pelican==4.9.1
markdown==3.6
```

2. **Sign** up at [netlify.com](https://www.netlify.com/) if you don't have an account.

3. **Connect** your repository by clicking "New site from Git" in the Netlify dashboard, choosing your Git provider, and selecting the repository.

4. **Configure** build settings in the dashboard or, preferably, through a `netlify.toml` file at the root of your repo:

```toml
[build]
  command = "pip install -r requirements.txt && pelican content -s publishconf.py"
  publish = "output"

[build.environment]
  PYTHON_VERSION = "3.11"
```

- **command** tells Netlify how to install dependencies and generate the site.
- **publish** points to the directory that contains the generated HTML files.

5. **Deploy** by clicking "Deploy site" or simply pushing a commit to the linked branch.

6. **Domain** settings let you use a custom domain or the auto-generated `*.netlify.app` subdomain:

   - **Navigate** to "Domain settings" in the site dashboard.
   - **Add** a custom domain and update DNS records with your registrar (CNAME or Netlify DNS).
   - **Wait** for DNS propagation, which can take a few minutes to 48 hours.

7. **SSL/TLS** is provisioned automatically through Let's Encrypt once DNS is verified:

   - **Check** the "SSL/TLS certificate" section in domain settings.
   - **Force** HTTPS by enabling the option so all HTTP traffic is redirected.

### Continuous Deployment

- **Trigger** builds automatically whenever you push to the production branch (usually `main`).
- **Configure** the branch in `netlify.toml` or in the dashboard under "Build & deploy → Branches":

```toml
[context.production]
  command = "pelican content -s publishconf.py"

[context.branch-deploy]
  command = "pelican content -s pelicanconf.py"
```

- **Limit** which branches trigger deploys to avoid unnecessary builds for feature branches.

### Preview Deploys

- **Open** a pull request against the production branch and Netlify creates a unique preview URL.
- **Share** the preview link with reviewers so they can see the exact changes before merging.
- **Review** the deploy log in the Netlify dashboard if the preview build fails.
- **Merge** the pull request once the preview looks correct, and the production site updates automatically.

### Environment Variables

- **Set** variables in the Netlify dashboard under **Site settings → Environment variables**:

```
PELICAN_SITEURL    = https://example.com
ANALYTICS_ID       = UA-XXXXXXXX-X
```

- **Reference** them in your build command or Python config:

```python
import os
SITEURL = os.environ.get("PELICAN_SITEURL", "http://localhost:8000")
```

- **Scope** variables to specific deploy contexts (production, branch-deploy, deploy-preview) in `netlify.toml`:

```toml
[context.production.environment]
  PELICAN_SITEURL = "https://example.com"

[context.deploy-preview.environment]
  PELICAN_SITEURL = "https://preview.example.com"
```

### Rollback

- **Open** the "Deploys" tab in the Netlify dashboard to see a list of every previous deploy.
- **Click** on any successful deploy and select "Publish deploy" to instantly revert the live site.
- **Understand** that rollbacks are instant because Netlify keeps the built output of every deploy.
- **Automate** rollback by pinning a known-good commit with a deploy lock through the Netlify CLI:

```bash
npm install -g netlify-cli
netlify deploy --prod --dir=output
```

### Monitoring and Troubleshooting

- **Check** build logs in the Netlify dashboard whenever a deploy fails.
- **Enable** Netlify Analytics (paid) or integrate a lightweight tool like Plausible for traffic insights.
- **Inspect** HTTP headers and redirect rules using `curl -I https://your-site.netlify.app`.
- **Add** a `_redirects` file or redirect rules in `netlify.toml` for custom routing:

```toml
[[redirects]]
  from = "/old-path"
  to = "/new-path"
  status = 301
```

With these steps and configurations, you can deploy, preview, and manage a static Python website on Netlify with full continuous deployment support.
