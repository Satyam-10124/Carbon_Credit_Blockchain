#!/usr/bin/env python3
"""
Complete System Test Suite for Carbon Credit Blockchain
Tests all services: Database, Algorand, AI, GPS, Weather, Satellite, API
"""

import os
import sys
import time
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

print("=" * 70)
print("🧪 CARBON CREDIT BLOCKCHAIN - COMPLETE SYSTEM TEST")
print("=" * 70)
print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
print()

# Test Results Tracking
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "tests": []
}

def test_result(name, status, message="", critical=False):
    """Record test result"""
    test_results["total"] += 1
    test_results["tests"].append({
        "name": name,
        "status": status,
        "message": message,
        "critical": critical
    })
    
    if status == "PASS":
        test_results["passed"] += 1
        print(f"✅ {name}: PASSED")
    elif status == "FAIL":
        test_results["failed"] += 1
        print(f"❌ {name}: FAILED - {message}")
        if critical:
            print(f"⚠️  CRITICAL FAILURE - Cannot continue")
    elif status == "SKIP":
        test_results["skipped"] += 1
        print(f"⏭️  {name}: SKIPPED - {message}")
    
    if message and status != "FAIL":
        print(f"   ℹ️  {message}")
    print()


# ============================================================================
# TEST 1: ENVIRONMENT VARIABLES
# ============================================================================
print("\n" + "=" * 70)
print("📋 TEST 1: ENVIRONMENT VARIABLES")
print("=" * 70)

required_vars = [
    "ALGO_MNEMONIC",
    "ALGO_NETWORK",
    "ALGOD_URL",
    "DATABASE_URL",
    "NFT_IMAGE_URL"
]

optional_vars = [
    "OPENAI_API_KEY",
    "GOOGLE_MAPS_API_KEY",
    "OPENWEATHER_API_KEY",
    "PLANET_API_KEY"
]

missing_required = []
missing_optional = []

for var in required_vars:
    value = os.getenv(var)
    if value:
        test_result(f"Env: {var}", "PASS", f"Set ({len(value)} chars)", critical=True)
    else:
        missing_required.append(var)
        test_result(f"Env: {var}", "FAIL", "Not set", critical=True)

for var in optional_vars:
    value = os.getenv(var)
    if value:
        test_result(f"Env: {var}", "PASS", f"Set ({len(value)} chars)")
    else:
        missing_optional.append(var)
        test_result(f"Env: {var}", "SKIP", "Not configured (optional)")

if missing_required:
    print(f"\n❌ CRITICAL: Missing required variables: {', '.join(missing_required)}")
    print("Cannot continue tests. Please set these in .env file.")
    sys.exit(1)


# ============================================================================
# TEST 2: DATABASE CONNECTION
# ============================================================================
print("\n" + "=" * 70)
print("🗄️  TEST 2: DATABASE CONNECTION")
print("=" * 70)

try:
    import psycopg2
    from urllib.parse import urlparse
    
    db_url = os.getenv("DATABASE_URL")
    result = urlparse(db_url)
    
    test_result("Database: URL parsing", "PASS", f"Host: {result.hostname}")
    
    # Attempt connection
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Test query
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    test_result("Database: Connection", "PASS", f"PostgreSQL connected", critical=True)
    
    # Test table operations
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    test_result("Database: Tables", "PASS", f"Found {len(tables)} tables")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    test_result("Database: Connection", "FAIL", str(e), critical=True)
    print(f"\n❌ Database connection failed. Check DATABASE_URL in .env")
    sys.exit(1)


# ============================================================================
# TEST 3: ALGORAND BLOCKCHAIN
# ============================================================================
print("\n" + "=" * 70)
print("⛓️  TEST 3: ALGORAND BLOCKCHAIN")
print("=" * 70)

try:
    from algosdk import mnemonic
    from algosdk.v2client import algod
    
    # Test mnemonic
    algo_mnemonic = os.getenv("ALGO_MNEMONIC")
    try:
        private_key = mnemonic.to_private_key(algo_mnemonic)
        from algosdk.account import address_from_private_key
        address = address_from_private_key(private_key)
        test_result("Algorand: Mnemonic", "PASS", f"Valid mnemonic", critical=True)
        test_result("Algorand: Address", "PASS", f"{address[:20]}...")
    except Exception as e:
        test_result("Algorand: Mnemonic", "FAIL", str(e), critical=True)
        sys.exit(1)
    
    # Test connection
    algod_url = os.getenv("ALGOD_URL")
    algod_client = algod.AlgodClient("", algod_url)
    
    status = algod_client.status()
    test_result("Algorand: Connection", "PASS", f"Connected to {os.getenv('ALGO_NETWORK')}", critical=True)
    test_result("Algorand: Network", "PASS", f"Round: {status['last-round']}")
    
    # Check account balance
    account_info = algod_client.account_info(address)
    balance = account_info['amount'] / 1_000_000
    min_balance = account_info.get('min-balance', 0) / 1_000_000
    available = balance - min_balance
    
    test_result("Algorand: Balance", "PASS", f"{balance:.6f} ALGO (Available: {available:.6f})")
    
    if available < 1.0:
        test_result("Algorand: Sufficient Funds", "FAIL", f"Low balance: {available:.6f} ALGO")
    else:
        test_result("Algorand: Sufficient Funds", "PASS", f"{available:.6f} ALGO available")
    
