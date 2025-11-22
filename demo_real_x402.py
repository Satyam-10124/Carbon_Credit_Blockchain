"""
Demo: Real Coinbase x402 Protocol
Shows how the official x402 payment flow works
"""

import json
from x402_real import (
    X402ResourceServer,
    X402Client,
    PaymentRequirements,
    PaymentPayload,
    CarbonCreditX402Integration
)


def demo_1_resource_server_setup():
    """Demo 1: Setting up a resource server with real x402"""
    print("\n" + "="*70)
    print("DEMO 1: RESOURCE SERVER SETUP (Real x402)")
    print("="*70 + "\n")
    
    # Your payment address
    pay_to = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
    
    # Create server
    server = X402ResourceServer()
    
    # Configure endpoint
    requirements = server.configure_endpoint(
        endpoint='/api/verify-plant',
        price_usdc=25.0,
        description='AI-powered plant species verification',
        pay_to_address=pay_to,
        scheme='exact',  # Official x402 scheme
        network='base'   # Base L2
    )
    
    print("✅ Endpoint Configured:")
    print(f"   Resource: {requirements.resource}")
    print(f"   Scheme: {requirements.scheme}")
    print(f"   Network: {requirements.network}")
    print(f"   Price: $25 USDC ({requirements.maxAmountRequired} atomic units)")
    print(f"   Pay To: {requirements.payTo}")
    print(f"   Asset (USDC): {requirements.asset}")
    print(f"   Timeout: {requirements.maxTimeoutSeconds}s")
    
    return server, requirements


def demo_2_payment_required_response(server, requirements):
    """Demo 2: Generate 402 Payment Required response"""
    print("\n" + "="*70)
    print("DEMO 2: 402 PAYMENT REQUIRED RESPONSE (Real x402)")
    print("="*70 + "\n")
    
    # Generate 402 response
    payment_required = server.require_payment('/api/verify-plant')
    
    print("📄 HTTP 402 Payment Required Response:")
    print(json.dumps(payment_required.to_dict(), indent=2))
    
    print("\n💡 What this means:")
    print("   • Client must pay to access the resource")
    print("   • Payment details are in 'accepts' array")
    print("   • Client can choose which payment method to use")
    print("   • This follows the REAL x402 specification")
    
    return payment_required


def demo_3_client_payment_payload():
    """Demo 3: Client creates payment payload"""
    print("\n" + "="*70)
    print("DEMO 3: CLIENT PAYMENT PAYLOAD (Real x402)")
    print("="*70 + "\n")
    
    # Simulate client creating payment
    wallet = "0x1234567890123456789012345678901234567890"
    private_key = "0xabc123..."
    
    client = X402Client(wallet, private_key)
    
    # Create mock requirements
    from x402_real import PaymentRequirements
    requirements = PaymentRequirements(
        scheme='exact',
        network='base',
        maxAmountRequired='25000000',  # 25 USDC in atomic units
        resource='/api/verify-plant',
        description='Plant verification',
        mimeType='application/json',
        payTo='0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0',
        maxTimeoutSeconds=30,
        asset='0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',  # USDC on Base
        extra={'name': 'USD Coin', 'version': '2'}
    )
    
    # Create payment
    signature = {'v': 27, 'r': '0xabc123...', 's': '0xdef456...'}
    payment_payload = client.create_payment_payload(requirements, signature)
    
    print("📦 Payment Payload (goes in X-PAYMENT header):")
    print(json.dumps({
        'x402Version': payment_payload.x402Version,
        'scheme': payment_payload.scheme,
        'network': payment_payload.network,
        'payload': payment_payload.payload
    }, indent=2))
    
    # Encode as base64 (real x402 format)
    encoded = payment_payload.to_base64_header()
    print(f"\n🔐 Base64 Encoded (X-PAYMENT header value):")
    print(f"   {encoded[:80]}...")
    
    print("\n💡 This is sent in HTTP headers:")
    print(f"   X-PAYMENT: {encoded}")
    
    return payment_payload


