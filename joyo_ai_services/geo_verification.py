"""
Geo-Verification AI - Location & Anti-Fraud
Ensures consistent location and detects GPS spoofing
"""

import os
import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import requests


class GeoVerificationAI:
    """
    AI service for GPS verification and location consistency
    Prevents location spoofing and ensures plant stays in same place
    """
    
    def __init__(
        self,
        google_maps_api_key: Optional[str] = None,
        openweather_api_key: Optional[str] = None
    ):
        """Initialize with API keys"""
        self.google_maps_api_key = google_maps_api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        self.openweather_api_key = openweather_api_key or os.getenv("OPENWEATHER_API_KEY")
    
    def extract_gps_from_image(self, image_path: str) -> Dict:
        """
        Extract GPS coordinates from image EXIF data
        """
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()
            
            if not exif_data:
                return {
                    "success": False,
                    "error": "No EXIF data found in image"
                }
            
            # Extract GPS info
            gps_info = {}
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == "GPSInfo":
                    for gps_tag in value:
                        gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                        gps_info[gps_tag_name] = value[gps_tag]
            
            if not gps_info:
                return {
                    "success": False,
                    "error": "No GPS data in EXIF"
                }
            
            # Convert to decimal degrees
            lat, lon = self._convert_to_degrees(gps_info)
            
            # Extract timestamp
            timestamp = None
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == "DateTime":
                    timestamp = value
            
            return {
                "success": True,
                "latitude": lat,
                "longitude": lon,
                "timestamp": timestamp,
                "raw_gps_info": gps_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _convert_to_degrees(self, gps_info: Dict) -> Tuple[float, float]:
        """Convert GPS coordinates to decimal degrees"""
        def convert(coord, ref):
            degrees = coord[0]
            minutes = coord[1]
            seconds = coord[2]
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            if ref in ['S', 'W']:
                decimal = -decimal
            return decimal
        
        lat = convert(gps_info['GPSLatitude'], gps_info['GPSLatitudeRef'])
        lon = convert(gps_info['GPSLongitude'], gps_info['GPSLongitudeRef'])
        
        return lat, lon
    
    def verify_location_consistency(
        self,
        historical_locations: List[Dict],
        max_distance_meters: float = 50.0
    ) -> Dict:
        """
        Verify that all photos/videos are from the same location
        Detects if user is moving plant or using different locations
        
        Args:
            historical_locations: List of GPS coordinates from different days
            max_distance_meters: Maximum allowed distance between locations
            
        Returns:
            Verification result
        """
        if len(historical_locations) < 2:
            return {
                "success": True,
                "consistent": True,
                "message": "Insufficient data for consistency check"
            }
        
        # Calculate distances between consecutive locations
        distances = []
        inconsistencies = []
        
        for i in range(1, len(historical_locations)):
            prev_loc = historical_locations[i-1]
            curr_loc = historical_locations[i]
            
            distance = self._haversine_distance(
                prev_loc['latitude'],
                prev_loc['longitude'],
                curr_loc['latitude'],
                curr_loc['longitude']
            )
            
            distances.append(distance)
            
            if distance > max_distance_meters:
                inconsistencies.append({
                    "day": i,
                    "distance_meters": distance,
                    "prev_location": f"{prev_loc['latitude']:.6f}, {prev_loc['longitude']:.6f}",
                    "curr_location": f"{curr_loc['latitude']:.6f}, {curr_loc['longitude']:.6f}"
                })
        
        is_consistent = len(inconsistencies) == 0
        avg_distance = sum(distances) / len(distances) if distances else 0
        max_distance = max(distances) if distances else 0
        
        return {
            "success": True,
            "consistent": is_consistent,
            "average_distance_meters": round(avg_distance, 2),
            "max_distance_meters": round(max_distance, 2),
            "threshold_meters": max_distance_meters,
            "total_checks": len(distances),
            "inconsistencies_found": len(inconsistencies),
            "inconsistency_details": inconsistencies,
            "fraud_risk": "high" if len(inconsistencies) > 2 else "medium" if len(inconsistencies) > 0 else "low"
        }
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two GPS coordinates in meters
        Using Haversine formula
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371000  # Earth radius in meters
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        distance = R * c
        return distance
    
    def get_location_name(self, latitude: float, longitude: float) -> Dict:
        """
        Reverse geocode GPS coordinates to location name
        Uses Google Maps API
        """
        if not self.google_maps_api_key:
            return {
                "success": False,
                "error": "Google Maps API key not configured"
            }
        
        try:
            url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={self.google_maps_api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'OK' and data['results']:
                    result = data['results'][0]
                    
                    # Extract address components
                    components = {}
                    for component in result.get('address_components', []):
                        types = component.get('types', [])
                        if 'locality' in types:
                            components['city'] = component['long_name']
                        elif 'administrative_area_level_1' in types:
                            components['state'] = component['long_name']
                        elif 'country' in types:
                            components['country'] = component['long_name']
                        elif 'postal_code' in types:
                            components['postal_code'] = component['long_name']
                    
                    return {
                        "success": True,
                        "formatted_address": result['formatted_address'],
                        "components": components,
                        "coordinates": {
                            "latitude": latitude,
                            "longitude": longitude
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Geocoding failed: {data['status']}"
                    }
            else:
                return {
                    "success": False,
                    "error": f"API request failed: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_weather_at_location(self, latitude: float, longitude: float) -> Dict:
        """
        Get current weather at location
        Helps verify location authenticity and conditions
        """
        if not self.openweather_api_key:
            return {
                "success": False,
                "error": "OpenWeather API key not configured"
            }
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={self.openweather_api_key}&units=metric"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    "success": True,
                    "location": data['name'],
                    "temperature": data['main']['temp'],
                    "feels_like": data['main']['feels_like'],
                    "humidity": data['main']['humidity'],
                    "pressure": data['main']['pressure'],
                    "weather": data['weather'][0]['description'],
                    "wind_speed": data['wind']['speed'],
                    "clouds": data['clouds']['all'],
                    "timestamp": datetime.fromtimestamp(data['dt']).isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Weather API failed: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def detect_gps_spoofing(self, location_data: Dict, weather_data: Optional[Dict] = None) -> Dict:
        """
        Detect potential GPS spoofing
        Checks for impossible patterns
        """
        red_flags = []
        suspicion_score = 0
        
        # Check 1: GPS precision (spoofed locations often have perfect coordinates)
        lat = location_data.get('latitude', 0)
        lon = location_data.get('longitude', 0)
        
        lat_decimals = len(str(lat).split('.')[-1]) if '.' in str(lat) else 0
        lon_decimals = len(str(lon).split('.')[-1]) if '.' in str(lon) else 0
        
        if lat_decimals < 4 or lon_decimals < 4:
            red_flags.append("GPS precision too low (possible manual input)")
            suspicion_score += 30
        
        # Check 2: Rounded coordinates (e.g., 22.0000, 75.0000)
        if lat == int(lat) or lon == int(lon):
            red_flags.append("Perfectly rounded coordinates (suspicious)")
            suspicion_score += 50
        
        # Check 3: Weather consistency
        if weather_data and weather_data.get('success'):
            # This is a placeholder - in production, compare reported weather with expected
            pass
        
        # Check 4: Location metadata
        if 'timestamp' not in location_data:
            red_flags.append("Missing timestamp in image metadata")
            suspicion_score += 20
        
        return {
            "spoofing_detected": suspicion_score > 50,
            "suspicion_score": min(suspicion_score, 100),
            "risk_level": "high" if suspicion_score > 70 else "medium" if suspicion_score > 40 else "low",
            "red_flags": red_flags,
            "recommendation": "reject" if suspicion_score > 70 else "manual_review" if suspicion_score > 40 else "approve"
        }
    
    def create_location_profile(self, latitude: float, longitude: float) -> Dict:
        """
        Create complete location profile for a plant
        This becomes the reference for all future verifications
        """
        # Get location name
        location_info = self.get_location_name(latitude, longitude)
        
        # Get weather
        weather_info = self.get_weather_at_location(latitude, longitude)
        
        # Create profile
        profile = {
            "created_at": datetime.now().isoformat(),
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude,
                "formatted": f"{latitude:.6f}, {longitude:.6f}"
            },
            "location_info": location_info,
            "initial_weather": weather_info,
            "verification_radius_meters": 50,  # Max allowed movement
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0
        }
        
        return profile
    
    def verify_against_profile(
        self,
        profile: Dict,
        new_latitude: float,
        new_longitude: float
    ) -> Dict:
        """
        Verify new location against established profile
        """
        profile_lat = profile['coordinates']['latitude']
        profile_lon = profile['coordinates']['longitude']
        max_distance = profile.get('verification_radius_meters', 50)
        
        # Calculate distance
        distance = self._haversine_distance(
            profile_lat,
            profile_lon,
            new_latitude,
            new_longitude
        )
        
        passed = distance <= max_distance
        
        return {
            "verification_passed": passed,
            "distance_from_profile_meters": round(distance, 2),
            "threshold_meters": max_distance,
            "profile_location": f"{profile_lat:.6f}, {profile_lon:.6f}",
            "current_location": f"{new_latitude:.6f}, {new_longitude:.6f}",
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    print("📍 Geo-Verification AI - Test")
    print("="*70)
    
    ai = GeoVerificationAI()
    
    # Test location profile creation
    test_lat, test_lon = 22.7196, 75.8577  # Indore
    profile = ai.create_location_profile(test_lat, test_lon)
    
    print(f"\n🗺️  Location Profile Created:")
    print(f"Coordinates: {profile['coordinates']['formatted']}")
    print(f"Verification Radius: {profile['verification_radius_meters']}m")
    
    # Test location verification
    nearby_lat, nearby_lon = 22.7197, 75.8578  # 10m away
    verification = ai.verify_against_profile(profile, nearby_lat, nearby_lon)
    
    print(f"\n✅ Verification Test:")
    print(f"Distance: {verification['distance_from_profile_meters']}m")
    print(f"Passed: {verification['verification_passed']}")
    
    print("\n✅ Geo-Verification AI initialized successfully!")
