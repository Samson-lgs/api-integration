"""
API Key Validation Script
Tests OpenWeather and IQAir API keys
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_openweather():
    """Test OpenWeather Air Pollution API"""
    print("\n[1/2] Testing OpenWeather API...")
    print("-" * 50)
    
    api_key = os.getenv('OPENWEATHER_API_KEY')
    
    if not api_key or api_key == 'your_key_here':
        print("✗ OpenWeather API key not configured in .env")
        print("  Get key at: https://openweathermap.org/api")
        return False
    
    # Test with Delhi coordinates
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat=28.7041&lon=77.1025&appid={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            components = data['list'][0]['components']
            aqi = data['list'][0]['main']['aqi']
            
            print("✓ OpenWeather API key is VALID")
            print(f"  Test Location: Delhi, India")
            print(f"  AQI: {aqi}")
            print(f"  PM2.5: {components.get('pm2_5', 'N/A')} µg/m³")
            print(f"  PM10: {components.get('pm10', 'N/A')} µg/m³")
            print(f"  NO2: {components.get('no2', 'N/A')} µg/m³")
            return True
            
        elif response.status_code == 401:
            print("✗ OpenWeather API key is INVALID")
            print("  Check your API key in .env file")
            return False
            
        else:
            print(f"✗ OpenWeather API error: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ OpenWeather API timeout")
        print("  Check your internet connection")
        return False
        
    except Exception as e:
        print(f"✗ OpenWeather API error: {e}")
        return False


def test_iqair():
    """Test IQAir AirVisual API"""
    print("\n[2/2] Testing IQAir API...")
    print("-" * 50)
    
    api_key = os.getenv('IQAIR_API_KEY')
    
    if not api_key or api_key == 'your_key_here':
        print("✗ IQAir API key not configured in .env")
        print("  Get key at: https://www.iqair.com/air-pollution-data-api")
        return False
    
    # Test with Delhi
    url = f"https://api.airvisual.com/v2/city?city=Delhi&state=Delhi&country=India&key={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                pollution = data['data']['current']['pollution']
                weather = data['data']['current']['weather']
                
                print("✓ IQAir API key is VALID")
                print(f"  Test Location: {data['data']['city']}, {data['data']['country']}")
                print(f"  AQI (US): {pollution.get('aqius', 'N/A')}")
                print(f"  AQI (CN): {pollution.get('aqicn', 'N/A')}")
                print(f"  Main Pollutant: {pollution.get('mainus', 'N/A').upper()}")
                print(f"  Temperature: {weather.get('tp', 'N/A')}°C")
                return True
            else:
                print(f"✗ IQAir API error: {data.get('message', 'Unknown error')}")
                return False
                
        elif response.status_code == 401:
            print("✗ IQAir API key is INVALID")
            print("  Check your API key in .env file")
            print("  Make sure your account is approved")
            return False
            
        elif response.status_code == 429:
            print("✗ IQAir API rate limit exceeded")
            print("  Free tier: 10,000 calls/month")
            print("  Wait 1 hour and try again")
            return False
            
        else:
            print(f"✗ IQAir API error: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ IQAir API timeout")
        print("  Check your internet connection")
        return False
        
    except Exception as e:
        print(f"✗ IQAir API error: {e}")
        return False


def main():
    """Run all API tests"""
    print("\n" + "="*50)
    print("API KEY VALIDATION TEST")
    print("="*50)
    
    # Test OpenWeather
    openweather_ok = test_openweather()
    
    # Test IQAir
    iqair_ok = test_iqair()
    
    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    if openweather_ok and iqair_ok:
        print("\n✓ SUCCESS! All API keys are configured correctly!")
        print("\nNext Steps:")
        print("  1. Run: python real_time_collector.py")
        print("  2. Check database for collected data")
        print("  3. Train ML models: python ml_prediction_engine.py")
        print("  4. Start scheduler: python automated_scheduler.py")
        
    elif openweather_ok or iqair_ok:
        print("\n⚠ WARNING: Some API keys are working")
        
        if not openweather_ok:
            print("\n✗ OpenWeather API key needed:")
            print("  1. Go to https://openweathermap.org/")
            print("  2. Sign up for free account")
            print("  3. Subscribe to Air Pollution API (FREE)")
            print("  4. Copy API key to .env file")
        
        if not iqair_ok:
            print("\n✗ IQAir API key needed:")
            print("  1. Go to https://www.iqair.com/air-pollution-data-api")
            print("  2. Request Community Edition (FREE)")
            print("  3. Wait for approval email (1-2 days)")
            print("  4. Copy API key to .env file")
    
    else:
        print("\n✗ FAILED: No API keys are configured")
        print("\nPlease configure API keys in .env file:")
        print("  OPENWEATHER_API_KEY=your_key_here")
        print("  IQAIR_API_KEY=your_key_here")
        print("\nSee API_KEY_REGISTRATION_GUIDE.md for details")
    
    print("\n" + "="*50 + "\n")
    
    return openweather_ok and iqair_ok


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
