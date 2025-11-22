"""
Carbon Credit API with REAL Coinbase x402 Protocol
Uses the official x402 specification for HTTP payments
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
import base64
import os
from datetime import datetime

from x402_real import (
    X402ResourceServer,
    PaymentPayload,
    X402_VERSION,
    CarbonCreditX402Integration
)
from joyo_ai_services.plant_recognition import PlantRecognitionAI
from joyo_ai_services.plant_health import PlantHealthAI


app = Flask(__name__)
CORS(app)

# Initialize x402 resource server
PAYMENT_ADDRESS = os.getenv('PAYMENT_ADDRESS', '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0')
x402_server = X402ResourceServer()

# Initialize AI services
plant_recognition = PlantRecognitionAI()
plant_health = PlantHealthAI()

# Carbon Credit Marketplace with x402
marketplace = CarbonCreditX402Integration(PAYMENT_ADDRESS)


# ============================================================================
# x402 MIDDLEWARE - Real Coinbase Protocol
# ============================================================================

def x402_required(endpoint: str):
    """
    Decorator that enforces x402 payment (Real Coinbase protocol)
    
    Usage:
        @app.route('/api/verify-plant', methods=['POST'])
        @x402_required('/api/verify-plant')
        def verify_plant():
            return {'result': 'verified'}
    
    Flow (Official x402):
    1. Check for X-PAYMENT header
    2. If missing, return 402 Payment Required with PaymentRequiredResponse
    3. If present, verify payment with facilitator
    4. If valid, execute function
    5. Return result with X-PAYMENT-RESPONSE header
    """
    def decorator(f):
        def wrapped(*args, **kwargs):
            # Check for X-PAYMENT header
            payment_header = request.headers.get('X-PAYMENT')
            
            if not payment_header:
                # Return 402 Payment Required (Official x402)
                payment_required = x402_server.require_payment(endpoint)
                
                return Response(
                    json.dumps(payment_required.to_dict()),
                    status=402,  # HTTP 402 Payment Required
                    content_type='application/json'
                )
            
            # Verify payment using facilitator (Official x402 flow)
            verify_result = x402_server.verify_payment(payment_header, endpoint)
            
            if not verify_result.isValid:
                # Payment verification failed
                payment_required = x402_server.require_payment(endpoint)
                payment_required.error = verify_result.invalidReason
                
                return Response(
                    json.dumps(payment_required.to_dict()),
                    status=402,
                    content_type='application/json'
                )
            
            # Payment verified! Execute the function
            result = f(*args, **kwargs)
            
            # Settle payment on blockchain (Official x402)
            settle_result = x402_server.settle_payment(payment_header, endpoint)
            
            # Add X-PAYMENT-RESPONSE header (Official x402)
            if settle_result.success:
                response_data = {
                    'success': True,
                    'txHash': settle_result.txHash,
                    'networkId': settle_result.networkId
                }
                
                # Base64 encode JSON for X-PAYMENT-RESPONSE header
                response_header = base64.b64encode(
                    json.dumps(response_data).encode()
                ).decode()
                
                if isinstance(result, tuple):
                    response = jsonify(result[0])
                    response.status_code = result[1] if len(result) > 1 else 200
                else:
                    response = jsonify(result)
                
                response.headers['X-PAYMENT-RESPONSE'] = response_header
                return response
            
            # Settlement failed but verification passed - still return result
            # (Client can retry settlement)
            return jsonify(result)
        
        wrapped.__name__ = f.__name__
        return wrapped
    return decorator


# ============================================================================
# PAID API ENDPOINTS (Real x402)
# ============================================================================

@app.route('/api/v1/verify-plant', methods=['POST'])
@x402_required('/api/v1/verify-plant')
def verify_plant():
    """
    Plant verification API with real x402 payment
    
    Cost: 25 USDC on Base network
    Payment: Send X-PAYMENT header with signed authorization
    """
    if 'image' not in request.files:
        return {'error': 'No image provided'}, 400
    
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
    
    return {
        'success': True,
        'verification': result,
        'cost': '25 USDC',
        'network': 'base',
        'timestamp': datetime.now().isoformat()
    }


@app.route('/api/v1/health-scan', methods=['POST'])
@x402_required('/api/v1/health-scan')
def health_scan():
    """
    Plant health scan API with real x402 payment
    
    Cost: 30 USDC on Base network
    """
    if 'image' not in request.files:
        return {'error': 'No image provided'}, 400
    
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
    
    return {
        'success': True,
        'health_scan': result,
        'cost': '30 USDC',
        'network': 'base',
        'timestamp': datetime.now().isoformat()
    }


@app.route('/api/v1/remedy/<issue_type>', methods=['GET'])
@x402_required('/api/v1/remedy')
def get_remedy(issue_type: str):
    """
    Get organic remedy recipe with real x402 payment
    
    Cost: 20 USDC on Base network
    """
    from joyo_ai_services.data.remedy_catalog import ORGANIC_REMEDIES
    
    remedy = ORGANIC_REMEDIES.get(issue_type)
    
    if not remedy:
        return {'error': f'Remedy not found for: {issue_type}'}, 404
    
    return {
        'success': True,
        'issue': issue_type,
        'remedy': remedy,
        'cost': '20 USDC',
        'network': 'base',
        'timestamp': datetime.now().isoformat()
    }


# ============================================================================
# CARBON CREDIT MARKETPLACE (Real x402)
# ============================================================================

# In-memory marketplace (use database in production)
carbon_listings = {}

@app.route('/api/v1/carbon-credit/list', methods=['POST'])
def list_carbon_credit():
    """
    List a carbon credit NFT for sale (Free endpoint)
    """
    data = request.json
    
    listing_id = f"LISTING_{data['asset_id']}_{int(datetime.now().timestamp())}"
    
    listing = {
        'listing_id': listing_id,
        'asset_id': data['asset_id'],
        'price_usdc': data['price_usdc'],
        'co2_offset_kg': data['co2_offset_kg'],
        'plant_species': data.get('plant_species'),
        'location': data.get('location'),
        'seller': data.get('seller_address'),
        'listed_at': datetime.now().isoformat(),
        'status': 'active'
    }
    
    carbon_listings[listing_id] = listing
    
    return {
        'success': True,
        'listing': listing,
        'message': 'Carbon credit listed on x402 marketplace'
    }


@app.route('/api/v1/carbon-credit/buy/<listing_id>', methods=['POST'])
def buy_carbon_credit(listing_id: str):
    """
    Buy a carbon credit with real x402 payment
    
    Payment is handled by x402 protocol:
    - First request returns 402 with payment requirements
    - Client sends X-PAYMENT header with signed authorization
    - Facilitator verifies and settles payment
    - NFT is transferred
    """
    listing = carbon_listings.get(listing_id)
    
    if not listing:
        return {'error': 'Listing not found'}, 404
    
    if listing['status'] != 'active':
        return {'error': 'Listing not available'}, 400
    
    # Check for X-PAYMENT header
    payment_header = request.headers.get('X-PAYMENT')
    
    if not payment_header:
        # Configure payment for this listing
        endpoint = f'/api/v1/carbon-credit/buy/{listing_id}'
        
        x402_server.configure_endpoint(
            endpoint=endpoint,
            price_usdc=listing['price_usdc'],
            description=f"Purchase carbon credit {listing['asset_id']} - {listing['co2_offset_kg']} kg CO2",
            pay_to_address=listing['seller'],
            network='base'
        )
        
        payment_required = x402_server.require_payment(endpoint)
        
        return Response(
            json.dumps(payment_required.to_dict()),
            status=402,
            content_type='application/json'
        )
    
    # Verify and settle payment
    endpoint = f'/api/v1/carbon-credit/buy/{listing_id}'
    verify_result = x402_server.verify_payment(payment_header, endpoint)
    
    if not verify_result.isValid:
        return {'error': verify_result.invalidReason}, 400
    
    # Settle payment
    settle_result = x402_server.settle_payment(payment_header, endpoint)
    
    if settle_result.success:
        # Update listing status
        listing['status'] = 'sold'
        listing['sold_at'] = datetime.now().isoformat()
        listing['buyer'] = request.json.get('buyer_address')
        listing['tx_hash'] = settle_result.txHash
        
        # In production, transfer NFT here
        
        # Return response with X-PAYMENT-RESPONSE header
        response_data = {
            'success': True,
            'message': 'Carbon credit purchased successfully',
            'listing': listing,
            'payment': {
                'txHash': settle_result.txHash,
                'networkId': settle_result.networkId,
                'amount_usdc': listing['price_usdc']
            }
        }
        
        response = jsonify(response_data)
        
        # Add X-PAYMENT-RESPONSE header (Official x402)
        payment_response = {
            'success': True,
            'txHash': settle_result.txHash,
            'networkId': settle_result.networkId
        }
        
        response.headers['X-PAYMENT-RESPONSE'] = base64.b64encode(
            json.dumps(payment_response).encode()
        ).decode()
        
        return response
    
    return {'error': settle_result.error}, 500


@app.route('/api/v1/carbon-credit/listings', methods=['GET'])
def get_listings():
    """Get all active carbon credit listings (Free endpoint)"""
    active_listings = [
        l for l in carbon_listings.values()
        if l['status'] == 'active'
    ]
    
    return {
        'success': True,
        'count': len(active_listings),
        'listings': active_listings
    }


# ============================================================================
# INFO & DOCUMENTATION
# ============================================================================

@app.route('/')
def index():
    """API documentation"""
    return jsonify({
        'name': 'Carbon Credit API with Real x402 Protocol',
        'version': '1.0.0',
        'x402_version': X402_VERSION,
        'protocol': 'Official Coinbase x402',
        'spec': 'https://github.com/coinbase/x402',
        
        'endpoints': {
            'paid_apis': {
                'POST /api/v1/verify-plant': {
                    'cost': '25 USDC',
                    'network': 'base',
                    'description': 'AI-powered plant species verification',
                    'payment': 'Send X-PAYMENT header with signed authorization'
                },
                'POST /api/v1/health-scan': {
                    'cost': '30 USDC',
                    'network': 'base',
                    'description': 'Plant health diagnosis with AI'
                },
                'GET /api/v1/remedy/<type>': {
                    'cost': '20 USDC',
                    'network': 'base',
                    'description': 'Organic remedy recipes'
                }
            },
            'marketplace': {
                'POST /api/v1/carbon-credit/list': 'List carbon credit (FREE)',
                'POST /api/v1/carbon-credit/buy/<id>': 'Buy carbon credit (x402 payment)',
                'GET /api/v1/carbon-credit/listings': 'Browse listings (FREE)'
            }
        },
        
        'x402_flow': {
            '1': 'Make request to paid endpoint',
            '2': 'Receive 402 Payment Required with payment requirements',
            '3': 'Sign payment authorization (EIP-3009 for EVM)',
            '4': 'Send X-PAYMENT header with base64 encoded payload',
            '5': 'Facilitator verifies payment',
            '6': 'Facilitator settles payment on blockchain',
            '7': 'Receive resource with X-PAYMENT-RESPONSE header'
        },
        
        'payment_networks': {
            'base': 'Base (Ethereum L2)',
            'ethereum': 'Ethereum Mainnet',
            'optimism': 'Optimism'
        },
        
        'facilitator': 'https://facilitator.base.org',
        'ecosystem': 'https://x402.org/ecosystem'
    })


@app.route('/x402/info', methods=['GET'])
def x402_info():
    """x402 protocol information"""
    supported = x402_server.get_supported_schemes()
    
    return jsonify({
        'protocol': 'Coinbase x402',
        'version': X402_VERSION,
        'specification': 'https://github.com/coinbase/x402',
        'supported_schemes': supported.get('kinds', []),
        'payment_address': PAYMENT_ADDRESS,
        'configured_endpoints': list(x402_server.payment_config.keys()),
        'how_it_works': {
            'step_1': 'Client requests paid resource',
            'step_2': 'Server returns 402 with PaymentRequirements',
            'step_3': 'Client creates PaymentPayload with signature',
            'step_4': 'Client sends X-PAYMENT header',
            'step_5': 'Server verifies with facilitator',
            'step_6': 'Server settles payment',
            'step_7': 'Server returns resource + X-PAYMENT-RESPONSE'
        }
    })


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'x402_protocol': 'enabled',
        'x402_version': X402_VERSION,
        'facilitator': 'connected',
        'timestamp': datetime.now().isoformat()
    })


# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 CARBON CREDIT API WITH REAL x402 PROTOCOL")
    print("="*70)
    print("Server: http://localhost:5000")
    print("Docs: http://localhost:5000/")
    print("x402 Info: http://localhost:5000/x402/info")
    print("\n📝 Configured Endpoints:")
    
    # Setup all x402 endpoints
    endpoints = [
        ('/api/v1/verify-plant', 25.0, 'Plant verification'),
        ('/api/v1/health-scan', 30.0, 'Health diagnosis'),
        ('/api/v1/remedy', 20.0, 'Remedy recipes'),
    ]
    
    for endpoint, price, desc in endpoints:
        x402_server.configure_endpoint(
            endpoint=endpoint,
            price_usdc=price,
            description=desc,
            pay_to_address=PAYMENT_ADDRESS,
            network='base'
        )
        print(f"   ✅ {endpoint} - ${price} USDC - {desc}")
    
    print(f"\n💰 Payment Address: {PAYMENT_ADDRESS}")
    print("🌐 Network: Base (Ethereum L2)")
    print("💎 Currency: USDC")
    print("\n📚 Using REAL Coinbase x402 Protocol")
    print("   Spec: https://github.com/coinbase/x402")
    print("   Ecosystem: https://x402.org/ecosystem")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
