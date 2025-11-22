# 🚀 Production Deployment Guide

Complete guide for deploying the Carbon Credit Blockchain System to production.

---

## 📋 Pre-Deployment Checklist

### ✅ Essential Requirements

- [ ] **Algorand MainNet account** with sufficient ALGO for transactions
- [ ] **OpenAI API key** with billing enabled
- [ ] **IPFS/Arweave account** for decentralized image storage
- [ ] **Domain name** for API (e.g., api.carboncredit.io)
- [ ] **SSL certificate** (Let's Encrypt recommended)
- [ ] **PostgreSQL database** for verification history
- [ ] **Redis instance** for caching
- [ ] **Monitoring setup** (Datadog, Sentry, etc.)

### 🔐 Security Requirements

- [ ] Secrets stored in environment variables (never in code)
- [ ] API rate limiting configured
- [ ] CORS properly restricted
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention
- [ ] DDoS protection (CloudFlare)
- [ ] Regular security audits

---

## 🏗️ Architecture Options

### Option 1: Railway (Simplest)

**Best for:** MVPs, small teams, <10k verifications/month

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Add environment variables
railway variables set ALGOD_URL=<mainnet-url>
railway variables set ALGO_MNEMONIC=<mainnet-mnemonic>
railway variables set OPENAI_API_KEY=<key>

# 5. Deploy
railway up
```

**Cost:** ~$5-20/month

### Option 2: AWS EC2 (Scalable)

**Best for:** Production, >10k verifications/month

#### Infrastructure:
- **EC2 Instance:** t3.medium (2 vCPU, 4GB RAM)
- **RDS PostgreSQL:** db.t3.micro
- **ElastiCache Redis:** cache.t3.micro
- **S3:** Image backup storage
- **CloudFront:** CDN for API
- **Route 53:** DNS management

**Cost:** ~$50-100/month

#### Setup:

```bash
# 1. Launch EC2 instance (Ubuntu 22.04)
# 2. SSH into instance
ssh -i key.pem ubuntu@<instance-ip>

# 3. Install dependencies
sudo apt update
sudo apt install python3.10 python3-pip nginx postgresql-client redis-tools

# 4. Clone repository
git clone <your-repo>
cd Carbon_Credit_Blockchain

# 5. Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Configure Nginx
sudo nano /etc/nginx/sites-available/carbon-credit

# Add configuration:
server {
    listen 80;
    server_name api.carboncredit.io;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 7. Enable site
sudo ln -s /etc/nginx/sites-available/carbon-credit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 8. Setup SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.carboncredit.io

# 9. Run API with systemd
sudo nano /etc/systemd/system/carbon-credit.service

# Add:
[Unit]
Description=Carbon Credit API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Carbon_Credit_Blockchain
Environment="PATH=/home/ubuntu/Carbon_Credit_Blockchain/venv/bin"
ExecStart=/home/ubuntu/Carbon_Credit_Blockchain/venv/bin/uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target

# 10. Start service
sudo systemctl daemon-reload
sudo systemctl enable carbon-credit
sudo systemctl start carbon-credit
```

### Option 3: Docker + Kubernetes (Enterprise)

**Best for:** Large scale, multiple regions, >100k verifications/month

See `Dockerfile` and `k8s/` directory below.

**Cost:** ~$500+/month

---

## 🐳 Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ALGOD_URL=${ALGOD_URL}
      - ALGO_MNEMONIC=${ALGO_MNEMONIC}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=postgresql://postgres:password@db:5432/carbon_credits
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: carbon_credits
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
```

**Deploy:**

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f api

# Scale workers
docker-compose up -d --scale api=4
```

---

## 🗄️ Database Setup

### PostgreSQL Schema

```sql
CREATE TABLE workers (
    id SERIAL PRIMARY KEY,
    worker_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE verifications (
    id SERIAL PRIMARY KEY,
    worker_id VARCHAR(50) REFERENCES workers(worker_id),
    trees_planted INTEGER NOT NULL,
    location VARCHAR(200),
    gps_coords VARCHAR(50),
    gesture_signature VARCHAR(64),
    ai_validation JSONB,
    image_url TEXT,
    transaction_id VARCHAR(100),
    asset_id BIGINT,
    carbon_offset_kg DECIMAL(10,2),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    verified_at TIMESTAMP
);

CREATE INDEX idx_worker_verifications ON verifications(worker_id, created_at DESC);
CREATE INDEX idx_status ON verifications(status);
CREATE INDEX idx_created_at ON verifications(created_at DESC);

CREATE TABLE fraud_alerts (
    id SERIAL PRIMARY KEY,
    worker_id VARCHAR(50),
    verification_id INTEGER REFERENCES verifications(id),
    alert_type VARCHAR(50),
    confidence DECIMAL(5,2),
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔧 Environment Variables (Production)

```bash
# Algorand (MainNet)
ALGOD_URL=https://mainnet-api.algonode.cloud
ALGO_MNEMONIC=<25-word mnemonic>  # CRITICAL: Use secrets manager
ALGOD_API_KEY=  # Optional for private node

# OpenAI
OPENAI_API_KEY=sk-...  # CRITICAL: Use secrets manager

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379

# IPFS/Storage
IPFS_API_URL=https://ipfs.infura.io:5001
IPFS_API_KEY=<key>
IPFS_API_SECRET=<secret>

# Application
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://app.carboncredit.io,https://admin.carboncredit.io

# Security
SECRET_KEY=<random-32-byte-hex>  # Generate with: openssl rand -hex 32
API_RATE_LIMIT=100  # requests per minute
JWT_EXPIRATION=3600  # seconds

# Monitoring
SENTRY_DSN=<sentry-url>
DATADOG_API_KEY=<key>
```

**Store secrets securely:**

```bash
# AWS Secrets Manager
aws secretsmanager create-secret --name ALGO_MNEMONIC --secret-string "<mnemonic>"

# Railway
railway variables set ALGO_MNEMONIC=<mnemonic>

# Kubernetes
kubectl create secret generic algo-secrets --from-literal=mnemonic=<mnemonic>
```

---

## 📊 Monitoring & Logging

### Setup Sentry (Error Tracking)

```python
# Add to main.py
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENVIRONMENT", "production"),
    traces_sample_rate=0.1
)
```

### Setup Prometheus (Metrics)

```python
# Add to api.py
from prometheus_client import Counter, Histogram, make_asgi_app

verification_counter = Counter('verifications_total', 'Total verifications')
verification_duration = Histogram('verification_duration_seconds', 'Verification duration')

# Mount metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

### Grafana Dashboards

**Key Metrics to Track:**
- Verifications per hour
- Success rate
- Average verification time
- NFT minting cost
- AI validation confidence
- Fraud detection rate
- API latency (p50, p95, p99)
- Error rate

---

## 🔄 CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python test_components.py

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        run: |
          npm install -g @railway/cli
          railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## 🧪 Load Testing

```bash
# Install locust
pip install locust

# Create locustfile.py
from locust import HttpUser, task, between

class CarbonCreditUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def validate_claim(self):
        self.client.post("/validate-claim", json={
            "trees_planted": 5,
            "location": "Test",
            "gps_coords": "0,0"
        })

# Run load test
locust -f locustfile.py --host=https://api.carboncredit.io
```

**Target Performance:**
- 100 concurrent users
- <500ms response time (p95)
- 0.01% error rate

---

## 💰 Cost Optimization

### Algorand Transactions
- Batch NFT minting (mint 10 at once)
- Use asset transfer instead of minting for duplicates
- Implement transaction queuing

### OpenAI API
- Cache validation results (Redis)
- Use GPT-4o-mini for simple checks
- Batch image analysis

### Infrastructure
- Auto-scaling based on traffic
- Spot instances for non-critical tasks
- CDN for static assets

**Expected Costs at Scale:**

| Volume | Algorand | OpenAI | Infrastructure | Total/Month |
|--------|----------|--------|----------------|-------------|
| 1k verifications | $2 | $10 | $20 | $32 |
| 10k verifications | $20 | $100 | $50 | $170 |
| 100k verifications | $200 | $1,000 | $500 | $1,700 |

---

## 🔒 Security Best Practices

1. **Never commit secrets** - Use `.gitignore` for `.env`
2. **Rotate keys monthly** - Especially Algorand mnemonics
3. **Use read-only API keys** where possible
4. **Implement rate limiting** - Prevent abuse
5. **Enable 2FA** on all admin accounts
6. **Regular security audits** - Quarterly reviews
7. **Backup Algorand keys** - Multiple secure locations
8. **Monitor for fraud patterns** - Daily AI analysis
9. **DDoS protection** - CloudFlare or similar
10. **Regular dependency updates** - Weekly `pip audit`

---

## 📱 Mobile App Integration

### React Native Example

```javascript
import axios from 'axios';

const API_URL = 'https://api.carboncredit.io';

async function verifyAndMint(data) {
  try {
    const response = await axios.post(`${API_URL}/verify`, {
      trees_planted: data.trees,
      location: data.location,
      gps_coords: data.gps,
      worker_id: data.workerId,
      image_url: data.imageUrl,
      verification_duration: 5
    });
    
    return response.data;
  } catch (error) {
    console.error('Verification failed:', error);
    throw error;
  }
}
```

---

## 🎓 Training Materials

### For Field Workers:
1. Video: "How to verify tree planting" (2 min)
2. Infographic: Proper hand gestures
3. FAQ: Common issues

### For Administrators:
1. Dashboard walkthrough
2. Fraud detection guide
3. Emergency procedures

---

## 📞 Support & Maintenance

### Monitoring Checklist (Daily)
- [ ] API uptime >99.9%
- [ ] Error rate <0.1%
- [ ] Algorand node responsive
- [ ] No fraud alerts
- [ ] Backup successful

### Weekly Tasks
- [ ] Review pending verifications
- [ ] Update fraud detection models
- [ ] Security patches
- [ ] Cost analysis

### Monthly Tasks
- [ ] Rotate API keys
- [ ] Full system audit
- [ ] Performance optimization
- [ ] Update documentation

---

## 🆘 Troubleshooting

### High Error Rate
```bash
# Check logs
docker-compose logs -f api | grep ERROR

# Check Algorand node
curl https://mainnet-api.algonode.cloud/v2/status

# Restart services
docker-compose restart api
```

### Slow Performance
```bash
# Check database queries
docker-compose exec db psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL

# Scale workers
docker-compose up -d --scale api=8
```

### NFT Minting Failed
- Check Algorand account balance
- Verify mnemonic is correct
- Ensure image URL <96 bytes
- Check network connectivity

---

## ✅ Go-Live Checklist

### 1 Week Before
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Backups configured
- [ ] Monitoring dashboards set up
- [ ] Documentation finalized

### 1 Day Before
- [ ] Final deployment to staging
- [ ] Smoke tests passed
- [ ] Team briefed
- [ ] Support tickets ready
- [ ] Rollback plan tested

### Launch Day
- [ ] Deploy to production
- [ ] Monitor for 4 hours
- [ ] Verify first real transaction
- [ ] Announce launch
- [ ] Celebrate! 🎉

---

**Need help? Open an issue or contact support@carboncredit.io**
