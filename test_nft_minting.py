"""
Test NFT Minting without Gesture Verification
Tests only the Algorand blockchain integration
"""

import os
import sys
from datetime import datetime
import hashlib

from dotenv import load_dotenv
load_dotenv()  # Add before checking environment variables
def test_algorand_connection():
    """Test connection to Algorand network"""
    print("\n" + "="*70)
    print("⛓️  TESTING ALGORAND CONNECTION")
    print("="*70 + "\n")
    
    try:
        from algorand_nft import get_algod_client, get_algorand_account
        
        # Test client
        print("📡 Connecting to Algorand node...")
        client = get_algod_client()
        status = client.status()
        
        print(f"✅ Connected successfully!")
        
        # Determine network
        url = os.getenv('ALGOD_URL', '')
        if 'testnet' in url.lower():
            network = 'TestNet'
        elif 'mainnet' in url.lower():
            network = 'MainNet'
        else:
            network = 'Unknown'
        
        print(f"   Network: {network}")
        print(f"   Last round: {status['last-round']}")
        
        # Genesis ID may not always be in status response
        if 'genesis-id' in status:
            print(f"   Genesis ID: {status['genesis-id']}")
        
        if 'genesis-hash' in status:
            genesis_hash = status['genesis-hash'][:16]  # First 16 chars
            print(f"   Genesis Hash: {genesis_hash}...")
        
        time_since = status.get('time-since-last-round', 0)
        print(f"   Time since last round: {time_since}ms")
        
        # Test account
        print("\n🔑 Checking account...")
        addr, _ = get_algorand_account()
        print(f"   Address: {addr}")
        
        # Check balance
        account_info = client.account_info(addr)
        balance_algos = account_info['amount'] / 1_000_000
        min_balance = account_info['min-balance'] / 1_000_000
        available = balance_algos - min_balance
        
        print(f"   Balance: {balance_algos:.6f} ALGO")
        print(f"   Min balance: {min_balance:.6f} ALGO")
        print(f"   Available: {available:.6f} ALGO")
        
        if available < 0.1:
            print(f"\n⚠️  WARNING: Low balance!")
            print(f"   You need at least 0.1 ALGO to mint NFTs")
            print(f"   Get more from: https://testnet.algoexplorer.io/dispenser")
            return False
        else:
            print(f"\n✅ Sufficient balance for minting!")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Make sure your .env file has:")
        print("   ALGOD_URL=https://testnet-api.algonode.cloud")
        print("   ALGO_MNEMONIC=your 25 word mnemonic here")
        return False


def test_nft_minting_dry_run():
    """Test NFT minting with mock data (no actual minting)"""
    print("\n" + "="*70)
    print("🧪 DRY RUN: NFT Minting Test (No Blockchain Transaction)")
    print("="*70 + "\n")
    
    try:
        from algorand_nft import _build_arc69_note
        
        # Mock data
        test_data = {
            "trees_planted": 5,
            "location": "Test Location, India",
            "gps_coords": "19.0760° N, 72.8777° E",
            "worker_id": "TEST_WORKER_001",
            "gesture_signature": hashlib.sha256(b"test_gesture").hexdigest(),
            "carbon_offset_kg": 5 * 21.77
        }
        
        # Use the same image URL from environment
        image_url = os.getenv("NFT_IMAGE_URL", "https://gateway.pinata.cloud/ipfs/bafybeif5ew2ao2pwio75aiuxpsaooeydiworkj7ubrdaycpa6rrwmmuxuu")
        asset_name = f"Carbon-{test_data['trees_planted']}Trees"
        
        # Build ARC-69 note
        note = _build_arc69_note(image_url, asset_name, test_data)
        
        print("📋 NFT Metadata Preview:")
        print("-" * 70)
        import json
        metadata = json.loads(note.decode('utf-8'))
        print(json.dumps(metadata, indent=2))
        print("-" * 70)
        
        print(f"\n✅ Metadata structure valid!")
        print(f"   Asset name: {asset_name}")
        print(f"   Image URL: {image_url}")
        print(f"   Properties: {len(test_data)} fields")
        
        return True
        
    except Exception as e:
        print(f"❌ Dry run failed: {e}")
        return False


