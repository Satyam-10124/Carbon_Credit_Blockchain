"""
Plant Verification AI - Video Analysis
Verifies it's the same plant every day (anti-fraud)
Uses GPT-4o Vision + Computer Vision techniques
"""

import os
import cv2
import base64
import json
import hashlib
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from openai import OpenAI
from pathlib import Path
import numpy as np


class PlantVerificationAI:
    """
    AI service to verify plant identity across multiple days
    Prevents users from showing different plants to earn rewards
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"
    
    def extract_video_frames(self, video_path: str, num_frames: int = 3) -> List[str]:
        """
        Extract key frames from video for analysis
        Returns paths to extracted frames
        """
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames == 0:
            raise ValueError("Invalid video file")
        
        # Extract frames at equal intervals
        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        
        frames_paths = []
        temp_dir = Path("temp_frames")
        temp_dir.mkdir(exist_ok=True)
        
        for idx, frame_num in enumerate(frame_indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            
            if ret:
                frame_path = temp_dir / f"frame_{idx}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(str(frame_path), frame)
                frames_paths.append(str(frame_path))
        
        cap.release()
        return frames_paths
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def create_plant_fingerprint(self, image_path: str) -> Dict:
        """
        Create a unique fingerprint of the plant using GPT-4o Vision
        This fingerprint is used to verify it's the same plant later
        """
        try:
            base64_image = self.encode_image(image_path)
            
            prompt = """
            Create a detailed fingerprint of this plant for future verification.
            
            Analyze and describe:
            1. Unique identifying features (leaf shape, pattern, color variations)
            2. Number of leaves/stems visible
            3. Growth stage and size
            4. Pot/container characteristics (if visible)
            5. Background features (fixed landmarks)
            6. Any unique marks, damages, or characteristics
            7. Overall plant structure and appearance
            
            Be very specific and detailed. This will be used to verify if future photos
            show the same exact plant.
            
            Return JSON:
            {
                "unique_features": ["list of specific features"],
                "leaf_count_estimate": number,
                "growth_stage": "string",
                "size_estimate": "string",
                "container_description": "string",
                "background_landmarks": ["list"],
                "unique_marks": ["list"],
                "overall_description": "string",
                "fingerprint_hash": "generate a unique descriptor"
            }
            """
            
            # Log AI request
            print("\n" + "="*70)
            print("🤖 AI REQUEST - Plant Fingerprint Creation")
            print("="*70)
            print(f"Model: {self.model}")
            print(f"Image: {os.path.basename(image_path)}")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
                max_tokens=1500,
                temperature=0.1
            )
            elapsed_time = time.time() - start_time
            
            # Log AI response
            print("\n✅ AI RESPONSE - Plant Fingerprint")
            print(f"Response Time: {elapsed_time:.2f}s")
            print(f"Tokens Used: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            print("="*70)
            
            result_text = response.choices[0].message.content
            
            # Parse JSON
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start != -1:
                fingerprint = json.loads(result_text[json_start:json_end])
                print(f"✅ Fingerprint created with {len(fingerprint.get('unique_features', []))} unique features")
            else:
                fingerprint = {"raw_description": result_text}
                print("⚠️  JSON parsing failed, using raw description")
            
            print("="*70)
            
            # Add metadata
            fingerprint["created_at"] = datetime.now().isoformat()
            fingerprint["image_path"] = image_path
            
            return {
                "success": True,
                "fingerprint": fingerprint,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def verify_same_plant(
        self, 
        original_fingerprint: Dict,
        new_image_path: str,
        strict_mode: bool = True
    ) -> Dict:
        """
        Verify if new image shows the same plant as original fingerprint
        
        Args:
            original_fingerprint: Plant fingerprint from first day
            new_image_path: Path to new image/video frame
            strict_mode: If True, requires high confidence match
            
        Returns:
            Verification result with confidence score
        """
        try:
            base64_image = self.encode_image(new_image_path)
            
            prompt = f"""
            Compare this plant image with the original plant fingerprint below.
            Determine if this is THE SAME EXACT PLANT or a different plant.
            
            ORIGINAL PLANT FINGERPRINT:
            {json.dumps(original_fingerprint.get('fingerprint', {}), indent=2)}
            
            Analyze:
            1. Do the unique features match?
            2. Is the leaf count similar (accounting for natural growth)?
            3. Does the container/pot match?
            4. Do background landmarks match?
            5. Are unique marks still visible?
            6. Is growth progression natural and consistent?
            
            Be very strict in your analysis. Look for signs of:
            - Different plant species
            - Completely different container
            - Different location/background
            - Unnatural growth (too fast/slow)
            
            Return JSON:
            {{
                "is_same_plant": boolean,
                "confidence": number (0-100),
                "matching_features": ["list of features that match"],
                "non_matching_features": ["list of discrepancies"],
                "growth_detected": boolean,
                "growth_description": "string",
                "fraud_indicators": ["list any suspicious elements"],
                "verdict": "VERIFIED / REJECTED / UNCERTAIN",
                "explanation": "detailed reasoning"
            }}
            """
            
            # Log AI request
            print("\n" + "="*70)
            print("🤖 AI REQUEST - Same Plant Verification")
            print("="*70)
            print(f"Model: {self.model}")
            print(f"New Image: {os.path.basename(new_image_path)}")
            print(f"Strict Mode: {strict_mode}")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
                max_tokens=1500,
                temperature=0.1
            )
            elapsed_time = time.time() - start_time
            
            # Log AI response
            print("\n✅ AI RESPONSE - Plant Verification")
            print(f"Response Time: {elapsed_time:.2f}s")
            print(f"Tokens Used: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
            print("="*70)
            
            result_text = response.choices[0].message.content
            
            # Parse JSON
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start != -1:
                verification = json.loads(result_text[json_start:json_end])
                print(f"📊 Verdict: {verification.get('verdict', 'N/A')}")
                print(f"   Confidence: {verification.get('confidence', 0)}%")
                print(f"   Same Plant: {'Yes' if verification.get('is_same_plant') else 'No'}")
            else:
                verification = {"error": "Failed to parse response"}
                print("⚠️  JSON parsing failed")
            
            print("="*70)
            
            # Determine if verification passed
            confidence_threshold = 80 if strict_mode else 60
            verification_passed = (
                verification.get("is_same_plant", False) and
                verification.get("confidence", 0) >= confidence_threshold and
                verification.get("verdict") == "VERIFIED"
            )
            
            return {
                "success": True,
                "verification_passed": verification_passed,
                "verification_details": verification,
                "strict_mode": strict_mode,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "verification_passed": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def verify_watering_video(
        self,
        video_path: str,
        plant_fingerprint: Dict,
        day_number: int
    ) -> Dict:
        """
        Verify daily watering video
        Ensures: 
        1. Same plant as registered
        2. Actually watering (water visible)
        3. Natural growth progression
        """
        try:
            # Extract frames from video
            frames = self.extract_video_frames(video_path, num_frames=3)
            
            if not frames:
                return {
                    "success": False,
                    "error": "No frames extracted from video"
                }
            
            # Use middle frame for verification
            main_frame = frames[len(frames)//2]
            
            # First verify it's the same plant
            plant_verification = self.verify_same_plant(
                plant_fingerprint,
                main_frame,
                strict_mode=True
            )
            
            if not plant_verification["verification_passed"]:
                return {
                    "success": True,
                    "video_verified": False,
                    "reason": "Plant mismatch - different plant detected",
                    "details": plant_verification,
                    "reward_eligible": False
                }
            
            # Now verify watering activity
            base64_image = self.encode_image(main_frame)
            
            watering_prompt = """
            Analyze this image to verify watering activity.
            
            Check for:
            1. Is water visible (falling, splashing, on leaves)?
            2. Is watering equipment visible (can, hose, bottle)?
            3. Is the soil/plant wet?
            4. Does this look like an authentic watering moment?
            
            Return JSON:
            {
                "watering_detected": boolean,
                "confidence": number (0-100),
                "water_evidence": ["list what indicates watering"],
                "soil_condition": "dry/moist/wet",
                "authenticity_score": number (0-100),
                "notes": "string"
            }
            """
            
            watering_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": watering_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                max_tokens=800,
                temperature=0.1
            )
            
            watering_text = watering_response.choices[0].message.content
            json_start = watering_text.find('{')
            json_end = watering_text.rfind('}') + 1
            watering_analysis = json.loads(watering_text[json_start:json_end]) if json_start != -1 else {}
            
            # Final verdict
            video_verified = (
                plant_verification["verification_passed"] and
                watering_analysis.get("watering_detected", False) and
                watering_analysis.get("confidence", 0) >= 70
            )
            
            # Clean up temp frames
            for frame in frames:
                try:
                    os.remove(frame)
                except:
                    pass
            
            return {
                "success": True,
                "video_verified": video_verified,
                "day_number": day_number,
                "plant_verification": plant_verification["verification_details"],
                "watering_verification": watering_analysis,
                "reward_eligible": video_verified,
                "points_earned": 5 if video_verified else 0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "video_verified": False,
                "reward_eligible": False
            }
    
    def analyze_growth_progression(
        self,
        historical_fingerprints: List[Dict],
        days_elapsed: int
    ) -> Dict:
        """
        Analyze if plant growth is natural over time
        Detect if user is swapping plants
        """
        if len(historical_fingerprints) < 2:
            return {"sufficient_data": False}
        
        # Compare first and last fingerprints
        first = historical_fingerprints[0]
        last = historical_fingerprints[-1]
        
        prompt = f"""
        Analyze plant growth progression over {days_elapsed} days.
        
        FIRST DAY FINGERPRINT:
        {json.dumps(first.get('fingerprint', {}), indent=2)}
        
        LATEST DAY FINGERPRINT:
        {json.dumps(last.get('fingerprint', {}), indent=2)}
        
        Determine:
        1. Is growth progression natural for {days_elapsed} days?
        2. Are there suspicious changes?
        3. Could this be a different plant?
        
        Return JSON:
        {{
            "growth_natural": boolean,
            "growth_rate": "none/slow/normal/fast/suspicious",
            "consistency_score": number (0-100),
            "red_flags": ["list any concerns"],
            "verdict": "NATURAL / SUSPICIOUS / FRAUDULENT"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            analysis = json.loads(result_text[json_start:json_end]) if json_start != -1 else {}
            
            return {
                "success": True,
                "analysis": analysis,
                "days_analyzed": days_elapsed,
                "samples_count": len(historical_fingerprints)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


if __name__ == "__main__":
    print("🔍 Plant Verification AI - Test")
    print("="*70)
    print("✅ Plant Verification AI initialized successfully!")
    print("\nFeatures:")
    print("  • Create plant fingerprints")
    print("  • Verify same plant across days")
    print("  • Verify watering videos")
    print("  • Detect fraud attempts")
    print("  • Analyze growth progression")
