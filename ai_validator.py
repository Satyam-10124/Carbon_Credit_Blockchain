"""
AI Validation Module using OpenAI
Validates environmental actions and generates verification reports
"""

import os
import base64
from typing import Dict, Optional, List
from openai import OpenAI
import json


class AIValidator:
    """Uses OpenAI to validate and verify environmental actions"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️  AI system unavailable: OPENAI_API_KEY environment variable is required")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=api_key)
            except Exception as e:
                print(f"⚠️  AI initialization failed: {e}")
                self.client = None
        
    def validate_tree_planting_claim(
        self,
        trees_claimed: int,
        location: str,
        gps_coords: str,
        image_path: Optional[str] = None
    ) -> Dict:
        """
        Use AI to validate tree planting claims and detect fraud.
        Analyzes contextual data and optionally images.
        """
        
        # If AI client not available, use simple validation
        if not self.client:
            return {
                "valid": trees_claimed <= 100,
                "confidence": 50,
                "plausibility_score": 70 if trees_claimed <= 100 else 30,
                "location_score": 70,
                "risk_level": "low" if trees_claimed <= 50 else "medium",
                "reasoning": "AI validation unavailable - using rule-based check",
                "recommendation": "approve" if trees_claimed <= 100 else "review",
                "carbon_offset_kg": trees_claimed * 21.77
            }
        
        prompt = f"""You are a carbon credit validator. Analyze this tree planting claim:

Trees Claimed: {trees_claimed}
Location: {location}
GPS Coordinates: {gps_coords}

Assess:
1. Plausibility (can one person plant {trees_claimed} trees in one session?)
2. Location validity (is this a real place suitable for tree planting?)
3. Risk factors (any red flags?)
4. Recommended action (approve, reject, or request more evidence)

Respond in JSON format:
{{
    "valid": true/false,
    "confidence": 0-100,
    "plausibility_score": 0-100,
    "location_score": 0-100,
    "risk_level": "low/medium/high",
    "reasoning": "explanation",
    "recommendation": "approve/reject/review",
    "carbon_offset_kg": estimated CO2 offset
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an environmental verification expert specializing in carbon credits."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            print(f"\n🤖 AI VALIDATION RESULT")
            print(f"   Valid: {result.get('valid')}")
            print(f"   Confidence: {result.get('confidence')}%")
            print(f"   Recommendation: {result.get('recommendation')}")
            print(f"   Reasoning: {result.get('reasoning')}\n")
            
            return result
            
        except Exception as e:
            print(f"❌ AI validation failed: {e}")
            return {
                "valid": False,
                "confidence": 0,
                "error": str(e),
                "recommendation": "review"
            }
    
    def analyze_verification_image(self, image_path: str, trees_claimed: int) -> Dict:
        """
        Use GPT-4 Vision to analyze photo evidence of tree planting.
        """
        
        # If AI client not available, skip image analysis
        if not self.client:
            return {
                "trees_visible": True,
                "genuine_activity": True,
                "fraud_indicators": [],
                "estimated_trees": trees_claimed,
                "confidence": 50,
                "recommendation": "review",
                "note": "AI image analysis unavailable"
            }
        
        try:
            with open(image_path, "rb") as img_file:
                image_data = base64.b64encode(img_file.read()).decode('utf-8')
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""Analyze this image as evidence of tree planting. 
                                
Worker claims: {trees_claimed} trees planted.

Verify:
1. Are trees visible?
2. Does it look like genuine planting activity?
3. Any signs of fraud or stock photos?
4. Environmental context appropriate?

Respond in JSON:
{{
    "trees_visible": true/false,
    "genuine_activity": true/false,
    "fraud_indicators": [],
    "estimated_trees": number,
    "confidence": 0-100,
    "recommendation": "approve/reject/review"
}}"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            print(f"\n📸 IMAGE ANALYSIS RESULT")
            print(f"   Trees visible: {result.get('trees_visible')}")
            print(f"   Genuine activity: {result.get('genuine_activity')}")
            print(f"   Confidence: {result.get('confidence')}%\n")
            
            return result
            
        except FileNotFoundError:
            return {
                "error": "Image file not found",
                "recommendation": "review"
            }
        except Exception as e:
            print(f"❌ Image analysis failed: {e}")
            return {
                "error": str(e),
                "recommendation": "review"
            }
    
    def generate_verification_report(
        self,
        gesture_result: Dict,
        ai_validation: Dict,
        image_analysis: Optional[Dict] = None
    ) -> str:
        """
        Generate comprehensive verification report using AI.
        """
        
        prompt = f"""Generate a professional carbon credit verification report.

GESTURE VERIFICATION:
{json.dumps(gesture_result, indent=2)}

AI VALIDATION:
{json.dumps(ai_validation, indent=2)}

{"IMAGE ANALYSIS:" if image_analysis else ""}
{json.dumps(image_analysis, indent=2) if image_analysis else "No image provided"}

Create a concise report (200 words) covering:
- Overall verification status
- Key findings
- Confidence level
- Recommendation for NFT minting
- Any concerns or notes
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a carbon credit auditor writing verification reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            report = response.choices[0].message.content
            return report
            
        except Exception as e:
            return f"Report generation failed: {e}"
    
    def detect_fraud_patterns(self, verification_history: List[Dict]) -> Dict:
        """
        Analyze multiple submissions from same worker to detect fraud patterns.
        """
        
        prompt = f"""Analyze these verification records for fraud patterns:

{json.dumps(verification_history, indent=2)}

Look for:
- Impossible frequencies (too many trees too fast)
- Duplicate GPS coordinates
- Suspiciously consistent gesture signatures
- Other anomalies

Respond in JSON:
{{
    "fraud_detected": true/false,
    "confidence": 0-100,
    "patterns": [],
    "recommendation": "continue/suspend/investigate"
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a fraud detection specialist for carbon credits."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {
                "fraud_detected": False,
                "error": str(e),
                "recommendation": "investigate"
            }
