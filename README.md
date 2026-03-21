# 🐍 FullStack Python — Task Manager Pro

A **full-stack project** designed to cover all key skills for a Senior Python Developer role.

---

## 🛠️ Tech Stack
- **Backend**: Python 3, FastAPI, PostgreSQL, SQLAlchemy ORM, JWT Auth, APScheduler (Background Jobs)
- **Frontend**: React, Vite, Axios, React Router, Custom CSS (Glassmorphism & Dark Mode)
- **DevOps**: Docker, Docker Compose, GitHub Actions (CI/CD), AWS EC2 + SSM (zero SSH-key deploy)

---

## 🚀 How to Run the Project (Two Options)

You can run the project either entirely using Docker, or manually process-by-process.

### Option 1: The Easy Way (Docker Compose)
*Ensure Docker Desktop is open and running on your Mac before executing this!*

```bash
cd fullstackpython
docker-compose up --build
```
* **Frontend UI**: http://127.0.0.1:5173
* **Backend API**: http://127.0.0.1:8001
* **API Swagger Docs**: http://127.0.0.1:8001/docs
* **PostgreSQL DB**: `localhost:5433`

*(To stop the containers later, press `Ctrl+C` or run `docker-compose down`)*

---

### Option 2: The Manual Way (Local Development)

If you prefer to run the components manually for development, follow these three steps in **three separate terminal windows**.

#### 1️⃣ Database (Terminal 1)
We'll spin up a PostgreSQL database using Docker, but map it to port **5433** to avoid conflicting with any existing databases on your Mac.
```bash
docker run -d --name taskdb -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=taskdb -p 5433:5432 postgres:16
```

#### 2️⃣ Backend API (Terminal 2)
Navigate to the backend, activate a virtual environment, install dependencies, and start the Uvicorn server on port **8001**.
```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --reload --port 8001
```

#### 3️⃣ Frontend UI (Terminal 3)
Navigate to the frontend, install Node.js dependencies, and run the Vite dev server.
```bash
cd frontend

# Install Node modules
npm install

# Start the React app
npm run dev
```
*(Open http://127.0.0.1:5173 in your web browser)*

---

## 🧪 Running Tests

Tests use an in-memory SQLite database so no PostgreSQL is needed.

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v --tb=short
```

> **Note:** `pytest.ini` at the backend root sets `pythonpath = .` so pytest can resolve the `app` module when run from the `backend/` directory.

---

## CI/CD — GitHub Actions + AWS EC2 (No SSH Keys)

Pushing to `main` automatically triggers a GitHub Actions workflow that deploys the app on your EC2 instance via **AWS SSM Session Manager** — no SSH keys, no long-lived AWS credentials stored anywhere.

### How it works

```
git push origin main
        │
        ▼
GitHub Actions (ubuntu-latest)
  1. Checkout code
  2. Authenticate to AWS via GitHub OIDC  ← no stored AWS keys
  3. aws ssm send-command → EC2           ← no SSH key
        │
        ▼ (inside EC2)
  4. git pull origin main
  5. docker compose up --build -d
```

---

### One-time AWS Setup (do this once)

#### Step 1 — Add GitHub as an OIDC identity provider in AWS IAM

1. Open **IAM → Identity providers → Add provider**
2. Provider type: **OpenID Connect**
3. Provider URL: `https://token.actions.githubusercontent.com` → click **Get thumbprint**
4. Audience: `sts.amazonaws.com`
5. Click **Add provider**

#### Step 2 — Create an IAM role for GitHub Actions

1. **IAM → Roles → Create role**
2. Trusted entity: **Web identity**
3. Identity provider: `token.actions.githubusercontent.com`
4. Audience: `sts.amazonaws.com`
5. Add a condition to lock it to your repo:
   ```
   token.actions.githubusercontent.com:sub  StringLike  repo:YOUR_GITHUB_USERNAME/YOUR_REPO_NAME:ref:refs/heads/main
   ```
6. Attach an inline policy (replace `REGION` and `ACCOUNT_ID`):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "ssm:SendCommand"
         ],
         "Resource": [
           "arn:aws:ec2:REGION:ACCOUNT_ID:instance/*",
           "arn:aws:ssm:REGION::document/AWS-RunShellScript"
         ]
       },
       {
         "Effect": "Allow",
         "Action": [
           "ssm:GetCommandInvocation",
           "ssm:ListCommandInvocations"
         ],
         "Resource": "*"
       }
     ]
   }
   ```
   > Name the inline policy using only alphanumeric characters and hyphens (e.g. `github-actions-ssm-policy`).

7. Name the role `github-actions-deploy` and save. Copy the **Role ARN** — you need it in Step 4.

> **Trust policy gotcha:** The `sub` condition must use the short repo format — `repo:owner/repo-name:ref:refs/heads/main` — not a full GitHub URL.

#### Step 3 — Prepare the EC2 instance

The EC2 instance needs Docker, the SSM agent running, an IAM instance profile, and the repo cloned.

**3a. Create an IAM instance profile for EC2**

1. **IAM → Roles → Create role**
2. Trusted entity: **AWS service → EC2**
3. Attach managed policy: `AmazonSSMManagedInstanceCore`
4. Name it `ec2-ssm-role` and save

**3b. Attach the role to your EC2 instance**

1. **EC2 → Instances → select your instance**
2. **Actions → Security → Modify IAM role**
3. Select `ec2-ssm-role` → **Update IAM role**

**3c. Install and start the SSM agent on Ubuntu**

```bash
# Install SSM agent (Ubuntu)
sudo snap install amazon-ssm-agent --classic
sudo systemctl enable snap.amazon-ssm-agent.amazon-ssm-agent.service
sudo systemctl start snap.amazon-ssm-agent.amazon-ssm-agent.service

