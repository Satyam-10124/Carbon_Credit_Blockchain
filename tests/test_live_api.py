#!/usr/bin/env python3
"""
FIXED: Complete User Flow Test for Live Railway API
Tests against actual endpoints that exist in api_joyo_core.py

Usage: python3 test_live_api.py
"""

import requests
import json
import time
from datetime import datetime
import io
from PIL import Image

# API Configuration
API_URL = "https://joyo-cc-production.up.railway.app"
TEST_USER_ID = f"USER_TEST_{int(time.time())}"

# Test Results
results = {"total": 0, "passed": 0, "failed": 0, "tests": []}

def log(name, passed, details=""):
    results["total"] += 1
    results["passed" if passed else "failed"] += 1
    status = "✅" if passed else "❌"
    results["tests"].append({"name": name, "passed": passed, "details": details})
    print(f"{status} {name}")
    if details:
        print(f"   {details}")

def create_test_image():
    """Create test image"""
    img = Image.new('RGB', (800, 600), color='green')
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf

print("="*70)
print("🌱 LIVE API TEST - Carbon Credit Blockchain")
print("="*70)
print(f"API: {API_URL}")
print(f"User: {TEST_USER_ID}")
print(f"Time: {datetime.now()}")
print("="*70)
print()

# TEST 1: Health Check
print("TEST 1: Health Check")
print("-"*70)
try:
    r = requests.get(f"{API_URL}/health", timeout=10)
    if r.status_code == 200:
        data = r.json()
        log("Health Check", True, f"DB: {data.get('database')}, AI: {data.get('ai_services')}")
    else:
        log("Health Check", False, f"Status: {r.status_code}")
except Exception as e:
    log("Health Check", False, str(e))

# TEST 2: API Info
print("\nTEST 2: API Info")
print("-"*70)
try:
    r = requests.get(f"{API_URL}/", timeout=10)
    if r.status_code == 200:
        data = r.json()
        log("API Info", True, f"v{data.get('version')} - {data.get('name')}")
    else:
        log("API Info", False, f"Status: {r.status_code}")
except Exception as e:
    log("API Info", False, str(e))

# TEST 3: Plant Catalog
print("\nTEST 3: Plant Catalog")
print("-"*70)
try:
    r = requests.get(f"{API_URL}/plants/catalog", timeout=10)
    if r.status_code == 200:
        data = r.json()
        plants = data.get('plants', {})
        log("Plant Catalog", True, f"Found {len(plants)} plants")
        for name in list(plants.keys())[:3]:
            print(f"   - {plants[name].get('name')}")
    else:
        log("Plant Catalog", False, f"Status: {r.status_code}")
        print(f"   Response: {r.text[:200]}")
except Exception as e:
    log("Plant Catalog", False, str(e))

# TEST 4: Register Plant (Auto-creates user)
print("\nTEST 4: Register Plant (Auto-creates User)")
print("-"*70)
plant_id = None
try:
    data = {
        'user_id': TEST_USER_ID,
        'name': 'Test User',
        'email': f'{TEST_USER_ID}@test.com',
        'plant_type': 'bamboo',
        'location': 'Mumbai, India',
        'gps_latitude': 19.0760,
        'gps_longitude': 72.8777
    }
    r = requests.post(f"{API_URL}/plants/register", data=data, timeout=10)
    if r.status_code in [200, 201]:
        result = r.json()
        plant_id = result.get('plant_id')
        log("Register Plant", True, f"ID: {plant_id}, Points: +{result.get('points_earned')}")
        print(f"   User: {result.get('user_id')}")
        print(f"   Total Points: {result.get('total_points')}")
    else:
        log("Register Plant", False, f"Status: {r.status_code}")
        print(f"   Response: {r.text[:300]}")
except Exception as e:
    log("Register Plant", False, str(e))

if not plant_id:
    print("\n❌ No plant_id - cannot continue")
    exit(1)

