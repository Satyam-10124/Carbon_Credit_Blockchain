# Joyo - Carbon Credit & Plant Verification System

Joyo tackles fraud in the global carbon credit market by combining real AI, biometric verification, and blockchain proof into a single platform. Users plant trees, verify them through a 7-stage AI pipeline, and mint immutable carbon credit NFTs on Algorand — all in under 2 seconds.

**Production API:** https://joyo-cc-production.up.railway.app
**Interactive Docs:** https://joyo-cc-production.up.railway.app/docs

---

## The Problem

The voluntary carbon credit market is plagued by fraud — fake plantings, duplicate claims, and unverifiable offsets. Traditional verification relies on manual audits that are slow, expensive, and easy to game.

## The Solution

Joyo replaces manual audits with an automated 7-stage verification pipeline:

1. **AI Plant Recognition** — GPT-4o Vision identifies the species from a photo (95% accuracy, 8 supported species)
2. **AI Health Diagnosis** — Scores plant health out of 100, detects diseases, suggests organic remedies
3. **GPS + Weather Cross-Check** — Validates planting location against real-time weather data from OpenWeather
4. **Biometric Gesture Verification** — Captures hand gesture signatures via MediaPipe to prove human presence
5. **AI Fraud Detection** — GPT-4 analyzes the full submission for inconsistencies and risk signals
6. **Report Generation** — Compiles all stage results into a comprehensive verification report
7. **NFT Minting** — Mints an ARC-69 carbon credit NFT on Algorand with full metadata baked in

The entire pipeline runs in **~1.5 seconds** for a single API call.

---

## What's Live and Working

Verified via E2E tests against production on Mar 20, 2026 — **19/21 endpoints passing (90.5%)**.

### As a user, you can:

**Register and track plants**
- Register a plant (bamboo, tulsi, neem, etc. — 8 species) with GPS coordinates and earn 30 points
- Upload a planting photo and get real-time AI species identification via GPT-4o Vision
- View plant details, list all your plants, and check your point balance anytime
- Record plant protection (netting, fencing) and earn 10 points

**Care for plants daily**
- Log daily watering with GPS proof, earn 5 points per watering, and build streaks
- Run AI health scans that return a health score (e.g. 85/100) with diagnosis and recommendations

**Get verified through the 7-stage pipeline (1.5 seconds)**
- Submit one request to `/verify/complete` and get back:
  - AI plant recognition — confirmed
  - AI health diagnosis — confirmed
  - GPS + live weather cross-check (e.g. 31C Mumbai) — confirmed
  - Biometric gesture signature — stored
  - GPT-4 fraud detection (risk=low, valid=true) — confirmed
  - Verification report — generated
  - Final status: **APPROVED**

**Earn blockchain proof**
- Mint a carbon credit NFT on Algorand with a real transaction ID (~6 seconds)
- NFT metadata includes species, GPS coordinates, biometric hash, health score, and carbon offset estimate

**View impact**
- System-wide stats dashboard for platform metrics
- CSR dashboard for corporate sponsors tracking their environmental contributions

---

## Architecture

```
User (Next.js frontend / API client)
  |
  v
FastAPI (api_joyo_core.py)
  |-- joyo_ai_services/       -> GPT-4o Vision (plant recognition + health)
  |-- enhanced_ai_validator    -> GPT-4 (fraud detection)
  |-- gps_validator            -> OpenWeather API (geo + weather verification)
  |-- gesture_verification     -> MediaPipe / TensorFlow.js (biometric capture)
  |-- algorand_nft             -> Algorand blockchain (ARC-69 NFT minting)
  |-- x402_real                -> Coinbase x402 protocol (USDC payments)
  +-- database_postgres        -> PostgreSQL (users, plants, points, history)
```

---

## Repo Structure

```
.
|-- api_joyo_core.py           # Main FastAPI application (production)
|-- database_postgres.py       # PostgreSQL database layer
|-- enhanced_ai_validator.py   # GPT-4 fraud detection engine
|-- ai_validator.py            # Fallback AI validator
|-- algorand_nft.py            # Algorand ARC-69 NFT minting
|-- x402_real.py               # Coinbase x402 payment protocol
|-- gps_validator.py           # GPS + weather verification
|-- gesture_verification.py    # Biometric gesture capture
|-- unified_main.py            # CLI for full 7-stage pipeline
|-- joyo_ai_services/          # AI modules (recognition, health, geo)
|-- frontend/                  # Next.js 14 web app
|-- tests/                     # E2E and unit tests
|-- scripts/                   # Shell scripts (run, deploy, demo)
|-- docs/                      # Extended documentation
|-- requirements.txt           # Python dependencies
|-- Dockerfile                 # Production container
|-- railway.json               # Railway deployment config
|-- start.sh                   # Production entrypoint
|-- setup.sh                   # Local dev setup
+-- .env.example               # Environment variable template
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
./scripts/run_joyo_demo.sh        # AI services demo
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
| GET | `/` | API info (name, version, available endpoints) |
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

Last test run (Mar 20, 2026): **19/21 passed, 90.5% pass rate, 19.1s total.**

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

## Tech Stack

- **Backend:** Python 3.10+, FastAPI, PostgreSQL
- **AI:** OpenAI GPT-4o Vision (plant ID + health), GPT-4 (fraud detection)
- **Blockchain:** Algorand (py-algorand-sdk), ARC-69 NFTs
- **Payments:** Coinbase x402 protocol, USDC on Base L2
- **Frontend:** Next.js 14, React 18, TailwindCSS, react-webcam
- **Biometrics:** MediaPipe, TensorFlow.js (hand gesture capture)
- **Weather:** OpenWeather API (real-time geo validation)
- **Infra:** Railway, Docker

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

---

## License

MIT
