import asyncio
import aiohttp
import logging
from typing import Dict, Optional
import json

from app.config import settings

logger = logging.getLogger(__name__)

class GeolocationService:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.use_free_apis = getattr(settings, 'use_free_geolocation', True)
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_ip_location(self, ip_address: str) -> Dict:
        """Get geolocation data for an IP address"""
        try:
            # Try different geolocation services in order of preference
            if settings.ipgeolocation_api_key and settings.ipgeolocation_api_key != "your_ipgeolocation_api_key_here":
                return await self._get_ipgeolocation_io(ip_address)
            elif self.use_free_apis:
                return await self._get_free_geolocation(ip_address)
            else:
                return self._get_mock_location(ip_address)
                
        except Exception as e:
            logger.error(f"Error getting geolocation for {ip_address}: {e}")
            return self._get_mock_location(ip_address)
    
    async def _get_ipgeolocation_io(self, ip_address: str) -> Dict:
        """Get location from IPGeolocation.io (requires API key)"""
        try:
            url = f"https://api.ipgeolocation.io/ipgeo"
            params = {
                'apiKey': settings.ipgeolocation_api_key,
                'ip': ip_address,
                'fields': 'country_code2,country_name,state_prov,city,latitude,longitude,isp,organization'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'ip': ip_address,
                        'country_code': data.get('country_code2', 'Unknown'),
                        'country_name': data.get('country_name', 'Unknown'),
                        'region': data.get('state_prov', 'Unknown'),
                        'city': data.get('city', 'Unknown'),
                        'latitude': float(data.get('latitude', 0)) if data.get('latitude') else 0.0,
                        'longitude': float(data.get('longitude', 0)) if data.get('longitude') else 0.0,
                        'isp': data.get('isp', 'Unknown'),
                        'organization': data.get('organization', 'Unknown'),
                        'source': 'ipgeolocation.io'
                    }
                else:
                    logger.warning(f"IPGeolocation.io API error: {response.status}")
                    return await self._get_free_geolocation(ip_address)
                    
        except Exception as e:
            logger.error(f"Error with IPGeolocation.io: {e}")
            return await self._get_free_geolocation(ip_address)
    
    async def _get_free_geolocation(self, ip_address: str) -> Dict:
        """Get location from free APIs (no API key required)"""
        
        # Try IP-API.com first (1000 requests/hour, no key required)
        try:
            url = f"http://ip-api.com/json/{ip_address}"
            params = {
                'fields': 'status,country,countryCode,region,regionName,city,lat,lon,isp,org,query'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        return {
                            'ip': ip_address,
                            'country_code': data.get('countryCode', 'Unknown'),
                            'country_name': data.get('country', 'Unknown'),
                            'region': data.get('regionName', 'Unknown'),
                            'city': data.get('city', 'Unknown'),
                            'latitude': float(data.get('lat', 0)) if data.get('lat') else 0.0,
                            'longitude': float(data.get('lon', 0)) if data.get('lon') else 0.0,
                            'isp': data.get('isp', 'Unknown'),
                            'organization': data.get('org', 'Unknown'),
                            'source': 'ip-api.com'
                        }
        except Exception as e:
            logger.warning(f"Error with IP-API.com: {e}")
        
        # Fallback to FreeGeoIP.app
        try:
            url = f"https://freegeoip.app/json/{ip_address}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'ip': ip_address,
                        'country_code': data.get('country_code', 'Unknown'),
                        'country_name': data.get('country_name', 'Unknown'),
                        'region': data.get('region_name', 'Unknown'),
                        'city': data.get('city', 'Unknown'),
                        'latitude': float(data.get('latitude', 0)) if data.get('latitude') else 0.0,
                        'longitude': float(data.get('longitude', 0)) if data.get('longitude') else 0.0,
                        'isp': 'Unknown',
                        'organization': 'Unknown',
                        'source': 'freegeoip.app'
                    }
        except Exception as e:
            logger.warning(f"Error with FreeGeoIP.app: {e}")
        
        # Final fallback to mock data
        return self._get_mock_location(ip_address)
    
    def _get_mock_location(self, ip_address: str) -> Dict:
        """Generate mock location data for demo purposes"""
        import random
        
        # Sample countries and cities for demo
        locations = [
            {'country_code': 'US', 'country_name': 'United States', 'city': 'New York', 'lat': 40.7128, 'lon': -74.0060},
            {'country_code': 'GB', 'country_name': 'United Kingdom', 'city': 'London', 'lat': 51.5074, 'lon': -0.1278},
            {'country_code': 'DE', 'country_name': 'Germany', 'city': 'Berlin', 'lat': 52.5200, 'lon': 13.4050},
            {'country_code': 'FR', 'country_name': 'France', 'city': 'Paris', 'lat': 48.8566, 'lon': 2.3522},
            {'country_code': 'JP', 'country_name': 'Japan', 'city': 'Tokyo', 'lat': 35.6762, 'lon': 139.6503},
            {'country_code': 'CA', 'country_name': 'Canada', 'city': 'Toronto', 'lat': 43.6532, 'lon': -79.3832},
            {'country_code': 'AU', 'country_name': 'Australia', 'city': 'Sydney', 'lat': -33.8688, 'lon': 151.2093},
            {'country_code': 'IN', 'country_name': 'India', 'city': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777},
            {'country_code': 'BR', 'country_name': 'Brazil', 'city': 'São Paulo', 'lat': -23.5505, 'lon': -46.6333},
            {'country_code': 'RU', 'country_name': 'Russia', 'city': 'Moscow', 'lat': 55.7558, 'lon': 37.6176}
        ]
        
        # Use IP hash to consistently return same location for same IP
        ip_hash = hash(ip_address) % len(locations)
        location = locations[ip_hash]
        
        return {
            'ip': ip_address,
            'country_code': location['country_code'],
            'country_name': location['country_name'],
            'region': 'Demo Region',
            'city': location['city'],
            'latitude': location['lat'] + random.uniform(-0.1, 0.1),  # Add small random offset
            'longitude': location['lon'] + random.uniform(-0.1, 0.1),
            'isp': 'Demo ISP',
            'organization': 'Demo Organization',
            'source': 'mock_data'
        }
    
    async def get_multiple_locations(self, ip_addresses: list) -> Dict[str, Dict]:
        """Get locations for multiple IP addresses"""
        results = {}
        
        # Process in batches to avoid rate limiting
        batch_size = 10
        for i in range(0, len(ip_addresses), batch_size):
            batch = ip_addresses[i:i + batch_size]
            
            # Create tasks for concurrent processing
            tasks = [self.get_ip_location(ip) for ip in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for ip, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Error processing {ip}: {result}")
                    results[ip] = self._get_mock_location(ip)
                else:
                    results[ip] = result
            
            # Small delay between batches to be respectful to free APIs
            if i + batch_size < len(ip_addresses):
                await asyncio.sleep(0.1)
        
        return results
    
    async def get_country_statistics(self, ip_addresses: list) -> Dict:
        """Get statistics about countries from IP addresses"""
        locations = await self.get_multiple_locations(ip_addresses)
        
        country_counts = {}
        city_counts = {}
        
        for ip, location in locations.items():
            country = location.get('country_name', 'Unknown')
            city = location.get('city', 'Unknown')
            
            country_counts[country] = country_counts.get(country, 0) + 1
            city_key = f"{city}, {country}"
            city_counts[city_key] = city_counts.get(city_key, 0) + 1
        
        return {
            'total_ips': len(ip_addresses),
            'unique_countries': len(country_counts),
            'unique_cities': len(city_counts),
            'top_countries': sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'top_cities': sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'country_distribution': country_counts
        }

# Convenience function for single IP lookup
async def get_ip_location(ip_address: str) -> Dict:
    """Convenience function to get location for a single IP"""
    async with GeolocationService() as geo_service:
        return await geo_service.get_ip_location(ip_address)

# Convenience function for multiple IP lookups
async def get_multiple_ip_locations(ip_addresses: list) -> Dict[str, Dict]:
    """Convenience function to get locations for multiple IPs"""
    async with GeolocationService() as geo_service:
        return await geo_service.get_multiple_locations(ip_addresses)