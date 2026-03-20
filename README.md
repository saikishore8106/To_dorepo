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

## 📚 Key Concepts Demonstrated

1. **REST API Design** — Modular routers mapping to standard HTTP GET/POST/PUT/DELETE methods.
2. **JWT Authentication** — Stateless, secure OAuth2 token exchange with hashed passwords (`passlib/bcrypt`).
3. **Database Relationships** — One-to-many relationship linking `Users` and `Tasks` using SQLAlchemy ORM.
4. **Python Automation** — `APScheduler` background job that automatically scans for overdue tasks every 60 minutes.
5. **Modern Frontend** — React hook state management, Axios global interceptors (for auto-attaching tokens), and protected routing.
6. **Containerization** — Multi-stage builds in Dockerfiles separating frontend build steps from serving steps for an ultra-lean final image.
