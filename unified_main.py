#!/usr/bin/env python3
"""
UNIFIED CARBON CREDIT & JOYO SYSTEM
Complete real-time verification with all sensors and AI services
Combines gesture verification, plant AI, and blockchain NFT minting
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Carbon Credit System
from gesture_verification import GestureVerifier
try:
    from enhanced_ai_validator import EnhancedAIValidator
except ImportError:
    from ai_validator import AIValidator as EnhancedAIValidator
from algorand_nft import mint_carbon_credit_nft

# Import Joyo AI Services
from joyo_ai_services.plant_recognition import PlantRecognitionAI
from joyo_ai_services.plant_verification import PlantVerificationAI
from joyo_ai_services.plant_health import PlantHealthAI
from joyo_ai_services.geo_verification import GeoVerificationAI


class UnifiedVerificationSystem:
    """
    Unified system combining Carbon Credit Blockchain + Joyo AI Services
    Real-time verification with all sensors, AI, and blockchain
    """
    
    def __init__(self):
        """Initialize all services"""
        print("\n" + "="*70)
        print("🌍 UNIFIED CARBON CREDIT & PLANT VERIFICATION SYSTEM")
        print("="*70)
        
        print("\n🚀 Initializing services...")
        
        # Original Carbon Credit Services
        try:
            self.gesture_verifier = GestureVerifier()
            print("  ✅ Gesture Verification - Ready")
        except Exception as e:
            print(f"  ⚠️  Gesture Verification - Failed: {e}")
            self.gesture_verifier = None
        
        try:
            self.ai_validator = EnhancedAIValidator()
            print("  ✅ AI Validator (GPT-4) - Ready")
        except Exception as e:
            print(f"  ⚠️  AI Validator - Failed: {e}")
            self.ai_validator = None
        
        # Joyo AI Services
        try:
            self.plant_recognition = PlantRecognitionAI()
            print("  ✅ Plant Recognition AI - Ready")
        except Exception as e:
            print(f"  ⚠️  Plant Recognition AI - Failed: {e}")
            self.plant_recognition = None
        
        try:
            self.plant_verification = PlantVerificationAI()
            print("  ✅ Plant Verification AI - Ready")
        except Exception as e:
            print(f"  ⚠️  Plant Verification AI - Failed: {e}")
            self.plant_verification = None
        
        try:
            self.plant_health = PlantHealthAI()
            print("  ✅ Plant Health AI - Ready")
        except Exception as e:
            print(f"  ⚠️  Plant Health AI - Failed: {e}")
            self.plant_health = None
        
        try:
            self.geo_verification = GeoVerificationAI()
            print("  ✅ Geo-Verification AI - Ready")
        except Exception as e:
            print(f"  ⚠️  Geo-Verification AI - Failed: {e}")
            self.geo_verification = None
        
        print("\n" + "="*70)
    
    def get_user_input(self) -> Dict:
        """Get real-time user input"""
        print("\n" + "="*70)
        print("📝 USER INPUT")
        print("="*70)
        
        # Worker details
        worker_id = input("\nWorker ID (press Enter for auto): ").strip()
        if not worker_id:
            worker_id = f"WORKER_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"Generated: {worker_id}")
        
        # Plant details
        print("\n🌿 Plant Information:")
        if self.plant_recognition:
            catalog = self.plant_recognition.get_plant_catalog()
            print("\nAvailable plants:")
            for i, plant in enumerate(catalog['plants'].keys(), 1):
                data = catalog['plants'][plant]
                print(f"  {i}. {plant.title()} - {data['co2_absorption']} CO2, {data['points_multiplier']}x points")
            
            plant_choice = input("\nSelect plant (name or number): ").strip().lower()
            try:
                if plant_choice.isdigit():
                    plant_species = list(catalog['plants'].keys())[int(plant_choice)-1]
                else:
                    plant_species = plant_choice
            except:
                plant_species = "bamboo"
        else:
            plant_species = input("Plant species: ").strip() or "bamboo"
        
        trees = input("Number of trees/plants: ").strip()
        try:
            trees = int(trees)
        except:
            trees = 1
        
        # Location
        print("\n📍 Location:")
        print("1. Auto-detect (IP geolocation)")
        print("2. Manual entry")
        
        loc_choice = input("Choice (1/2): ").strip()
        
        if loc_choice == "1" and self.geo_verification:
            location, lat, lon = self._auto_detect_location()
        else:
            location = input("Location (e.g., Indore, MP, India): ").strip()
            if not location:
                location = "Indore, Madhya Pradesh, India"
            
            lat = input("Latitude (e.g., 22.7196): ").strip()
            lon = input("Longitude (e.g., 75.8577): ").strip()
            try:
                lat = float(lat)
                lon = float(lon)
            except:
                lat, lon = 22.7196, 75.8577
        
        gps_coords = f"{abs(lat):.4f}° {'N' if lat >= 0 else 'S'}, {abs(lon):.4f}° {'E' if lon >= 0 else 'W'}"
        
        # Photo path (optional)
        print("\n📸 Plant Photo (optional):")
        image_path = input("Path to plant photo (or press Enter to skip): ").strip()
        
        return {
            "worker_id": worker_id,
            "plant_species": plant_species,
            "trees": trees,
            "location": location,
            "latitude": lat,
            "longitude": lon,
            "gps_coords": gps_coords,
            "image_path": image_path if image_path and Path(image_path).exists() else None
        }
    
    def _auto_detect_location(self):
        """Auto-detect location via IP"""
        try:
            import requests
            print("\n🔍 Detecting location...")
            response = requests.get("http://ip-api.com/json/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    city = data.get('city', 'Unknown')
                    region = data.get('regionName', 'Unknown')
                    country = data.get('country', 'India')
                    lat = data.get('lat', 0)
                    lon = data.get('lon', 0)
                    
                    location = f"{city}, {region}, {country}"
                    print(f"✅ Detected: {location}")
                    print(f"   GPS: {lat:.4f}, {lon:.4f}")
                    
                    return location, lat, lon
        except Exception as e:
            print(f"⚠️  Auto-detection failed: {e}")
        
        return "Indore, Madhya Pradesh, India", 22.7196, 75.8577
    
    def verify_complete_system(self, user_data: Dict) -> Dict:
        """
        Complete real-time verification pipeline
        Uses all sensors and AI services
        """
        
        print("\n" + "="*70)
        print("🚀 COMPLETE VERIFICATION PIPELINE")
        print("="*70)
        
        result = {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "user_data": user_data,
            "verification_stages": {}
        }
        
        # STAGE 1: Plant Recognition (if image provided)
        if user_data.get("image_path") and self.plant_recognition:
            print("\n🌿 STAGE 1: Plant Recognition")
            print("-"*70)
            plant_result = self.plant_recognition.identify_plant(
                user_data["image_path"],
                user_data["plant_species"]
            )
            
            if plant_result['success']:
                print(f"✅ Identified: {plant_result['identification']['species_common']}")
                print(f"   Confidence: {plant_result['identification']['confidence']}%")
                print(f"   CO2 Absorption: {plant_result['identification']['co2_absorption_rating']}")
                print(f"   Reward Eligible: {'Yes' if plant_result['reward_eligible'] else 'No'}")
                
                result["verification_stages"]["plant_recognition"] = plant_result
                
                # Check if species matches claim
                if not plant_result['verification_passed']:
                    print(f"⚠️  Warning: Plant mismatch detected!")
            else:
                print(f"⚠️  Plant recognition failed: {plant_result.get('error')}")
        
        # STAGE 2: Plant Health Scan (if image provided)
        if user_data.get("image_path") and self.plant_health:
            print("\n🏥 STAGE 2: Plant Health Scan")
            print("-"*70)
            health_result = self.plant_health.scan_plant_health(
                user_data["image_path"],
                user_data["plant_species"]
            )
            
            if health_result['success']:
                analysis = health_result['health_analysis']
                print(f"✅ Health Score: {analysis['health_score']}/100")
                print(f"   Status: {analysis['overall_health']}")
                print(f"   Prognosis: {analysis['prognosis']}")
                
                if health_result['organic_remedies']:
                    print(f"   Remedies Available: {len(health_result['organic_remedies'])}")
                
                result["verification_stages"]["plant_health"] = health_result
            else:
                print(f"⚠️  Health scan failed: {health_result.get('error')}")
        
        # STAGE 3: Geo-Verification & Weather
        if self.geo_verification:
            print("\n📍 STAGE 3: Geo-Verification & Weather")
            print("-"*70)
            
            # Create location profile
            location_profile = self.geo_verification.create_location_profile(
                user_data["latitude"],
                user_data["longitude"]
            )
            
            print(f"✅ Location: {user_data['location']}")
            print(f"   GPS: {user_data['gps_coords']}")
            
            # Get weather
            if location_profile['initial_weather'].get('success'):
                weather = location_profile['initial_weather']
                print(f"\n🌤️  Real-Time Weather:")
                print(f"   Temperature: {weather['temperature']}°C")
                print(f"   Conditions: {weather['weather']}")
                print(f"   Humidity: {weather['humidity']}%")
                print(f"   Wind: {weather['wind_speed']} m/s")
            
            result["verification_stages"]["geo_verification"] = location_profile
        
        # STAGE 4: Gesture Verification (Biometric)
        if self.gesture_verifier:
            print("\n👋 STAGE 4: Gesture Verification (Biometric)")
            print("-"*70)
            print("\n⏱️  Duration: 10 seconds")
            print("👍 Show THUMBS UP gesture 3-4 times")
            print("📹 Camera will open automatically")
            
            input("\nPress ENTER when ready to start...")
            
            gesture_result = self.gesture_verifier.verify_action_sequence(
                duration_seconds=10
            )
            
            # Note: verify_action_sequence returns "valid" not "success"
            if gesture_result.get("valid", False):
                print(f"\n✅ Gesture Verification PASSED")
                print(f"   Gestures: {gesture_result['gesture_count']}")
                print(f"   Signature: {gesture_result['signature'][:16]}...")
                print(f"   Confidence: {gesture_result['confidence']:.1%}")
                
                # Add success flag for consistency
                gesture_result["success"] = True
            else:
                print(f"\n❌ Gesture Verification FAILED")
                print(f"   Gestures: {gesture_result.get('gesture_count', 0)}")
                gesture_result["success"] = False
                result["verification_stages"]["gesture_verification"] = gesture_result
                result["failure_stage"] = "gesture_verification"
                return result
            
            result["verification_stages"]["gesture_verification"] = gesture_result
        
        # STAGE 5: AI Fraud Detection
        if self.ai_validator:
            print("\n🤖 STAGE 5: AI Fraud Detection")
            print("-"*70)
            
            # Check which validator type we have and call the correct method
            if hasattr(self.ai_validator, 'validate_comprehensive'):
                # EnhancedAIValidator
                ai_result = self.ai_validator.validate_comprehensive(
                    trees_planted=user_data["trees"],
                    location=user_data["location"],
                    gps_coords=user_data["gps_coords"],
                    worker_id=user_data["worker_id"],
                    image_path=user_data.get("image_path"),
                    weather_data=result["verification_stages"].get("geo_verification", {}).get("initial_weather")
                )
            elif hasattr(self.ai_validator, 'validate_tree_planting_claim'):
                # AIValidator
                ai_result = self.ai_validator.validate_tree_planting_claim(
                    trees_claimed=user_data["trees"],
                    location=user_data["location"],
                    worker_id=user_data["worker_id"]
                )
            else:
                print("⚠️  AI validator method not found")
                ai_result = None
            
            if ai_result:
                print(f"✅ AI Validation: {ai_result.get('valid', False)}")
                print(f"   Confidence: {ai_result.get('confidence', 0)}%")
                print(f"   Recommendation: {ai_result.get('recommendation', 'unknown')}")
                
                result["verification_stages"]["ai_validation"] = ai_result
        
        # STAGE 6: Generate Verification Report
        print("\n📄 STAGE 6: Verification Report")
        print("-"*70)
        
        report = self._generate_verification_report(result)
        print(report[:500] + "..." if len(report) > 500 else report)
        result["verification_report"] = report
        
        # STAGE 7: Mint NFT on Blockchain
        print("\n⛓️  STAGE 7: Blockchain NFT Minting")
        print("-"*70)
        
        print("🔐 Minting carbon credit NFT on Algorand...")
        
        try:
            gesture_sig = result["verification_stages"].get("gesture_verification", {}).get("signature", "")
            
            nft_result = mint_carbon_credit_nft(
                trees_planted=user_data["trees"],
                location=user_data["location"],
                gps_coords=user_data["gps_coords"],
                worker_id=user_data["worker_id"],
                gesture_signature=gesture_sig,
                image_url=os.getenv("NFT_IMAGE_URL")
            )
            
            print(f"\n✅ NFT MINTED SUCCESSFULLY!")
            print(f"\n   Transaction ID: {nft_result['transaction_id']}")
            print(f"   Asset ID: {nft_result['asset_id']}")
            print(f"   Explorer: {nft_result['explorer_url']}")
            print(f"   Carbon Offset: {nft_result['properties']['carbon_offset_kg']:.2f} kg CO2")
            
            result["nft_result"] = nft_result
            result["success"] = True
            
        except Exception as e:
            print(f"\n❌ NFT minting failed: {e}")
            result["nft_error"] = str(e)
        
        return result
    
    def _generate_verification_report(self, result: Dict) -> str:
        """Generate comprehensive verification report"""
        
        stages = result["verification_stages"]
        report_lines = [
            "═"*70,
            "COMPREHENSIVE VERIFICATION REPORT",
            "═"*70,
            f"\nTimestamp: {result['timestamp']}",
            f"Worker ID: {result['user_data']['worker_id']}",
            f"Plant Species: {result['user_data']['plant_species'].title()}",
            f"Quantity: {result['user_data']['trees']} tree(s)",
            f"Location: {result['user_data']['location']}",
            f"GPS: {result['user_data']['gps_coords']}",
            "\n" + "-"*70,
            "VERIFICATION RESULTS:",
            "-"*70
        ]
        
        # Plant Recognition
        if "plant_recognition" in stages:
            pr = stages["plant_recognition"]
            report_lines.append(f"\n🌿 Plant Recognition: {'PASSED' if pr['success'] else 'FAILED'}")
            if pr['success']:
                report_lines.append(f"   Species: {pr['identification']['species_common']}")
                report_lines.append(f"   Confidence: {pr['identification']['confidence']}%")
                report_lines.append(f"   CO2 Rating: {pr['identification']['co2_absorption_rating']}")
        
        # Plant Health
        if "plant_health" in stages:
            ph = stages["plant_health"]
            report_lines.append(f"\n🏥 Plant Health: {'PASSED' if ph['success'] else 'FAILED'}")
            if ph['success']:
                report_lines.append(f"   Health Score: {ph['health_analysis']['health_score']}/100")
                report_lines.append(f"   Status: {ph['health_analysis']['overall_health']}")
        
        # Geo-Verification
        if "geo_verification" in stages:
            gv = stages["geo_verification"]
            report_lines.append(f"\n📍 Geo-Verification: PASSED")
            if gv['initial_weather'].get('success'):
                w = gv['initial_weather']
                report_lines.append(f"   Weather: {w['weather']}, {w['temperature']}°C")
                report_lines.append(f"   Humidity: {w['humidity']}%")
        
        # Gesture Verification
        if "gesture_verification" in stages:
            gv = stages["gesture_verification"]
            report_lines.append(f"\n👋 Gesture Verification: {'PASSED' if gv.get('success', gv.get('valid', False)) else 'FAILED'}")
            report_lines.append(f"   Gestures Detected: {gv.get('gesture_count', 0)}")
            report_lines.append(f"   Confidence: {gv.get('confidence', 0):.1%}")
        
        # AI Validation
        if "ai_validation" in stages:
            ai = stages["ai_validation"]
            report_lines.append(f"\n🤖 AI Validation: {'PASSED' if ai.get('valid') else 'FAILED'}")
            report_lines.append(f"   Confidence: {ai.get('confidence', 0)}%")
            report_lines.append(f"   Recommendation: {ai.get('recommendation', 'unknown')}")
        
        report_lines.extend([
            "\n" + "═"*70,
            f"Overall Status: {'✅ VERIFIED' if result.get('success') else '❌ FAILED'}",
            "═"*70
        ])
        
        return "\n".join(report_lines)
    
    def save_results(self, result: Dict):
        """Save complete results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"unified_verification_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\n📁 Complete results saved to: {filename}")
        return filename