# TEST 5: Get User Points
print("\nTEST 5: Get User Points")
print("-"*70)
try:
    r = requests.get(f"{API_URL}/users/{TEST_USER_ID}/points", timeout=10)
    if r.status_code == 200:
        data = r.json()
        points = data.get('points', {})
        log("User Points", True, f"Total: {points.get('total_points')} pts")
        print(f"   Level: {data.get('level', {}).get('level_name')}")
        print(f"   Plants: {data.get('stats', {}).get('total_plants')}")
    else:
        log("User Points", False, f"Status: {r.status_code}")
except Exception as e:
    log("User Points", False, str(e))

# TEST 6: Get Plant Details
print("\nTEST 6: Get Plant Details")
print("-"*70)
try:
    r = requests.get(f"{API_URL}/plants/{plant_id}", timeout=10)
    if r.status_code == 200:
        data = r.json()
        plant = data.get('plant', {})
        log("Plant Details", True, f"Health: {plant.get('health_score')}/100")
        print(f"   Type: {plant.get('plant_type')}")
        print(f"   Status: {plant.get('status')}")
    else:
        log("Plant Details", False, f"Status: {r.status_code}")
except Exception as e:
    log("Plant Details", False, str(e))

# TEST 7: Upload Planting Photo
print("\nTEST 7: Upload Planting Photo")
print("-"*70)
try:
    files = {'image': ('plant.jpg', create_test_image(), 'image/jpeg')}
    data = {'gps_latitude': 19.0760, 'gps_longitude': 72.8777}
    r = requests.post(f"{API_URL}/plants/{plant_id}/planting-photo", files=files, data=data, timeout=15)
    if r.status_code == 200:
        result = r.json()
        log("Upload Photo", True, f"Points: +{result.get('points_earned')}")
        print(f"   Total Points: {result.get('total_points')}")
    else:
        log("Upload Photo", False, f"Status: {r.status_code}")
        print(f"   Response: {r.text[:300]}")
except Exception as e:
    log("Upload Photo", False, str(e))

# TEST 8: Water Plant
print("\nTEST 8: Water Plant")
print("-"*70)
try:
    # Create dummy video file
    files = {'video': ('water.mp4', create_test_image(), 'video/mp4')}
    data = {'gps_latitude': 19.0760, 'gps_longitude': 72.8777}
    r = requests.post(f"{API_URL}/plants/{plant_id}/water", files=files, data=data, timeout=15)
    if r.status_code == 200:
        result = r.json()
        log("Water Plant", True, f"Points: +{result.get('points_earned')}, Streak: {result.get('streak')}")
    else:
        log("Water Plant", False, f"Status: {r.status_code}")
        print(f"   Response: {r.text[:300]}")
except Exception as e:
    log("Water Plant", False, str(e))

# TEST 9: Duplicate Watering (Should Fail)
print("\nTEST 9: Duplicate Watering (Should Reject)")
print("-"*70)
try:
    files = {'video': ('water2.mp4', create_test_image(), 'video/mp4')}
    data = {'gps_latitude': 19.0760, 'gps_longitude': 72.8777}
    r = requests.post(f"{API_URL}/plants/{plant_id}/water", files=files, data=data, timeout=15)
    if r.status_code == 400:
        result = r.json()
        log("Duplicate Rejection", True, f"Correctly rejected: {result.get('error')}")
    elif r.status_code == 200:
        log("Duplicate Rejection", False, "Should have rejected!")
    else:
        log("Duplicate Rejection", True, f"Status: {r.status_code}")
except Exception as e:
    log("Duplicate Rejection", False, str(e))

# TEST 10: Health Scan
print("\nTEST 10: Health Scan")
print("-"*70)
try:
    files = {'image': ('scan.jpg', create_test_image(), 'image/jpeg')}
    data = {'gps_latitude': 19.0760, 'gps_longitude': 72.8777}
    r = requests.post(f"{API_URL}/plants/{plant_id}/health-scan", files=files, data=data, timeout=15)
    if r.status_code == 200:
        result = r.json()
        health = result.get('health_analysis', {})
        log("Health Scan", True, f"Score: {health.get('health_score')}/100, Points: +{result.get('points_earned')}")
    else:
        log("Health Scan", False, f"Status: {r.status_code}")
        print(f"   Response: {r.text[:300]}")
