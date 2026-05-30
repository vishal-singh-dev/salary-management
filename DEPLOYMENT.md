# Deployment

This project uses three deployed pieces:

```text
Vercel frontend -> Render HTTPS proxy -> AWS EC2 backend -> Neon PostgreSQL
```

## Frontend

The frontend is a Next.js app deployed on Vercel.

The browser loads the app from an HTTPS URL such as:

```text
https://salary-management.vercel.app
```

Set this Vercel environment variable:

```text
PUBLIC_API_BASE_URL=https://<render-proxy>.onrender.com/api
```

The frontend API client sends requests to that base URL.

## Backend

The backend is a FastAPI app packaged as a Docker image and running on an AWS EC2 instance.

The backend container exposes:

```text
http://<ec2-public-ip>:8000
```

It uses environment variables such as:

```text
ENVIRONMENT=production
DATABASE_URL=<neon-postgres-url>
CORS_ORIGINS=["*"]
SQL_ECHO=false
SEED_EMPLOYEE_COUNT=10000
SEED_RANDOM_SEED=2026
SEED_BATCH_SIZE=1000
```

On startup, the backend Docker image runs:

```text
Alembic migrations -> bootstrap seed -> Uvicorn API server
```

The bootstrap seed ensures exchange rates and master data exist. Employee demo data is created only
when the employee table is empty.

## Proxy

The proxy is a small Node/Express app in `proxy/`, deployed as a Render Web Service.

Render provides an HTTPS URL:

```text
https://<render-proxy>.onrender.com
```

The proxy forwards:

```text
https://<render-proxy>.onrender.com/api/*
-> http://<ec2-public-ip>:8000/api/v1/*
```

and:

```text
https://<render-proxy>.onrender.com/health
-> http://<ec2-public-ip>:8000/health
```

Render settings:

```text
Root Directory: proxy
Build Command: npm install
Start Command: npm start
```

Render environment variables:

```text
BACKEND_BASE_URL=http://<ec2-public-ip>:8000
FRONTEND_ORIGIN=https://<vercel-frontend>.vercel.app
NODE_VERSION=22
```

## Why The Proxy Is Needed

Vercel serves the frontend over HTTPS. Browsers block HTTPS pages from calling an HTTP backend
directly. This is called mixed-content blocking.

This fails in the browser:

```text
https://<vercel-frontend>.vercel.app
-> http://<ec2-public-ip>:8000
```

The Render proxy fixes that by keeping the browser request HTTPS:

```text
https://<vercel-frontend>.vercel.app
-> https://<render-proxy>.onrender.com
-> http://<ec2-public-ip>:8000
```

This is an MVP bridge. The cleaner long-term option is to put HTTPS directly on the backend with a
domain name, Nginx, and a Let's Encrypt certificate, or use a managed AWS HTTPS entrypoint.

## Verification

Backend from EC2:

```bash
curl http://localhost:8000/health
```

Backend from public internet:

```bash
curl http://<ec2-public-ip>:8000/health
```

Proxy:

```bash
curl https://<render-proxy>.onrender.com/health
curl "https://<render-proxy>.onrender.com/api/master-data?category=Currency"
```

Frontend:

```text
https://<vercel-frontend>.vercel.app
```

The frontend should load employees, dashboard data, and master-data dropdowns without mixed-content
errors in the browser console.
