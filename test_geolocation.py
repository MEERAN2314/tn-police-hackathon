#!/usr/bin/env python3
"""
Test script for geolocation service
Run this to test if geolocation is working properly
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.geolocation_service import GeolocationService

async def test_geolocation():
    """Test the geolocation service with sample IPs"""
    
    # Test IPs (these are public DNS servers, safe to test)
    test_ips = [
        '8.8.8.8',      # Google DNS (US)
        '1.1.1.1',      # Cloudflare DNS (US)
        '208.67.222.222', # OpenDNS (US)
        '9.9.9.9',      # Quad9 DNS (Switzerland)
    ]
    
    print("🌍 Testing Geolocation Service")
    print("=" * 50)
    
    async with GeolocationService() as geo_service:
        for ip in test_ips:
            print(f"\n📍 Testing IP: {ip}")
            try:
                location = await geo_service.get_ip_location(ip)
                print(f"   Country: {location['country_name']} ({location['country_code']})")
                print(f"   City: {location['city']}")
                print(f"   Coordinates: {location['latitude']}, {location['longitude']}")
                print(f"   ISP: {location['isp']}")
                print(f"   Source: {location['source']}")
                print(f"   ✅ Success")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Geolocation test completed!")
    print("\nIf you see 'mock_data' as source, it means:")
    print("1. No API key is configured, OR")
    print("2. Free APIs are not accessible")
    print("3. The system is using demo data (which is fine for testing)")

if __name__ == "__main__":
    asyncio.run(test_geolocation())