#!/usr/bin/env python3
"""
Comprehensive Test Suite for Joyo Environment Mini App
Tests all implemented features including AI and database
"""

import os
import sys
from datetime import datetime
import json

print("="*80)
print("🧪 JOYO COMPREHENSIVE TEST SUITE")
print("="*80)
print(f"Started: {datetime.now().isoformat()}")
print()

# Test results tracker
test_results = {
    'passed': 0,
    'failed': 0,
    'skipped': 0,
    'tests': []
}

def log_test(name, status, message=""):
    """Log test result"""
    icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{icon} {name}: {status}")
    if message:
        print(f"   {message}")
    
    test_results['tests'].append({
        'name': name,
        'status': status,
        'message': message,
        'timestamp': datetime.now().isoformat()
    })
    
    if status == "PASS":
        test_results['passed'] += 1
    elif status == "FAIL":
        test_results['failed'] += 1
    else:
        test_results['skipped'] += 1

print("\n" + "="*80)
print("TEST 1: DATABASE CONNECTION & SCHEMA")
print("="*80 + "\n")

try:
    from database_postgres import db
    log_test("Import database_postgres", "PASS", "PostgreSQL database module imported")
    
    # Test database connection
    try:
        stats = db.get_stats()
        log_test("Database connection", "PASS", f"Connected to PostgreSQL")
        log_test("Get stats query", "PASS", f"Users: {stats['total_users']}, Plants: {stats['total_plants']}")
    except Exception as e:
        log_test("Database connection", "FAIL", str(e))
        
except Exception as e:
    log_test("Import database_postgres", "FAIL", str(e))

print("\n" + "="*80)
print("TEST 2: USER & PLANT REGISTRATION")
print("="*80 + "\n")

try:
    # Create test user
    test_user_id = f"TEST_USER_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        result = db.create_user(
            user_id=test_user_id,
            name="Test User",
            email="test@joyo.app",
            location="Mumbai, India"
        )
        log_test("Create user", "PASS", f"User ID: {test_user_id}")
    except Exception as e:
        log_test("Create user", "FAIL", str(e))
    
    # Get user
    try:
        user = db.get_user(test_user_id)
        if user and user['user_id'] == test_user_id:
            log_test("Get user", "PASS", f"Retrieved user: {user['name']}")
        else:
            log_test("Get user", "FAIL", "User not found or mismatch")
    except Exception as e:
        log_test("Get user", "FAIL", str(e))
    
    # Register plant
    test_plant_id = f"PLANT_TEST_{datetime.now().strftime('%H%M%S')}"
    
    try:
        result = db.register_plant(
            plant_id=test_plant_id,
            user_id=test_user_id,
            plant_type="bamboo",
            location="Mumbai, Maharashtra, India",
            gps_latitude=19.0760,
            gps_longitude=72.8777,
            plant_species="Bambusa vulgaris"
        )
        log_test("Register plant", "PASS", f"Plant ID: {test_plant_id}")
    except Exception as e:
        log_test("Register plant", "FAIL", str(e))
    
    # Get plant
    try:
        plant = db.get_plant(test_plant_id)
        if plant and plant['plant_id'] == test_plant_id:
            log_test("Get plant", "PASS", f"Retrieved plant: {plant['plant_type']}")
        else:
            log_test("Get plant", "FAIL", "Plant not found or mismatch")
    except Exception as e:
        log_test("Get plant", "FAIL", str(e))

except Exception as e:
    log_test("User & Plant registration setup", "FAIL", str(e))

print("\n" + "="*80)
print("TEST 3: POINTS SYSTEM")
print("="*80 + "\n")

try:
    # Award points for plant purchase
    txn_id = f"TXN_TEST_{datetime.now().strftime('%H%M%S')}"
    
    try:
        result = db.add_points(
            transaction_id=txn_id,
            user_id=test_user_id,
            points=30,
            transaction_type='plant_purchase',
            description='Test plant purchase',
            plant_id=test_plant_id
        )
        
        if result['success'] and result['points_added'] == 30:
            log_test("Add points (plant purchase)", "PASS", f"Awarded 30 points, Total: {result['total_points']}")
        else:
            log_test("Add points", "FAIL", "Points not added correctly")
    except Exception as e:
        log_test("Add points", "FAIL", str(e))
    
    # Get points history
    try:
        history = db.get_user_points_history(test_user_id, limit=10)
        if len(history) > 0:
            log_test("Get points history", "PASS", f"Found {len(history)} transactions")
        else:
            log_test("Get points history", "FAIL", "No transactions found")
    except Exception as e:
        log_test("Get points history", "FAIL", str(e))
    
    # Check user total points
    try:
        user = db.get_user(test_user_id)
        if user['total_points'] >= 30:
            log_test("User total points update", "PASS", f"User has {user['total_points']} points")
        else:
            log_test("User total points update", "FAIL", f"Expected >=30, got {user['total_points']}")
    except Exception as e:
        log_test("User total points update", "FAIL", str(e))

