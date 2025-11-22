"""
GPS and Location Validation Module
Validates GPS coordinates, checks planting suitability, and integrates weather data
"""

import os
import requests
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json


class GPSValidator:
    """Validate GPS coordinates and location suitability for tree planting"""
    
    def __init__(self):
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        
    def parse_coordinates(self, gps_string: str) -> Optional[Tuple[float, float]]:
        """
        Parse GPS coordinates from various formats
        
        Supports:
        - "19.0760° N, 72.8777° E"
        - "19.0760, 72.8777"
        - "(19.0760, 72.8777)"
        """
        try:
            # Remove common characters
            cleaned = gps_string.replace("°", "").replace("N", "").replace("S", "").replace("E", "").replace("W", "")
            cleaned = cleaned.replace("(", "").replace(")", "").strip()
            
            # Split by comma
            parts = [p.strip() for p in cleaned.split(",")]
            
            if len(parts) != 2:
                return None
            
            lat = float(parts[0])
            lon = float(parts[1])
            
            # Validate ranges
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                return None
            
            return (lat, lon)
            
        except Exception as e:
            print(f"⚠️  GPS parsing error: {e}")
            return None
    
    def validate_coordinates(self, gps_coords: str) -> Dict[str, Any]:
        """Validate GPS coordinates"""
        
        coords = self.parse_coordinates(gps_coords)
        
        if not coords:
            return {
                "valid": False,
                "reason": "Invalid GPS format",
                "coordinates": None
            }
        
        lat, lon = coords
        
        return {
            "valid": True,
            "coordinates": {
                "latitude": lat,
                "longitude": lon
            },
            "formatted": f"{lat:.6f}, {lon:.6f}"
        }
    
    def get_location_info(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get location information using reverse geocoding"""
        
        if not self.google_api_key:
            return self._mock_location_info(lat, lon)
        
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "latlng": f"{lat},{lon}",
                "key": self.google_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("status") == "OK" and data.get("results"):
                result = data["results"][0]
                
                # Extract location components
                components = {}
                for comp in result.get("address_components", []):
                    comp_type = comp["types"][0]
                    components[comp_type] = comp.get("long_name", "")
                
                return {
                    "formatted_address": result.get("formatted_address", ""),
                    "country": components.get("country", "Unknown"),
                    "state": components.get("administrative_area_level_1", "Unknown"),
                    "city": components.get("locality", "Unknown"),
                    "place_id": result.get("place_id", ""),
                    "location_type": result.get("geometry", {}).get("location_type", "")
                }
            
            return {"error": "Location not found"}
            
        except Exception as e:
            print(f"⚠️  Geocoding error: {e}")
            return self._mock_location_info(lat, lon)
    
    def get_weather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get current weather data for location"""
        
        if not self.weather_api_key:
            return self._mock_weather_data()
        
        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.weather_api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                return {
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "conditions": data["weather"][0]["main"],
                    "description": data["weather"][0]["description"],
                    "wind_speed": data["wind"]["speed"],
                    "precipitation": data.get("rain", {}).get("1h", 0),
                    "timestamp": datetime.now().isoformat()
                }
            
            return {"error": "Weather data unavailable"}
            
        except Exception as e:
            print(f"⚠️  Weather API error: {e}")
            return self._mock_weather_data()
    
    def check_planting_suitability(
        self,
        lat: float,
        lon: float,
        weather: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Check if location and weather are suitable for tree planting
        """
        
        if not weather:
            weather = self.get_weather_data(lat, lon)
        
        suitability_score = 100
        issues = []
        warnings = []
        
        # Temperature check
        temp = weather.get("temperature", 20)
        if temp < 0:
            issues.append("Temperature below freezing - unsuitable for planting")
            suitability_score -= 50
        elif temp < 5:
            warnings.append("Very cold - planting may be challenging")
            suitability_score -= 20
        elif temp > 40:
            warnings.append("Very hot - requires extra watering")
            suitability_score -= 15
        
        # Precipitation check
        precip = weather.get("precipitation", 0)
        if precip > 50:
            warnings.append("Heavy rainfall - may delay planting")
            suitability_score -= 10
        
        # Humidity check
        humidity = weather.get("humidity", 50)
        if humidity < 20:
            warnings.append("Low humidity - requires frequent watering")
            suitability_score -= 10
        
        # Determine suitability
        if suitability_score >= 80:
            suitable = "excellent"
        elif suitability_score >= 60:
            suitable = "good"
        elif suitability_score >= 40:
            suitable = "moderate"
        else:
            suitable = "poor"
        
        return {
            "suitable": suitability_score >= 40,
            "suitability_level": suitable,
            "score": suitability_score,
            "issues": issues,
            "warnings": warnings,
            "weather_summary": f"{temp}°C, {weather.get('description', 'Unknown')}"
        }
    
    def validate_location_comprehensive(
        self,
        gps_coords: str,
        location_name: str
    ) -> Dict[str, Any]:
        """
        Comprehensive location validation
        
        Returns GPS validity, location info, weather, and suitability
        """
        
        # Validate coordinates
        coord_validation = self.validate_coordinates(gps_coords)
        
        if not coord_validation["valid"]:
            return {
                "valid": False,
                "reason": coord_validation["reason"],
                "gps_validation": coord_validation
            }
        
        lat = coord_validation["coordinates"]["latitude"]
        lon = coord_validation["coordinates"]["longitude"]
        
        # Get location info
        location_info = self.get_location_info(lat, lon)
        
        # Get weather data
        weather_data = self.get_weather_data(lat, lon)
        
        # Check planting suitability
        suitability = self.check_planting_suitability(lat, lon, weather_data)
        
        # Verify location name matches GPS
        location_match = self._check_location_match(
            location_name,
            location_info.get("formatted_address", "")
        )
        
        return {
            "valid": True,
            "gps_validation": coord_validation,
            "location_info": location_info,
            "weather": weather_data,
            "planting_suitability": suitability,
            "location_name_match": location_match,
            "validated_at": datetime.now().isoformat()
        }
    
    def _check_location_match(self, claimed: str, actual: str) -> Dict[str, Any]:
        """Check if claimed location matches GPS coordinates"""
        
        # Simple keyword matching
        claimed_lower = claimed.lower()
        actual_lower = actual.lower()
        
        # Extract key terms
        claimed_words = set(claimed_lower.replace(",", " ").split())
        actual_words = set(actual_lower.replace(",", " ").split())
        
        # Calculate overlap
        common_words = claimed_words & actual_words
        match_ratio = len(common_words) / max(len(claimed_words), 1)
        
        if match_ratio >= 0.5:
            match = "strong"
        elif match_ratio >= 0.3:
            match = "moderate"
        else:
            match = "weak"
        
        return {
            "match_level": match,
            "match_ratio": round(match_ratio, 2),
            "claimed": claimed,
            "geocoded": actual,
            "warning": match == "weak"
        }
    
    def _mock_location_info(self, lat: float, lon: float) -> Dict[str, Any]:
        """Mock location info when API unavailable"""
        return {
            "formatted_address": f"Location at {lat:.4f}, {lon:.4f}",
            "country": "Unknown",
            "state": "Unknown",
            "city": "Unknown",
            "note": "Google Maps API not configured"
        }
    
    def _mock_weather_data(self) -> Dict[str, Any]:
        """Mock weather data when API unavailable"""
        return {
            "temperature": 25,
            "feels_like": 27,
            "humidity": 65,
            "conditions": "Clear",
            "description": "clear sky",
            "wind_speed": 3.5,
            "precipitation": 0,
            "timestamp": datetime.now().isoformat(),
            "note": "OpenWeather API not configured - using default values"
        }


def test_gps_validator():
    """Test GPS validator"""
    print("\n" + "="*70)
    print("🌍 TESTING GPS VALIDATOR")
    print("="*70 + "\n")
    
    validator = GPSValidator()
    
    # Test coordinate parsing
    print("Test 1: Coordinate Parsing")
    test_coords = [
        "19.0760° N, 72.8777° E",
        "19.0760, 72.8777",
        "(19.0760, 72.8777)",
        "invalid coords"
    ]
    
    for coord in test_coords:
        result = validator.parse_coordinates(coord)
        print(f"  {coord:30} → {result}")
    
    print("\n" + "-"*70 + "\n")
    
    # Test comprehensive validation
    print("Test 2: Comprehensive Location Validation")
    result = validator.validate_location_comprehensive(
        gps_coords="19.0760° N, 72.8777° E",
        location_name="Mumbai, Maharashtra, India"
    )
    
    print(f"Valid: {result['valid']}")
    print(f"Coordinates: {result['gps_validation']['formatted']}")
    print(f"Location: {result['location_info'].get('formatted_address', 'Unknown')}")
    print(f"Weather: {result['weather']['temperature']}°C, {result['weather']['description']}")
    print(f"Planting Suitability: {result['planting_suitability']['suitability_level']} ({result['planting_suitability']['score']}/100)")
    
    if result['planting_suitability']['warnings']:
        print(f"Warnings: {', '.join(result['planting_suitability']['warnings'])}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    test_gps_validator()
