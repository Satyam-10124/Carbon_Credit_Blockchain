"""
Joyo Database Manager - SQLite
Manages users, plants, activities, points ledger, and rewards
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager


DATABASE_PATH = os.getenv("JOYO_DB_PATH", "joyo_app.db")


class JoyoDatabase:
    """Database manager for Joyo environment app"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize all tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    name TEXT,
                    email TEXT,
                    phone TEXT,
                    location TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_points INTEGER DEFAULT 0,
                    total_coins INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # Plants table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plant_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    plant_type TEXT NOT NULL,
                    plant_species TEXT,
                    location TEXT NOT NULL,
                    gps_latitude REAL NOT NULL,
                    gps_longitude REAL NOT NULL,
                    planting_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    fingerprint_data TEXT,
                    last_watered_at TIMESTAMP,
                    last_scanned_at TIMESTAMP,
                    health_score INTEGER DEFAULT 100,
                    total_points_earned INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Activities table (watering, scanning, remedies, etc.)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_id TEXT UNIQUE NOT NULL,
                    plant_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    description TEXT,
                    image_url TEXT,
                    video_url TEXT,
                    gps_latitude REAL,
                    gps_longitude REAL,
                    verification_status TEXT DEFAULT 'pending',
                    ai_confidence REAL,
                    points_earned INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verified_at TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (plant_id) REFERENCES plants(plant_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Points ledger
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS points_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    plant_id TEXT,
                    activity_id TEXT,
                    transaction_type TEXT NOT NULL,
                    points INTEGER NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (plant_id) REFERENCES plants(plant_id),
                    FOREIGN KEY (activity_id) REFERENCES activities(activity_id)
                )
            """)
            
            # Watering streaks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS streaks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plant_id TEXT UNIQUE NOT NULL,
                    current_streak INTEGER DEFAULT 0,
                    longest_streak INTEGER DEFAULT 0,
                    last_watered_date DATE,
                    total_waterings INTEGER DEFAULT 0,
                    streak_bonus_points INTEGER DEFAULT 0,
                    FOREIGN KEY (plant_id) REFERENCES plants(plant_id)
                )
            """)
            
            # Health scans
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS health_scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT UNIQUE NOT NULL,
                    plant_id TEXT NOT NULL,
                    health_score INTEGER,
                    issues_detected TEXT,
                    remedies_suggested TEXT,
                    scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    image_url TEXT,
                    ai_analysis TEXT,
                    FOREIGN KEY (plant_id) REFERENCES plants(plant_id)
                )
            """)
            
            # Remedies applied
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS remedies_applied (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    remedy_id TEXT UNIQUE NOT NULL,
                    plant_id TEXT NOT NULL,
                    scan_id TEXT,
                    remedy_type TEXT NOT NULL,
                    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    before_image_url TEXT,
                    after_image_url TEXT,
                    effectiveness_score INTEGER,
                    points_earned INTEGER DEFAULT 0,
                    follow_up_date TIMESTAMP,
                    FOREIGN KEY (plant_id) REFERENCES plants(plant_id),
                    FOREIGN KEY (scan_id) REFERENCES health_scans(scan_id)
                )
            """)
            
            # Coins (conversion from points)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS coins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    coin_transaction_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    coins INTEGER NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # NFTs minted
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nfts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nft_id TEXT UNIQUE NOT NULL,
                    plant_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    transaction_id TEXT NOT NULL,
                    asset_id INTEGER NOT NULL,
                    explorer_url TEXT,
                    carbon_offset_kg REAL,
                    properties TEXT,
                    minted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (plant_id) REFERENCES plants(plant_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
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
            
            print("✅ Database initialized successfully!")
    
    # ==================== User Operations ====================
    
    def create_user(self, user_id: str, name: str = None, email: str = None, 
                   phone: str = None, location: str = None) -> Dict:
        """Create a new user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (user_id, name, email, phone, location)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, name, email, phone, location))
            
            return {
                'success': True,
                'user_id': user_id,
                'message': 'User created successfully'
            }
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_user_points(self, user_id: str, points: int) -> bool:
        """Update user's total points"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET total_points = total_points + ?
                WHERE user_id = ?
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (plant_id, user_id, plant_type, plant_species, 
                  location, gps_latitude, gps_longitude, fingerprint_data))
            
            # Initialize streak record
            cursor.execute("""
                INSERT INTO streaks (plant_id)
                VALUES (?)
            """, (plant_id,))
            
            return {
                'success': True,
                'plant_id': plant_id,
                'message': 'Plant registered successfully'
            }
    
    def get_plant(self, plant_id: str) -> Optional[Dict]:
        """Get plant by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM plants WHERE plant_id = ?", (plant_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_user_plants(self, user_id: str) -> List[Dict]:
        """Get all plants for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM plants 
                WHERE user_id = ? 
                ORDER BY planting_date DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_plant_fingerprint(self, plant_id: str, fingerprint_data: str) -> bool:
        """Update plant fingerprint"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE plants 
                SET fingerprint_data = ?
                WHERE plant_id = ?
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
            cursor.execute("""
                INSERT INTO activities (
                    activity_id, plant_id, user_id, activity_type, description,
                    image_url, video_url, gps_latitude, gps_longitude,
                    points_earned, metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (activity_id, plant_id, user_id, activity_type, description,
                  image_url, video_url, gps_latitude, gps_longitude,
                  points_earned, metadata))
            
            return {
                'success': True,
                'activity_id': activity_id,
                'points_earned': points_earned
            }
    
    def get_plant_activities(self, plant_id: str, limit: int = 50) -> List[Dict]:
        """Get activities for a plant"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM activities 
                WHERE plant_id = ? 
                ORDER BY created_at DESC
                LIMIT ?
            """, (plant_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
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
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (transaction_id, user_id, plant_id, activity_id,
                  transaction_type, points, description))
            
            # Update user total
            cursor.execute("""
                UPDATE users 
                SET total_points = total_points + ?
                WHERE user_id = ?
            """, (points, user_id))
            
            # Update plant total if applicable
            if plant_id:
                cursor.execute("""
                    UPDATE plants 
                    SET total_points_earned = total_points_earned + ?
                    WHERE plant_id = ?
                """, (points, plant_id))
            
            # Get new total
            cursor.execute("SELECT total_points FROM users WHERE user_id = ?", (user_id,))
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
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM points_ledger 
                WHERE user_id = ? 
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== Streak Operations ====================
    
    def update_watering_streak(self, plant_id: str) -> Dict:
        """Update watering streak for a plant"""
        from datetime import date
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current streak info
            cursor.execute("""
                SELECT current_streak, last_watered_date, longest_streak, total_waterings
                FROM streaks WHERE plant_id = ?
            """, (plant_id,))
            row = cursor.fetchone()
            
            if not row:
                # Initialize if doesn't exist
                cursor.execute("""
                    INSERT INTO streaks (plant_id, current_streak, total_waterings, last_watered_date)
                    VALUES (?, 1, 1, ?)
                """, (plant_id, date.today()))
                return {'current_streak': 1, 'longest_streak': 1, 'bonus_points': 0}
            
            current_streak, last_watered, longest_streak, total_waterings = row
            today = date.today()
            
            # Parse last_watered if it's a string
            if isinstance(last_watered, str):
                last_watered = datetime.strptime(last_watered, "%Y-%m-%d").date()
            
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
                SET current_streak = ?,
                    longest_streak = ?,
                    last_watered_date = ?,
                    total_waterings = total_waterings + 1,
                    streak_bonus_points = streak_bonus_points + ?
                WHERE plant_id = ?
            """, (new_streak, new_longest, today, bonus_points, plant_id))
            
            return {
                'current_streak': new_streak,
                'longest_streak': new_longest,
                'bonus_points': bonus_points,
                'total_waterings': total_waterings + 1
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
            
            cursor.execute("SELECT SUM(points) FROM points_ledger")
            total_points_issued = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM activities WHERE activity_type = 'watering'")
            total_waterings = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT SUM(CAST(p.plant_type AS INTEGER)) 
                FROM plants p 
                WHERE p.status = 'active'
            """)
            
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


# Global database instance
db = JoyoDatabase()


if __name__ == "__main__":
    print("🗄️  Initializing Joyo Database...")
    db = JoyoDatabase()
    print("✅ Database ready!")
    print(f"📊 Stats: {db.get_stats()}")