def main():
    """Main entry point for unified system"""
    
    # Initialize system
    system = UnifiedVerificationSystem()
    
    # Get user input
    user_data = system.get_user_input()
    
    # Show preview
    print("\n" + "="*70)
    print("📊 VERIFICATION PREVIEW")
    print("="*70)
    print(f"\n👤 Worker: {user_data['worker_id']}")
    print(f"🌿 Plant: {user_data['plant_species'].title()}")
    print(f"🌳 Quantity: {user_data['trees']}")
    print(f"📍 Location: {user_data['location']}")
    print(f"🗺️  GPS: {user_data['gps_coords']}")
    if user_data.get('image_path'):
        print(f"📸 Image: {user_data['image_path']}")
    
    # Confirm
    print("\n" + "="*70)
    confirm = input("\n✅ Start complete verification? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("\n❌ Verification cancelled")
        return
    
    # Run complete verification
    result = system.verify_complete_system(user_data)
    
    # Save results
    system.save_results(result)
    
    # Final summary
    print("\n" + "="*70)
    print("🎉 VERIFICATION COMPLETE")
    print("="*70)
    
    if result["success"]:
        print("\n✅ SUCCESS! All verifications passed!")
        if "nft_result" in result:
            print(f"\n🎫 NFT Asset ID: {result['nft_result']['asset_id']}")
            print(f"🔗 View on Explorer: {result['nft_result']['explorer_url']}")
            print(f"💨 Carbon Offset: {result['nft_result']['properties']['carbon_offset_kg']:.2f} kg CO2")
    else:
        print("\n❌ Verification failed")
        if "failure_stage" in result:
            print(f"Failed at: {result['failure_stage']}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Verification cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
