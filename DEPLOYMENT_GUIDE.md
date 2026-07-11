# Deployment Guide: Retail Policy Intelligence System

## Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ with pgvector extension
- Ollama (for local LLM, optional)

### Step 1: Backend Setup

```bash
cd RetailPolicyAssistant/

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m app.db_init

# Create .env file with required variables
cat > .env << 'EOF'
DATABASE_URL=postgresql://user:password@localhost:5432/retail_policy
OLLAMA_MODEL=phi3:mini
OLLAMA_BASE_URL=http://localhost:11434
LANGFUSE_PUBLIC_KEY=your_langfuse_key
LANGFUSE_SECRET_KEY=your_langfuse_secret
LANGFUSE_HOST=https://cloud.langfuse.com
JWT_SECRET_KEY=your-secret-key-change-in-production
EOF

# Start backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# The server will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
# Health check: http://localhost:8000/health
```

### Step 2: Frontend Setup

```bash
cd frontend-nextjs/

# Install dependencies
npm install

# Create .env.local file
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Start development server
npm run dev

# The app will be available at http://localhost:3000
```

### Step 3: Verification

```bash
# Test backend health
curl http://localhost:8000/health

# Test token generation
curl http://localhost:8000/token

# Test query endpoint (from frontend or using curl with token)
curl -X POST http://localhost:8000/ask \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is our data retention policy?"}'
```

---

## Production Deployment

### Architecture
```
┌─────────────────────────────────────────┐
│  Frontend (Next.js) - Port 3000         │
│  - Static files + React components      │
│  - API client with auth interceptor     │
└────────────┬────────────────────────────┘
             │ HTTPS/API
┌────────────▼────────────────────────────┐
│  Backend (FastAPI) - Port 8000          │
│  - Orchestrator + Agents                │
│  - Database queries                     │
│  - Observability/Tracing                │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  PostgreSQL + pgvector (Neon/AWS RDS)   │
│  - AIQuery, Vendor, AuditLog tables     │
│  - Policy document embeddings (pgvector)│
└─────────────────────────────────────────┘
```

### Step 1: Prepare Production Environment

#### 1a. Database (Neon PostgreSQL)
```sql
-- Create database
CREATE DATABASE retail_policy_prod;

-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Connection string
postgresql://user:password@your-neon-db.neon.tech/retail_policy_prod
```

#### 1b. Environment Variables
```bash
# Production .env
DATABASE_URL=postgresql://user:password@prod-db:5432/retail_policy_prod
OLLAMA_MODEL=phi3:mini
OLLAMA_BASE_URL=http://ollama-service:11434
LANGFUSE_PUBLIC_KEY=prod_pk_...
LANGFUSE_SECRET_KEY=prod_sk_...
LANGFUSE_HOST=https://cloud.langfuse.com
JWT_SECRET_KEY=use-strong-random-key-here
ENVIRONMENT=production
```

#### 1c. Ollama Setup (Optional)
```bash
# If using Ollama for LLM
docker run -d \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama:latest

# Pull model
curl http://localhost:11434/api/pull -d '{"name":"phi3:mini"}'
```

### Step 2: Backend Deployment (Docker)

#### Build Docker Image
```bash
cd RetailPolicyAssistant/

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Build image
docker build -t retail-policy-api:latest .

# Run container
docker run -d \
  --name retail-policy-api \
  -p 8000:8000 \
  --env-file .env \
  -e DATABASE_URL=${DATABASE_URL} \
  -e LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY} \
  -e LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY} \
  retail-policy-api:latest
```

### Step 3: Frontend Deployment (Vercel/AWS/Docker)

#### Option A: Vercel (Recommended for Next.js)
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
cd frontend-nextjs/
vercel --prod

# Set environment variables in Vercel dashboard
# NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

#### Option B: Docker
```bash
cd frontend-nextjs/

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine as runner

WORKDIR /app
ENV NODE_ENV production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"]
EOF

# Build and run
docker build -t retail-policy-web:latest .
docker run -d \
  --name retail-policy-web \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://api.yourdomain.com \
  retail-policy-web:latest
```

#### Option C: AWS EC2
```bash
# SSH into EC2 instance
ssh -i key.pem ec2-user@your-instance

# Install Node.js
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# Clone repo and deploy
git clone https://github.com/your-repo/retail-policy.git
cd retail-policy/frontend-nextjs/

npm install
npm run build

# Set environment and start
export NEXT_PUBLIC_API_URL=https://api.yourdomain.com
npm run start
```

### Step 4: Nginx Reverse Proxy

```bash
# Install Nginx
sudo apt-get install -y nginx

# Configure reverse proxy
cat > /etc/nginx/sites-available/retail-policy << 'EOF'
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:3000;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Backend API
    location /ask {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/retail-policy /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### Step 5: SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Step 6: Monitoring & Logging

#### Application Logging
```bash
# Backend logs
tail -f /var/log/retail-policy-api.log

# Frontend logs
tail -f /var/log/retail-policy-web.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

#### Uptime Monitoring
```bash
# Install Supervisor for process management
sudo apt-get install -y supervisor

# Configure backend service
cat > /etc/supervisor/conf.d/retail-policy-api.conf << 'EOF'
[program:retail-policy-api]
directory=/home/app/retail-policy/RetailPolicyAssistant
command=/home/app/retail-policy/RetailPolicyAssistant/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
user=app
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/retail-policy-api.log
EOF

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start retail-policy-api
```

