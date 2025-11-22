"""
Plant Recognition AI - Using GPT-4o Vision
Identifies plant species from photos with high accuracy
"""

import os
import base64
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from openai import OpenAI
from pathlib import Path


class PlantRecognitionAI:
    """
    AI service to identify plant species from images
    Uses GPT-4o Vision model for accurate plant identification
    """
    
    # Air-purifying plants database
    AIR_PURIFYING_PLANTS = {
        "bamboo": {
            "co2_absorption": "high",
            "daily_absorption_kg": 12.0,
            "growth_rate": "fast",
            "difficulty": "easy",
            "suitable_for": ["outdoor", "indoor"],
            "points_multiplier": 1.5
        },
        "tulsi": {
            "co2_absorption": "medium",
            "daily_absorption_kg": 8.0,
            "growth_rate": "medium",
            "difficulty": "easy",
            "suitable_for": ["outdoor", "indoor"],
            "points_multiplier": 1.2
        },
        "neem": {
            "co2_absorption": "high",
            "daily_absorption_kg": 10.0,
            "growth_rate": "medium",
            "difficulty": "medium",
            "suitable_for": ["outdoor"],
            "points_multiplier": 1.4
        },
        "peepal": {
            "co2_absorption": "very_high",
            "daily_absorption_kg": 15.0,
            "growth_rate": "slow",
            "difficulty": "easy",
            "suitable_for": ["outdoor"],
            "points_multiplier": 1.8
        },
        "areca_palm": {
            "co2_absorption": "high",
            "daily_absorption_kg": 9.0,
            "growth_rate": "medium",
            "difficulty": "easy",
            "suitable_for": ["indoor", "outdoor"],
            "points_multiplier": 1.3
        },
        "snake_plant": {
            "co2_absorption": "medium",
            "daily_absorption_kg": 6.0,
            "growth_rate": "slow",
            "difficulty": "very_easy",
            "suitable_for": ["indoor"],
            "points_multiplier": 1.1
        },
        "aloe_vera": {
            "co2_absorption": "medium",
            "daily_absorption_kg": 5.0,
            "growth_rate": "slow",
            "difficulty": "easy",
            "suitable_for": ["indoor", "outdoor"],
            "points_multiplier": 1.0
        },
        "money_plant": {
            "co2_absorption": "medium",
            "daily_absorption_kg": 7.0,
            "growth_rate": "fast",
            "difficulty": "very_easy",
            "suitable_for": ["indoor"],
            "points_multiplier": 1.2
        }
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"  # GPT-4o with vision
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def identify_plant(self, image_path: str, user_claimed_species: Optional[str] = None) -> Dict:
        """
        Identify plant species from image using GPT-4o Vision
        
        Args:
            image_path: Path to plant image
            user_claimed_species: Optional species claimed by user for verification
            
        Returns:
            Dictionary with plant identification results
        """
        
        try:
            # Encode image
            base64_image = self.encode_image(image_path)
            
            # Create prompt for GPT-4o Vision
            prompt = """
            Analyze this plant image and provide detailed identification.
            
            Please identify:
            1. Plant species (common name and scientific name)
            2. Confidence level (0-100%)
            3. Whether it's an air-purifying plant (CO2 absorbing)
            4. Current health status (healthy/unhealthy/stressed)
            5. Approximate age/maturity
            6. Suitable environment (indoor/outdoor)
            
            Return response in JSON format:
            {
                "species_common": "string",
                "species_scientific": "string",
                "confidence": number,
                "is_air_purifying": boolean,
                "co2_absorption_rating": "low/medium/high/very_high",
                "health_status": "string",
                "age_estimate": "string",
                "environment": "indoor/outdoor/both",
                "additional_notes": "string"
            }
            """
            
            if user_claimed_species:
                prompt += f"\n\nUser claims this is a '{user_claimed_species}'. Verify if correct."
            
            # Log AI request
            print("\n" + "="*70)
            print("🤖 AI REQUEST - Plant Recognition")
            print("="*70)
            print(f"Model: {self.model}")
            print(f"Image: {os.path.basename(image_path)}")
            print(f"Claimed Species: {user_claimed_species or 'Not specified'}")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\nPrompt Preview:")
            print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
            print("="*70)
            
            # Call GPT-4o Vision API
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.2  # Low temperature for consistent results
            )
            elapsed_time = time.time() - start_time
            
            # Log AI response
            print("\n" + "="*70)
            print("✅ AI RESPONSE - Plant Recognition")
            print("="*70)
            print(f"Response Time: {elapsed_time:.2f}s")
            print(f"Tokens Used: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            print(f"\nRaw Response:")
            print("-"*70)
            
            # Parse response
            result_text = response.choices[0].message.content
            print(result_text[:500] + "..." if len(result_text) > 500 else result_text)
            print("-"*70)
            
            # Extract JSON from response
            try:
                # Find JSON in response
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    result_json = json.loads(result_text[json_start:json_end])
                else:
                    result_json = json.loads(result_text)
                
                # Log parsed results
                print("\n📊 Parsed Results:")
                print(f"  Species: {result_json.get('species_common', 'N/A')}")
                print(f"  Confidence: {result_json.get('confidence', 0)}%")
                print(f"  CO2 Rating: {result_json.get('co2_absorption_rating', 'N/A')}")
                print(f"  Health: {result_json.get('health_status', 'N/A')}")
                
            except json.JSONDecodeError as e:
                print(f"\n⚠️  JSON Parse Error: {e}")
                # If JSON parsing fails, create structured response from text
                result_json = {
                    "species_common": "Unknown",
                    "species_scientific": "Unknown",
                    "confidence": 0,
                    "is_air_purifying": False,
                    "co2_absorption_rating": "unknown",
                    "health_status": "unknown",
                    "age_estimate": "unknown",
                    "environment": "unknown",
                    "additional_notes": result_text
                }
            
            print("="*70)
            
            # Add metadata
            species_lower = result_json.get('species_common', '').lower()
            plant_data = self._get_plant_data(species_lower)
            
            result = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "identification": result_json,
                "plant_database_info": plant_data,
                "user_claimed_species": user_claimed_species,
                "verification_passed": self._verify_species(species_lower, user_claimed_species),
                "reward_eligible": self._is_reward_eligible(result_json),
                "recommended_points_multiplier": plant_data.get("points_multiplier", 1.0) if plant_data else 1.0
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_plant_data(self, species_name: str) -> Optional[Dict]:
        """Get plant data from database"""
        for key, data in self.AIR_PURIFYING_PLANTS.items():
            if key in species_name.lower():
                return data
        return None
    
    def _verify_species(self, identified: str, claimed: Optional[str]) -> bool:
        """Verify if identified species matches user claim"""
        if not claimed:
            return True
        return claimed.lower() in identified.lower() or identified.lower() in claimed.lower()
    
    def _is_reward_eligible(self, identification: Dict) -> bool:
        """Check if plant is eligible for rewards"""
        return (
            identification.get("confidence", 0) >= 70 and
            identification.get("is_air_purifying", False) and
            identification.get("health_status", "").lower() != "dead"
        )
    
    def bulk_identify(self, image_paths: List[str]) -> List[Dict]:
        """Identify multiple plants from a list of images"""
        results = []
        for image_path in image_paths:
            result = self.identify_plant(image_path)
            results.append(result)
        return results
    
    def get_plant_catalog(self) -> Dict:
        """Get catalog of supported air-purifying plants"""
        return {
            "total_plants": len(self.AIR_PURIFYING_PLANTS),
            "plants": self.AIR_PURIFYING_PLANTS,
            "categories": {
                "very_high_absorption": [k for k, v in self.AIR_PURIFYING_PLANTS.items() 
                                        if v["co2_absorption"] == "very_high"],
                "high_absorption": [k for k, v in self.AIR_PURIFYING_PLANTS.items() 
                                   if v["co2_absorption"] == "high"],
                "medium_absorption": [k for k, v in self.AIR_PURIFYING_PLANTS.items() 
                                     if v["co2_absorption"] == "medium"]
            }
        }
    
    def validate_planting_photo(self, image_path: str, expected_species: str) -> Dict:
        """
        Validate that a planting photo shows the correct plant
        Used when user uploads photo after planting
        """
        result = self.identify_plant(image_path, expected_species)
        
        validation = {
            "is_valid": False,
            "confidence": 0,
            "message": "",
            "reward_eligible": False
        }
        
        if result["success"]:
            if result["verification_passed"]:
                validation["is_valid"] = True
                validation["confidence"] = result["identification"]["confidence"]
                validation["message"] = f"✅ Verified: {result['identification']['species_common']}"
                validation["reward_eligible"] = result["reward_eligible"]
            else:
                validation["message"] = f"❌ Plant mismatch. Expected: {expected_species}, Found: {result['identification']['species_common']}"
        else:
            validation["message"] = f"❌ Identification failed: {result.get('error')}"
        
        return validation


if __name__ == "__main__":
    # Test the service
    print("🌱 Plant Recognition AI - Test")
    print("="*70)
    
    ai = PlantRecognitionAI()
    
    # Show catalog
    catalog = ai.get_plant_catalog()
    print(f"\n📚 Plant Catalog: {catalog['total_plants']} species")
    print(f"Very High CO2 Absorption: {catalog['categories']['very_high_absorption']}")
    print(f"High CO2 Absorption: {catalog['categories']['high_absorption']}")
    
    print("\n✅ Plant Recognition AI initialized successfully!")