def test_actual_nft_minting():
    """Test actual NFT minting on blockchain (requires ALGO)"""
    print("\n" + "="*70)
    print("🚀 REAL NFT MINTING TEST")
    print("="*70 + "\n")
    
    # Confirm with user
    print("⚠️  This will mint an actual NFT on the blockchain!")
    print("   Cost: ~0.001 ALGO (~$0.0002)")
    print("")
    
    confirmation = input("Type 'yes' to proceed: ").strip().lower()
    if confirmation != 'yes':
        print("\n❌ Minting cancelled by user")
        return False
    
    print("\n🔨 Minting NFT...")
    
    try:
        from algorand_nft import mint_carbon_credit_nft
        
        # Test data
        result = mint_carbon_credit_nft(
            trees_planted=1,
            location="Test Mint - Mumbai, India",
            gps_coords="19.0760° N, 72.8777° E",
            worker_id="TEST_WORKER_001",
            gesture_signature=hashlib.sha256(b"test_gesture").hexdigest(),
            image_url=None  # Will use NFT_IMAGE_URL from environment
        )
        
        print("\n" + "="*70)
        print("🎉 NFT MINTED SUCCESSFULLY!")
        print("="*70)
        print(f"Transaction ID: {result['transaction_id']}")
        print(f"Asset ID: {result['asset_id']}")
        print(f"Explorer: {result['explorer_url']}")
        print(f"Carbon Offset: {result['properties']['carbon_offset_kg']:.2f} kg CO2")
        print("="*70 + "\n")
        
        print("📝 View your NFT on the blockchain:")
        print(f"   {result['explorer_url']}")
        print("")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Minting failed: {e}")
        print("\n💡 Common issues:")
        print("   - Insufficient ALGO balance")
        print("   - Network connectivity")
        print("   - Invalid mnemonic")
        return False


def run_all_nft_tests():
    """Run all NFT minting tests"""
    print("\n" + "="*70)
    print("🧪 NFT MINTING TEST SUITE")
    print("="*70)
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except:
        print("⚠️  .env file not found - using system environment")
    
    # Check credentials
    if not os.getenv("ALGOD_URL"):
        print("\n❌ ALGOD_URL not set in .env file")
        print("\n📝 Quick setup:")
        print("1. Copy .env.example to .env")
        print("2. Add: ALGOD_URL=https://testnet-api.algonode.cloud")
        print("3. Add: ALGO_MNEMONIC=your 25 word mnemonic")
        print("4. Get TestNet ALGO: https://testnet.algoexplorer.io/dispenser")
        return False
    
    if not os.getenv("ALGO_MNEMONIC"):
        print("\n❌ ALGO_MNEMONIC not set in .env file")
        print("\n📝 Get a TestNet account:")
        print("   https://testnet.algoexplorer.io/dispenser")
        return False
    
    # Run tests
    results = {
        "connection": test_algorand_connection(),
        "dry_run": test_nft_minting_dry_run()
    }
    
    # Only offer real minting if previous tests pass
    if all(results.values()):
        print("\n" + "="*70)
        print("✅ All preliminary tests passed!")
        print("="*70)
        
        print("\n🎯 Ready to mint a real NFT?")
        results["actual_mint"] = test_actual_nft_minting()
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    for test_name, success in results.items():
        icon = "✅" if success else "❌"
        status = "PASSED" if success else "FAILED"
        print(f"{icon} {test_name.replace('_', ' ').title()}: {status}")
    
    passed = sum(results.values())
    total = len(results)
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests successful! NFT minting is operational!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - check configuration")
    
    print("="*70 + "\n")
    
    return passed == total


def main():
    """Main entry point"""
    print("\n🌍 Carbon Credit NFT Minting Test")
    print("Testing blockchain integration without gesture verification\n")
    
    success = run_all_nft_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