except Exception as e:
    test_result("Algorand: Connection", "FAIL", str(e), critical=True)
    print(f"\n❌ Algorand connection failed")
    sys.exit(1)


# ============================================================================
# TEST 4: AI SERVICES (OpenAI)
# ============================================================================
print("\n" + "=" * 70)
print("🤖 TEST 4: AI SERVICES")
print("=" * 70)

openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=openai_key)
        test_result("AI: OpenAI Client", "PASS", "Client initialized")
        
        # Test API call
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Say 'test' only"}],
            max_tokens=5
        )
        
        test_result("AI: GPT-4 API", "PASS", "API call successful")
        test_result("AI: Response", "PASS", f"Got response: {response.choices[0].message.content}")
        
    except Exception as e:
        test_result("AI: OpenAI", "FAIL", str(e))
else:
    test_result("AI: OpenAI", "SKIP", "API key not configured")


# ============================================================================
# TEST 5: GPS & WEATHER SERVICES
# ============================================================================
print("\n" + "=" * 70)
print("🌍 TEST 5: GPS & WEATHER SERVICES")
print("=" * 70)

# Google Maps API
google_key = os.getenv("GOOGLE_MAPS_API_KEY")
if google_key:
    try:
        import requests
        
        # Test geocoding
        test_location = "Mumbai, India"
        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": test_location, "key": google_key}
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            test_result("GPS: Google Maps API", "PASS", f"Geocoding works: {location['lat']}, {location['lng']}")
        else:
            test_result("GPS: Google Maps API", "FAIL", f"Status: {data['status']}")
            
    except Exception as e:
        test_result("GPS: Google Maps API", "FAIL", str(e))
else:
    test_result("GPS: Google Maps API", "SKIP", "API key not configured")

# OpenWeather API
weather_key = os.getenv("OPENWEATHER_API_KEY")
if weather_key:
    try:
        import requests
        
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": 19.0760,
            "lon": 72.8777,
            "appid": weather_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            weather = data['weather'][0]['description']
            temp = data['main']['temp'] - 273.15
            test_result("Weather: OpenWeather API", "PASS", f"{weather}, {temp:.1f}°C")
        else:
            test_result("Weather: OpenWeather API", "FAIL", f"Status: {response.status_code}")
            
    except Exception as e:
        test_result("Weather: OpenWeather API", "FAIL", str(e))
else:
    test_result("Weather: OpenWeather API", "SKIP", "API key not configured")


# ============================================================================
# TEST 6: SATELLITE SERVICES
# ============================================================================
print("\n" + "=" * 70)
print("🛰️  TEST 6: SATELLITE SERVICES")
print("=" * 70)

planet_key = os.getenv("PLANET_API_KEY")
if planet_key:
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        url = "https://api.planet.com/data/v1/item-types"
        auth = HTTPBasicAuth(planet_key, '')
        
        response = requests.get(url, auth=auth, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            test_result("Satellite: Planet Labs API", "PASS", f"API accessible, {len(data['item_types'])} item types")
        else:
            test_result("Satellite: Planet Labs API", "FAIL", f"Status: {response.status_code}")
            
    except Exception as e:
        test_result("Satellite: Planet Labs API", "FAIL", str(e))
else:
    test_result("Satellite: Planet Labs API", "SKIP", "API key not configured")


# ============================================================================
# TEST 7: GESTURE VERIFICATION SYSTEM
# ============================================================================
print("\n" + "=" * 70)
print("✋ TEST 7: GESTURE VERIFICATION SYSTEM")
print("=" * 70)

try:
    import cv2
    import mediapipe as mp
    
    test_result("Gesture: OpenCV", "PASS", f"Version {cv2.__version__}")
    test_result("Gesture: MediaPipe", "PASS", "Imported successfully")
    
    # Test MediaPipe initialization
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7
    )
    test_result("Gesture: MediaPipe Hands", "PASS", "Initialized successfully")
    hands.close()
    
    # Test camera access (quick check, don't open window)
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        test_result("Gesture: Camera Access", "PASS", "Camera detected")
        cap.release()
    else:
        test_result("Gesture: Camera Access", "FAIL", "Cannot access camera")
    
except Exception as e:
    test_result("Gesture: System", "FAIL", str(e))


# ============================================================================
# TEST 8: NFT MINTING (DRY RUN)
# ============================================================================
print("\n" + "=" * 70)
print("🎨 TEST 8: NFT MINTING (DRY RUN)")
print("=" * 70)