except Exception as e:
    log_test("Points system setup", "FAIL", str(e))

print("\n" + "="*80)
print("TEST 4: WATERING STREAKS")
print("="*80 + "\n")

try:
    # Update watering streak
    try:
        streak = db.update_watering_streak(test_plant_id)
        if streak['current_streak'] >= 1:
            log_test("Update watering streak", "PASS", 
                    f"Streak: {streak['current_streak']}, Bonus: {streak['bonus_points']}")
        else:
            log_test("Update watering streak", "FAIL", "Streak not updated")
    except Exception as e:
        log_test("Update watering streak", "FAIL", str(e))
    
    # Try watering again same day (should be rejected)
    try:
        streak2 = db.update_watering_streak(test_plant_id)
        if 'message' in streak2 and 'already watered' in streak2['message'].lower():
            log_test("Duplicate watering check", "PASS", "Correctly rejected duplicate watering")
        else:
            log_test("Duplicate watering check", "FAIL", "Should reject duplicate watering")
    except Exception as e:
        log_test("Duplicate watering check", "FAIL", str(e))

except Exception as e:
    log_test("Watering streaks setup", "FAIL", str(e))

print("\n" + "="*80)
print("TEST 5: ACTIVITY RECORDING")
print("="*80 + "\n")

try:
    activity_id = f"ACT_TEST_{datetime.now().strftime('%H%M%S')}"
    
    try:
        result = db.record_activity(
            activity_id=activity_id,
            plant_id=test_plant_id,
            user_id=test_user_id,
            activity_type='watering',
            description='Test watering activity',
            gps_latitude=19.0760,
            gps_longitude=72.8777,
            points_earned=5,
            metadata=json.dumps({'test': True})
        )
        
        if result['success']:
            log_test("Record activity", "PASS", f"Activity ID: {activity_id}")
        else:
            log_test("Record activity", "FAIL", "Activity not recorded")
    except Exception as e:
        log_test("Record activity", "FAIL", str(e))
    
    # Get plant activities
    try:
        activities = db.get_plant_activities(test_plant_id, limit=10)
        if len(activities) > 0:
            log_test("Get plant activities", "PASS", f"Found {len(activities)} activities")
        else:
            log_test("Get plant activities", "FAIL", "No activities found")
    except Exception as e:
        log_test("Get plant activities", "FAIL", str(e))

except Exception as e:
    log_test("Activity recording setup", "FAIL", str(e))

print("\n" + "="*80)
print("TEST 6: AI SERVICES - PLANT RECOGNITION")
print("="*80 + "\n")

try:
    from joyo_ai_services.plant_recognition import PlantRecognitionAI
    log_test("Import PlantRecognitionAI", "PASS")
    
    try:
        plant_ai = PlantRecognitionAI()
        log_test("Initialize PlantRecognitionAI", "PASS")
    except Exception as e:
        log_test("Initialize PlantRecognitionAI", "FAIL", str(e))
        plant_ai = None
    
    # Test plant catalog
    if plant_ai:
        try:
            catalog = plant_ai.get_plant_catalog()
            if catalog['total_plants'] > 0:
                log_test("Get plant catalog", "PASS", 
                        f"Found {catalog['total_plants']} air-purifying plants")
            else:
                log_test("Get plant catalog", "FAIL", "Empty catalog")
        except Exception as e:
            log_test("Get plant catalog", "FAIL", str(e))
    
    # Check OpenAI API key
    if os.getenv('OPENAI_API_KEY'):
        log_test("OpenAI API key", "PASS", "API key configured")
    else:
        log_test("OpenAI API key", "SKIP", "No API key - live AI tests will be skipped")
    
except Exception as e:
    log_test("AI Services import", "FAIL", str(e))

print("\n" + "="*80)
print("TEST 7: AI SERVICES - PLANT HEALTH")
print("="*80 + "\n")

try:
    from joyo_ai_services.plant_health import PlantHealthAI
    log_test("Import PlantHealthAI", "PASS")
    
    try:
        health_ai = PlantHealthAI()
        log_test("Initialize PlantHealthAI", "PASS")
    except Exception as e:
        log_test("Initialize PlantHealthAI", "FAIL", str(e))
        health_ai = None
    
    # Test organic remedies
    if health_ai:
        try:
            remedy = health_ai.suggest_organic_fertilizer(
                deficiency_type='nitrogen_deficiency',
                plant_type='bamboo'
            )
            if remedy['success']:
                log_test("Get organic remedy", "PASS", 
                        f"Remedy: {remedy['deficiency']}, Points: {remedy['points_reward']}")
            else:
                log_test("Get organic remedy", "FAIL", remedy.get('message', 'Unknown error'))
        except Exception as e:
            log_test("Get organic remedy", "FAIL", str(e))
        
        # Check available remedies
        try:
            remedies_count = len(health_ai.ORGANIC_REMEDIES)
            log_test("Organic remedies database", "PASS", f"{remedies_count} remedies available")
        except Exception as e:
            log_test("Organic remedies database", "FAIL", str(e))

