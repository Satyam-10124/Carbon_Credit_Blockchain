"""
Plant Health AI - Disease & Deficiency Detection
Scans plants for health issues and suggests organic remedies
Uses GPT-4o Vision for accurate diagnosis
"""

import os
import base64
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from openai import OpenAI


class PlantHealthAI:
    """
    AI service to diagnose plant health issues
    Detects diseases, pests, nutrient deficiencies
    Suggests organic remedies
    """
    
    # Organic remedy database
    ORGANIC_REMEDIES = {
        "nitrogen_deficiency": {
            "symptoms": ["yellowing leaves", "stunted growth", "pale color"],
            "remedies": [
                "Cow dung manure (mixed with soil)",
                "Compost tea",
                "Urea diluted in water (1 tsp per liter)",
                "Green manure (decomposed leaves)"
            ],
            "application": "Apply around base, water thoroughly",
            "prevention": "Regular composting, mulching"
        },
        "phosphorus_deficiency": {
            "symptoms": ["purple/dark leaves", "slow growth", "weak stems"],
            "remedies": [
                "Bone meal powder",
                "Rock phosphate",
                "Banana peels (chopped and buried)",
                "Fish waste compost"
            ],
            "application": "Mix into soil around plant",
            "prevention": "Add organic matter regularly"
        },
        "potassium_deficiency": {
            "symptoms": ["brown leaf edges", "weak stems", "poor flowering"],
            "remedies": [
                "Wood ash (small amounts)",
                "Banana peel tea",
                "Seaweed extract",
                "Coconut coir compost"
            ],
            "application": "Sprinkle around plant, water in",
            "prevention": "Balanced fertilization"
        },
        "overwatering": {
            "symptoms": ["yellow leaves", "wilting", "root rot", "fungus"],
            "remedies": [
                "Stop watering for 3-5 days",
                "Improve drainage",
                "Add sand to soil",
                "Ensure proper pot drainage"
            ],
            "application": "Let soil dry between watering",
            "prevention": "Water only when top soil is dry"
        },
        "underwatering": {
            "symptoms": ["dry soil", "crispy leaves", "drooping", "brown tips"],
            "remedies": [
                "Deep watering (soak thoroughly)",
                "Mulch to retain moisture",
                "Increase watering frequency",
                "Add water retention materials"
            ],
            "application": "Water deeply, then maintain schedule",
            "prevention": "Regular watering schedule"
        },
        "aphids": {
            "symptoms": ["small insects on leaves", "sticky residue", "curled leaves"],
            "remedies": [
                "Neem oil spray (1 tsp per liter water)",
                "Soapy water spray",
                "Garlic-chili spray",
                "Introduce ladybugs (natural predators)"
            ],
            "application": "Spray on affected areas, repeat every 3 days",
            "prevention": "Regular neem oil spray, companion planting"
        },
        "fungal_infection": {
            "symptoms": ["white powder", "spots on leaves", "mold", "wilting"],
            "remedies": [
                "Baking soda spray (1 tsp per liter)",
                "Neem oil application",
                "Remove affected leaves",
                "Improve air circulation"
            ],
            "application": "Spray weekly, remove infected parts",
            "prevention": "Avoid overhead watering, good spacing"
        },
        "spider_mites": {
            "symptoms": ["tiny webs", "yellow speckling", "fine dots on leaves"],
            "remedies": [
                "Strong water spray to dislodge",
                "Neem oil spray",
                "Onion-garlic spray",
                "Increase humidity"
            ],
            "application": "Spray undersides of leaves daily",
            "prevention": "Regular misting, neem oil prevention"
        }
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def scan_plant_health(self, image_path: str, plant_species: Optional[str] = None) -> Dict:
        """
        Comprehensive plant health scan using GPT-4o Vision
        
        Args:
            image_path: Path to plant image
            plant_species: Optional species for specific diagnosis
            
        Returns:
            Detailed health report with remedies
        """
        try:
            base64_image = self.encode_image(image_path)
            
            prompt = f"""
            Perform a comprehensive health analysis of this plant.
            {f"Plant species: {plant_species}" if plant_species else ""}
            
            Analyze for:
            1. Overall health status (healthy/stressed/diseased/dying)
            2. Nutrient deficiencies (nitrogen, phosphorus, potassium, etc.)
            3. Pest infestations (insects, mites, etc.)
            4. Diseases (fungal, bacterial, viral)
            5. Environmental stress (water, light, temperature)
            6. Leaf condition and color
            7. Stem and root visible condition
            
            For each issue found, provide:
            - Specific diagnosis
            - Severity (low/medium/high/critical)
            - Symptoms visible
            - Recommended organic remedies
            
            Return JSON:
            {{
                "overall_health": "healthy/mild_stress/moderate_stress/severe_stress/critical",
                "health_score": number (0-100),
                "issues_detected": [
                    {{
                        "issue_type": "deficiency/pest/disease/environmental",
                        "specific_diagnosis": "string",
                        "severity": "low/medium/high/critical",
                        "confidence": number (0-100),
                        "symptoms_observed": ["list"],
                        "affected_areas": ["leaves/stems/roots/flowers"]
                    }}
                ],
                "environmental_conditions": {{
                    "watering_status": "underwatered/optimal/overwatered",
                    "light_exposure": "insufficient/adequate/excessive",
                    "temperature_stress": "none/cold/heat"
                }},
                "immediate_actions": ["list of urgent actions needed"],
                "recommended_care": ["list of care recommendations"],
                "prognosis": "excellent/good/fair/poor/critical"
            }}
            """
            
            # Log AI request
            print("\n" + "="*70)
            print("🤖 AI REQUEST - Plant Health Scan")
            print("="*70)
            print(f"Model: {self.model}")
            print(f"Image: {os.path.basename(image_path)}")
            print(f"Plant Species: {plant_species or 'Not specified'}")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\nPrompt Preview:")
            print(prompt[:250] + "..." if len(prompt) > 250 else prompt)
            print("="*70)
            
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
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.2
            )
            elapsed_time = time.time() - start_time
            
            # Log AI response
            print("\n" + "="*70)
            print("✅ AI RESPONSE - Plant Health Scan")
            print("="*70)
            print(f"Response Time: {elapsed_time:.2f}s")
            print(f"Tokens Used: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            print(f"\nRaw Response:")
            print("-"*70)
            
            result_text = response.choices[0].message.content
            print(result_text[:500] + "..." if len(result_text) > 500 else result_text)
            print("-"*70)
            
            # Parse JSON
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start != -1:
                health_analysis = json.loads(result_text[json_start:json_end])
                
                # Log parsed results
                print("\n📊 Parsed Results:")
                print(f"  Health Score: {health_analysis.get('health_score', 'N/A')}/100")
                print(f"  Overall Health: {health_analysis.get('overall_health', 'N/A')}")
                print(f"  Issues Found: {len(health_analysis.get('issues_detected', []))}")
                print(f"  Prognosis: {health_analysis.get('prognosis', 'N/A')}")
            else:
                print("\n⚠️  Failed to parse JSON response")
                health_analysis = {"error": "Failed to parse response", "raw": result_text}
            
            print("="*70)
            
            # Add organic remedies from database
            remedies = self._match_remedies(health_analysis.get("issues_detected", []))
            
            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "health_analysis": health_analysis,
                "organic_remedies": remedies,
                "scan_points_earned": 5,
                "requires_immediate_action": self._requires_immediate_action(health_analysis)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _match_remedies(self, issues: List[Dict]) -> List[Dict]:
        """Match detected issues with organic remedies from database"""
        remedies = []
        
        for issue in issues:
            diagnosis = issue.get("specific_diagnosis", "").lower()
            
            # Try to match with known remedies
            for key, remedy_data in self.ORGANIC_REMEDIES.items():
                if key.replace("_", " ") in diagnosis:
                    remedies.append({
                        "issue": issue.get("specific_diagnosis"),
                        "severity": issue.get("severity"),
                        "remedy_name": key.replace("_", " ").title(),
                        "solutions": remedy_data["remedies"],
                        "application_method": remedy_data["application"],
                        "prevention_tips": remedy_data["prevention"],
                        "points_if_applied": 25
                    })
                    break
        
        return remedies
    
    def _requires_immediate_action(self, health_analysis: Dict) -> bool:
        """Check if plant requires immediate intervention"""
        overall_health = health_analysis.get("overall_health", "").lower()
        health_score = health_analysis.get("health_score", 100)
        
        critical_issues = [
            issue for issue in health_analysis.get("issues_detected", [])
            if issue.get("severity") in ["high", "critical"]
        ]
        
        return (
            overall_health in ["severe_stress", "critical"] or
            health_score < 40 or
            len(critical_issues) > 0
        )
    
    def suggest_organic_fertilizer(
        self,
        deficiency_type: str,
        plant_type: Optional[str] = None
    ) -> Dict:
        """
        Get specific organic fertilizer suggestions
        
        Args:
            deficiency_type: Type of deficiency detected
            plant_type: Optional plant type for specific recommendations
        """
        remedies = self.ORGANIC_REMEDIES.get(deficiency_type.lower().replace(" ", "_"), {})
        
        if not remedies:
            return {
                "success": False,
                "message": f"No specific remedy found for: {deficiency_type}"
            }
        
        # Create DIY recipe
        diy_recipe = self._generate_diy_recipe(deficiency_type, plant_type)
        
        return {
            "success": True,
            "deficiency": deficiency_type,
            "symptoms": remedies.get("symptoms", []),
            "organic_solutions": remedies.get("remedies", []),
            "application_method": remedies.get("application", ""),
            "prevention": remedies.get("prevention", ""),
            "diy_recipe": diy_recipe,
            "points_reward": 25
        }
    
    def _generate_diy_recipe(self, deficiency_type: str, plant_type: Optional[str]) -> Dict:
        """Generate DIY organic fertilizer recipe"""
        recipes = {
            "nitrogen_deficiency": {
                "name": "Cow Dung Tea",
                "ingredients": [
                    "1 kg cow dung",
                    "10 liters water",
                    "Optional: handful of dried leaves"
                ],
                "preparation": [
                    "Mix cow dung in water",
                    "Let it ferment for 3-5 days",
                    "Stir daily",
                    "Strain before use",
                    "Dilute 1:10 before applying"
                ],
                "application_frequency": "Once every 2 weeks",
                "shelf_life": "Use within 1 week of preparation"
            },
            "phosphorus_deficiency": {
                "name": "Banana Peel Fertilizer",
                "ingredients": [
                    "5-6 banana peels",
                    "2 liters water"
                ],
                "preparation": [
                    "Cut banana peels into small pieces",
                    "Soak in water for 24-48 hours",
                    "Blend or mash the mixture",
                    "Strain the liquid"
                ],
                "application_frequency": "Once every 2 weeks",
                "shelf_life": "Use immediately"
            },
            "potassium_deficiency": {
                "name": "Wood Ash Solution",
                "ingredients": [
                    "2 tablespoons wood ash",
                    "1 liter water"
                ],
                "preparation": [
                    "Mix wood ash in water",
                    "Let it sit for 24 hours",
                    "Stir well before use",
                    "Apply around plant base"
                ],
                "application_frequency": "Once a month",
                "shelf_life": "Use within 2 days"
            }
        }
        
        return recipes.get(deficiency_type.lower().replace(" ", "_"), {
            "name": "General Compost Tea",
            "ingredients": ["Compost", "Water"],
            "preparation": ["Mix and ferment for 5 days"],
            "application_frequency": "Weekly",
            "shelf_life": "1 week"
        })
    
    def verify_remedy_application(
        self,
        before_image: str,
        after_image: str,
        remedy_applied: str,
        days_elapsed: int
    ) -> Dict:
        """
        Verify that user applied remedy and check improvement
        Used to reward user for following treatment plan
        """
        try:
            before_b64 = self.encode_image(before_image)
            after_b64 = self.encode_image(after_image)
            
            prompt = f"""
            Compare these two plant images taken {days_elapsed} days apart.
            User claims they applied: {remedy_applied}
            
            Analyze:
            1. Is there visible improvement in plant health?
            2. Have symptoms reduced?
            3. Is the improvement consistent with the remedy applied?
            4. Any signs of recovery?
            
            Return JSON:
            {{
                "improvement_detected": boolean,
                "improvement_percentage": number (0-100),
                "symptoms_before": ["list"],
                "symptoms_after": ["list"],
                "recovery_progress": "excellent/good/moderate/poor/none",
                "remedy_effectiveness": "highly_effective/effective/somewhat_effective/ineffective",
                "reward_eligible": boolean,
                "notes": "string"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "text", "text": "BEFORE:"},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{before_b64}"}
                            },
                            {"type": "text", "text": "AFTER:"},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{after_b64}"}
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            result_text = response.choices[0].message.content
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            comparison = json.loads(result_text[json_start:json_end]) if json_start != -1 else {}
            
            # Calculate points
            points = 0
            if comparison.get("reward_eligible"):
                effectiveness = comparison.get("remedy_effectiveness", "")
                if "highly_effective" in effectiveness:
                    points = 30
                elif "effective" in effectiveness:
                    points = 25
                elif "somewhat" in effectiveness:
                    points = 15
            
            return {
                "success": True,
                "comparison": comparison,
                "points_earned": points,
                "days_elapsed": days_elapsed,
                "remedy_applied": remedy_applied,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_remedy_catalog(self) -> Dict:
        """Get complete catalog of organic remedies"""
        return {
            "total_remedies": len(self.ORGANIC_REMEDIES),
            "remedies": self.ORGANIC_REMEDIES,
            "categories": {
                "nutrient_deficiencies": ["nitrogen_deficiency", "phosphorus_deficiency", "potassium_deficiency"],
                "water_issues": ["overwatering", "underwatering"],
                "pests": ["aphids", "spider_mites"],
                "diseases": ["fungal_infection"]
            }
        }


if __name__ == "__main__":
    print("🏥 Plant Health AI - Test")
    print("="*70)
    
    ai = PlantHealthAI()
    
    # Show remedy catalog
    catalog = ai.get_remedy_catalog()
    print(f"\n💊 Remedy Catalog: {catalog['total_remedies']} remedies")
    print(f"Categories: {list(catalog['categories'].keys())}")
    
    # Test organic fertilizer suggestion
    suggestion = ai.suggest_organic_fertilizer("nitrogen_deficiency")
    if suggestion["success"]:
        print(f"\n🌿 Sample Recipe: {suggestion['diy_recipe']['name']}")
        print(f"Ingredients: {len(suggestion['diy_recipe']['ingredients'])} items")
    
    print("\n✅ Plant Health AI initialized successfully!")