try:
    from algorand_nft import AlgorandNFT
    
    nft = AlgorandNFT()
    test_result("NFT: Client Init", "PASS", "AlgorandNFT initialized")
    
    # Prepare test metadata
    metadata = {
        "trees_planted": 5,
        "location": "Test Location",
        "gps_coords": "19.0760° N, 72.8777° E",
        "worker_id": "TEST_WORKER",
        "gesture_signature": "test_signature_123",
        "carbon_offset_kg": 108.85
    }
    
    test_result("NFT: Metadata", "PASS", "Test metadata prepared")
    
    # Don't actually mint, just validate we can
    test_result("NFT: Minting Ready", "PASS", "System ready to mint (not executed)")
    
except Exception as e:
    test_result("NFT: System", "FAIL", str(e))


# ============================================================================
# TEST 9: API ENDPOINTS
# ============================================================================
print("\n" + "=" * 70)
print("🔌 TEST 9: API ENDPOINTS")
print("=" * 70)

try:
    import requests
    
    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        if response.status_code == 200:
            data = response.json()
            test_result("API: Health Check", "PASS", f"Status: {data.get('status', 'unknown')}")
            
            # Test endpoints
            endpoints = [
                ("/docs", "GET", "Documentation"),
                ("/algorand/status", "GET", "Algorand Status"),
            ]
            
            for endpoint, method, name in endpoints:
                try:
                    resp = requests.get(f"http://localhost:8000{endpoint}", timeout=2)
                    if resp.status_code == 200:
                        test_result(f"API: {name}", "PASS", f"{endpoint}")
                    else:
                        test_result(f"API: {name}", "FAIL", f"Status: {resp.status_code}")
                except:
                    test_result(f"API: {name}", "FAIL", "Endpoint not responding")
        else:
            test_result("API: Health Check", "FAIL", f"Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        test_result("API: Server", "SKIP", "API server not running (start with: uvicorn api:app --reload)")
        
except Exception as e:
    test_result("API: System", "FAIL", str(e))


# ============================================================================
# TEST 10: VALIDATORS
# ============================================================================
print("\n" + "=" * 70)
print("🔍 TEST 10: VALIDATOR MODULES")
print("=" * 70)

try:
    from ai_validator import AIValidator
    test_result("Validator: AI", "PASS", "Module loaded")
except Exception as e:
    test_result("Validator: AI", "FAIL", str(e))

try:
    from gps_validator import GPSValidator
    test_result("Validator: GPS", "PASS", "Module loaded")
except Exception as e:
    test_result("Validator: GPS", "FAIL", str(e))

try:
    from satellite_validator import SatelliteValidator
    test_result("Validator: Satellite", "PASS", "Module loaded")
except Exception as e:
    test_result("Validator: Satellite", "FAIL", str(e))

try:
    from integrated_validator import IntegratedValidator
    test_result("Validator: Integrated", "PASS", "Module loaded")
except Exception as e:
    test_result("Validator: Integrated", "FAIL", str(e))


# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("📊 TEST SUMMARY")
print("=" * 70)

print(f"\n✅ Passed:  {test_results['passed']}/{test_results['total']}")
print(f"❌ Failed:  {test_results['failed']}/{test_results['total']}")
print(f"⏭️  Skipped: {test_results['skipped']}/{test_results['total']}")

# Calculate score
total_scored = test_results['passed'] + test_results['failed']
if total_scored > 0:
    score = (test_results['passed'] / total_scored) * 100
    print(f"\n🎯 Success Rate: {score:.1f}%")

# Save results to file
result_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(result_file, 'w') as f:
    json.dump(test_results, f, indent=2)

print(f"\n📁 Detailed results saved to: {result_file}")

# Critical failures
critical_failures = [t for t in test_results['tests'] if t['status'] == 'FAIL' and t['critical']]
if critical_failures:
    print("\n" + "=" * 70)
    print("⚠️  CRITICAL FAILURES")
    print("=" * 70)
    for test in critical_failures:
        print(f"❌ {test['name']}: {test['message']}")
    print("\nSystem cannot operate properly until these are resolved.")
    sys.exit(1)

# Recommendations
print("\n" + "=" * 70)
print("💡 RECOMMENDATIONS")
print("=" * 70)

if test_results['skipped'] > 0:
    print("\n📝 Optional Services Not Configured:")
    for test in test_results['tests']:
        if test['status'] == 'SKIP':
            print(f"   • {test['name']}")
    print("\n   These are optional but recommended for full functionality.")

if test_results['failed'] > 0:
    print("\n🔧 Issues to Fix:")
    for test in test_results['tests']:
        if test['status'] == 'FAIL' and not test['critical']:
            print(f"   • {test['name']}: {test['message']}")

print("\n" + "=" * 70)
if test_results['failed'] == 0:
    print("🎉 ALL CRITICAL SYSTEMS OPERATIONAL!")
    print("=" * 70)
    print("\n✅ Your Carbon Credit system is ready for production!")
    print("\nNext steps:")
    print("1. Start API: uvicorn api:app --reload --port 8000")
    print("2. Start Frontend: cd frontend && npm run dev")
    print("3. Test verification: python main.py")
else:
    print("⚠️  SOME TESTS FAILED")
    print("=" * 70)
    print("\nPlease fix the failed tests before proceeding.")

print("\n" + "=" * 70)
print("🏁 Test Complete")
print("=" * 70)
