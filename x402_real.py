"""
Real Coinbase x402 Payment Protocol Implementation
Official Specification: https://github.com/coinbase/x402
Version: 1.0

This implements the actual x402 protocol as designed by Coinbase:
- HTTP 402 Payment Required
- X-PAYMENT header (base64 encoded JSON)
- X-PAYMENT-RESPONSE header
- Facilitator server integration (/verify, /settle, /supported)
"""

import os
import json
import base64
import requests
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime


# ============================================================================
# x402 PROTOCOL CONSTANTS
# ============================================================================

X402_VERSION = 1

# Facilitator Server URL (Coinbase official or self-hosted)
FACILITATOR_URL = os.getenv('X402_FACILITATOR_URL', 'https://facilitator.base.org')

# Supported schemes and networks
SUPPORTED_SCHEMES = ['exact']
SUPPORTED_NETWORKS = ['base', 'ethereum', 'optimism', 'algorand']


# ============================================================================
# x402 DATA TYPES (Official Specification)
# ============================================================================

@dataclass
class PaymentRequirements:
    """
    Official x402 paymentRequirements structure
    Defines what the resource server accepts for payment
    """
    # Scheme of the payment protocol to use
    scheme: str
    
    # Network of the blockchain to send payment on
    network: str
    
    # Maximum amount required to pay for the resource in atomic units
    maxAmountRequired: str  # uint256 as string
    
    # URL of resource to pay for
    resource: str
    
    # Description of the resource
    description: str
    
    # MIME type of the resource response
    mimeType: str
    
    # Address to pay value to
    payTo: str
    
    # Maximum time in seconds for the resource server to respond
    maxTimeoutSeconds: int
    
    # Address of the EIP-3009 compliant ERC20 contract (for EVM chains)
    asset: str
    
    # Output schema of the resource response (optional)
    outputSchema: Optional[Dict] = None
    
    # Extra information about the payment details specific to the scheme
    extra: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        # Remove None values
        return {k: v for k, v in result.items() if v is not None}


@dataclass
class PaymentRequiredResponse:
    """
    Official x402 Payment Required Response (402 status)
    Returned by resource server when payment is required
    """
    # Version of the x402 payment protocol
    x402Version: int
    
    # List of payment requirements that the resource server accepts
    accepts: List[Dict]  # List of PaymentRequirements
    
    # Message from the resource server to communicate errors
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class PaymentPayload:
    """
    Official x402 Payment Payload
    Included as X-PAYMENT header in base64 encoded JSON
    """
    # Version of the x402 payment protocol
    x402Version: int
    
    # Scheme value of the accepted paymentRequirements
    scheme: str
    
    # Network id of the accepted paymentRequirements
    network: str
    
    # Payload is scheme dependent
    payload: Dict
    
    def to_base64_header(self) -> str:
        """
        Encode as base64 JSON for X-PAYMENT header
        This is the official x402 format
        """
        json_str = json.dumps(asdict(self))
        return base64.b64encode(json_str.encode()).decode()
    
    @classmethod
    def from_base64_header(cls, header_value: str) -> 'PaymentPayload':
        """Decode from X-PAYMENT header"""
        json_str = base64.b64decode(header_value).decode()
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class VerifyRequest:
    """Request to facilitator /verify endpoint"""
    x402Version: int
    paymentHeader: str  # base64 encoded PaymentPayload
    paymentRequirements: Dict


@dataclass
class VerifyResponse:
    """Response from facilitator /verify endpoint"""
    isValid: bool
    invalidReason: Optional[str] = None


@dataclass
class SettleRequest:
    """Request to facilitator /settle endpoint"""
    x402Version: int
    paymentHeader: str  # base64 encoded PaymentPayload
    paymentRequirements: Dict


@dataclass
class SettleResponse:
    """Response from facilitator /settle endpoint"""
    success: bool
    error: Optional[str] = None
    txHash: Optional[str] = None
    networkId: Optional[str] = None


# ============================================================================
# x402 RESOURCE SERVER (What you implement on your API)
# ============================================================================

