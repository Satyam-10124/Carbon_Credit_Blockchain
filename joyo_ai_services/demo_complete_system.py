"""
Joyo AI Services - Complete Demo
Demonstrates all Phase 1 AI capabilities
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from parent directory
parent_dir = Path(__file__).parent.parent
env_path = parent_dir / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()  # Try to load from current directory

# Add parent directory to path
sys.path.insert(0, str(parent_dir))

from joyo_ai_services.plant_recognition import PlantRecognitionAI
from joyo_ai_services.plant_verification import PlantVerificationAI
from joyo_ai_services.plant_health import PlantHealthAI
from joyo_ai_services.geo_verification import GeoVerificationAI


class JoyoAIDemo:
    """Complete demo of Joyo AI system"""
    
    def __init__(self):
        """Initialize all AI services"""
        print("\n" + "="*70)
        print("🌱 JOYO AI SERVICES - PHASE 1 DEMO")
        print("="*70)
        
        print("\n🚀 Initializing AI Services...")
        
        try:
            self.plant_recognition = PlantRecognitionAI()
            print("  ✅ Plant Recognition AI - Ready")
        except Exception as e:
            print(f"  ❌ Plant Recognition AI - Failed: {e}")
            self.plant_recognition = None
        
        try:
            self.plant_verification = PlantVerificationAI()
            print("  ✅ Plant Verification AI - Ready")
        except Exception as e:
            print(f"  ❌ Plant Verification AI - Failed: {e}")
            self.plant_verification = None
        
        try:
            self.plant_health = PlantHealthAI()
            print("  ✅ Plant Health AI - Ready")
        except Exception as e:
            print(f"  ❌ Plant Health AI - Failed: {e}")
            self.plant_health = None
        
        try:
            self.geo_verification = GeoVerificationAI()
            print("  ✅ Geo-Verification AI - Ready")
        except Exception as e:
            print(f"  ❌ Geo-Verification AI - Failed: {e}")
            self.geo_verification = None
        
        print("\n" + "="*70)
    
    def demo_plant_catalog(self):
        """Demo: Show plant catalog"""
        print("\n📚 DEMO 1: PLANT CATALOG")
        print("-"*70)
        
        if not self.plant_recognition:
            print("❌ Plant Recognition AI not available")
            return
        
        catalog = self.plant_recognition.get_plant_catalog()
        
        print(f"\nTotal Air-Purifying Plants: {catalog['total_plants']}")
        print(f"\nCategories:")
        for category, plants in catalog['categories'].items():
            print(f"  • {category}: {', '.join(plants)}")
        
        print(f"\n💰 Point Multipliers:")
        for plant, data in catalog['plants'].items():
            print(f"  • {plant.title()}: {data['points_multiplier']}x (CO2: {data['co2_absorption']})")
    
    def demo_plant_identification(self, image_path: str = None):
        """Demo: Identify plant from image"""
        print("\n🔍 DEMO 2: PLANT IDENTIFICATION")
        print("-"*70)
        
        if not self.plant_recognition:
            print("❌ Plant Recognition AI not available")
            return
        
        if not image_path:
            print("ℹ️  To test: Provide plant image path")
            print("   Example: demo.demo_plant_identification('plant.jpg')")
            return
        
        print(f"\nAnalyzing image: {image_path}")
        result = self.plant_recognition.identify_plant(image_path)
        
        if result['success']:
            print(f"\n✅ Identification Successful!")
            print(f"\n🌿 Species: {result['identification']['species_common']}")
            print(f"🔬 Scientific: {result['identification']['species_scientific']}")
            print(f"📊 Confidence: {result['identification']['confidence']}%")
            print(f"🌬️  CO2 Absorption: {result['identification']['co2_absorption_rating']}")
            print(f"❤️  Health: {result['identification']['health_status']}")
            print(f"🏠 Environment: {result['identification']['environment']}")
            
            if result['plant_database_info']:
                print(f"\n💰 Reward Multiplier: {result['recommended_points_multiplier']}x")
                print(f"📈 Daily CO2: {result['plant_database_info']['daily_absorption_kg']} kg")
            
            print(f"\n🎁 Reward Eligible: {'✅ Yes' if result['reward_eligible'] else '❌ No'}")
        else:
            print(f"\n❌ Identification Failed: {result.get('error')}")
    
    def demo_health_scan(self, image_path: str = None):
        """Demo: Plant health scan"""
        print("\n🏥 DEMO 3: PLANT HEALTH SCAN")
        print("-"*70)
        
        if not self.plant_health:
            print("❌ Plant Health AI not available")
            return
        
        if not image_path:
            print("ℹ️  To test: Provide plant image path")
            return
        
        print(f"\nScanning plant health: {image_path}")
        result = self.plant_health.scan_plant_health(image_path)
        
        if result['success']:
            analysis = result['health_analysis']
            print(f"\n✅ Health Scan Complete!")
            print(f"\n🏥 Overall Health: {analysis['overall_health']}")
            print(f"📊 Health Score: {analysis['health_score']}/100")
            print(f"🔮 Prognosis: {analysis['prognosis']}")
            
            if analysis.get('issues_detected'):
                print(f"\n⚠️  Issues Detected: {len(analysis['issues_detected'])}")
                for i, issue in enumerate(analysis['issues_detected'], 1):
                    print(f"\n  Issue #{i}:")
                    print(f"    Type: {issue['issue_type']}")
                    print(f"    Diagnosis: {issue['specific_diagnosis']}")
                    print(f"    Severity: {issue['severity']}")
                    print(f"    Confidence: {issue['confidence']}%")
            
            if result.get('organic_remedies'):
                print(f"\n💊 Organic Remedies Available: {len(result['organic_remedies'])}")
                for remedy in result['organic_remedies']:
                    print(f"\n  Remedy: {remedy['remedy_name']}")
                    print(f"    Solutions: {', '.join(remedy['solutions'][:2])}")
                    print(f"    Points if Applied: {remedy['points_if_applied']}")
            
            print(f"\n🎁 Scan Points Earned: {result['scan_points_earned']}")
            print(f"🚨 Immediate Action Required: {'✅ Yes' if result['requires_immediate_action'] else '❌ No'}")
        else:
            print(f"\n❌ Health Scan Failed: {result.get('error')}")
    
    def demo_remedy_catalog(self):
        """Demo: Show organic remedy catalog"""
        print("\n💊 DEMO 4: ORGANIC REMEDY CATALOG")
        print("-"*70)
        
        if not self.plant_health:
            print("❌ Plant Health AI not available")
            return
        
        catalog = self.plant_health.get_remedy_catalog()
        
        print(f"\nTotal Remedies: {catalog['total_remedies']}")
        print(f"\nCategories:")
        for category, remedies in catalog['categories'].items():
            print(f"\n  {category.replace('_', ' ').title()}:")
            for remedy in remedies:
                remedy_data = catalog['remedies'][remedy]
                print(f"    • {remedy.replace('_', ' ').title()}")
                print(f"      Symptoms: {', '.join(remedy_data['symptoms'][:2])}")
                print(f"      Solutions: {len(remedy_data['remedies'])} organic options")
    
    def demo_diy_recipe(self, deficiency: str = "nitrogen_deficiency"):
        """Demo: Get DIY organic fertilizer recipe"""
        print(f"\n🧪 DEMO 5: DIY RECIPE - {deficiency.replace('_', ' ').title()}")
        print("-"*70)
        
        if not self.plant_health:
            print("❌ Plant Health AI not available")
            return
        
        suggestion = self.plant_health.suggest_organic_fertilizer(deficiency)
        
        if suggestion['success']:
            recipe = suggestion['diy_recipe']
            print(f"\n📝 Recipe: {recipe['name']}")
            print(f"\n🥘 Ingredients:")
            for ingredient in recipe['ingredients']:
                print(f"  • {ingredient}")
            
            print(f"\n👨‍🍳 Preparation:")
            for i, step in enumerate(recipe['preparation'], 1):
                print(f"  {i}. {step}")
            
            print(f"\n📅 Application Frequency: {recipe['application_frequency']}")
            print(f"⏱️  Shelf Life: {recipe['shelf_life']}")
            print(f"\n🎁 Points Reward: {suggestion['points_reward']}")
        else:
            print(f"\n❌ {suggestion['message']}")
    
    def demo_location_profile(self):
        """Demo: Create location profile"""
        print("\n📍 DEMO 6: GEO-LOCATION PROFILE")
        print("-"*70)
        
        if not self.geo_verification:
            print("❌ Geo-Verification AI not available")
            return
        
        # Example: Indore, India
        lat, lon = 22.7196, 75.8577
        
        print(f"\nCreating location profile for: {lat}, {lon}")
        profile = self.geo_verification.create_location_profile(lat, lon)
        
        print(f"\n✅ Location Profile Created!")
        print(f"\n📍 Coordinates: {profile['coordinates']['formatted']}")
        print(f"🔒 Verification Radius: {profile['verification_radius_meters']}m")
        
        if profile['location_info'].get('success'):
            loc = profile['location_info']
            print(f"\n🏙️  Location: {loc.get('formatted_address', 'Unknown')}")
            if loc.get('components'):
                print(f"   City: {loc['components'].get('city', 'Unknown')}")
                print(f"   State: {loc['components'].get('state', 'Unknown')}")
                print(f"   Country: {loc['components'].get('country', 'Unknown')}")
        
        if profile['initial_weather'].get('success'):
            weather = profile['initial_weather']
            print(f"\n🌤️  Current Weather:")
            print(f"   Temperature: {weather['temperature']}°C")
            print(f"   Conditions: {weather['weather']}")
            print(f"   Humidity: {weather['humidity']}%")
            print(f"   Wind: {weather['wind_speed']} m/s")
        
        return profile
    
    def demo_location_verification(self, profile: dict):
        """Demo: Verify location consistency"""
        print("\n🔒 DEMO 7: LOCATION VERIFICATION")
        print("-"*70)
        
        if not self.geo_verification:
            print("❌ Geo-Verification AI not available")
            return
        
        # Simulate different days with slightly different coordinates
        test_locations = [
            (22.7196, 75.8577),  # Day 1: Original
            (22.7197, 75.8578),  # Day 2: 10m away (OK)
            (22.7198, 75.8579),  # Day 3: 20m away (OK)
            (22.7196, 75.8577),  # Day 4: Back to original (OK)
            (22.7250, 75.8620),  # Day 5: 500m away (SUSPICIOUS!)
        ]
        
        print("\n🧪 Testing location consistency over 5 days...")
        
        historical = []
        for day, (lat, lon) in enumerate(test_locations, 1):
            historical.append({
                'day': day,
                'latitude': lat,
                'longitude': lon
            })
            
            verification = self.geo_verification.verify_against_profile(profile, lat, lon)
            status = "✅" if verification['verification_passed'] else "❌"
            print(f"\n  Day {day}: {status}")
            print(f"    Location: {lat}, {lon}")
            print(f"    Distance: {verification['distance_from_profile_meters']}m")
        
        # Check overall consistency
        print("\n📊 Overall Consistency Check:")
        consistency = self.geo_verification.verify_location_consistency(historical)
        
        print(f"\n  Consistent: {'✅ Yes' if consistency['consistent'] else '❌ No'}")
        print(f"  Average Distance: {consistency['average_distance_meters']}m")
        print(f"  Max Distance: {consistency['max_distance_meters']}m")
        print(f"  Fraud Risk: {consistency['fraud_risk'].upper()}")
        
        if consistency['inconsistencies_found'] > 0:
            print(f"\n  ⚠️  Inconsistencies: {consistency['inconsistencies_found']}")
            for inc in consistency['inconsistency_details']:
                print(f"    Day {inc['day']}: {inc['distance_meters']}m movement")
    
    def demo_complete_workflow(self):
        """Demo: Complete user workflow simulation"""
        print("\n🎬 DEMO 8: COMPLETE USER WORKFLOW")
        print("="*70)
        print("\nSimulating 30-day user journey...")
        
        # Day 0: User selects plant
        print("\n📅 DAY 0: PLANT PURCHASE")
        print("-"*40)
        print("User: Satyam")
        print("Action: Selects 'Bamboo' from catalog")
        print("Points Earned: 30")
        print("Total Points: 30")
        
        # Day 1: Plant and photograph
        print("\n📅 DAY 1: PLANTING")
        print("-"*40)
        print("Action: Plants bamboo outside house")
        print("Photo: Uploaded with GPS (22.7196, 75.8577)")
        print("AI Verification: ✅ Bamboo confirmed")
        print("Points Earned: 20")
        print("Total Points: 50")
        
        # Days 2-7: Daily watering
        print("\n📅 DAY 2-7: DAILY WATERING")
        print("-"*40)
        for day in range(2, 8):
            print(f"Day {day}: ✅ Watering verified (+5 pts)")
        print("Points Earned: 30 (6 days × 5)")
        print("Total Points: 80")
        
        # Day 8: Weekly health scan
        print("\n📅 DAY 8: HEALTH SCAN")
        print("-"*40)
        print("Action: Scans plant for health check")
        print("AI Detection: Healthy, no issues")
        print("Points Earned: 5")
        print("Total Points: 85")
        
        # Day 10: Add netting
        print("\n📅 DAY 10: PROTECTION")
        print("-"*40)
        print("Action: Adds bamboo netting")
        print("Photo: Uploaded with verification")
        print("Points Earned: 10")
        print("Total Points: 95")
        
        # Day 15: Issue detected
        print("\n📅 DAY 15: ISSUE DETECTED")
        print("-"*40)
        print("Health Scan: Nitrogen deficiency detected")
        print("AI Suggestion: Apply cow dung manure")
        print("Points Earned: 5 (scan)")
        print("Total Points: 100")
        
        # Day 16: Apply remedy
        print("\n📅 DAY 16: REMEDY APPLIED")
        print("-"*40)
        print("Action: Applies cow dung manure")
        print("Video: Uploaded with verification")
        print("Points Earned: 25")
        print("Total Points: 125")
        
        # Day 30: Summary
        print("\n📅 DAY 30: MONTHLY SUMMARY")
        print("="*40)
        print("Total Days: 30")
        print("Total Points: 275")
        print("Conversion Rate: 1 point = 1 coin")
        print("Total Coins Earned: 275")
        print("Plant Status: ✅ Healthy & Growing")
        print("CO2 Absorbed: ~360 kg (12 kg/day × 30 days)")
        print("\n🎉 Success! User maintained plant for 30 days!")
    
    def run_all_demos(self):
        """Run all demos"""
        self.demo_plant_catalog()
        self.demo_remedy_catalog()
        self.demo_diy_recipe()
        
        profile = self.demo_location_profile()
        if profile:
            self.demo_location_verification(profile)
        
        self.demo_complete_workflow()
        
        print("\n" + "="*70)
        print("🎉 ALL DEMOS COMPLETED!")
        print("="*70)
        print("\n📊 Phase 1 AI Services Summary:")
        print("  ✅ Plant Recognition - Identifies 8+ species")
        print("  ✅ Plant Verification - Tracks same plant over time")
        print("  ✅ Plant Health - Detects 8+ issues")
        print("  ✅ Geo-Verification - Ensures location consistency")
        print("\n💰 Total Organic Remedies: 8")
        print("🎁 Total Point Opportunities: 100+ per month")
        print("\n🚀 Ready for Phase 2: Point System & Blockchain Integration!")


def main():
    """Main demo entry point"""
    demo = JoyoAIDemo()
    
    print("\n" + "="*70)
    print("Select Demo Option:")
    print("  1. Plant Catalog")
    print("  2. Remedy Catalog")
    print("  3. DIY Recipe")
    print("  4. Location Profile")
    print("  5. Complete Workflow")
    print("  9. Run All Demos")
    print("="*70)
    
    choice = input("\nEnter choice (or press Enter for all demos): ").strip()
    
    if not choice or choice == '9':
        demo.run_all_demos()
    elif choice == '1':
        demo.demo_plant_catalog()
    elif choice == '2':
        demo.demo_remedy_catalog()
    elif choice == '3':
        demo.demo_diy_recipe()
    elif choice == '4':
        profile = demo.demo_location_profile()
        if profile:
            demo.demo_location_verification(profile)
    elif choice == '5':
        demo.demo_complete_workflow()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
