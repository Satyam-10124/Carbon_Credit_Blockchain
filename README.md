# Joyo - Carbon Credit & Plant Verification System

Blockchain-based carbon credit verification with AI plant recognition, health monitoring, and Coinbase x402 payments.

**Production API:** https://joyo-cc-production.up.railway.app

---

## Repo Structure

```
.
├── api_joyo_core.py           # Main FastAPI application (production)
├── database_postgres.py       # PostgreSQL database layer
├── enhanced_ai_validator.py   # GPT-4 fraud detection engine
├── ai_validator.py            # Fallback AI validator
├── algorand_nft.py            # Algorand ARC-69 NFT minting
├── x402_real.py               # Coinbase x402 payment protocol
├── gps_validator.py           # GPS + weather verification
├── gesture_verification.py    # Biometric gesture capture
├── unified_main.py            # CLI for full 7-stage pipeline
├── joyo_ai_services/          # AI modules (recognition, health, geo)
├── frontend/                  # Next.js 14 web app
├── tests/                     # E2E and unit tests
├── scripts/                   # Shell scripts (run, deploy, demo)
├── docs/                      # Extended documentation
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Production container
├── railway.json               # Railway deployment config
├── start.sh                   # Production entrypoint
├── setup.sh                   # Local dev setup
└── .env.example               # Environment variable template
```

---

## Features

- **7-Stage Verification Pipeline** - Plant recognition, health scan, GPS + weather, biometric gesture, GPT-4 fraud detection, report generation, Algorand NFT minting
- **AI Services** - GPT-4o Vision for plant ID (95% accuracy) and health diagnosis (85+ score), GPT-4 for fraud detection
- **Blockchain** - ARC-69 NFTs on Algorand with full metadata (species, GPS, biometric hash, carbon offset)
- **Payments** - Coinbase x402 protocol for USDC micropayments on Base L2
- **Points & Rewards** - Gamified system (30 pts for planting, 5 pts for watering/scans, streaks)
- **Real-time Weather** - OpenWeather API for geo cross-validation

---

## Architecture

```
User (Frontend / API client)
  │
  ▼
FastAPI (api_joyo_core.py)
  ├── joyo_ai_services/     → GPT-4o Vision (plant recognition + health)
  ├── enhanced_ai_validator  → GPT-4 (fraud detection)
  ├── gps_validator          → OpenWeather API (geo verification)
  ├── gesture_verification   → Biometric capture
  ├── algorand_nft           → Algorand blockchain (NFT minting)
  ├── x402_real              → Coinbase x402 (payments)
  └── database_postgres      → PostgreSQL (users, plants, points)
```

---

## Quick Start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your API keys
```

### Run the API server locally

```bash
uvicorn api_joyo_core:app --reload --port 8000
```

### Run the CLI verification pipeline

```bash
python3 unified_main.py
```

### Run helper scripts

```bash
./scripts/run_unified_system.sh   # full 7-stage pipeline
./scripts/run_real_x402.sh        # x402 payment API
```

---

## Environment Variables

```bash
# Required
OPENAI_API_KEY="sk-..."              # GPT-4o Vision + GPT-4
ALGORAND_PRIVATE_KEY="..."           # Algorand wallet
OPENWEATHER_API_KEY="..."            # Weather data
DATABASE_URL="postgresql://..."      # PostgreSQL connection

# Optional (x402 payments)
PAYMENT_ADDRESS="0x742d35..."        # USDC payment address
X402_FACILITATOR_URL="https://facilitator.base.org"
```

---

## API Endpoints

Full interactive docs at `/docs` on the running server.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check (DB, AI, Algorand status) |
| GET | `/plants/catalog` | List 8 available plant species |
| POST | `/plants/register` | Register a new plant (30 pts) |
| GET | `/plants/{id}` | Get plant details |
| GET | `/plants/user/{user_id}` | List user's plants |
| POST | `/plants/{id}/planting-photo` | Upload photo + AI recognition |
| POST | `/plants/{id}/health-scan` | AI health diagnosis (5 pts) |
| POST | `/plants/{id}/water` | Log watering (5 pts + streak) |
| POST | `/plants/{id}/remedy-apply` | Record remedy application |
| POST | `/plants/{id}/protection` | Record plant protection (10 pts) |
| GET | `/plants/{id}/verification-report` | Full verification report |
| GET | `/users/{id}/points` | User point balance |
| GET | `/users/{id}/history` | User activity history |
| POST | `/users/{id}/biometric` | Store biometric signature |
| GET | `/weather?lat=X&lon=Y` | Real-time weather data |
| POST | `/verify/fraud-check` | GPT-4 fraud detection |
| POST | `/verify/complete` | Full 7-stage verification pipeline |
| POST | `/nft/mint` | Mint carbon credit NFT on Algorand |
| GET | `/stats` | System-wide statistics |
| GET | `/stats/csr` | CSR dashboard for sponsors |

---

## Testing

```bash
# Run the full E2E test suite against the live server
python3 tests/test_live_server.py

# Run other test suites
python3 tests/test_complete_e2e.py
python3 tests/test_complete_system.py
python3 tests/test_nft_minting.py
```

---

## Deployment

Currently deployed on **Railway** at https://joyo-cc-production.up.railway.app

```bash
# Docker
docker build -t joyo .
docker run -p 8000:8000 --env-file .env joyo

# Railway
./scripts/deploy.sh
```

See `docs/DEPLOYMENT.md` for full production instructions.

---

## Documentation

Extended docs live in `docs/`:

| Document | Description |
|----------|-------------|
| `docs/DEPLOYMENT.md` | Production deployment guide |
| `docs/FRONTEND_INTEGRATION_GUIDE.md` | Frontend integration reference |
| `docs/UNIFIED_SYSTEM.md` | 7-stage pipeline specification |
| `docs/API_ENDPOINTS.md` | API endpoint details |
| `docs/X402_IMPLEMENTATION_SUMMARY.md` | x402 payment protocol |
| `docs/GESTURE_GUIDE.md` | Biometric gesture system |
| `docs/ENHANCED_FEATURES.md` | Advanced features |
| `docs/POSTGRESQL_MIGRATION.md` | Database migration guide |
| `docs/JOYO_QUICKSTART.md` | Quickstart walkthrough |
| `docs/ETH_BUENOS_AIRES_PITCH_DECK.md` | Pitch deck |
| `joyo_ai_services/README.md` | AI services API reference |

---

## Tech Stack

- **Backend:** Python 3.10+, FastAPI, PostgreSQL
- **AI:** OpenAI GPT-4o Vision, GPT-4
- **Blockchain:** Algorand (py-algorand-sdk), ARC-69 NFTs
- **Payments:** Coinbase x402, USDC on Base L2
- **Frontend:** Next.js 14, React 18, TailwindCSS
- **Infra:** Railway, Docker

---

## License

MIT
