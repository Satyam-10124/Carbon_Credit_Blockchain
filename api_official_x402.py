"""
Carbon Credit API with OFFICIAL Coinbase x402 Package
Uses the real x402 Python package from Coinbase
https://github.com/coinbase/x402/tree/main/examples/python
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime

# Import official x402 package
try:
    from x402.flask.middleware import PaymentMiddleware
    from x402.types import TokenAmount, TokenAsset, EIP712Domain
    X402_AVAILABLE = True
except ImportError:
    print("⚠️  Official x402 package not installed!")
    print("   Install with: pip install x402")
    X402_AVAILABLE = False

from joyo_ai_services.plant_recognition import PlantRecognitionAI
from joyo_ai_services.plant_health import PlantHealthAI

# Load environment
load_dotenv()

# Configuration
PAYMENT_ADDRESS = os.getenv("ADDRESS") or os.getenv("PAYMENT_ADDRESS", "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0")
NETWORK = "base-sepolia"  # Testnet (use "base" for mainnet)

# USDC Contract on Base Sepolia
USDC_BASE_SEPOLIA = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Initialize AI services
plant_recognition = PlantRecognitionAI()
plant_health = PlantHealthAI()

# ============================================================================
# SETUP OFFICIAL x402 MIDDLEWARE
# ============================================================================

if X402_AVAILABLE:
    # Initialize payment middleware
    payment_middleware = PaymentMiddleware(app)
    
    # Plant Verification API - $25 USDC
    payment_middleware.add(
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
    
    # Health Scan API - $30 USDC
    payment_middleware.add(
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
    
    # Remedy Database API - $20 USDC
    payment_middleware.add(
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
    
    # Carbon Credit Purchase - Variable pricing
    payment_middleware.add(
        path="/api/v1/carbon-credit/buy/*",
        price="$100",  # Simplified price (will be dynamic in production)
        pay_to_address=PAYMENT_ADDRESS,
        network=NETWORK,
    )
    
    print("✅ Official x402 middleware configured!")
    print(f"   Payment Address: {PAYMENT_ADDRESS}")
    print(f"   Network: {NETWORK}")
    print(f"   USDC Contract: {USDC_BASE_SEPOLIA}")

else:
    print("⚠️  Running without x402 payment protection!")
    print("   Install: pip install x402")


# ============================================================================
# PAID API ENDPOINTS (Protected by Official x402)
# ============================================================================

@app.route("/api/v1/verify-plant", methods=["POST"])
def verify_plant():
    """
    Plant verification API with official x402 payment
    
    Cost: $25 USDC on Base Sepolia
    Payment: Automatically handled by x402 middleware
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image = request.files['image']
    claimed_species = request.form.get('species', 'unknown')
    
    # Save temp file
    temp_path = f"/tmp/verify_{datetime.now().timestamp()}.jpg"
    image.save(temp_path)
    
    # Run AI verification
    result = plant_recognition.identify_plant(
        image_path=temp_path,
        claimed_species=claimed_species
    )
    
    # Clean up
    os.remove(temp_path)
    
    return jsonify({
        'success': True,
        'verification': result,
        'cost': '$25 USDC',
        'network': NETWORK,
        'timestamp': datetime.now().isoformat()
    })


