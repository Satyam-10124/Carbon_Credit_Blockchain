"""
Test script for new unified verification features
"""
import requests
import json

BASE_URL = "https://joyo-cc-production.up.railway.app"

def test_weather_api():
    """Test weather API endpoint"""
    print("\n🌤️  Testing Weather API...")
    response = requests.get(
        f"{BASE_URL}/weather",
        params={
            "latitude": 19.0760,
            "longitude": 72.8777
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_fraud_detection():
    """Test fraud detection endpoint"""
    print("\n🤖 Testing AI Fraud Detection...")
    response = requests.post(
        f"{BASE_URL}/verify/fraud-check",
        data={
            "plant_type": "bamboo",
            "location": "Mumbai, India",
            "gps_latitude": 19.0760,
            "gps_longitude": 72.8777,
            "trees_planted": 5
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_biometric_storage():
    """Test biometric signature storage"""
    print("\n✋ Testing Biometric Storage...")
    response = requests.post(
        f"{BASE_URL}/users/TEST_USER_123/biometric",
        data={
            "signature": "abc123def456hash",
            "gesture_count": 5,
            "confidence": 85.5
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

if __name__ == "__main__":
    print("="*70)
    print("🚀 TESTING NEW UNIFIED VERIFICATION FEATURES")
    print("="*70)
    
    results = {
        "Weather API": test_weather_api(),
        "AI Fraud Detection": test_fraud_detection(),
        "Biometric Storage": test_biometric_storage()
    }
    
    print("\n" + "="*70)
    print("📊 TEST RESULTS")
    print("="*70)
    
    passed = sum(results.values())
    total = len(results)
    
    for feature, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {feature}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({(passed/total)*100:.0f}%)")