except Exception as e:
    log("Health Scan", False, str(e))

# TEST 11: Get User History
print("\nTEST 11: Get User History")
print("-"*70)
try:
    r = requests.get(f"{API_URL}/users/{TEST_USER_ID}/history?limit=10", timeout=10)
    if r.status_code == 200:
        data = r.json()
        txns = data.get('transactions', [])
        log("User History", True, f"Found {len(txns)} transactions")
        for txn in txns[:3]:
            print(f"   - {txn.get('transaction_type')}: +{txn.get('points')} pts")
    else:
        log("User History", False, f"Status: {r.status_code}")
except Exception as e:
    log("User History", False, str(e))

# TEST 12: Get User's Plants
print("\nTEST 12: Get User's Plants")
print("-"*70)
try:
    r = requests.get(f"{API_URL}/plants/user/{TEST_USER_ID}", timeout=10)
    if r.status_code == 200:
        data = r.json()
        plants = data.get('plants', [])
        log("User's Plants", True, f"Found {len(plants)} plant(s)")
        for p in plants:
            print(f"   - {p.get('plant_type')}: Health {p.get('health_score')}/100")
    else:
        log("User's Plants", False, f"Status: {r.status_code}")
except Exception as e:
    log("User's Plants", False, str(e))

# TEST 13: System Stats
print("\nTEST 13: System Stats")
print("-"*70)
try:
    r = requests.get(f"{API_URL}/stats", timeout=10)
    if r.status_code == 200:
        data = r.json()
        stats = data.get('stats', {})
        log("System Stats", True, f"Users: {stats.get('total_users')}, Plants: {stats.get('total_plants')}")
        print(f"   CO2 Offset: {stats.get('total_co2_offset_kg', 0):.2f} kg")
    else:
        log("System Stats", False, f"Status: {r.status_code}")
except Exception as e:
    log("System Stats", False, str(e))

# TEST 14: CSR Dashboard
print("\nTEST 14: CSR Dashboard")
print("-"*70)
try:
    r = requests.get(f"{API_URL}/stats/csr", timeout=10)
    if r.status_code == 200:
        data = r.json()
        csr = data.get('csr_data', {})
        monthly = csr.get('monthly_summary', {})
        log("CSR Dashboard", True, f"Monthly Plants: {monthly.get('plants_registered', 0)}")
    else:
        log("CSR Dashboard", False, f"Status: {r.status_code}")
except Exception as e:
    log("CSR Dashboard", False, str(e))

# TEST 15: Invalid Plant ID
print("\nTEST 15: Invalid Plant ID (Error Handling)")
print("-"*70)
try:
    r = requests.get(f"{API_URL}/plants/INVALID_123", timeout=10)
    if r.status_code == 404:
        log("Error Handling", True, "Correctly returned 404")
    else:
        log("Error Handling", False, f"Status: {r.status_code}")
except Exception as e:
    log("Error Handling", False, str(e))

# SUMMARY
print("\n" + "="*70)
print("📊 TEST SUMMARY")
print("="*70)
print(f"Total:  {results['total']}")
print(f"✅ Pass: {results['passed']}")
print(f"❌ Fail: {results['failed']}")
rate = (results['passed']/results['total']*100) if results['total'] > 0 else 0
print(f"Rate:   {rate:.1f}%")
print(f"\nUser ID: {TEST_USER_ID}")
print(f"Plant ID: {plant_id}")

# Save results
output = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to: {output}")

print("="*70)
if results['failed'] == 0:
    print("🎉 ALL TESTS PASSED!")
else:
    print(f"⚠️  {results['failed']} test(s) failed")
print("="*70)