#### Health Checks
```bash
# Automated health check script
cat > /usr/local/bin/health-check.sh << 'EOF'
#!/bin/bash
BACKEND=$(curl -s http://localhost:8000/health | jq .status)
FRONTEND=$(curl -s http://localhost:3000 | head -1)

if [ "$BACKEND" != '"healthy"' ]; then
  echo "ALERT: Backend health check failed"
  systemctl restart retail-policy-api
fi

if [ -z "$FRONTEND" ]; then
  echo "ALERT: Frontend health check failed"
  systemctl restart retail-policy-web
fi
EOF

chmod +x /usr/local/bin/health-check.sh

# Add cron job
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/health-check.sh") | crontab -
```

---

## Database Migrations

### Initial Setup
```bash
# Initialize database schema
python -m app.db_init

# Seed with sample data (optional)
python -m app.scripts.seed_database
```

### Backups
```bash
# PostgreSQL backup
pg_dump -h your-db.neon.tech -U postgres retail_policy_prod > backup.sql

# Restore
psql -h your-db.neon.tech -U postgres retail_policy_prod < backup.sql

# Automated daily backups (cron)
0 2 * * * pg_dump -h your-db.neon.tech -U postgres retail_policy_prod | gzip > /backups/retail_policy_$(date +\%Y\%m\%d).sql.gz
```

---

## Troubleshooting

### Common Issues

#### Backend Connection Error
```
Error: (psycopg2.OperationalError) could not translate host name "your-db" to address
```
**Fix**: Verify DATABASE_URL in .env and network connectivity

#### CORS Error in Frontend
```
Access to XMLHttpRequest blocked by CORS policy
```
**Fix**: Ensure CORS_ORIGINS in app/main.py includes frontend URL

#### Token Expiration
```
401 Unauthorized: Token expired
```
**Fix**: Token refresh is automatic; clear browser localStorage and reload

#### Ollama Not Found
```
Connection refused when calling Ollama
```
**Fix**: Start Ollama service or disable LLM features (fallback will be used)

### Performance Issues

#### Slow Dashboard Loading
**Solution**: Add database indexes
```sql
CREATE INDEX idx_aiquery_created_at ON ai_query(created_at DESC);
CREATE INDEX idx_aiquery_risk_level ON ai_query(risk_level);
CREATE INDEX idx_aiquery_route ON ai_query(route);
```

#### High Memory Usage
**Solution**: Reduce cache size in `app/core/cache.py`
```python
MAX_CACHE_ENTRIES = 1000  # Default 5000
```

#### Slow Query Responses
**Solution**: Enable RAG caching
```bash
# In .env
RAG_CACHE_ENABLED=true
RAG_CACHE_TTL=3600  # seconds
```

---

## Scaling for Production

### Horizontal Scaling
```bash
# Run multiple backend instances with load balancing
docker run -d --name api1 -p 8001:8000 retail-policy-api:latest
docker run -d --name api2 -p 8002:8000 retail-policy-api:latest
docker run -d --name api3 -p 8003:8000 retail-policy-api:latest

# Nginx upstream configuration
upstream backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
    keepalive 32;
}
```

### Caching Strategy
```bash
# Add Redis for distributed caching
docker run -d --name redis -p 6379:6379 redis:latest

# Update app configuration
REDIS_URL=redis://localhost:6379/0
CACHE_BACKEND=redis
```

### CDN for Static Assets
```bash
# CloudFront distribution for frontend assets
# Configure S3 bucket for static files
# Update frontend to use CDN URLs
```

---

## Security Checklist

- [ ] Environment variables not committed to git
- [ ] HTTPS/SSL certificates installed
- [ ] Database credentials rotated
- [ ] JWT secret key is strong (32+ characters)
- [ ] CORS whitelist configured correctly
- [ ] Rate limiting enabled
- [ ] PII detection active
- [ ] SQL injection protection verified
- [ ] Firewall rules configured (allow only necessary ports)
- [ ] Regular security updates applied
- [ ] Logs monitored for suspicious activity
- [ ] Backups encrypted and stored securely

---

## Monitoring & Metrics

### Key Metrics to Monitor
- Query success rate (target: ≥ 95%)
- Average latency (target: < 2000ms)
- P95 latency (target: < 3000ms)
- Error rate (target: < 5%)
- Escalation rate (track for quality)
- Cost per query (track for budget)

### Langfuse Dashboard
- Navigate to https://cloud.langfuse.com
- View query traces and performance
- Monitor LLM token usage
- Check agent execution details

---

## Support & Maintenance

### Regular Tasks
- [ ] Weekly: Review error logs
- [ ] Weekly: Check database growth
- [ ] Monthly: Audit access logs
- [ ] Monthly: Review system metrics
- [ ] Quarterly: Security scan
- [ ] Quarterly: Database optimization
- [ ] Annually: Disaster recovery test

### Contacts
- **Technical Support**: dev-team@example.com
- **Emergency Hotline**: +1-555-RETAIL
- **Escalation Manager**: compliance@example.com

---

**Last Updated**: 2026-07-11  
**Version**: 1.0  
**Next Review**: 2026-08-11

