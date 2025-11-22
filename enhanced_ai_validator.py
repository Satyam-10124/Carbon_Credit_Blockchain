"""
Enhanced AI Validation with GPT-4 Vision and Multi-Modal Analysis
Includes fraud detection, image analysis, and location validation
"""

import os
import base64
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class EnhancedAIValidator:
    """Enhanced AI validation with vision and multi-modal analysis"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        
        if self.api_key and OpenAI:
            try:
                self.client = OpenAI(api_key=self.api_key)
                print("✅ Enhanced AI Validator initialized with GPT-4 Vision")
            except Exception as e:
                print(f"⚠️  Enhanced AI initialization failed: {e}")
                self.client = None
        else:
            print("⚠️  Enhanced AI unavailable: Missing OpenAI API key or library")
    
    def validate_comprehensive(
        self,
        trees_planted: int,
        location: str,
        gps_coords: str,
        worker_id: str,
        image_url: Optional[str] = None,
        image_path: Optional[str] = None,
        weather_data: Optional[Dict] = None,
        historical_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive multi-modal validation
        
        Analyzes:
        - Claim plausibility
        - Location validity
        - Image authenticity
        - Historical patterns
        - Weather conditions
        - Fraud indicators
        """
        
        if not self.client:
            return self._mock_validation(trees_planted, location)
        
        try:
            # Build multi-modal context
            context = self._build_validation_context(
                trees_planted, location, gps_coords, worker_id,
                weather_data, historical_data
            )
            
            # Perform different validation layers
            validations = []
            
            # 1. Text-based plausibility check
            plausibility = self._validate_plausibility(context)
            validations.append(plausibility)
            
            # 2. Image analysis (if provided)
            if image_url or image_path:
                image_analysis = self._analyze_image(
                    image_url, image_path, trees_planted, location
                )
                validations.append(image_analysis)
            
            # 3. Fraud detection
            fraud_check = self._detect_fraud_patterns(
                trees_planted, worker_id, historical_data
            )
            validations.append(fraud_check)
            
            # Aggregate results
            return self._aggregate_validations(validations)
            
        except Exception as e:
            print(f"❌ Enhanced AI validation error: {e}")
            return {
                "valid": False,
                "confidence": 0.0,
                "reason": f"Validation error: {str(e)}",
                "recommendation": "manual_review"
            }
    
    def _build_validation_context(
        self,
        trees: int,
        location: str,
        gps: str,
        worker: str,
        weather: Optional[Dict],
        history: Optional[Dict]
    ) -> str:
        """Build comprehensive context for AI analysis"""
        
        context = f"""
Carbon Credit Verification Request:

CLAIM DETAILS:
- Trees Planted: {trees}
- Location: {location}
- GPS Coordinates: {gps}
- Worker ID: {worker}
- Submission Time: {datetime.now().isoformat()}

ADDITIONAL CONTEXT:
"""
        
        if weather:
            context += f"""
WEATHER CONDITIONS:
- Temperature: {weather.get('temp', 'Unknown')}°C
- Conditions: {weather.get('conditions', 'Unknown')}
- Precipitation: {weather.get('precipitation', 'Unknown')}mm
"""
        
        if history:
            context += f"""
WORKER HISTORY:
- Previous Verifications: {history.get('total_verifications', 0)}
- Average Trees/Day: {history.get('avg_trees_per_day', 0)}
- Success Rate: {history.get('success_rate', 100)}%
- Last Verification: {history.get('last_verification', 'Never')}
"""
        
        return context
    
    def _validate_plausibility(self, context: str) -> Dict[str, Any]:
        """Validate claim plausibility using GPT-4"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert environmental verification AI specializing in 
detecting fraudulent carbon credit claims. Analyze claims for physical plausibility, 
geographical consistency, and fraud indicators.

Respond in JSON format:
{
  "plausible": boolean,
  "confidence": float (0-1),
  "reasoning": string,
  "red_flags": [list of concerns],
  "recommendation": "approve" | "reject" | "manual_review"
}"""
                    },
                    {
                        "role": "user",
                        "content": f"""{context}

ANALYZE THIS CLAIM:
1. Is the number of trees physically plausible for one day's work?
2. Is the location suitable for tree planting?
3. Are there any obvious fraud indicators?
4. What is your confidence level?

Provide detailed reasoning."""
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result["validation_type"] = "plausibility"
            return result
            
        except Exception as e:
            print(f"⚠️  Plausibility check failed: {e}")
            return {
                "plausible": True,
                "confidence": 0.5,
                "reasoning": "Could not perform plausibility check",
                "red_flags": [],
                "recommendation": "manual_review",
                "validation_type": "plausibility"
            }
    
    def _analyze_image(
        self,
        image_url: Optional[str],
        image_path: Optional[str],
        trees_claimed: int,
        location: str
    ) -> Dict[str, Any]:
        """Analyze image using GPT-4 Vision"""
        
        try:
            # Prepare image for analysis
            if image_path and os.path.exists(image_path):
                with open(image_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                    image_input = f"data:image/jpeg;base64,{image_data}"
            elif image_url:
                image_input = image_url
            else:
                return {
                    "valid": True,
                    "confidence": 0.5,
                    "reasoning": "No image provided",
                    "validation_type": "image_analysis"
                }
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert at detecting fraudulent tree planting images. 
Analyze images for authenticity, tree count estimation, and fraud indicators.

Respond in JSON format:
{
  "authentic": boolean,
  "trees_visible": integer,
  "confidence": float (0-1),
  "observations": [list of key observations],
  "fraud_indicators": [list of concerns],
  "recommendation": "approve" | "reject" | "manual_review"
}"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""Analyze this tree planting verification image:

CLAIMED: {trees_claimed} trees planted at {location}

VERIFY:
1. Are trees or saplings visible?
2. Approximately how many trees can you see?
3. Does this appear to be a genuine tree planting activity?
4. Are there signs of stock photos, screenshots, or manipulation?
5. Is the environment consistent with tree planting?

Provide detailed analysis."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": image_input}
                            }
                        ]
                    }
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result["validation_type"] = "image_analysis"
            return result
            
        except Exception as e:
            print(f"⚠️  Image analysis failed: {e}")
            return {
                "authentic": True,
                "trees_visible": 0,
                "confidence": 0.5,
                "observations": [f"Analysis failed: {str(e)}"],
                "fraud_indicators": [],
                "recommendation": "manual_review",
                "validation_type": "image_analysis"
            }
    
    def _detect_fraud_patterns(
        self,
        trees: int,
        worker_id: str,
        historical_data: Optional[Dict]
    ) -> Dict[str, Any]:
        """Detect fraud patterns based on historical data"""
        
        fraud_indicators = []
        confidence = 1.0
        
        # Check for suspicious patterns
        if historical_data:
            # Unusual spike in productivity
            avg_trees = historical_data.get('avg_trees_per_day', 0)
            if avg_trees > 0 and trees > avg_trees * 3:
                fraud_indicators.append(
                    f"Unusual spike: {trees} trees vs avg {avg_trees}"
                )
                confidence -= 0.2
            
            # Too many verifications in short time
            recent_count = historical_data.get('verifications_last_24h', 0)
            if recent_count > 10:
                fraud_indicators.append(
                    f"Too many verifications: {recent_count} in 24h"
                )
                confidence -= 0.3
            
            # Low historical success rate
            success_rate = historical_data.get('success_rate', 100)
            if success_rate < 50:
                fraud_indicators.append(
                    f"Low success rate: {success_rate}%"
                )
                confidence -= 0.2
        
        # Physical impossibility check
        if trees > 500:
            fraud_indicators.append(
                f"Physically implausible: {trees} trees in one day"
            )
            confidence -= 0.5
        
        # Determine recommendation
        if confidence < 0.4:
            recommendation = "reject"
        elif confidence < 0.7:
            recommendation = "manual_review"
        else:
            recommendation = "approve"
        
        return {
            "fraud_detected": len(fraud_indicators) > 0,
            "fraud_indicators": fraud_indicators,
            "confidence": max(0.0, confidence),
            "recommendation": recommendation,
            "validation_type": "fraud_detection"
        }
    
    def _aggregate_validations(self, validations: List[Dict]) -> Dict[str, Any]:
        """Aggregate multiple validation results"""
        
        # Extract key metrics
        confidences = [v.get('confidence', 0.5) for v in validations]
        recommendations = [v.get('recommendation', 'manual_review') for v in validations]
        
        # Calculate overall confidence
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        
        # Determine final recommendation (most conservative)
        if "reject" in recommendations:
            final_recommendation = "reject"
        elif "manual_review" in recommendations:
            final_recommendation = "manual_review"
        else:
            final_recommendation = "approve"
        
        # Aggregate all findings
        all_concerns = []
        for v in validations:
            if 'red_flags' in v:
                all_concerns.extend(v['red_flags'])
            if 'fraud_indicators' in v:
                all_concerns.extend(v['fraud_indicators'])
        
        return {
            "valid": final_recommendation == "approve",
            "confidence": round(overall_confidence, 2),
            "recommendation": final_recommendation,
            "validations": validations,
            "concerns": all_concerns,
            "summary": self._generate_summary(validations, final_recommendation),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_summary(self, validations: List[Dict], recommendation: str) -> str:
        """Generate human-readable summary"""
        
        summaries = []
        
        for v in validations:
            vtype = v.get('validation_type', 'unknown')
            
            if vtype == 'plausibility':
                if v.get('plausible'):
                    summaries.append("✅ Claim is physically plausible")
                else:
                    summaries.append("❌ Claim appears implausible")
            
            elif vtype == 'image_analysis':
                if v.get('authentic'):
                    trees = v.get('trees_visible', 0)
                    summaries.append(f"✅ Image appears authentic (~{trees} trees visible)")
                else:
                    summaries.append("❌ Image shows fraud indicators")
            
            elif vtype == 'fraud_detection':
                if not v.get('fraud_detected'):
                    summaries.append("✅ No fraud patterns detected")
                else:
                    summaries.append(f"⚠️  {len(v.get('fraud_indicators', []))} fraud indicators found")
        
        summary = " | ".join(summaries)
        
        if recommendation == "approve":
            summary += " | 🎉 APPROVED for NFT minting"
        elif recommendation == "reject":
            summary += " | ❌ REJECTED - do not mint"
        else:
            summary += " | ⏳ MANUAL REVIEW required"
        
        return summary
    
    def _mock_validation(self, trees: int, location: str) -> Dict[str, Any]:
        """Mock validation when AI is unavailable"""
        
        # Simple rule-based validation
        valid = trees <= 100 and trees > 0
        confidence = 0.7 if valid else 0.3
        
        return {
            "valid": valid,
            "confidence": confidence,
            "recommendation": "approve" if valid else "manual_review",
            "validations": [{
                "validation_type": "basic_rules",
                "reasoning": f"Basic validation: {trees} trees at {location}",
                "note": "Enhanced AI unavailable - using rule-based validation"
            }],
            "concerns": [] if valid else ["Tree count seems high"],
            "summary": f"Basic validation: {'PASS' if valid else 'REVIEW NEEDED'}",
            "timestamp": datetime.now().isoformat()
        }


def test_enhanced_validator():
    """Test the enhanced validator"""
    print("\n" + "="*70)
    print("🧪 TESTING ENHANCED AI VALIDATOR")
    print("="*70 + "\n")
    
    validator = EnhancedAIValidator()
    
    # Test case 1: Normal claim
    print("Test 1: Normal claim")
    result = validator.validate_comprehensive(
        trees_planted=25,
        location="Mumbai, Maharashtra, India",
        gps_coords="19.0760° N, 72.8777° E",
        worker_id="WORKER001",
        historical_data={
            'total_verifications': 10,
            'avg_trees_per_day': 20,
            'success_rate': 95,
            'last_verification': '2024-01-15'
        }
    )
    
    print(f"Result: {result['recommendation']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Summary: {result['summary']}\n")
    
    # Test case 2: Suspicious claim
    print("Test 2: Suspicious claim (too many trees)")
    result = validator.validate_comprehensive(
        trees_planted=500,
        location="Mumbai, India",
        gps_coords="19.0760° N, 72.8777° E",
        worker_id="WORKER002",
        historical_data={
            'total_verifications': 1,
            'avg_trees_per_day': 10,
            'success_rate': 40
        }
    )
    
    print(f"Result: {result['recommendation']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Summary: {result['summary']}\n")
    
    print("="*70)


if __name__ == "__main__":
    test_enhanced_validator()
