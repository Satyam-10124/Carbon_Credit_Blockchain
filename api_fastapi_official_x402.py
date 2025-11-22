"""
Carbon Credit FastAPI with OFFICIAL Coinbase x402 Package
Uses the real x402 Python package from Coinbase (FastAPI version)
https://github.com/coinbase/x402/tree/main/examples/python/servers/fastapi
"""

import os
from typing import Dict, Any
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from datetime import datetime

# Import official x402 package
try:
    from x402.fastapi.middleware import require_payment
    from x402.types import TokenAmount, TokenAsset, EIP712Domain
    X402_AVAILABLE = True
except ImportError:
    print("⚠️  Official x402 package not installed!")
    print("   Install with: pip install x402")
    X402_AVAILABLE = False

from joyo_ai_services.plant_recognition import PlantRecognitionAI
from joyo_ai_services.plant_health import PlantHealthAI

# Import Algorand NFT minting
try:
    from algorand_nft import mint_carbon_credit_nft
    ALGORAND_AVAILABLE = True
except ImportError:
    print("⚠️  Algorand NFT module not available")
    ALGORAND_AVAILABLE = False

# Load environment
load_dotenv()

# Configuration
PAYMENT_ADDRESS = os.getenv("ADDRESS") or os.getenv("PAYMENT_ADDRESS", "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0")
NETWORK = "base-sepolia"  # Testnet (use "base" for mainnet)

# USDC Contract on Base Sepolia
USDC_BASE_SEPOLIA = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"

# Initialize FastAPI
app = FastAPI(
    title="Carbon Credit API with Official x402",
    description="Official Coinbase x402 protocol for carbon credit payments",
    version="2.0.0"
)

# Initialize AI services
plant_recognition = PlantRecognitionAI()
plant_health = PlantHealthAI()

# ============================================================================
# SETUP OFFICIAL x402 MIDDLEWARE
# ============================================================================

if X402_AVAILABLE:
    # Plant Verification API - $25 USDC
    app.middleware("http")(
        require_payment(
            path="/api/v1/verify-plant",
            price=TokenAmount(
                amount="25000000",  # 25 USDC (6 decimals)
                asset=TokenAsset(
                    address=USDC_BASE_SEPOLIA,
                    decimals=6,
                    eip712=EIP712Domain(name="USDC", version="2"),
                ),
            ),
            pay_to_address=PAYMENT_ADDRESS,
            network=NETWORK,
        )
    )
    
    # Health Scan API - $30 USDC
    app.middleware("http")(
        require_payment(
            path="/api/v1/health-scan",
            price=TokenAmount(
                amount="30000000",  # 30 USDC (6 decimals)
                asset=TokenAsset(
                    address=USDC_BASE_SEPOLIA,
                    decimals=6,
                    eip712=EIP712Domain(name="USDC", version="2"),
                ),
            ),
            pay_to_address=PAYMENT_ADDRESS,
            network=NETWORK,
        )
    )
    
    # Remedy Database API - $20 USDC
    app.middleware("http")(
        require_payment(
            path="/api/v1/remedy/*",
            price=TokenAmount(
                amount="20000000",  # 20 USDC (6 decimals)
                asset=TokenAsset(
                    address=USDC_BASE_SEPOLIA,
                    decimals=6,
                    eip712=EIP712Domain(name="USDC", version="2"),
                ),
            ),
            pay_to_address=PAYMENT_ADDRESS,
            network=NETWORK,
        )
    )
    
    # Premium/Carbon Credit endpoints - $100 USDC
    app.middleware("http")(
        require_payment(
            path="/api/v1/premium/*",
            price="$100",
            pay_to_address=PAYMENT_ADDRESS,
            network=NETWORK,
        )
    )
    
    print("✅ Official x402 middleware configured on FastAPI!")

else:
    print("⚠️  Running without x402 payment protection!")


# ============================================================================
# PAID API ENDPOINTS (Protected by Official x402)
# ============================================================================

@app.post("/api/v1/verify-plant")
async def verify_plant(
    image: UploadFile = File(...),
    species: str = Form(...)
) -> Dict[str, Any]:
    """
    Plant verification API with official x402 payment
    
    Cost: $25 USDC on Base Sepolia
    Payment: Automatically handled by x402 middleware
    """
    # Save temp file
    temp_path = f"/tmp/verify_{datetime.now().timestamp()}.jpg"
    
    with open(temp_path, "wb") as f:
        f.write(await image.read())
    
    # Run AI verification
    result = plant_recognition.identify_plant(
        image_path=temp_path,
        claimed_species=species
    )
    
    # Clean up
    os.remove(temp_path)
    
    return {
        'success': True,
        'verification': result,
        'cost': '$25 USDC',
        'network': NETWORK,
        'timestamp': datetime.now().isoformat()
    }


@app.post("/api/v1/health-scan")
async def health_scan(
    image: UploadFile = File(...),
    species: str = Form(...)
) -> Dict[str, Any]:
    """
    Plant health scan API with official x402 payment
    
    Cost: $30 USDC on Base Sepolia
    """
    # Save temp file
    temp_path = f"/tmp/health_{datetime.now().timestamp()}.jpg"
    
    with open(temp_path, "wb") as f:
        f.write(await image.read())
    
    # Run health scan
    result = plant_health.scan_plant_health(
        image_path=temp_path,
        plant_species=species
    )
    
    # Clean up
    os.remove(temp_path)
    
    return {
        'success': True,
        'health_scan': result,
        'cost': '$30 USDC',
        'network': NETWORK,
        'timestamp': datetime.now().isoformat()
    }