def demo_4_complete_flow():
    """Demo 4: Complete x402 payment flow"""
    print("\n" + "="*70)
    print("DEMO 4: COMPLETE x402 PAYMENT FLOW (Real Protocol)")
    print("="*70 + "\n")
    
    print("🔄 Official x402 Flow:\n")
    
    steps = [
        ("1️⃣  Client Request", "GET /api/verify-plant", "Initial request without payment"),
        ("2️⃣  Server Response", "402 Payment Required", "Returns PaymentRequirements JSON"),
        ("3️⃣  Client Signs", "Create PaymentPayload", "Sign with EIP-3009 authorization"),
        ("4️⃣  Client Retry", "X-PAYMENT: <base64>", "Send payment in header"),
        ("5️⃣  Server Verifies", "POST /verify to facilitator", "Facilitator validates signature"),
        ("6️⃣  Verification OK", "isValid: true", "Payment is valid"),
        ("7️⃣  Server Executes", "Run AI verification", "Process the actual request"),
        ("8️⃣  Server Settles", "POST /settle to facilitator", "Submit to blockchain"),
        ("9️⃣  Blockchain Confirm", "Transaction mined", "Payment confirmed on chain"),
        ("🔟 Server Returns", "200 OK + X-PAYMENT-RESPONSE", "Resource + settlement proof"),
    ]
    
    for emoji, action, detail in steps:
        print(f"{emoji} {action:25} → {detail}")
    
    print("\n✅ Result:")
    print("   • Client gets the resource (plant verification)")
    print("   • Payment settled on blockchain (Base L2)")
    print("   • Transaction hash in X-PAYMENT-RESPONSE header")
    print("   • All without gas fees for client or server!")


def demo_5_carbon_credit_marketplace():
    """Demo 5: Carbon credit marketplace with x402"""
    print("\n" + "="*70)
    print("DEMO 5: CARBON CREDIT MARKETPLACE (Real x402)")
    print("="*70 + "\n")
    
    pay_to = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
    marketplace = CarbonCreditX402Integration(pay_to)
    
    print("🌍 Carbon Credit Marketplace with x402:\n")
    
    print("📊 Configured Endpoints:")
    print("   ✅ /api/v1/verify-plant - $25 USDC")
    print("   ✅ /api/v1/health-scan - $30 USDC")
    print("   ✅ /api/v1/remedy - $20 USDC")
    print("   ✅ /api/v1/carbon-credit/buy - Variable USDC")
    
    print("\n💰 How It Works:")
    print("   1. User plants tree → Mints NFT")
    print("   2. NFT listed on marketplace")
    print("   3. Company AI agent discovers listing")
    print("   4. AI agent makes x402 payment")
    print("   5. Payment verified & settled")
    print("   6. NFT transferred automatically")
    print("   7. Seller receives USDC instantly")
    
    print("\n🤖 AI Agent Example:")
    print("   Agent: Tesla Carbon Offset Bot")
    print("   Action: Buy carbon credit")
    print("   Payment: 500 USDC via x402")
    print("   Flow:")
    print("      GET /api/v1/carbon-credit/buy/LISTING_123")
    print("      ← 402 Payment Required")
    print("      POST with X-PAYMENT header")
    print("      ← 200 OK + X-PAYMENT-RESPONSE")
    print("      ✅ NFT transferred, payment settled")


def demo_6_comparison():
    """Demo 6: x402 vs Traditional Payments"""
    print("\n" + "="*70)
    print("DEMO 6: x402 vs TRADITIONAL PAYMENTS")
    print("="*70 + "\n")
    
    print("📊 Comparison:\n")
    
    comparison = [
        ("Metric", "Traditional (Stripe)", "x402 Protocol"),
        ("-" * 20, "-" * 30, "-" * 30),
        ("Integration", "Complex SDK, webhooks", "1 decorator, 1 header"),
        ("Minimum Payment", "$0.50", "$0.000001 (1 micro-cent)"),
        ("Fees", "2.9% + 30¢", "Gas fees only (~$0.01)"),
        ("Settlement Time", "2-7 days", "Instant (15 seconds)"),
        ("Cross-border", "Multiple currencies", "Global USDC"),
        ("Refunds", "Complex disputes", "On-chain reversible"),
        ("AI Agents", "Not supported", "Native support"),
        ("Account Required", "Yes + KYC", "Just wallet address"),
        ("Chargebacks", "Yes (risky)", "No (immutable)"),
        ("For $25 Payment", "$1.23 fee", "$0.01 fee"),
    ]
    
    for row in comparison:
        print(f"{row[0]:20} | {row[1]:30} | {row[2]:30}")
    
    print("\n💡 Key Advantages:")
    print("   ✅ Perfect for micropayments")
    print("   ✅ AI-native (bots can pay)")
    print("   ✅ Global by default")
    print("   ✅ Instant settlement")
    print("   ✅ Low fees")
    print("   ✅ No intermediaries")


