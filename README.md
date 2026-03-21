# 🐍 FullStack Python — Task Manager Pro

A **full-stack project** designed to cover all key skills for a Senior Python Developer role.

---

## 🛠️ Tech Stack
- **Backend**: Python 3, FastAPI, PostgreSQL, SQLAlchemy ORM, JWT Auth, APScheduler (Background Jobs)
- **Frontend**: React, Vite, Axios, React Router, Custom CSS (Glassmorphism & Dark Mode)
- **DevOps**: Docker, Docker Compose, GitHub Actions (CI/CD pipeline configuration)

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

# Install requirements (includes the passlib+bcrypt version fix!)
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

### One-time AWS setup (do this once)

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
6. Attach the following inline policy (replace `REGION` and `ACCOUNT_ID`):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "ssm:SendCommand",
           "ssm:GetCommandInvocation",
           "ssm:ListCommandInvocations"
         ],
         "Resource": [
           "arn:aws:ssm:REGION::document/AWS-RunShellScript",
           "arn:aws:ec2:REGION:ACCOUNT_ID:instance/*",
           "arn:aws:ssm:REGION:ACCOUNT_ID:*"
         ]
       }
     ]
   }
   ```
7. Name the role (e.g. `github-actions-deploy`) and save.
   Copy the **Role ARN** — you will need it in step 4.

#### Step 3 — Prepare the EC2 instance

The EC2 instance needs Docker, Docker Compose, the SSM agent, and the repo cloned.

```bash
# On your EC2 instance (Amazon Linux 2023 / Ubuntu 22.04)

# 1. Install SSM agent (already installed on Amazon Linux 2; Ubuntu may need it)
sudo snap install amazon-ssm-agent --classic   # Ubuntu
# or:
sudo yum install -y amazon-ssm-agent && sudo systemctl enable --now amazon-ssm-agent

# 2. Install Docker
sudo yum install -y docker || sudo apt-get install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user   # so the ssm user can run docker

# 3. Install Docker Compose plugin
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# 4. Attach an IAM instance profile with AmazonSSMManagedInstanceCore
#    (do this in the EC2 console: Actions → Security → Modify IAM role)

# 5. Clone the repo
sudo mkdir -p /home/ec2-user/app
sudo chown ec2-user:ec2-user /home/ec2-user/app
git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git /home/ec2-user/app
```

> **IAM instance profile for SSM** — create a role with the `AmazonSSMManagedInstanceCore` managed policy and attach it to the EC2 instance.

#### Step 4 — Add GitHub repository secrets

Go to your GitHub repo → **Settings → Secrets and variables → Actions** → **New repository secret**:

| Secret name | Value |
|---|---|
| `AWS_ROLE_ARN` | `arn:aws:iam::ACCOUNT_ID:role/github-actions-deploy` |
| `AWS_REGION` | e.g. `us-east-1` |
| `EC2_INSTANCE_ID` | e.g. `i-0abc123def456789` |

That's it. Push to `main` and the workflow runs automatically.

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