# Verify it is running
sudo systemctl status snap.amazon-ssm-agent.amazon-ssm-agent.service
```

After starting, wait ~2 minutes then verify the instance appears in **Systems Manager → Fleet Manager**.

**3d. Install Docker and Docker Compose**

```bash
# Install Docker
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl enable --now docker

# Install Docker Compose plugin
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
```

**3e. Clone the repo**

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git /home/ubuntu/app
```

#### Step 4 — Add GitHub repository secrets

Go to your GitHub repo → **Settings → Secrets and variables → Actions** → **New repository secret**:

| Secret name | Value | Notes |
|---|---|---|
| `AWS_ROLE_ARN` | `arn:aws:iam::ACCOUNT_ID:role/github-actions-deploy` | |
| `AWS_REGION` | e.g. `us-east-2` | Use the **region** (e.g. `us-east-2`), not the availability zone (e.g. `us-east-2c`) |
| `EC2_INSTANCE_ID` | e.g. `i-0abc123def456789` | Found in EC2 console |

> **Common mistake:** Setting `AWS_REGION` to an availability zone (like `us-east-2c`) instead of the region (`us-east-2`) causes a DNS failure when the action tries to reach `sts.us-east-2c.amazonaws.com`.

That's it. Push to `main` and the workflow runs automatically.

---

### Accessing the deployed app

Once the workflow succeeds:

| Service | URL |
|---|---|
| Frontend UI | `http://<EC2_PUBLIC_DNS>:5173` |
| Backend API | `http://<EC2_PUBLIC_DNS>:8001` |
| API Docs | `http://<EC2_PUBLIC_DNS>:8001/docs` |

Make sure your EC2 **Security Group inbound rules** allow traffic on ports `5173` and `8001`.

---

### Troubleshooting common deploy errors

| Error | Cause | Fix |
|---|---|---|
| `ENOTFOUND sts.***.amazonaws.com` | `AWS_REGION` secret is wrong or is an AZ not a region | Set `AWS_REGION` to the region only, e.g. `us-east-2` |
| `Could not assume role with OIDC` | IAM trust policy `sub` contains full GitHub URL | Use `repo:owner/repo-name:ref:refs/heads/main` (no URL, no `.git`) |
| `AccessDeniedException: ssm:SendCommand` | GitHub Actions IAM role missing SSM permissions | Add the inline policy from Step 2 above |
| `InvalidInstanceId` | EC2 instance not registered with SSM | Attach `ec2-ssm-role` with `AmazonSSMManagedInstanceCore` to the instance and restart the SSM agent |
| `fatal: $HOME not set` | SSM runs commands as root without a full environment | `export HOME=/root` is set at the start of the deploy script |
| `fatal: detected dubious ownership` | SSM runs as root but repo is owned by `ubuntu` | `git config --global --add safe.directory /home/ubuntu/app` is set in the deploy script |

---

### Checking a deployment

```bash
# View the latest GitHub Actions run in your browser, or via CLI:
gh run list --workflow=deploy.yml
gh run view <run-id> --log
```

---

## 📚 Key Concepts Demonstrated

1. **REST API Design** — Modular routers mapping to standard HTTP GET/POST/PUT/DELETE methods.
2. **JWT Authentication** — Stateless, secure OAuth2 token exchange with hashed passwords (`passlib/bcrypt`).
3. **Database Relationships** — One-to-many relationship linking `Users` and `Tasks` using SQLAlchemy ORM.
4. **Python Automation** — `APScheduler` background job that automatically scans for overdue tasks every 60 minutes.
5. **Modern Frontend** — React hook state management, Axios global interceptors (for auto-attaching tokens), and protected routing.
6. **Containerization** — Multi-stage builds in Dockerfiles separating frontend build steps from serving steps for an ultra-lean final image.
7. **Zero-credential CI/CD** — GitHub OIDC + AWS SSM replaces stored AWS keys and SSH keys entirely.