def demo_7_real_world_use_cases():
    """Demo 7: Real-world use cases"""
    print("\n" + "="*70)
    print("DEMO 7: REAL-WORLD USE CASES")
    print("="*70 + "\n")
    
    use_cases = [
        {
            'title': 'AI-Powered APIs',
            'example': 'Carbon Credit Verification',
            'payment': '$25 per verification',
            'benefit': 'AI agents automatically pay for API calls'
        },
        {
            'title': 'Content Monetization',
            'example': 'Premium plant care guides',
            'payment': '$5 per article',
            'benefit': 'Readers pay once, access forever'
        },
        {
            'title': 'LLM Token Metering',
            'example': 'Pay per AI response',
            'payment': '$0.001 per token',
            'benefit': 'Micropayments for exact usage'
        },
        {
            'title': 'Data Access',
            'example': 'Carbon offset data API',
            'payment': '$10 per query',
            'benefit': 'Pay-per-use, no subscriptions'
        },
        {
            'title': 'NFT Marketplace',
            'example': 'Carbon credit trading',
            'payment': 'Variable (e.g., $500)',
            'benefit': 'Instant settlement, no escrow'
        },
    ]
    
    for i, uc in enumerate(use_cases, 1):
        print(f"\n{i}. {uc['title']}")
        print(f"   Example: {uc['example']}")
        print(f"   Payment: {uc['payment']}")
        print(f"   Benefit: {uc['benefit']}")
    
    print("\n🎯 Your Carbon Credit System:")
    print("   • Plant verification API: $25/call")
    print("   • Health diagnosis API: $30/call")
    print("   • Remedy database: $20/query")
    print("   • NFT marketplace: Variable pricing")
    print("   • All powered by real x402!")


def main():
    """Run all demos"""
    print("\n" + "█"*70)
    print("█" + "  REAL COINBASE x402 PROTOCOL - COMPLETE DEMO  ".center(68) + "█")
    print("█"*70)
    
    # Run demos
    server, requirements = demo_1_resource_server_setup()
    payment_required = demo_2_payment_required_response(server, requirements)
    payment_payload = demo_3_client_payment_payload()
    demo_4_complete_flow()
    demo_5_carbon_credit_marketplace()
    demo_6_comparison()
    demo_7_real_world_use_cases()
    
    # Summary
    print("\n" + "="*70)
    print("🎉 DEMO COMPLETE!")
    print("="*70)
    print("\n📚 What You Learned:")
    print("   ✅ Official x402 protocol structure")
    print("   ✅ PaymentRequirements format")
    print("   ✅ X-PAYMENT header encoding")
    print("   ✅ Facilitator integration")
    print("   ✅ Complete payment flow")
    print("   ✅ Carbon credit marketplace")
    print("   ✅ Real-world use cases")
    
    print("\n🚀 Next Steps:")
    print("   1. Run API: python api_with_real_x402.py")
    print("   2. Test endpoints with curl")
    print("   3. Integrate with your frontend")
    print("   4. Deploy to production")
    print("   5. Join x402 ecosystem: https://x402.org")
    
    print("\n📖 Resources:")
    print("   • Official Spec: https://github.com/coinbase/x402")
    print("   • Ecosystem: https://x402.org/ecosystem")
    print("   • Facilitator: https://facilitator.base.org")
    print("   • Base Network: https://base.org")
    
    print("\n💡 This is the REAL x402 protocol by Coinbase!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
