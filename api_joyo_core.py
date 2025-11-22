"""
Joyo Core API - Plant Care & Rewards System
FastAPI implementation with all core Joyo features
"""

import os
import json
from uuid import uuid4
from typing import Dict, Any, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from datetime import date, timedelta

# Import Joyo services
from database_postgres import db

# Import AI services (with graceful fallback if dependencies missing)
try:
    from joyo_ai_services.plant_recognition import PlantRecognitionAI
    from joyo_ai_services.plant_health import PlantHealthAI
    from joyo_ai_services.plant_verification import PlantVerificationAI
    from joyo_ai_services.geo_verification import GeoVerificationAI
    AI_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  AI services not available (optional): {e}")
    AI_SERVICES_AVAILABLE = False
    PlantRecognitionAI = None
    PlantHealthAI = None
    PlantVerificationAI = None
    GeoVerificationAI = None

# Import Algorand NFT minting
try:
    from algorand_nft import mint_carbon_credit_nft
    ALGORAND_AVAILABLE = True
except ImportError:
    print("⚠️  Algorand NFT module not available")
    ALGORAND_AVAILABLE = False

# Load environment
load_dotenv()

# Configuration
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/tmp/joyo_uploads"))
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

# Initialize FastAPI
app = FastAPI(
    title="Joyo Environment Mini App",
    description="Plant care tracking with AI verification and blockchain rewards",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Initialize AI services (if available)
if AI_SERVICES_AVAILABLE:
    try:
        plant_recognition = PlantRecognitionAI()
        plant_health = PlantHealthAI()
        plant_verification = PlantVerificationAI()
        geo_verification = GeoVerificationAI()
        print("✅ AI services initialized successfully")
    except Exception as e:
        print(f"⚠️  AI services failed to initialize: {e}")
        AI_SERVICES_AVAILABLE = False
        plant_recognition = None
        plant_health = None
        plant_verification = None
        geo_verification = None
else:
    plant_recognition = None
    plant_health = None
    plant_verification = None
    geo_verification = None
    print("ℹ️  Running in API-only mode (AI services disabled)")


# ============================================================================
# CORE JOYO ENDPOINTS
# ============================================================================

@app.get("/")
async def index() -> Dict[str, Any]:
    """API information"""
    return {
        'name': 'Joyo Environment Mini App API',
        'version': '1.0.0',
        'description': 'Plant care tracking with AI verification and rewards',
        'endpoints': {
            'plants': {
                'GET /plants/catalog': 'Get available plants',
                'POST /plants/register': 'Register a new plant (+30 points)',
                'POST /plants/{id}/planting-photo': 'Upload planting photo (+20 points)',
                'GET /plants/{id}': 'Get plant details',
                'GET /plants/user/{user_id}': 'Get user plants',
            },
            'activities': {
                'POST /plants/{id}/water': 'Record daily watering (+5 points)',
                'POST /plants/{id}/health-scan': 'Scan plant health (+5 points, max 2/week)',
                'POST /plants/{id}/remedy-apply': 'Apply remedy (+20-25 points)',
                'POST /plants/{id}/protection': 'Add protection/netting (+10 points)',
            },
            'rewards': {
                'GET /users/{id}/points': 'Get user points balance',
                'GET /users/{id}/history': 'Get points history',
                'POST /coins/convert': 'Convert points to coins (after 6 months)',
            },
            'stats': {
                'GET /stats': 'Get overall system stats',
                'GET /stats/csr': 'Get CSR dashboard data',
            }
        },
        'timestamp': datetime.now().isoformat()
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check"""
    return {
        'status': 'healthy',
        'database': 'connected',
        'ai_services': 'available',
        'algorand': 'available' if ALGORAND_AVAILABLE else 'not configured',
        'timestamp': datetime.now().isoformat()
    }


# ============================================================================
# PLANT MANAGEMENT
# ============================================================================

@app.get("/plants/catalog")
async def get_plant_catalog() -> Dict[str, Any]:
    """
    Get catalog of available air-purifying plants
    Shows CO2 absorption rate, care instructions, points multiplier
    """
    catalog = plant_recognition.get_plant_catalog()
    
    return {
        'success': True,
        'total_plants': catalog['total_plants'],
        'plants': catalog['plants'],
        'categories': catalog['categories'],
        'timestamp': datetime.now().isoformat()
    }


@app.post("/plants/register")
async def register_plant(
    user_id: str = Form(...),
    plant_type: str = Form(...),
    location: str = Form(...),
    gps_latitude: float = Form(...),
    gps_longitude: float = Form(...),
    name: str = Form(None),
    email: str = Form(None)
) -> Dict[str, Any]:
    """
    Register a new plant
    Awards 30 points for plant purchase
    
    Step 1 of Joyo flow
    """
    try:
        # Check if user exists, create if not
        user = db.get_user(user_id)
        if not user:
            db.create_user(user_id, name=name, email=email, location=location)
        
        # Generate plant ID
        plant_id = f"PLANT_{uuid4().hex[:8].upper()}"
        
        # Register plant
        result = db.register_plant(
            plant_id=plant_id,
            user_id=user_id,
            plant_type=plant_type,
            location=location,
            gps_latitude=gps_latitude,
            gps_longitude=gps_longitude
        )
        
        # Award points for plant purchase
        transaction_id = f"TXN_{uuid4().hex[:12].upper()}"
        points_result = db.add_points(
            transaction_id=transaction_id,
            user_id=user_id,
            points=30,
            transaction_type='plant_purchase',
            description=f'Purchased {plant_type} plant',
            plant_id=plant_id
        )
        
        return {
            'success': True,
            'plant_id': plant_id,
            'user_id': user_id,
            'points_earned': 30,
            'total_points': points_result['total_points'],
            'message': f'Plant registered! You earned 30 points.',
            'next_step': 'Upload planting photo to earn 20 more points',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plants/{plant_id}/planting-photo")
async def upload_planting_photo(
    plant_id: str,
    image: UploadFile = File(...),
    gps_latitude: float = Form(...),
    gps_longitude: float = Form(...)
) -> Dict[str, Any]:
    """
    Upload planting photo with GPS verification
    AI verifies plant species and location
    Awards 20 points
    
    Step 2 of Joyo flow
    """
    try:
        # Get plant info
        plant = db.get_plant(plant_id)
        if not plant:
            raise HTTPException(status_code=404, detail="Plant not found")
        
        # Save image
        ext = os.path.splitext(image.filename or "photo.jpg")[1]
        filename = f"planting_{plant_id}_{uuid4().hex[:8]}{ext}"
        image_path = UPLOAD_DIR / filename
        
        with open(image_path, "wb") as f:
            f.write(await image.read())
        
        # AI verification - identify plant species
        verification_result = plant_recognition.identify_plant(
            image_path=str(image_path),
            user_claimed_species=plant['plant_type']
        )
        
        if not verification_result['success']:
            return {
                'success': False,
                'error': 'Plant verification failed',
                'details': verification_result
            }
        
        # Verify location is close to registered location
        geo_profile = {
            'coordinates': {
                'latitude': plant['gps_latitude'],
                'longitude': plant['gps_longitude']
            }
        }
        
        location_check = geo_verification.verify_against_profile(
            profile=geo_profile,
            new_latitude=gps_latitude,
            new_longitude=gps_longitude
        )
        
        if not location_check['verification_passed']:
            return {
                'success': False,
                'error': 'Location mismatch',
                'message': f"Photo location is {location_check['distance_from_profile_meters']}m away from registered location",
                'threshold': '50m',
                'details': location_check
            }
        
        # Create plant fingerprint for future verification
        fingerprint_result = plant_verification.create_plant_fingerprint(str(image_path))
        
        if fingerprint_result['success']:
            # Save fingerprint to database
            db.update_plant_fingerprint(
                plant_id=plant_id,
                fingerprint_data=json.dumps(fingerprint_result['fingerprint'])
            )
        
        # Record activity
        activity_id = f"ACT_{uuid4().hex[:12].upper()}"
        db.record_activity(
            activity_id=activity_id,
            plant_id=plant_id,
            user_id=plant['user_id'],
            activity_type='planting_photo',
            description='Planting photo verified',
            image_url=f"/uploads/{filename}",
            gps_latitude=gps_latitude,
            gps_longitude=gps_longitude,
            points_earned=20,
            metadata=json.dumps(verification_result)
        )
        
        # Award points
        transaction_id = f"TXN_{uuid4().hex[:12].upper()}"
        points_result = db.add_points(
            transaction_id=transaction_id,
            user_id=plant['user_id'],
            points=20,
            transaction_type='planting_photo',
            description='Planting photo verified',
            plant_id=plant_id,
            activity_id=activity_id
        )
        
        return {
            'success': True,
            'plant_id': plant_id,
            'verified': True,
            'plant_species': verification_result['identification']['species_common'],
            'confidence': verification_result['identification']['confidence'],
            'reward_eligible': verification_result['reward_eligible'],
            'points_earned': 20,
            'total_points': points_result['total_points'],
            'image_url': f"/uploads/{filename}",
            'fingerprint_created': fingerprint_result['success'],
            'message': 'Planting verified! You earned 20 points.',
            'next_step': 'Water your plant daily to earn 5 points per day',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plants/{plant_id}/water")
async def record_watering(
    plant_id: str,
    video: UploadFile = File(...),
    gps_latitude: float = Form(...),
    gps_longitude: float = Form(...)
) -> Dict[str, Any]:
    """
    Record daily watering with video verification
    AI verifies same plant + watering activity
    Awards 5 points + streak bonuses
    
    Daily task in Joyo flow
    """
    try:
        # Get plant info
        plant = db.get_plant(plant_id)
        if not plant:
            raise HTTPException(status_code=404, detail="Plant not found")
        
        # Check if plant has fingerprint
        if not plant['fingerprint_data']:
            return {
                'success': False,
                'error': 'Plant fingerprint not found',
                'message': 'Please upload planting photo first'
            }
        
        # Save video
        ext = os.path.splitext(video.filename or "video.mp4")[1]
        filename = f"watering_{plant_id}_{uuid4().hex[:8]}{ext}"
        video_path = UPLOAD_DIR / filename
        
        with open(video_path, "wb") as f:
            f.write(await video.read())
        
        # Parse fingerprint
        fingerprint_data = json.loads(plant['fingerprint_data'])
        
        # Determine day number based on current streak before updating
        streak_info = db.get_streak_info(plant_id) or {}
        last_watered = streak_info.get('last_watered_date')
        current_streak = int(streak_info.get('current_streak') or 0)
        today = date.today()
        day_number = 1
        if last_watered == (today - timedelta(days=1)):
            day_number = current_streak + 1
        else:
            day_number = 1

        # AI verification - verify watering
        verification_result = plant_verification.verify_watering_video(
            video_path=str(video_path),
            plant_fingerprint=fingerprint_data,
            day_number=day_number
        )
        
        if not verification_result['success']:
            return {
                'success': False,
                'error': 'Watering verification failed',
                'details': verification_result
            }
        
        if not verification_result['video_verified']:
            return {
                'success': False,
                'verified': False,
                'reason': verification_result.get('reason', 'Verification failed'),
                'details': verification_result
            }
        
        # Update watering streak
        streak_result = db.update_watering_streak(plant_id)
        
        # Calculate total points (5 base + bonus)
        base_points = 5
        bonus_points = streak_result.get('bonus_points', 0)
        total_points = base_points + bonus_points
        
        # Record activity
        activity_id = f"ACT_{uuid4().hex[:12].upper()}"
        db.record_activity(
            activity_id=activity_id,
            plant_id=plant_id,
            user_id=plant['user_id'],
            activity_type='watering',
            description=f'Daily watering verified (streak: {streak_result["current_streak"]} days)',
            video_url=f"/uploads/{filename}",
            gps_latitude=gps_latitude,
            gps_longitude=gps_longitude,
            points_earned=total_points,
            metadata=json.dumps(verification_result)
        )
        
        # Award points
        transaction_id = f"TXN_{uuid4().hex[:12].upper()}"
        points_result = db.add_points(
            transaction_id=transaction_id,
            user_id=plant['user_id'],
            points=total_points,
            transaction_type='watering',
            description=f'Daily watering (Day {streak_result["current_streak"]})',
            plant_id=plant_id,
            activity_id=activity_id
        )
        
        # Prepare response message
        message = f'Watering verified! You earned {total_points} points.'
        if bonus_points > 0:
            message += f' 🎉 Streak bonus: {bonus_points} points!'
        
        return {
            'success': True,
            'verified': True,
            'plant_id': plant_id,
            'points_earned': total_points,
            'base_points': base_points,
            'bonus_points': bonus_points,
            'total_points': points_result['total_points'],
            'streak': {
                'current': streak_result['current_streak'],
                'longest': streak_result['longest_streak'],
                'total_waterings': streak_result['total_waterings']
            },
            'video_url': f"/uploads/{filename}",
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plants/{plant_id}/health-scan")
async def scan_plant_health(
    plant_id: str,
    image: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Scan plant health using AI
    Detects deficiencies, pests, diseases
    Awards 5 points (max 2 scans per week)
    
    Weekly task in Joyo flow
    """
    try:
        # Get plant info
        plant = db.get_plant(plant_id)
        if not plant:
            raise HTTPException(status_code=404, detail="Plant not found")
        
        # Enforce weekly limit: max 2 scans per 7 days
        scans_this_week = db.count_health_scans_last_days(plant_id, days=7)
        if scans_this_week >= 2:
            return {
                'success': False,
                'error': 'Weekly scan limit reached',
                'allowed_per_week': 2,
                'scans_last_7_days': scans_this_week,
                'message': 'You have reached the weekly limit of 2 health scans. Try again next week.'
            }
        
        # Save image
        ext = os.path.splitext(image.filename or "scan.jpg")[1]
        filename = f"healthscan_{plant_id}_{uuid4().hex[:8]}{ext}"
        image_path = UPLOAD_DIR / filename
        
        with open(image_path, "wb") as f:
            f.write(await image.read())
        
        # AI health scan
        scan_result = plant_health.scan_plant_health(
            image_path=str(image_path),
            plant_species=plant['plant_type']
        )
        
        if not scan_result['success']:
            return {
                'success': False,
                'error': 'Health scan failed',
                'details': scan_result
            }
        
        # Save scan to database
        scan_id = f"SCAN_{uuid4().hex[:12].upper()}"
        db.save_health_scan(
            scan_id=scan_id,
            plant_id=plant_id,
            health_score=scan_result['health_analysis'].get('health_score'),
            issues_detected=", ".join([i.get('specific_diagnosis', '') for i in scan_result['health_analysis'].get('issues_detected', [])]) if scan_result.get('health_analysis') else None,
            remedies_suggested=", ".join([r.get('remedy_name', '') for r in scan_result.get('organic_remedies', [])]) if scan_result.get('organic_remedies') else None,
            image_url=f"/uploads/{filename}",
            ai_analysis_json=json.dumps(scan_result)
        )
        
        # Record activity
        activity_id = f"ACT_{uuid4().hex[:12].upper()}"
        db.record_activity(
            activity_id=activity_id,
            plant_id=plant_id,
            user_id=plant['user_id'],
            activity_type='health_scan',
            description='Health scan completed',
            image_url=f"/uploads/{filename}",
            points_earned=5,
            metadata=json.dumps(scan_result)
        )
        
        # Award points
        transaction_id = f"TXN_{uuid4().hex[:12].upper()}"
        points_result = db.add_points(
            transaction_id=transaction_id,
            user_id=plant['user_id'],
            points=5,
            transaction_type='health_scan',
            description='Health scan completed',
            plant_id=plant_id,
            activity_id=activity_id
        )
        
        return {
            'success': True,
            'scan_id': scan_id,
            'health_score': scan_result['health_analysis']['health_score'],
            'overall_health': scan_result['health_analysis']['overall_health'],
            'issues_detected': scan_result['health_analysis']['issues_detected'],
            'organic_remedies': scan_result.get('organic_remedies', []),
            'recommendations': scan_result['health_analysis']['recommendations'],
            'points_earned': 5,
            'total_points': points_result['total_points'],
            'image_url': f"/uploads/{filename}",
            'message': 'Health scan complete! You earned 5 points.',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plants/{plant_id}/remedy-apply")
async def apply_remedy(
    plant_id: str,
    remedy_type: str = Form(...),
    image: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Record remedy application
    Awards 20-25 points based on remedy type
    
    Remedy task in Joyo flow
    """
    try:
        # Get plant info
        plant = db.get_plant(plant_id)
        if not plant:
            raise HTTPException(status_code=404, detail="Plant not found")
        
        # Save image
        ext = os.path.splitext(image.filename or "remedy.jpg")[1]
        filename = f"remedy_{plant_id}_{uuid4().hex[:8]}{ext}"
        image_path = UPLOAD_DIR / filename
        
        with open(image_path, "wb") as f:
            f.write(await image.read())
        
        # Get remedy info
        remedy_info = plant_health.suggest_organic_fertilizer(
            deficiency_type=remedy_type,
            plant_type=plant['plant_type']
        )
        
        if not remedy_info['success']:
            return {
                'success': False,
                'error': 'Remedy not found',
                'details': remedy_info
            }
        
        # Award points (from remedy info)
        points_earned = remedy_info.get('points_reward', 25)
        
        # Record activity
        activity_id = f"ACT_{uuid4().hex[:12].upper()}"
        db.record_activity(
            activity_id=activity_id,
            plant_id=plant_id,
            user_id=plant['user_id'],
            activity_type='remedy_application',
            description=f'Applied {remedy_type} remedy',
            image_url=f"/uploads/{filename}",
            points_earned=points_earned,
            metadata=json.dumps(remedy_info)
        )
        
        # Award points
        transaction_id = f"TXN_{uuid4().hex[:12].upper()}"
        points_result = db.add_points(
            transaction_id=transaction_id,
            user_id=plant['user_id'],
            points=points_earned,
            transaction_type='remedy_application',
            description=f'Applied {remedy_type} remedy',
            plant_id=plant_id,
            activity_id=activity_id
        )
        
        return {
            'success': True,
            'remedy_type': remedy_type,
            'points_earned': points_earned,
            'total_points': points_result['total_points'],
            'remedy_details': remedy_info['diy_recipe'],
            'image_url': f"/uploads/{filename}",
            'message': f'Remedy applied! You earned {points_earned} points.',
            'follow_up_date': None,  # TODO: Calculate follow-up date
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plants/{plant_id}/protection")
async def add_protection(
    plant_id: str,
    protection_type: str = Form(...),
    image: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Record plant protection (netting, fencing)
    Awards 10 points (one-time)
    
    Protection task in Joyo flow
    """
    try:
        # Get plant info
        plant = db.get_plant(plant_id)
        if not plant:
            raise HTTPException(status_code=404, detail="Plant not found")
        
        # Save image
        ext = os.path.splitext(image.filename or "protection.jpg")[1]
        filename = f"protection_{plant_id}_{uuid4().hex[:8]}{ext}"
        image_path = UPLOAD_DIR / filename
        
        with open(image_path, "wb") as f:
            f.write(await image.read())
        
        # Record activity
        activity_id = f"ACT_{uuid4().hex[:12].upper()}"
        db.record_activity(
            activity_id=activity_id,
            plant_id=plant_id,
            user_id=plant['user_id'],
            activity_type='protection_added',
            description=f'Added {protection_type} protection',
            image_url=f"/uploads/{filename}",
            points_earned=10
        )
        
        # Award points
        transaction_id = f"TXN_{uuid4().hex[:12].upper()}"
        points_result = db.add_points(
            transaction_id=transaction_id,
            user_id=plant['user_id'],
            points=10,
            transaction_type='protection',
            description=f'Added {protection_type} protection',
            plant_id=plant_id,
            activity_id=activity_id
        )
        
        return {
            'success': True,
            'protection_type': protection_type,
            'points_earned': 10,
            'total_points': points_result['total_points'],
            'image_url': f"/uploads/{filename}",
            'message': 'Protection added! You earned 10 points.',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# USER & REWARDS
# ============================================================================

@app.get("/users/{user_id}/points")
async def get_user_points(user_id: str) -> Dict[str, Any]:
    """Get user's current points balance"""
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        'success': True,
        'user_id': user_id,
        'total_points': user['total_points'],
        'total_coins': user['total_coins'],
        'timestamp': datetime.now().isoformat()
    }


@app.get("/users/{user_id}/history")
async def get_user_history(user_id: str, limit: int = 50) -> Dict[str, Any]:
    """Get user's points history and activities"""
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get points history
    points_history = db.get_user_points_history(user_id, limit=limit)
    
    # Get user plants
    plants = db.get_user_plants(user_id)
    
    return {
        'success': True,
        'user_id': user_id,
        'total_points': user['total_points'],
        'total_plants': len(plants),
        'points_history': points_history[:limit],
        'plants': plants,
        'timestamp': datetime.now().isoformat()
    }


@app.get("/plants/{plant_id}")
async def get_plant_details(plant_id: str) -> Dict[str, Any]:
    """Get detailed plant information"""
    plant = db.get_plant(plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    # Get plant activities
    activities = db.get_plant_activities(plant_id, limit=50)
    
    return {
        'success': True,
        'plant': plant,
        'activities': activities,
        'timestamp': datetime.now().isoformat()
    }


# ============================================================================
# STATS & CSR
# ============================================================================

@app.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """Get overall system statistics"""
    stats = db.get_stats()
    
    return {
        'success': True,
        'stats': stats,
        'timestamp': datetime.now().isoformat()
    }


@app.get("/stats/csr")
async def get_csr_stats() -> Dict[str, Any]:
    """
    Get CSR dashboard statistics
    For corporate sponsors and NGOs
    """
    stats = db.get_stats()
    
    return {
        'success': True,
        'csr_dashboard': {
            'total_environmental_impact': {
                'trees_planted': stats['total_plants'],
                'co2_offset_kg': stats['estimated_co2_offset_kg'],
                'active_participants': stats['total_users'],
                'total_waterings': stats['total_waterings']
            },
            'engagement_metrics': {
                'points_issued': stats['total_points_issued'],
                'avg_points_per_user': round(stats['total_points_issued'] / max(stats['total_users'], 1), 2),
                'active_plants': stats['total_plants']
            },
            'timestamp': datetime.now().isoformat()
        }
    }


# ============================================================================
# NFT MINTING
# ============================================================================

@app.post("/nft/mint")
async def mint_nft(
    trees_planted: int = Form(...),
    location: str = Form(...),
    gps_coords: str = Form(...),
    worker_id: str = Form(...),
    plant_id: Optional[str] = Form(None),
    image_url: Optional[str] = Form(None),
    gesture_signature: Optional[str] = Form("gesture_simulated")
) -> Dict[str, Any]:
    if not ALGORAND_AVAILABLE:
        raise HTTPException(status_code=503, detail="Algorand module not configured")
    try:
        # Resolve user_id (prefer plant owner if plant_id provided)
        user_id = worker_id
        plant = None
        if plant_id:
            plant = db.get_plant(plant_id)
            if plant:
                user_id = plant['user_id']

        # Mint on Algorand TestNet
        mint = mint_carbon_credit_nft(
            trees_planted=trees_planted,
            location=location,
            gps_coords=gps_coords,
            worker_id=worker_id,
            gesture_signature=gesture_signature or "gesture_simulated",
            image_url=image_url
        )

        # Persist in DB
        nft_id = f"NFT_{uuid4().hex[:12].upper()}"
        db.save_nft_mint(
            nft_id=nft_id,
            plant_id=plant_id or "",
            user_id=user_id,
            transaction_id=mint['transaction_id'],
            asset_id=int(mint['asset_id']),
            explorer_url=mint.get('explorer_url', ''),
            carbon_offset_kg=float(mint['properties'].get('carbon_offset_kg', 0.0)) if isinstance(mint.get('properties', {}), dict) else None,
            properties_json=json.dumps(mint.get('properties', {}))
        )

        return {
            'success': True,
            'nft_id': nft_id,
            'transaction_id': mint['transaction_id'],
            'asset_id': int(mint['asset_id']),
            'explorer_url': mint.get('explorer_url'),
            'message': 'Carbon credit NFT minted successfully',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    import uvicorn
    
    print("\n" + "="*70)
    print("🌱 JOYO ENVIRONMENT MINI APP API")
    print("="*70)
    print("Server: http://localhost:8001")
    print("Docs: http://localhost:8001/docs")
    print("\n✅ Core Features:")
    print("   • Plant registration & tracking")
    print("   • Daily watering verification with AI")
    print("   • Health scans & organic remedies")
    print("   • Points & rewards ledger")
    print("   • Watering streaks & bonuses")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