@app.route("/api/v1/health-scan", methods=["POST"])
def health_scan():
    """
    Plant health scan API with official x402 payment
    
    Cost: $30 USDC on Base Sepolia
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image = request.files['image']
    plant_species = request.form.get('species', 'unknown')
    
    # Save temp file
    temp_path = f"/tmp/health_{datetime.now().timestamp()}.jpg"
    image.save(temp_path)
    
    # Run health scan
    result = plant_health.scan_plant_health(
        image_path=temp_path,
        plant_species=plant_species
    )
    
    # Clean up
    os.remove(temp_path)
    
    return jsonify({
        'success': True,
        'health_scan': result,
        'cost': '$30 USDC',
        'network': NETWORK,
        'timestamp': datetime.now().isoformat()
    })


@app.route("/api/v1/remedy/<issue_type>", methods=["GET"])
def get_remedy(issue_type: str):
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
        return jsonify({'error': f'Remedy not found for: {issue_type}'}), 404
    
    return jsonify({
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
    })


@app.route("/api/v1/carbon-credit/buy/<listing_id>", methods=["POST"])
def buy_carbon_credit(listing_id: str):
    """
    Buy a carbon credit NFT with official x402 payment
    
    Payment automatically handled by x402 middleware
    """
    # In production, fetch listing from database
    return jsonify({
        'success': True,
        'message': f'Carbon credit {listing_id} purchased',
        'cost': '$100 USDC',
        'network': NETWORK,
        'timestamp': datetime.now().isoformat()
    })


# ============================================================================
# PUBLIC ENDPOINTS (No Payment Required)
# ============================================================================

@app.route("/")
def index():
    """API information"""
    return jsonify({
        'name': 'Carbon Credit API with Official x402',
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
                'GET /api/v1/remedy/<type>': '$20 USDC - Organic remedy recipes',
                'POST /api/v1/carbon-credit/buy/<id>': '$100 USDC - Buy carbon credit NFT',
            },
            'public_apis': {
                'GET /': 'API information (this page)',
                'GET /health': 'Health check',
                'GET /x402/info': 'x402 protocol info',
            }
        },
        
        'how_to_use': {
            'step_1': 'Install x402 client: pip install x402',
            'step_2': 'Create Ethereum account with private key',
            'step_3': 'Fund account with USDC on Base Sepolia',
            'step_4': 'Use x402_requests session to make authenticated requests',
            'step_5': 'Payments are automatically handled by x402',
        },
        
        'example_client': {
            'language': 'python',
            'code': '''
from x402.clients.requests import x402_requests
from eth_account import Account

# Your wallet
account = Account.from_key("YOUR_PRIVATE_KEY")

# Create x402-enabled session
session = x402_requests(account)

# Make paid request (payment automatic!)
response = session.post(
    "http://localhost:5000/api/v1/verify-plant",
    files={"image": open("plant.jpg", "rb")},
    data={"species": "bamboo"}
)

print(response.json())
# Payment automatically settled!
            '''
        }
    })


@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'x402_enabled': X402_AVAILABLE,
        'x402_package': 'Official Coinbase x402' if X402_AVAILABLE else 'Not installed',
        'timestamp': datetime.now().isoformat()
    })


@app.route("/x402/info")
def x402_info():
    """x402 protocol information"""
    return jsonify({
        'protocol': 'Coinbase x402',
        'package': 'Official Python package',
        'github': 'https://github.com/coinbase/x402',
        'examples': 'https://github.com/coinbase/x402/tree/main/examples/python',
        'enabled': X402_AVAILABLE,
        
        'configuration': {
            'payment_address': PAYMENT_ADDRESS,
            'network': NETWORK,
            'usdc_contract': USDC_BASE_SEPOLIA,
        },
        
        'protected_endpoints': [
            '/api/v1/verify-plant',
            '/api/v1/health-scan',
            '/api/v1/remedy/*',
            '/api/v1/carbon-credit/buy/*',
        ] if X402_AVAILABLE else [],
        
        'installation': {
            'command': 'pip install x402',
            'requires': ['flask', 'eth-account', 'web3'],
        },
        
        'client_example': '''
# Install client
pip install x402

# Use in Python
from x402.clients.requests import x402_requests
from eth_account import Account

account = Account.from_key("0x...")
session = x402_requests(account)

# Automatic payment handling!
response = session.get("http://localhost:5000/api/v1/verify-plant")
'''
    })


# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 CARBON CREDIT API WITH OFFICIAL x402")
    print("="*70)
    print("Official Package: https://github.com/coinbase/x402")
    print("Server: http://localhost:5000")
    print("Docs: http://localhost:5000/")
    print("x402 Info: http://localhost:5000/x402/info")
    
    if X402_AVAILABLE:
        print("\n✅ Official x402 middleware active!")
        print(f"   Payment Address: {PAYMENT_ADDRESS}")
        print(f"   Network: {NETWORK}")
        print("\n💰 Protected Endpoints:")
        print("   POST /api/v1/verify-plant - $25 USDC")
        print("   POST /api/v1/health-scan - $30 USDC")
        print("   GET /api/v1/remedy/<type> - $20 USDC")
        print("   POST /api/v1/carbon-credit/buy/<id> - $100 USDC")
    else:
        print("\n⚠️  x402 package not installed!")
        print("   Install with: pip install x402")
        print("   Running in demo mode (no payment protection)")
    
    print("\n" + "="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
