"""
Carbon Credit API Client with Official x402 Package
Uses the real x402 Python client from Coinbase
https://github.com/coinbase/x402/tree/main/examples/python/clients
"""

import os
from dotenv import load_dotenv

# Import official x402 package
try:
    from x402.clients.requests import x402_requests
    from x402.clients.base import decode_x_payment_response, x402Client
    from eth_account import Account
    X402_AVAILABLE = True
except ImportError:
    print("❌ Official x402 package not installed!")
    print("   Install with: pip install x402")
    print("   Then: pip install eth-account")
    exit(1)

# Load environment
load_dotenv()

# Configuration
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
API_BASE_URL = os.getenv("RESOURCE_SERVER_URL", "http://localhost:5000")

if not PRIVATE_KEY:
    print("❌ Missing PRIVATE_KEY in .env file!")
    print("   Add: PRIVATE_KEY=0x...")
    exit(1)

# Create account from private key
account = Account.from_key(PRIVATE_KEY)
print(f"✅ Initialized account: {account.address}\n")


def custom_payment_selector(accepts, network_filter=None, scheme_filter=None, max_value=None):
    """
    Custom payment selector that filters by network
    Uses base-sepolia testnet for development
    """
    return x402Client.default_payment_requirements_selector(
        accepts,
        network_filter="base-sepolia",  # Testnet (change to "base" for mainnet)
        scheme_filter=scheme_filter,
        max_value=max_value,
    )


def verify_plant(session, image_path: str, species: str):
    """
    Verify a plant species (costs $25 USDC)
    Payment is automatically handled by x402!
    """
    print("="*70)
    print("🌱 PLANT VERIFICATION")
    print("="*70)
    print(f"Image: {image_path}")
    print(f"Species: {species}")
    print("Cost: $25 USDC (auto-paid by x402)")
    print()
    
    try:
        with open(image_path, 'rb') as f:
            response = session.post(
                f"{API_BASE_URL}/api/v1/verify-plant",
                files={'image': f},
                data={'species': species}
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"   Verification: {result.get('verification', {})}")
            
            # Check payment response
            if "X-Payment-Response" in response.headers:
                payment_response = decode_x_payment_response(
                    response.headers["X-Payment-Response"]
                )
                print(f"\n💰 Payment settled!")
                print(f"   Transaction: {payment_response.get('transaction', 'N/A')}")
            
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def health_scan(session, image_path: str, species: str):
    """
    Scan plant health (costs $30 USDC)
    Payment is automatically handled by x402!
    """
    print("\n" + "="*70)
    print("🏥 HEALTH SCAN")
    print("="*70)
    print(f"Image: {image_path}")
    print(f"Species: {species}")
    print("Cost: $30 USDC (auto-paid by x402)")
    print()
    
    try:
        with open(image_path, 'rb') as f:
            response = session.post(
                f"{API_BASE_URL}/api/v1/health-scan",
                files={'image': f},
                data={'species': species}
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"   Health Scan: {result.get('health_scan', {})}")
            
            # Check payment response
            if "X-Payment-Response" in response.headers:
                payment_response = decode_x_payment_response(
                    response.headers["X-Payment-Response"]
                )
                print(f"\n💰 Payment settled!")
                print(f"   Transaction: {payment_response.get('transaction', 'N/A')}")
            
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def get_remedy(session, issue_type: str):
    """
    Get organic remedy recipe (costs $20 USDC)
    Payment is automatically handled by x402!
    """
    print("\n" + "="*70)
    print("💊 GET REMEDY")
    print("="*70)
    print(f"Issue: {issue_type}")
    print("Cost: $20 USDC (auto-paid by x402)")
    print()
    
    try:
        response = session.get(
            f"{API_BASE_URL}/api/v1/remedy/{issue_type}"
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"   Remedy: {result.get('remedy', {})}")
            
            # Check payment response
            if "X-Payment-Response" in response.headers:
                payment_response = decode_x_payment_response(
                    response.headers["X-Payment-Response"]
                )
                print(f"\n💰 Payment settled!")
                print(f"   Transaction: {payment_response.get('transaction', 'N/A')}")
            
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def buy_carbon_credit(session, listing_id: str):
    """
    Buy carbon credit NFT (costs $100 USDC)
    Payment is automatically handled by x402!
    """
    print("\n" + "="*70)
    print("💎 BUY CARBON CREDIT NFT")
    print("="*70)
    print(f"Listing ID: {listing_id}")
    print("Cost: $100 USDC (auto-paid by x402)")
    print()
    
    try:
        response = session.post(
            f"{API_BASE_URL}/api/v1/carbon-credit/buy/{listing_id}"
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"   Purchase: {result}")
            
            # Check payment response
            if "X-Payment-Response" in response.headers:
                payment_response = decode_x_payment_response(
                    response.headers["X-Payment-Response"]
                )
                print(f"\n💰 Payment settled!")
                print(f"   Transaction: {payment_response.get('transaction', 'N/A')}")
            
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Main demo"""
    print("\n" + "="*70)
    print("🚀 OFFICIAL x402 CLIENT DEMO")
    print("="*70)
    print("Using real Coinbase x402 Python package")
    print("https://github.com/coinbase/x402")
    print("="*70 + "\n")
    
    # Create x402-enabled requests session
    print("🔧 Creating x402-enabled session...")
    session = x402_requests(
        account,
        payment_requirements_selector=custom_payment_selector,
    )
    print("✅ Session created!\n")
    
    # Example 1: Verify plant
    # verify_plant(session, "path/to/plant.jpg", "bamboo")
    
    # Example 2: Health scan
    # health_scan(session, "path/to/plant.jpg", "tulsi")
    
    # Example 3: Get remedy
    get_remedy(session, "nitrogen-deficiency")
    
    # Example 4: Buy carbon credit
    # buy_carbon_credit(session, "LISTING_123")
    
    print("\n" + "="*70)
    print("🎉 DEMO COMPLETE!")
    print("="*70)
    print("\n💡 All payments were automatically handled by x402!")
    print("   No manual payment logic needed!")
    print("   Just use the session like normal requests!\n")


if __name__ == "__main__":
    main()
