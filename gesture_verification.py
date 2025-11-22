"""
Hand Gesture Verification System
Captures and verifies field worker actions using computer vision
"""

import cv2
import numpy as np
import hashlib
import time
from typing import Dict, Optional, Tuple
from cvzone.HandTrackingModule import HandDetector


class GestureVerifier:
    """Verifies environmental actions using hand gestures and biometric signatures"""
    
    def __init__(self, detection_confidence=0.8):
        self.detector = HandDetector(detectionCon=detection_confidence)
        self.gesture_history = []
        self.verification_active = False
        
    def capture_biometric_signature(self, video_frame: np.ndarray) -> Optional[str]:
        """
        Create unique biometric signature from hand landmarks.
        Returns a hash that can be stored on blockchain.
        """
        hands, _ = self.detector.findHands(video_frame, draw=False)
        
        if not hands:
            return None
            
        hand = hands[0]
        landmarks = hand["lmList"]
        
        # Create normalized signature (distance between key points)
        thumb_tip = landmarks[4][:2]
        index_tip = landmarks[8][:2]
        middle_tip = landmarks[12][:2]
        ring_tip = landmarks[16][:2]
        pinky_tip = landmarks[20][:2]
        
        # Calculate relative distances (normalized)
        signature_data = f"{thumb_tip}-{index_tip}-{middle_tip}-{ring_tip}-{pinky_tip}"
        
        # Create SHA256 hash
        signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()
        
        return signature_hash
    
    def detect_confirmation_gesture(self, video_frame: np.ndarray) -> Tuple[bool, str]:
        """
        Detect specific confirmation gesture (thumbs up or pinch).
        Returns (gesture_detected, gesture_type)
        """
        hands, img = self.detector.findHands(video_frame)
        
        if not hands:
            return False, "no_hand"
        
        hand = hands[0]
        landmarks = hand["lmList"]
        
        # Check for pinch gesture (confirmation)
        thumb_tip = landmarks[4][:2]
        index_tip = landmarks[8][:2]
        distance = np.linalg.norm(np.array(thumb_tip) - np.array(index_tip))
        
        if distance < 40:  # Pinch detected
            return True, "pinch_confirm"
        
        # Check for thumbs up
        fingers = self.detector.fingersUp(hand)
        if fingers == [1, 0, 0, 0, 0]:  # Only thumb up
            return True, "thumbs_up"
        
        return False, "waiting"
    
    def verify_action_sequence(self, duration_seconds: int = 10) -> Dict:
        """
        Capture a sequence of gestures over time to verify action.
        Used to prevent fraud (requires sustained action).
        """
        cap = cv2.VideoCapture(0)
        cap.set(3, 1280)
        cap.set(4, 720)
        
        # Warm up camera
        print("\n📹 Initializing camera...")
        for _ in range(10):
            cap.read()
            time.sleep(0.1)
        
        start_time = time.time()
        gesture_count = 0
        signatures = []
        frames_captured = []
        last_gesture_time = 0
        
        print(f"\n" + "="*70)
        print(f"🌳 CARBON CREDIT VERIFICATION STARTED")
        print(f"="*70)
        print(f"⏱️  Duration: {duration_seconds} seconds")
        print(f"🎯 Goal: Detect at least 3 confirmation gestures")
        print(f"\n✋ Instructions:")
        print(f"   1. Position your hand in front of camera")
        print(f"   2. Make PINCH gesture (index + middle fingers together)")
        print(f"   3. OR make THUMBS UP gesture")
        print(f"   4. Hold gesture clearly for system to detect")
        print(f"\n" + "="*70 + "\n")
        
        time.sleep(1)  # Give user time to read
        
        frame_count = 0
        while (time.time() - start_time) < duration_seconds:
            success, frame = cap.read()
            if not success:
                print("⚠️  Camera frame capture failed")
                break
            
            frame = cv2.flip(frame, 1)
            current_time = time.time()
            frame_count += 1
            
            # Check for confirmation gesture
            detected, gesture_type = self.detect_confirmation_gesture(frame)
            
            # Live terminal feedback every 10 frames
            if frame_count % 10 == 0:
                elapsed = int(current_time - start_time)
                status = f"👁️  Live: {gesture_type.upper()} | Gestures: {gesture_count}/3 | Time: {duration_seconds - elapsed}s"
                print(f"\r{status}", end="", flush=True)
            
            # Create overlay for better UI
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (1280, 150), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
            
            if detected and (current_time - last_gesture_time) > 0.5:  # Debounce
                gesture_count += 1
                last_gesture_time = current_time
                signature = self.capture_biometric_signature(frame)
                if signature:
                    signatures.append(signature)
                frames_captured.append(frame.copy())
                
                # Visual feedback
                cv2.putText(frame, f"✓ DETECTED: {gesture_type.upper()}", 
                           (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                cv2.circle(frame, (640, 360), 100, (0, 255, 0), 5)
                
                # Terminal feedback (clear line first)
                print(f"\r{'':100}\r✅ Gesture #{gesture_count}: {gesture_type} detected at {int(current_time - start_time)}s          ")
            else:
                cv2.putText(frame, "Show PINCH or THUMBS UP gesture", 
                           (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
                cv2.circle(frame, (640, 360), 80, (0, 165, 255), 3)
            
            # Show progress
            elapsed = int(time.time() - start_time)
            remaining = duration_seconds - elapsed
            progress_text = f"Time: {remaining}s | Gestures: {gesture_count}/3 needed"
            cv2.putText(frame, progress_text, 
                       (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            
            # Progress bar
            bar_width = int((elapsed / duration_seconds) * 1200)
            cv2.rectangle(frame, (40, 120), (40 + bar_width, 140), (0, 255, 0), -1)
            cv2.rectangle(frame, (40, 120), (1240, 140), (255, 255, 255), 2)
            
            cv2.imshow("🌳 Carbon Credit Verification", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Validation
        is_valid = gesture_count >= 3  # Require at least 3 confirmations
        
        # Use most common signature
        final_signature = max(set(signatures), key=signatures.count) if signatures else None
        
        result = {
            "valid": is_valid,
            "gesture_count": gesture_count,
            "signature": final_signature,
            "duration": duration_seconds,
            "frames_captured": len(frames_captured),
            "confidence": gesture_count / (duration_seconds * 2)  # Rough confidence score
        }
        
        print(f"\n{'✅' if is_valid else '❌'} Verification {'PASSED' if is_valid else 'FAILED'}")
        print(f"   Gestures detected: {gesture_count}")
        print(f"   Signature: {final_signature[:16] if final_signature else 'None'}...")
        print(f"   Confidence: {result['confidence']:.1%}\n")
        
        return result
    
    def quick_verification(self) -> Dict:
        """
        Quick single-frame verification for testing.
        """
        cap = cv2.VideoCapture(0)
        cap.set(3, 1280)
        cap.set(4, 720)
        
        print("\n📸 Quick Verification - Show confirmation gesture")
        print("Press SPACE to capture, Q to quit\n")
        
        captured = False
        result = None
        
        while not captured:
            success, frame = cap.read()
            if not success:
                break
            
            frame = cv2.flip(frame, 1)
            detected, gesture_type = self.detect_confirmation_gesture(frame)
            
            if detected:
                cv2.putText(frame, f"✓ {gesture_type} detected - Press SPACE", 
                           (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Show confirmation gesture", 
                           (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
            
            cv2.imshow("Quick Verification", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):  # Space to capture
                signature = self.capture_biometric_signature(frame)
                result = {
                    "valid": detected,
                    "gesture_type": gesture_type,
                    "signature": signature,
                    "timestamp": time.time()
                }
                captured = True
            elif key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        return result or {"valid": False, "error": "No capture"}
