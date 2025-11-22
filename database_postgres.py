"""
Joyo Database Manager - PostgreSQL (Railway)
Manages users, plants, activities, points ledger, and rewards
"""

import os
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
import json
from dotenv import load_dotenv
import time

# Load environment variables from .env if present
load_dotenv()


# Railway PostgreSQL Connection String
# SECURITY: Database URL must be provided via environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Set it in Railway dashboard or .env file."
    )
DB_CONNECT_RETRIES = int(os.getenv("DB_CONNECT_RETRIES", "5"))
DB_CONNECT_RETRY_INTERVAL_SEC = int(os.getenv("DB_CONNECT_RETRY_INTERVAL_SEC", "2"))


class JoyoDatabase:
    """Database manager for Joyo environment app using PostgreSQL"""
    
    def __init__(self, db_url: str = DATABASE_URL):
        self.db_url = db_url
        # Create connection pool with retry logic for better resiliency
        attempts = 0
        last_exc: Optional[Exception] = None
        while attempts < DB_CONNECT_RETRIES:
            try:
                self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dsn=db_url
                )
                print(f"✅ Connected to PostgreSQL database")
                break
            except Exception as e:
                last_exc = e
                attempts += 1
                print(f"⚠️  PostgreSQL connect attempt {attempts}/{DB_CONNECT_RETRIES} failed: {e}")
                if attempts < DB_CONNECT_RETRIES:
                    time.sleep(DB_CONNECT_RETRY_INTERVAL_SEC)
        if not getattr(self, "connection_pool", None):
            raise RuntimeError(
                f"Could not connect to PostgreSQL after {DB_CONNECT_RETRIES} attempts"
            ) from last_exc
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections from pool"""
        conn = self.connection_pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.connection_pool.putconn(conn)
    
    def init_database(self):
        """Initialize all tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Enable UUID extension for PostgreSQL
            cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255),
                    email VARCHAR(255),
                    phone VARCHAR(50),
                    location TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_points INTEGER DEFAULT 0,
                    total_coins INTEGER DEFAULT 0,
                    status VARCHAR(50) DEFAULT 'active'
                )
            """)
            
            # Plants table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plants (
                    id SERIAL PRIMARY KEY,
                    plant_id VARCHAR(255) UNIQUE NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    plant_type VARCHAR(255) NOT NULL,
                    plant_species VARCHAR(255),
                    location TEXT NOT NULL,
                    gps_latitude DECIMAL(10, 8) NOT NULL,
                    gps_longitude DECIMAL(11, 8) NOT NULL,
                    planting_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'active',
                    fingerprint_data TEXT,
                    last_watered_at TIMESTAMP,
                    last_scanned_at TIMESTAMP,
                    health_score INTEGER DEFAULT 100,
                    total_points_earned INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            
            # Activities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    id SERIAL PRIMARY KEY,
                    activity_id VARCHAR(255) UNIQUE NOT NULL,
                    plant_id VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    activity_type VARCHAR(100) NOT NULL,
                    description TEXT,
                    image_url TEXT,
                    video_url TEXT,
                    gps_latitude DECIMAL(10, 8),
                    gps_longitude DECIMAL(11, 8),
                    verification_status VARCHAR(50) DEFAULT 'pending',
                    ai_confidence DECIMAL(5, 2),
                    points_earned INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verified_at TIMESTAMP,
                    metadata JSONB,
                    FOREIGN KEY (plant_id) REFERENCES plants(plant_id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            
            # Points ledger
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS points_ledger (
                    id SERIAL PRIMARY KEY,
                    transaction_id VARCHAR(255) UNIQUE NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    plant_id VARCHAR(255),
                    activity_id VARCHAR(255),
                    transaction_type VARCHAR(100) NOT NULL,
                    points INTEGER NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (plant_id) REFERENCES plants(plant_id) ON DELETE SET NULL,
                    FOREIGN KEY (activity_id) REFERENCES activities(activity_id) ON DELETE SET NULL
                )
            """)
            
            # Watering streaks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS streaks (
                    id SERIAL PRIMARY KEY,
                    plant_id VARCHAR(255) UNIQUE NOT NULL,
                    current_streak INTEGER DEFAULT 0,
                    longest_streak INTEGER DEFAULT 0,
                    last_watered_date DATE,
                    total_waterings INTEGER DEFAULT 0,
                    streak_bonus_points INTEGER DEFAULT 0,
                    FOREIGN KEY (plant_id) REFERENCES plants(plant_id) ON DELETE CASCADE
                )
            """)
            
            # Health scans
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS health_scans (
                    id SERIAL PRIMARY KEY,
                    scan_id VARCHAR(255) UNIQUE NOT NULL,
                    plant_id VARCHAR(255) NOT NULL,
                    health_score INTEGER,
                    issues_detected TEXT,
                    remedies_suggested TEXT,
                    scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    image_url TEXT,
                    ai_analysis JSONB,
                    FOREIGN KEY (plant_id) REFERENCES plants(plant_id) ON DELETE CASCADE
                )
            """)
            
            # Remedies applied
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS remedies_applied (
                    id SERIAL PRIMARY KEY,
                    remedy_id VARCHAR(255) UNIQUE NOT NULL,
                    plant_id VARCHAR(255) NOT NULL,
                    scan_id VARCHAR(255),
                    remedy_type VARCHAR(255) NOT NULL,
                    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    before_image_url TEXT,
                    after_image_url TEXT,
                    effectiveness_score INTEGER,
                    points_earned INTEGER DEFAULT 0,
                    follow_up_date TIMESTAMP,
                    FOREIGN KEY (plant_id) REFERENCES plants(plant_id) ON DELETE CASCADE,
                    FOREIGN KEY (scan_id) REFERENCES health_scans(scan_id) ON DELETE SET NULL
                )
            """)
            
            # Coins (conversion from points)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS coins (
                    id SERIAL PRIMARY KEY,
                    coin_transaction_id VARCHAR(255) UNIQUE NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    transaction_type VARCHAR(100) NOT NULL,
                    coins INTEGER NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            
            # NFTs minted
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nfts (
                    id SERIAL PRIMARY KEY,
                    nft_id VARCHAR(255) UNIQUE NOT NULL,
                    plant_id VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    transaction_id VARCHAR(500) NOT NULL,
                    asset_id BIGINT NOT NULL,
                    explorer_url TEXT,
                    carbon_offset_kg DECIMAL(10, 2),
                    properties JSONB,
                    minted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plant_id) REFERENCES plants(plant_id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_plants_user_id ON plants(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_plants_plant_id ON plants(plant_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_plant_id ON activities(plant_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_user_id ON activities(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_points_user_id ON points_ledger(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_streaks_plant_id ON streaks(plant_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_created ON activities(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_points_created ON points_ledger(created_at)")
            
            print("✅ All tables created successfully in PostgreSQL!")
    
    # ==================== User Operations ====================
    
    def create_user(self, user_id: str, name: str = None, email: str = None, 
                   phone: str = None, location: str = None) -> Dict:
        """Create a new user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (user_id, name, email, phone, location)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING
            """, (user_id, name, email, phone, location))
            
            return {
                'success': True,
                'user_id': user_id,
                'message': 'User created successfully'
            }
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_user_points(self, user_id: str, points: int) -> bool:
        """Update user's total points"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET total_points = total_points + %s
                WHERE user_id = %s
            """, (points, user_id))
            return cursor.rowcount > 0
    
    # ==================== Plant Operations ====================
    
    def register_plant(self, plant_id: str, user_id: str, plant_type: str,
                      location: str, gps_latitude: float, gps_longitude: float,
                      plant_species: str = None, fingerprint_data: str = None) -> Dict:
        """Register a new plant"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO plants (
                    plant_id, user_id, plant_type, plant_species,
                    location, gps_latitude, gps_longitude, fingerprint_data
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (plant_id, user_id, plant_type, plant_species, 
                  location, gps_latitude, gps_longitude, fingerprint_data))
            
            # Initialize streak record
            cursor.execute("""
                INSERT INTO streaks (plant_id)
                VALUES (%s)
            """, (plant_id,))
            
            return {
                'success': True,
                'plant_id': plant_id,
                'message': 'Plant registered successfully'
            }
    
    def get_plant(self, plant_id: str) -> Optional[Dict]:
        """Get plant by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM plants WHERE plant_id = %s", (plant_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_plants(self, user_id: str) -> List[Dict]:
        """Get all plants for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM plants 
                WHERE user_id = %s 
                ORDER BY planting_date DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_plant_fingerprint(self, plant_id: str, fingerprint_data: str) -> bool:
        """Update plant fingerprint"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE plants 
                SET fingerprint_data = %s
                WHERE plant_id = %s
            """, (fingerprint_data, plant_id))
            return cursor.rowcount > 0
    
    # ==================== Activity Operations ====================
    
    def record_activity(self, activity_id: str, plant_id: str, user_id: str,
                       activity_type: str, description: str = None,
                       image_url: str = None, video_url: str = None,
                       gps_latitude: float = None, gps_longitude: float = None,
                       points_earned: int = 0, metadata: str = None) -> Dict:
        """Record a new activity"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Convert metadata string to JSONB if provided
            metadata_json = json.loads(metadata) if metadata else None
            
            cursor.execute("""
                INSERT INTO activities (
                    activity_id, plant_id, user_id, activity_type, description,
                    image_url, video_url, gps_latitude, gps_longitude,
                    points_earned, metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (activity_id, plant_id, user_id, activity_type, description,
                  image_url, video_url, gps_latitude, gps_longitude,
                  points_earned, json.dumps(metadata_json) if metadata_json else None))
            
            return {
                'success': True,
                'activity_id': activity_id,
                'points_earned': points_earned
            }
    
    def get_plant_activities(self, plant_id: str, limit: int = 50) -> List[Dict]:
        """Get activities for a plant"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM activities 
                WHERE plant_id = %s 
                ORDER BY created_at DESC
                LIMIT %s
            """, (plant_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def save_health_scan(self, scan_id: str, plant_id: str, health_score: Optional[int],
                         issues_detected: Optional[str], remedies_suggested: Optional[str],
                         image_url: Optional[str], ai_analysis_json: Optional[str]) -> Dict:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO health_scans (
                    scan_id, plant_id, health_score, issues_detected,
                    remedies_suggested, image_url, ai_analysis
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (scan_id, plant_id, health_score, issues_detected,
                 remedies_suggested, image_url, ai_analysis_json)
            )
            return {"success": True, "scan_id": scan_id}
    
    def count_health_scans_last_days(self, plant_id: str, days: int = 7) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Safe since days is an int
            cursor.execute(
                f"""
                SELECT COUNT(*) FROM health_scans
                WHERE plant_id = %s
                  AND scan_date >= NOW() - INTERVAL '{int(days)} days'
                """,
                (plant_id,)
            )
            row = cursor.fetchone()
            return int(row[0]) if row else 0
    
    # ==================== Points Operations ====================
    
    def add_points(self, transaction_id: str, user_id: str, points: int,
                  transaction_type: str, description: str = None,
                  plant_id: str = None, activity_id: str = None) -> Dict:
        """Add points to user's ledger"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Add to ledger
            cursor.execute("""
                INSERT INTO points_ledger (
                    transaction_id, user_id, plant_id, activity_id,
                    transaction_type, points, description
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (transaction_id, user_id, plant_id, activity_id,
                  transaction_type, points, description))
            
            # Update user total
            cursor.execute("""
                UPDATE users 
                SET total_points = total_points + %s
                WHERE user_id = %s
            """, (points, user_id))
            
            # Update plant total if applicable
            if plant_id:
                cursor.execute("""
                    UPDATE plants 
                    SET total_points_earned = total_points_earned + %s
                    WHERE plant_id = %s
                """, (points, plant_id))
            
            # Get new total
            cursor.execute("SELECT total_points FROM users WHERE user_id = %s", (user_id,))
            row = cursor.fetchone()
            total_points = row[0] if row else points
            
            return {
                'success': True,
                'points_added': points,
                'total_points': total_points,
                'transaction_id': transaction_id
            }
    
    def get_user_points_history(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get points transaction history"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM points_ledger 
                WHERE user_id = %s 
                ORDER BY created_at DESC
                LIMIT %s
            """, (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== Streak Operations ====================
    
    def update_watering_streak(self, plant_id: str) -> Dict:
        """Update watering streak for a plant"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current streak info
            cursor.execute("""
                SELECT current_streak, last_watered_date, longest_streak, total_waterings
                FROM streaks WHERE plant_id = %s
            """, (plant_id,))
            row = cursor.fetchone()
            
            if not row:
                # Initialize if doesn't exist
                cursor.execute("""
                    INSERT INTO streaks (plant_id, current_streak, total_waterings, last_watered_date)
                    VALUES (%s, 1, 1, %s)
                """, (plant_id, date.today()))
                return {'current_streak': 1, 'longest_streak': 1, 'bonus_points': 0}
            
            current_streak, last_watered, longest_streak, total_waterings = row
            today = date.today()
            
            # Check if already watered today
            if last_watered == today:
                return {
                    'current_streak': current_streak,
                    'longest_streak': longest_streak,
                    'bonus_points': 0,
                    'message': 'Already watered today'
                }
            
            # Check if streak continues (yesterday)
            from datetime import timedelta
            yesterday = today - timedelta(days=1)
            
            if last_watered == yesterday:
                # Continue streak
                new_streak = current_streak + 1
            else:
                # Streak broken, restart
                new_streak = 1
            
            # Update longest streak
            new_longest = max(longest_streak, new_streak)
            
            # Calculate bonus points for milestones
            bonus_points = 0
            if new_streak == 7:
                bonus_points = 10
            elif new_streak == 30:
                bonus_points = 50
            elif new_streak == 100:
                bonus_points = 200
            
            # Update streak
            cursor.execute("""
                UPDATE streaks 
                SET current_streak = %s,
                    longest_streak = %s,
                    last_watered_date = %s,
                    total_waterings = total_waterings + 1,
                    streak_bonus_points = streak_bonus_points + %s
                WHERE plant_id = %s
            """, (new_streak, new_longest, today, bonus_points, plant_id))
            
            return {
                'current_streak': new_streak,
                'longest_streak': new_longest,
                'bonus_points': bonus_points,
                'total_waterings': total_waterings + 1
            }
    
    def get_streak_info(self, plant_id: str) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT current_streak, longest_streak, last_watered_date, total_waterings
                FROM streaks WHERE plant_id = %s
                """,
                (plant_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            current_streak, longest_streak, last_watered_date, total_waterings = row
            return {
                'current_streak': current_streak,
                'longest_streak': longest_streak,
                'last_watered_date': last_watered_date,
                'total_waterings': total_waterings
            }
    
    # ==================== Utility Operations ====================
    
    def get_stats(self) -> Dict:
        """Get overall system stats"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'active'")
            total_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM plants WHERE status = 'active'")
            total_plants = cursor.fetchone()[0]
            
            cursor.execute("SELECT COALESCE(SUM(points), 0) FROM points_ledger")
            total_points_issued = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM activities WHERE activity_type = 'watering'")
            total_waterings = cursor.fetchone()[0]
            
            # Estimate CO2 offset (rough calculation)
            estimated_co2_kg = total_plants * 130  # ~130kg per plant per 6 months
            
            return {
                'total_users': total_users,
                'total_plants': total_plants,
                'total_points_issued': total_points_issued,
                'total_waterings': total_waterings,
                'estimated_co2_offset_kg': estimated_co2_kg,
                'timestamp': datetime.now().isoformat()
            }
    
    def save_nft_mint(self, nft_id: str, plant_id: str, user_id: str,
                      transaction_id: str, asset_id: int, explorer_url: str,
                      carbon_offset_kg: Optional[float], properties_json: Optional[str]) -> Dict:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO nfts (nft_id, plant_id, user_id, transaction_id, asset_id, explorer_url, carbon_offset_kg, properties)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (nft_id, plant_id, user_id, transaction_id, asset_id, explorer_url, carbon_offset_kg, properties_json)
            )
            return {"success": True, "nft_id": nft_id}
    
    def close(self):
        """Close connection pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✅ PostgreSQL connection pool closed")


# Global database instance
db = JoyoDatabase()


if __name__ == "__main__":
    print("🗄️  Initializing Joyo PostgreSQL Database...")
    print(f"📡 Connecting to Railway PostgreSQL...")
    
    db = JoyoDatabase()
    
    print("\n" + "="*70)
    print("✅ PostgreSQL Database Ready!")
    print("="*70)
    
    stats = db.get_stats()
    print(f"\n📊 Current Stats:")
    print(f"   Users: {stats['total_users']}")
    print(f"   Plants: {stats['total_plants']}")
    print(f"   Points Issued: {stats['total_points_issued']}")
    print(f"   Total Waterings: {stats['total_waterings']}")
    print(f"   Est. CO2 Offset: {stats['estimated_co2_offset_kg']} kg")
    print("\n" + "="*70)