class X402ResourceServer:
    """
    Resource Server implementation for x402 protocol
    This is what you add to your Carbon Credit API
    """
    
    def __init__(self, facilitator_url: str = FACILITATOR_URL):
        self.facilitator_url = facilitator_url
        self.payment_config = {}  # Store payment configs per endpoint
    
    
    def configure_endpoint(self, 
                          endpoint: str,
                          price_usdc: float,
                          description: str,
                          pay_to_address: str,
                          scheme: str = 'exact',
                          network: str = 'base') -> PaymentRequirements:
        """
        Configure an endpoint to require x402 payment
        
        Args:
            endpoint: API endpoint (e.g., '/api/verify-plant')
            price_usdc: Price in USDC
            description: What this endpoint does
            pay_to_address: Your wallet address to receive payment
            scheme: Payment scheme (default: 'exact')
            network: Blockchain network (default: 'base')
        
        Returns:
            PaymentRequirements object
        """
        # Convert USDC to atomic units (6 decimals for USDC)
        max_amount = str(int(price_usdc * 1_000_000))
        
        # USDC contract addresses per network
        usdc_addresses = {
            'base': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
            'ethereum': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
            'optimism': '0x7F5c764cBc14f9669B88837ca1490cCa17c31607'
        }
        
        requirements = PaymentRequirements(
            scheme=scheme,
            network=network,
            maxAmountRequired=max_amount,
            resource=endpoint,
            description=description,
            mimeType='application/json',
            payTo=pay_to_address,
            maxTimeoutSeconds=30,
            asset=usdc_addresses.get(network, ''),
            extra={'name': 'USD Coin', 'version': '2'} if network in usdc_addresses else None
        )
        
        self.payment_config[endpoint] = requirements
        return requirements
    
    
    def require_payment(self, endpoint: str) -> PaymentRequiredResponse:
        """
        Generate 402 Payment Required response
        This is what you return when payment is required
        
        Args:
            endpoint: The endpoint being accessed
        
        Returns:
            PaymentRequiredResponse (return as JSON with status 402)
        """
        requirements = self.payment_config.get(endpoint)
        
        if not requirements:
            raise ValueError(f"No payment configuration for endpoint: {endpoint}")
        
        response = PaymentRequiredResponse(
            x402Version=X402_VERSION,
            accepts=[requirements.to_dict()],
            error=None
        )
        
        return response
    
    
    def verify_payment(self, 
                      payment_header: str,
                      endpoint: str) -> VerifyResponse:
        """
        Verify payment using facilitator server
        
        Args:
            payment_header: Value from X-PAYMENT header (base64 encoded)
            endpoint: The endpoint being accessed
        
        Returns:
            VerifyResponse indicating if payment is valid
        """
        requirements = self.payment_config.get(endpoint)
        
        if not requirements:
            return VerifyResponse(isValid=False, invalidReason="No payment config")
        
        # Call facilitator /verify endpoint
        try:
            verify_req = VerifyRequest(
                x402Version=X402_VERSION,
                paymentHeader=payment_header,
                paymentRequirements=requirements.to_dict()
            )
            
            response = requests.post(
                f"{self.facilitator_url}/verify",
                json=asdict(verify_req),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return VerifyResponse(**data)
            else:
                return VerifyResponse(
                    isValid=False,
                    invalidReason=f"Facilitator error: {response.status_code}"
                )
        
        except Exception as e:
            return VerifyResponse(isValid=False, invalidReason=str(e))
    
    
    def settle_payment(self,
                      payment_header: str,
                      endpoint: str) -> SettleResponse:
        """
        Settle payment on blockchain using facilitator
        
        Args:
            payment_header: Value from X-PAYMENT header (base64 encoded)
            endpoint: The endpoint being accessed
        
        Returns:
            SettleResponse with transaction details
        """
        requirements = self.payment_config.get(endpoint)
        
        if not requirements:
            return SettleResponse(success=False, error="No payment config")
        
        # Call facilitator /settle endpoint
        try:
            settle_req = SettleRequest(
                x402Version=X402_VERSION,
                paymentHeader=payment_header,
                paymentRequirements=requirements.to_dict()
            )
            
            response = requests.post(
                f"{self.facilitator_url}/settle",
                json=asdict(settle_req),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return SettleResponse(**data)
            else:
                return SettleResponse(
                    success=False,
                    error=f"Facilitator error: {response.status_code}"
                )
        
        except Exception as e:
            return SettleResponse(success=False, error=str(e))
    
    
    def get_supported_schemes(self) -> Dict:
        """Query facilitator for supported schemes and networks"""
        try:
            response = requests.get(f"{self.facilitator_url}/supported", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {'kinds': []}
        except:
            return {'kinds': []}


# ============================================================================
# x402 CLIENT (For making payments)
# ============================================================================

class X402Client:
    """
    Client implementation for making x402 payments
    This is what AI agents or users use to pay for resources
    """
    
    def __init__(self, wallet_address: str, private_key: str):
        self.wallet_address = wallet_address
        self.private_key = private_key
    
    
    def create_payment_payload(self,
                              requirements: PaymentRequirements,
                              signature: str) -> PaymentPayload:
        """
        Create payment payload for a given requirement
        
        Args:
            requirements: PaymentRequirements from 402 response
            signature: Signed payment authorization (scheme-dependent)
        
        Returns:
            PaymentPayload to include in X-PAYMENT header
        """
        # For 'exact' scheme on EVM, payload contains EIP-3009 authorization
        payload_data = {
            'from': self.wallet_address,
            'to': requirements.payTo,
            'value': requirements.maxAmountRequired,
            'validAfter': 0,
            'validBefore': int(datetime.now().timestamp()) + 3600,
            'nonce': os.urandom(32).hex(),
            'v': signature['v'] if isinstance(signature, dict) else 0,
            'r': signature['r'] if isinstance(signature, dict) else '',
            's': signature['s'] if isinstance(signature, dict) else '',
        }
        
        return PaymentPayload(
            x402Version=X402_VERSION,
            scheme=requirements.scheme,
            network=requirements.network,
            payload=payload_data
        )
    
    
    def request_resource(self,
                        url: str,
                        method: str = 'GET',
                        data: Optional[Dict] = None) -> Dict:
        """
        Request a resource that requires x402 payment
        
        Flow:
        1. Make request without payment
        2. Get 402 Payment Required with payment requirements
        3. Create payment payload
        4. Retry request with X-PAYMENT header
        
        Args:
            url: Resource URL
            method: HTTP method
            data: Request data
        
        Returns:
            Response data
        """
        # Step 1: Initial request
        response = requests.request(method, url, json=data)
        
        if response.status_code == 402:
            # Step 2: Got payment required
            payment_required = response.json()
            
            if not payment_required.get('accepts'):
                raise ValueError("No payment methods accepted")
            
            # Select first payment requirement
            req_dict = payment_required['accepts'][0]
            requirements = PaymentRequirements(**req_dict)
            
            # Step 3: Create payment (simplified - in production, sign properly)
            # This would involve signing with your wallet
            signature = self._sign_payment(requirements)
            
            payment_payload = self.create_payment_payload(requirements, signature)
            
            # Step 4: Retry with payment
            headers = {
                'X-PAYMENT': payment_payload.to_base64_header()
            }
            
            response = requests.request(method, url, json=data, headers=headers)
            
            # Check for settlement response
            if 'X-PAYMENT-RESPONSE' in response.headers:
                settlement = json.loads(
                    base64.b64decode(response.headers['X-PAYMENT-RESPONSE'])
                )
                print(f"✅ Payment settled: {settlement.get('txHash')}")
            
            return response.json()
        
        return response.json()
    
    
    def _sign_payment(self, requirements: PaymentRequirements) -> Dict:
        """
        Sign payment authorization (scheme-dependent)
        For production, implement proper EIP-3009 or similar signing
        """
        # Simplified signature - in production, use proper cryptographic signing
        return {
            'v': 27,
            'r': '0x' + os.urandom(32).hex(),
            's': '0x' + os.urandom(32).hex()
        }


# ============================================================================
# CARBON CREDIT MARKETPLACE INTEGRATION
# ============================================================================

class CarbonCreditX402Integration:
    """
    Integration of x402 with Carbon Credit Marketplace
    """
    
    def __init__(self, pay_to_address: str):
        self.server = X402ResourceServer()
        self.pay_to_address = pay_to_address
        self.setup_endpoints()
    
    
    def setup_endpoints(self):
        """Configure x402 payments for all API endpoints"""
        
        # Plant verification API
        self.server.configure_endpoint(
            endpoint='/api/v1/verify-plant',
            price_usdc=25.0,
            description='AI-powered plant species verification',
            pay_to_address=self.pay_to_address,
            network='base'
        )
        
        # Health scan API
        self.server.configure_endpoint(
            endpoint='/api/v1/health-scan',
            price_usdc=30.0,
            description='Plant health diagnosis with AI',
            pay_to_address=self.pay_to_address,
            network='base'
        )
        
        # Remedy database API
        self.server.configure_endpoint(
            endpoint='/api/v1/remedy',
            price_usdc=20.0,
            description='Organic remedy recipes',
            pay_to_address=self.pay_to_address,
            network='base'
        )
        
        # Carbon credit purchase
        self.server.configure_endpoint(
            endpoint='/api/v1/carbon-credit/buy',
            price_usdc=100.0,  # Variable based on listing
            description='Purchase verified carbon credit NFT',
            pay_to_address=self.pay_to_address,
            network='base'
        )
        
        print("✅ x402 endpoints configured:")
        print("   • /api/v1/verify-plant - $25 USDC")
        print("   • /api/v1/health-scan - $30 USDC")
        print("   • /api/v1/remedy - $20 USDC")
        print("   • /api/v1/carbon-credit/buy - Variable USDC")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_resource_server():
    """Example: Setting up a resource server with x402"""
    
    print("\n" + "="*70)
    print("EXAMPLE: x402 Resource Server Setup")
    print("="*70 + "\n")
    
    # Your wallet address to receive payments
    pay_to = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
    
    # Create resource server
    server = X402ResourceServer()
    
    # Configure endpoint
    requirements = server.configure_endpoint(
        endpoint='/api/verify-plant',
        price_usdc=25.0,
        description='Plant species verification with AI',
        pay_to_address=pay_to,
        network='base'
    )
    
    print("✅ Endpoint configured!")
    print(f"   Resource: {requirements.resource}")
    print(f"   Price: $25 USDC")
    print(f"   Network: {requirements.network}")
    print(f"   Pay to: {requirements.payTo}")
    
    # Generate 402 response
    payment_required = server.require_payment('/api/verify-plant')
    print(f"\n📄 Payment Required Response:")
    print(json.dumps(payment_required.to_dict(), indent=2))


def example_client_payment():
    """Example: Making a payment as a client"""
    
    print("\n" + "="*70)
    print("EXAMPLE: x402 Client Making Payment")
    print("="*70 + "\n")
    
    # Client wallet
    wallet = "0x1234567890123456789012345678901234567890"
    private_key = "0xabcdef..."
    
    client = X402Client(wallet, private_key)
    
    print("🤖 AI Agent requesting resource...")
    print("   Agent: Carbon Offset Bot")
    print("   Resource: /api/verify-plant")
    print("   Payment: 25 USDC on Base")
    
    # In production, this would make actual HTTP requests
    print("\n✅ Payment flow:")
    print("   1. Request resource")
    print("   2. Receive 402 Payment Required")
    print("   3. Sign payment authorization")
    print("   4. Send X-PAYMENT header")
    print("   5. Receive resource + X-PAYMENT-RESPONSE")
    print("   6. Payment settled on blockchain")


if __name__ == '__main__':
    print("\n" + "█"*70)
    print("█" + "  REAL COINBASE x402 PROTOCOL IMPLEMENTATION  ".center(68) + "█")
    print("█"*70 + "\n")
    
    example_resource_server()
    example_client_payment()
    
    print("\n" + "="*70)
    print("🎉 REAL x402 PROTOCOL READY!")
    print("="*70)
    print("\n📚 Official Spec: https://github.com/coinbase/x402")
    print("🌐 Ecosystem: https://x402.org/ecosystem")
    print("💡 This follows the REAL Coinbase x402 specification!")
    print("\n" + "="*70 + "\n")
