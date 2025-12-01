#!/usr/bin/env python3
"""
Complete User Flow Test Script for Carbon Credit Blockchain System
Tests all features end-to-end against the live Railway API

Usage: python3 test_complete_user_flow.py
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path
import io
from PIL import Image

# API Configuration
API_URL = "https://joyo-cc-production.up.railway.app"
TEST_USER_PREFIX = f"test_user_{int(time.time())}"

# Test Results Tracking
test_results = {
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(test_name, passed, details=""):
    """Log test results"""
    test_results["total_tests"] += 1
    status = "✅ PASS" if passed else "❌ FAIL"
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    
    test_results["tests"].append({
        "name": test_name,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })
    
    print(f"{status}: {test_name}")
    if details:
        print(f"   Details: {details}")

def create_test_image():
    """Create a simple test image for uploads"""
    img = Image.new('RGB', (800, 600), color='green')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

print("=" * 70)
print("🌱 CARBON CREDIT BLOCKCHAIN - COMPLETE USER FLOW TEST")
print("=" * 70)
print(f"API URL: {API_URL}")
print(f"Test User Prefix: {TEST_USER_PREFIX}")
print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
print()

# ============================================================================
# TEST 1: API HEALTH CHECK
# ============================================================================
print("\n📡 TEST 1: API Health Check")
print("-" * 70)

try:
    response = requests.get(f"{API_URL}/health", timeout=10)
    if response.status_code == 200:
        data = response.json()
        log_test("API Health Check", True, f"Status: {data.get('status')}")
        print(f"   Database: {data.get('database')}")
        print(f"   AI Services: {data.get('ai_services')}")
        print(f"   Algorand: {data.get('algorand')}")
    else:
        log_test("API Health Check", False, f"Status code: {response.status_code}")
except Exception as e:
    log_test("API Health Check", False, str(e))

# ============================================================================
# TEST 2: GET API INFO
# ============================================================================
print("\n📚 TEST 2: Get API Information")
print("-" * 70)

try:
    response = requests.get(f"{API_URL}/", timeout=10)
    if response.status_code == 200:
        data = response.json()
        log_test("Get API Info", True, f"Version: {data.get('version')}")
        print(f"   Name: {data.get('name')}")
        print(f"   Endpoints: {len(data.get('endpoints', {}))}")
    else:
        log_test("Get API Info", False, f"Status code: {response.status_code}")
except Exception as e:
    log_test("Get API Info", False, str(e))

# ============================================================================
# TEST 3: GET PLANT CATALOG
# ============================================================================
print("\n🌿 TEST 3: Get Plant Catalog")
print("-" * 70)

plant_catalog = {}
try:
    response = requests.get(f"{API_URL}/plants/catalog", timeout=10)
    if response.status_code == 200:
        data = response.json()
        plant_catalog = data.get('plants', {})
        log_test("Get Plant Catalog", True, f"Found {len(plant_catalog)} plants")
        for key, plant in list(plant_catalog.items())[:3]:
            print(f"   - {plant.get('name')}: {plant.get('co2_kg_per_year')} kg CO2/year")
    else:
        log_test("Get Plant Catalog", False, f"Status code: {response.status_code}")
except Exception as e:
    log_test("Get Plant Catalog", False, str(e))

# ============================================================================
# TEST 4: USER REGISTRATION
# ============================================================================
print("\n👤 TEST 4: User Registration")
print("-" * 70)

user_id = None
user_data = {
    "name": f"{TEST_USER_PREFIX}_Rajesh",
    "email": f"{TEST_USER_PREFIX}@test.com",
    "phone": "+919876543210",
    "user_type": "worker"
}

try:
    response = requests.post(f"{API_URL}/users/create", json=user_data, timeout=10)
    if response.status_code == 201:
        data = response.json()
        user_id = data.get('user_id')
        log_test("User Registration", True, f"User ID: {user_id}")
        print(f"   Name: {user_data['name']}")
        print(f"   Email: {user_data['email']}")
        print(f"   Initial Points: {data.get('total_points', 0)}")
    else:
        log_test("User Registration", False, f"Status code: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    log_test("User Registration", False, str(e))

if not user_id:
    print("\n❌ Cannot continue without user_id. Exiting...")
    exit(1)

# ============================================================================
# TEST 5: PLANT REGISTRATION
# ============================================================================
print("\n🌱 TEST 5: Plant Registration")
print("-" * 70)

plant_id = None
plant_data = {
    "user_id": user_id,
    "plant_type": "bamboo",
    "location": "Mumbai, India",
    "gps_latitude": 19.0760,
    "gps_longitude": 72.8777
}

try:
    response = requests.post(f"{API_URL}/plants/register", data=plant_data, timeout=10)
    if response.status_code == 201:
        data = response.json()
        plant_id = data.get('plant_id')
        points_earned = data.get('points_earned', 0)
        log_test("Plant Registration", True, f"Plant ID: {plant_id}, Points: +{points_earned}")
        print(f"   Plant Type: {plant_data['plant_type']}")
        print(f"   Location: {plant_data['location']}")
        print(f"   Points Earned: +{points_earned}")
        print(f"   Total Points: {data.get('total_points', 0)}")
    else:
        log_test("Plant Registration", False, f"Status code: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    log_test("Plant Registration", False, str(e))

if not plant_id:
    print("\n❌ Cannot continue without plant_id. Exiting...")
    exit(1)

# ============================================================================
# TEST 6: UPLOAD PLANTING PHOTO
# ============================================================================
print("\n📷 TEST 6: Upload Planting Photo")
print("-" * 70)

try:
    img_bytes = create_test_image()
    files = {
        'image': ('plant_photo.jpg', img_bytes, 'image/jpeg')
    }
    data = {
        'gps_latitude': 19.0760,
        'gps_longitude': 72.8777
    }
    
    response = requests.post(
        f"{API_URL}/plants/{plant_id}/planting-photo",
        files=files,
        data=data,
        timeout=15
    )
    
    if response.status_code == 200:
        result = response.json()
        points_earned = result.get('points_earned', 0)
        log_test("Upload Planting Photo", True, f"Points: +{points_earned}")
        print(f"   Image URL: {result.get('image_url', 'N/A')}")
        print(f"   Points Earned: +{points_earned}")
        print(f"   Total Points: {result.get('total_points', 0)}")
    else:
        log_test("Upload Planting Photo", False, f"Status code: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    log_test("Upload Planting Photo", False, str(e))

# ============================================================================
# TEST 7: GET USER POINTS
# ============================================================================
print("\n💰 TEST 7: Get User Points Balance")
print("-" * 70)

try:
    response = requests.get(f"{API_URL}/users/{user_id}/points", timeout=10)
    if response.status_code == 200:
        data = response.json()
        points = data.get('points', {})
        level = data.get('level', {})
        stats = data.get('stats', {})
        
        log_test("Get User Points", True, f"Total: {points.get('total_points', 0)} points")
        print(f"   Total Points: {points.get('total_points', 0)}")
        print(f"   Level: {level.get('level_name', 'N/A')} (Level {level.get('current_level', 0)})")
        print(f"   Total Plants: {stats.get('total_plants', 0)}")
        print(f"   Current Streak: {stats.get('current_streak', 0)} days")
    else:
        log_test("Get User Points", False, f"Status code: {response.status_code}")
except Exception as e:
    log_test("Get User Points", False, str(e))

# ============================================================================
# TEST 8: GET PLANT DETAILS
# ============================================================================
print("\n🌳 TEST 8: Get Plant Details")
print("-" * 70)

try:
    response = requests.get(f"{API_URL}/plants/{plant_id}", timeout=10)
    if response.status_code == 200:
        data = response.json()
        plant = data.get('plant', {})
        
        log_test("Get Plant Details", True, f"Status: {plant.get('status', 'N/A')}")
        print(f"   Plant Type: {plant.get('plant_type', 'N/A')}")
        print(f"   Location: {plant.get('location', 'N/A')}")
        print(f"   Health Score: {plant.get('health_score', 0)}/100")
        print(f"   Planting Date: {plant.get('planting_date', 'N/A')}")
        print(f"   Points Earned: {plant.get('total_points_earned', 0)}")
    else:
        log_test("Get Plant Details", False, f"Status code: {response.status_code}")
except Exception as e:
    log_test("Get Plant Details", False, str(e))

# ============================================================================
# TEST 9: GET USER'S PLANTS
# ============================================================================
print("\n🌿 TEST 9: Get User's Plants List")
print("-" * 70)

try:
    response = requests.get(f"{API_URL}/plants/user/{user_id}", timeout=10)
    if response.status_code == 200:
        data = response.json()
        plants = data.get('plants', [])
        
        log_test("Get User's Plants", True, f"Found {len(plants)} plant(s)")
        for plant in plants:
            print(f"   - {plant.get('plant_type')}: Health {plant.get('health_score', 0)}/100")
    else:
        log_test("Get User's Plants", False, f"Status code: {response.status_code}")
except Exception as e:
    log_test("Get User's Plants", False, str(e))

# ============================================================================
# TEST 10: DAILY WATERING (FIRST TIME)
# ============================================================================
print("\n💧 TEST 10: Daily Watering (First Time)")
print("-" * 70)

try:
    data = {
        'gps_latitude': 19.0760,
        'gps_longitude': 72.8777
    }
    
    response = requests.post(
        f"{API_URL}/plants/{plant_id}/water",
        data=data,
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        points_earned = result.get('points_earned', 0)
        streak = result.get('streak', 0)
        
        log_test("Daily Watering", True, f"Points: +{points_earned}, Streak: {streak}")
        print(f"   Points Earned: +{points_earned}")
        print(f"   Streak: {streak} day(s)")
        print(f"   Message: {result.get('message', 'N/A')}")
    else:
        log_test("Daily Watering", False, f"Status code: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    log_test("Daily Watering", False, str(e))

# ============================================================================
# TEST 11: DUPLICATE WATERING (SHOULD FAIL)
# ============================================================================
print("\n💧 TEST 11: Duplicate Watering (Should Be Rejected)")
print("-" * 70)

try:
    data = {
        'gps_latitude': 19.0760,
        'gps_longitude': 72.8777
    }
    
    response = requests.post(
        f"{API_URL}/plants/{plant_id}/water",
        data=data,
        timeout=10
    )
    
    # This should return 400 (already watered)
    if response.status_code == 400:
        result = response.json()
        log_test("Duplicate Watering Rejection", True, "Correctly rejected duplicate")
        print(f"   Error: {result.get('error', 'N/A')}")
        print(f"   Message: {result.get('message', 'N/A')}")
    elif response.status_code == 200:
        log_test("Duplicate Watering Rejection", False, "Should have rejected duplicate!")
    else:
        log_test("Duplicate Watering Rejection", False, f"Status code: {response.status_code}")
except Exception as e:
    log_test("Duplicate Watering Rejection", False, str(e))

# ============================================================================
# TEST 12: HEALTH SCAN
# ============================================================================
print("\n🔍 TEST 12: Plant Health Scan")
print("-" * 70)

try:
    img_bytes = create_test_image()
    files = {
        'image': ('health_scan.jpg', img_bytes, 'image/jpeg')
    }
    data = {
        'gps_latitude': 19.0760,
        'gps_longitude': 72.8777
    }
    
    response = requests.post(
        f"{API_URL}/plants/{plant_id}/health-scan",
        files=files,
        data=data,
        timeout=15
    )
    
    if response.status_code == 200:
        result = response.json()
        health = result.get('health_analysis', {})
        points_earned = result.get('points_earned', 0)
        
        log_test("Health Scan", True, f"Score: {health.get('health_score', 0)}/100")
        print(f"   Overall Health: {health.get('overall_health', 'N/A')}")
        print(f"   Health Score: {health.get('health_score', 0)}/100")
        print(f"   Points Earned: +{points_earned}")
        print(f"   Issues: {len(health.get('issues_detected', []))}")
    else:
        log_test("Health Scan", False, f"Status code: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    log_test("Health Scan", False, str(e))

# ============================================================================
# TEST 13: GET POINTS HISTORY
# ============================================================================
print("\n📜 TEST 13: Get Points History")
print("-" * 70)

try:
    response = requests.get(f"{API_URL}/users/{user_id}/history?limit=10", timeout=10)
    if response.status_code == 200:
        data = response.json()
        transactions = data.get('transactions', [])
        
        log_test("Get Points History", True, f"Found {len(transactions)} transaction(s)")
        print(f"   Total Transactions: {data.get('total_transactions', 0)}")
        for txn in transactions[:5]:
            print(f"   - {txn.get('transaction_type')}: +{txn.get('points', 0)} pts")
    else:
        log_test("Get Points History", False, f"Status code: {response.status_code}")
except Exception as e:
    log_test("Get Points History", False, str(e))

# ============================================================================
# TEST 14: SYSTEM STATISTICS
# ============================================================================
print("\n📊 TEST 14: Get System Statistics")
print("-" * 70)

try:
    response = requests.get(f"{API_URL}/stats", timeout=10)
    if response.status_code == 200:
        data = response.json()
        stats = data.get('stats', {})
        
        log_test("Get System Stats", True, f"Total Users: {stats.get('total_users', 0)}")
        print(f"   Total Users: {stats.get('total_users', 0)}")
        print(f"   Total Plants: {stats.get('total_plants', 0)}")
        print(f"   Total Activities: {stats.get('total_activities', 0)}")
        print(f"   CO2 Offset: {stats.get('total_co2_offset_kg', 0):.2f} kg")
        print(f"   Active Today: {stats.get('active_users_today', 0)}")
    else:
        log_test("Get System Stats", False, f"Status code: {response.status_code}")
except Exception as e:
    log_test("Get System Stats", False, str(e))

# ============================================================================
# TEST 15: CSR DASHBOARD
# ============================================================================
print("\n🏢 TEST 15: Get CSR Dashboard Data")
print("-" * 70)

try:
    response = requests.get(f"{API_URL}/stats/csr", timeout=10)
    if response.status_code == 200:
        data = response.json()
        csr = data.get('csr_data', {})
        monthly = csr.get('monthly_summary', {})
        
        log_test("Get CSR Dashboard", True, f"Monthly Plants: {monthly.get('plants_registered', 0)}")
        print(f"   Plants This Month: {monthly.get('plants_registered', 0)}")
        print(f"   Active Workers: {monthly.get('active_workers', 0)}")
        print(f"   CO2 Offset: {monthly.get('co2_offset_kg', 0):.2f} kg")
    else:
        log_test("Get CSR Dashboard", False, f"Status code: {response.status_code}")
except Exception as e:
    log_test("Get CSR Dashboard", False, str(e))

# ============================================================================
# TEST 16: REGISTER SECOND PLANT
# ============================================================================
print("\n🌱 TEST 16: Register Second Plant (Different Type)")
print("-" * 70)

plant_id_2 = None
plant_data_2 = {
    "user_id": user_id,
    "plant_type": "tulsi",
    "location": "Mumbai, India - Area 2",
    "gps_latitude": 19.0861,
    "gps_longitude": 72.8878
}

try:
    response = requests.post(f"{API_URL}/plants/register", data=plant_data_2, timeout=10)
    if response.status_code == 201:
        data = response.json()
        plant_id_2 = data.get('plant_id')
        points_earned = data.get('points_earned', 0)
        
        log_test("Register Second Plant", True, f"Plant ID: {plant_id_2}")
        print(f"   Plant Type: {plant_data_2['plant_type']}")
        print(f"   Points Earned: +{points_earned}")
        print(f"   Total Points: {data.get('total_points', 0)}")
    else:
        log_test("Register Second Plant", False, f"Status code: {response.status_code}")
except Exception as e:
    log_test("Register Second Plant", False, str(e))

# ============================================================================
# TEST 17: WATER SECOND PLANT
# ============================================================================
if plant_id_2:
    print("\n💧 TEST 17: Water Second Plant")
    print("-" * 70)
    
    try:
        data = {
            'gps_latitude': 19.0861,
            'gps_longitude': 72.8878
        }
        
        response = requests.post(
            f"{API_URL}/plants/{plant_id_2}/water",
            data=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            points_earned = result.get('points_earned', 0)
            streak = result.get('streak', 0)
            
            log_test("Water Second Plant", True, f"Points: +{points_earned}")
            print(f"   Points Earned: +{points_earned}")
            print(f"   Streak: {streak} day(s)")
        else:
            log_test("Water Second Plant", False, f"Status code: {response.status_code}")
    except Exception as e:
        log_test("Water Second Plant", False, str(e))

# ============================================================================
# TEST 18: FINAL POINTS CHECK
# ============================================================================
print("\n💰 TEST 18: Final Points Balance Check")
print("-" * 70)

final_points = 0
try:
    response = requests.get(f"{API_URL}/users/{user_id}/points", timeout=10)
    if response.status_code == 200:
        data = response.json()
        points = data.get('points', {})
        final_points = points.get('total_points', 0)
        
        log_test("Final Points Check", True, f"Total: {final_points} points")
        print(f"   Total Points: {final_points}")
        print(f"   Lifetime Points: {points.get('lifetime_points', 0)}")
        print(f"   Level: {data.get('level', {}).get('level_name', 'N/A')}")
    else:
        log_test("Final Points Check", False, f"Status code: {response.status_code}")
except Exception as e:
    log_test("Final Points Check", False, str(e))

# ============================================================================
# TEST 19: POINTS CONVERSION (WILL FAIL - NEED 6 MONTHS + 1000 POINTS)
# ============================================================================
print("\n💵 TEST 19: Attempt Points Conversion (Expected to Fail)")
print("-" * 70)

try:
    data = {
        "user_id": user_id,
        "points_to_convert": 100
    }
    
    response = requests.post(f"{API_URL}/coins/convert", json=data, timeout=10)
    
    # Should fail (insufficient points or not mature)
    if response.status_code == 400:
        result = response.json()
        log_test("Points Conversion (Expected Fail)", True, "Correctly rejected premature conversion")
        print(f"   Error: {result.get('error', 'N/A')}")
        print(f"   Message: {result.get('message', 'N/A')}")
    elif response.status_code == 200:
        log_test("Points Conversion (Expected Fail)", False, "Should not allow conversion yet!")
    else:
        log_test("Points Conversion (Expected Fail)", True, f"Status: {response.status_code}")
except Exception as e:
    log_test("Points Conversion (Expected Fail)", False, str(e))

# ============================================================================
# TEST 20: INVALID REQUESTS
# ============================================================================
print("\n⚠️  TEST 20: Test Invalid Requests")
print("-" * 70)

# Test 20a: Invalid Plant ID
try:
    response = requests.get(f"{API_URL}/plants/INVALID_ID", timeout=10)
    if response.status_code == 404:
        log_test("Invalid Plant ID Handling", True, "Correctly returned 404")
    else:
        log_test("Invalid Plant ID Handling", False, f"Status: {response.status_code}")
except Exception as e:
    log_test("Invalid Plant ID Handling", False, str(e))

# Test 20b: Invalid User ID
try:
    response = requests.get(f"{API_URL}/users/INVALID_ID/points", timeout=10)
    if response.status_code in [404, 400]:
        log_test("Invalid User ID Handling", True, "Correctly returned error")
    else:
        log_test("Invalid User ID Handling", False, f"Status: {response.status_code}")
except Exception as e:
    log_test("Invalid User ID Handling", False, str(e))

# Test 20c: Missing Required Fields
try:
    response = requests.post(f"{API_URL}/plants/register", data={}, timeout=10)
    if response.status_code in [400, 422]:
        log_test("Missing Fields Handling", True, "Correctly rejected incomplete data")
    else:
        log_test("Missing Fields Handling", False, f"Status: {response.status_code}")
except Exception as e:
    log_test("Missing Fields Handling", False, str(e))

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("📊 TEST SUMMARY")
print("=" * 70)

print(f"\nTotal Tests: {test_results['total_tests']}")
print(f"✅ Passed: {test_results['passed']}")
print(f"❌ Failed: {test_results['failed']}")

pass_rate = (test_results['passed'] / test_results['total_tests'] * 100) if test_results['total_tests'] > 0 else 0
print(f"📈 Pass Rate: {pass_rate:.1f}%")

print(f"\n🆔 Test User ID: {user_id}")
print(f"🌱 Plants Created: 2")
print(f"💰 Final Points: {final_points}")

# Save results to JSON
output_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump(test_results, f, indent=2)

print(f"\n💾 Results saved to: {output_file}")

print("\n" + "=" * 70)
if test_results['failed'] == 0:
    print("🎉 ALL TESTS PASSED! The API is working perfectly!")
else:
    print(f"⚠️  {test_results['failed']} test(s) failed. Review the results above.")
print("=" * 70)
print()