except Exception as e:
    log_test("Plant Health AI import", "FAIL", str(e))

print("\n" + "="*80)
print("TEST 8: AI SERVICES - PLANT VERIFICATION")
print("="*80 + "\n")

try:
    from joyo_ai_services.plant_verification import PlantVerificationAI
    log_test("Import PlantVerificationAI", "PASS")
    
    try:
        verify_ai = PlantVerificationAI()
        log_test("Initialize PlantVerificationAI", "PASS")
    except Exception as e:
        log_test("Initialize PlantVerificationAI", "FAIL", str(e))

except Exception as e:
    log_test("Plant Verification AI import", "FAIL", str(e))

print("\n" + "="*80)
print("TEST 9: AI SERVICES - GEO VERIFICATION")
print("="*80 + "\n")

try:
    from joyo_ai_services.geo_verification import GeoVerificationAI
    log_test("Import GeoVerificationAI", "PASS")
    
    try:
        geo_ai = GeoVerificationAI()
        log_test("Initialize GeoVerificationAI", "PASS")
    except Exception as e:
        log_test("Initialize GeoVerificationAI", "FAIL", str(e))
        geo_ai = None
    
    # Test GPS validation
    if geo_ai:
        try:
            result = geo_ai.verify_against_profile(
                profile={'coordinates': {'latitude': 19.0760, 'longitude': 72.8777}},
                new_latitude=19.0761,
                new_longitude=72.8778
            )
            if result['verification_passed']:
                log_test("GPS verification", "PASS", 
                        f"Distance: {result['distance_from_profile_meters']:.2f}m")
            else:
                log_test("GPS verification", "FAIL", "Verification failed unexpectedly")
        except Exception as e:
            log_test("GPS verification", "FAIL", str(e))

except Exception as e:
    log_test("Geo Verification AI import", "FAIL", str(e))

print("\n" + "="*80)
print("TEST 10: ALGORAND NFT INTEGRATION")
print("="*80 + "\n")

try:
    from algorand_nft import mint_carbon_credit_nft
    log_test("Import algorand_nft", "PASS")
    
    # Check if Algorand env vars are set
    if os.getenv('ALGO_MNEMONIC') and os.getenv('ALGOD_URL'):
        log_test("Algorand configuration", "PASS", "Credentials configured")
    else:
        log_test("Algorand configuration", "SKIP", 
                "No credentials - NFT minting will be skipped")

except Exception as e:
    log_test("Algorand NFT import", "FAIL", str(e))

print("\n" + "="*80)
print("TEST 11: API SERVER STATUS")
print("="*80 + "\n")

try:
    # Check if API modules can be imported
    from api_joyo_core import app
    log_test("Import api_joyo_core", "PASS")
    
    # Check FastAPI app
    if app:
        log_test("FastAPI app creation", "PASS")
        
        # Count routes
        routes_count = len([r for r in app.routes if hasattr(r, 'path')])
        log_test("API routes registered", "PASS", f"{routes_count} routes available")
    else:
        log_test("FastAPI app creation", "FAIL", "App is None")

except Exception as e:
    log_test("API server import", "FAIL", str(e))

print("\n" + "="*80)
print("TEST 12: FRONTEND WORKER UI CHECK")
print("="*80 + "\n")

try:
    import subprocess
    
    # Check if frontend exists
    frontend_path = "/Users/satyamsinghal/Desktop/Face_Cascade/Carbon_Credit_Blockchain/frontend"
    if os.path.exists(frontend_path):
        log_test("Frontend directory", "PASS", "Frontend exists")
        
        # Check key files
        worker_page = os.path.join(frontend_path, "app/worker/page.tsx")
        if os.path.exists(worker_page):
            log_test("Worker UI page", "PASS", "Worker portal exists")
        else:
            log_test("Worker UI page", "FAIL", "Worker page not found")
    else:
        log_test("Frontend directory", "FAIL", "Frontend not found")

except Exception as e:
    log_test("Frontend check", "FAIL", str(e))

print("\n" + "="*80)
print("📊 TEST SUMMARY")
print("="*80 + "\n")

total_tests = test_results['passed'] + test_results['failed'] + test_results['skipped']

print(f"Total Tests:   {total_tests}")
print(f"✅ Passed:      {test_results['passed']}")
print(f"❌ Failed:      {test_results['failed']}")
print(f"⚠️  Skipped:     {test_results['skipped']}")
print()

if test_results['failed'] == 0:
    print("🎉 ALL TESTS PASSED!")
else:
    print(f"⚠️  {test_results['failed']} test(s) failed")
    print("\nFailed tests:")
    for test in test_results['tests']:
        if test['status'] == 'FAIL':
            print(f"  - {test['name']}: {test['message']}")

print("\n" + "="*80)
print(f"Completed: {datetime.now().isoformat()}")
print("="*80)

# Save results to JSON
results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
try:
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    print(f"\n📄 Results saved to: {results_file}")
except Exception as e:
    print(f"\n⚠️  Could not save results: {e}")