@app.get("/api/v1/remedy/{issue_type}")
async def get_remedy(issue_type: str) -> Dict[str, Any]:
    """
    Get organic remedy recipe with official x402 payment
    
    Cost: $20 USDC on Base Sepolia
    """
    # Use PlantHealthAI to get remedy suggestions
    remedy_result = plant_health.suggest_organic_fertilizer(
        deficiency_type=issue_type,
        plant_type=None
    )
    
    if not remedy_result.get('success'):
        return JSONResponse(
            status_code=404,
            content={'error': f'Remedy not found for: {issue_type}'}
        )
    
    return {
        'success': True,
        'issue': issue_type,
        'remedy': {
            'deficiency': remedy_result['deficiency'],
            'symptoms': remedy_result['symptoms'],
            'organic_solutions': remedy_result['organic_solutions'],
            'application_method': remedy_result['application_method'],
            'prevention': remedy_result['prevention'],
            'diy_recipe': remedy_result['diy_recipe']
        },
        'points_reward': remedy_result['points_reward'],
        'cost': '$20 USDC',
        'network': NETWORK,
        'timestamp': datetime.now().isoformat()
    }


@app.post("/api/v1/premium/carbon-credit/buy/{listing_id}")
async def buy_carbon_credit(listing_id: str) -> Dict[str, Any]:
    """
    Buy a carbon credit NFT with official x402 payment
    
    Cost: $100 USDC
    """
    return {
        'success': True,
        'message': f'Carbon credit {listing_id} purchased',
        'listing_id': listing_id,
        'cost': '$100 USDC',
        'network': NETWORK,
        'timestamp': datetime.now().isoformat()
    }


@app.post("/api/v1/premium/mint-carbon-nft")
async def mint_carbon_nft(
    trees_planted: int = Form(...),
    location: str = Form(...),
    gps_coords: str = Form(...),
    worker_id: str = Form(...),
    gesture_signature: str = Form("biometric_verified"),
    image_url: str = Form(None)
) -> Dict[str, Any]:
    """
    Mint a Carbon Credit NFT on Algorand blockchain
    Protected by x402 payment (covered under /api/v1/premium/*)
    
    Cost: Included in $100 USDC premium tier
    """
    if not ALGORAND_AVAILABLE:
        return {
            'success': False,
            'error': 'Algorand NFT minting not configured',
            'message': 'Set ALGOD_URL and ALGO_MNEMONIC environment variables'
        }
    
    try:
        # Mint the NFT on Algorand
        mint_result = mint_carbon_credit_nft(
            trees_planted=trees_planted,
            location=location,
            gps_coords=gps_coords,
            worker_id=worker_id,
            gesture_signature=gesture_signature,
            image_url=image_url
        )
        
        # Calculate carbon offset
        carbon_offset_kg = trees_planted * 21.77
        
        return {
            'success': True,
            'transaction_id': mint_result['transaction_id'],
            'asset_id': mint_result['asset_id'],
            'explorer_url': mint_result['explorer_url'],
            'carbon_offset_kg': round(carbon_offset_kg, 2),
            'properties': mint_result['properties'],
            'network': 'Algorand TestNet',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'NFT minting failed'
        }


# ============================================================================
# PUBLIC ENDPOINTS (No Payment Required)
# ============================================================================

@app.get("/")
async def index() -> Dict[str, Any]:
    """API information"""
    return {
        'name': 'Carbon Credit FastAPI with Official x402',
        'version': '2.0.0',
        'x402_package': 'Official Coinbase x402',
        'github': 'https://github.com/coinbase/x402',
        
        'payment_config': {
            'enabled': X402_AVAILABLE,
            'network': NETWORK,
            'payment_address': PAYMENT_ADDRESS,
            'usdc_contract': USDC_BASE_SEPOLIA,
        },
        
        'endpoints': {
            'paid_apis': {
                'POST /api/v1/verify-plant': '$25 USDC - Plant species verification',
                'POST /api/v1/health-scan': '$30 USDC - Health diagnosis',
                'GET /api/v1/remedy/{type}': '$20 USDC - Organic remedy recipes',
                'POST /api/v1/premium/carbon-credit/buy/{id}': '$100 USDC - Buy carbon credit NFT',
            },
            'public_apis': {
                'GET /': 'API information',
                'GET /health': 'Health check',
                'GET /docs': 'Interactive API documentation',
            }
        },
        
        'documentation': {
            'interactive_docs': '/docs',
            'openapi_spec': '/openapi.json',
        }
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'x402_enabled': X402_AVAILABLE,
        'x402_package': 'Official Coinbase x402' if X402_AVAILABLE else 'Not installed',
        'timestamp': datetime.now().isoformat()
    }


# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    import uvicorn
    
    print("\n" + "="*70)
    print("🚀 CARBON CREDIT FASTAPI WITH OFFICIAL x402")
    print("="*70)
    print("Official Package: https://github.com/coinbase/x402")
    print("Server: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("API Info: http://localhost:8000/")
    
    if X402_AVAILABLE:
        print("\n✅ Official x402 middleware active!")
        print(f"   Payment Address: {PAYMENT_ADDRESS}")
        print(f"   Network: {NETWORK}")
        print("\n💰 Protected Endpoints:")
        print("   POST /api/v1/verify-plant - $25 USDC")
        print("   POST /api/v1/health-scan - $30 USDC")
        print("   GET /api/v1/remedy/{type} - $20 USDC")
        print("   POST /api/v1/premium/carbon-credit/buy/{id} - $100 USDC")
    else:
        print("\n⚠️  x402 package not installed!")
        print("   Install with: pip install x402")
    
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
