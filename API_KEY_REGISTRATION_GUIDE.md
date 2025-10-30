# API Key Registration Guide

## Required API Keys

To run the AQI Prediction System, you need API keys from these three services:

---

## 1. OpenWeather Air Pollution API ⭐ **REQUIRED**

### Why We Need It
- Provides PM2.5, PM10, NO2, SO2, CO, O3, NH3 data
- Global coverage with 60 calls/minute
- Most comprehensive pollutant data

### Registration Steps
1. **Go to**: https://openweathermap.org/
2. **Click**: "Sign In" → "Create an Account"
3. **Fill in**: Email, username, password
4. **Verify**: Check your email and click verification link
5. **Subscribe**: Go to https://openweathermap.org/api/air-pollution
   - Click "Subscribe" under "Air Pollution API"
   - Select **"Free" plan** (1,000 calls/day, 60 calls/minute)
6. **Get API Key**: Go to "API keys" tab → Copy your key

### Free Tier Limits
- ✅ 1,000 calls per day
- ✅ 60 calls per minute
- ✅ No credit card required
- ✅ Enough for 10 cities (24 calls/day each)

### Example API Call
```bash
curl "https://api.openweathermap.org/data/2.5/air_pollution?lat=28.7&lon=77.1&appid=YOUR_API_KEY"
```

### Expected Response
```json
{
  "coord": {"lon": 77.1, "lat": 28.7},
  "list": [{
    "main": {"aqi": 3},
    "components": {
      "pm2_5": 55.3,
      "pm10": 85.2,
      "no2": 42.1,
      "so2": 12.5,
      "co": 890
    }
  }]
}
```

---

## 2. IQAir AirVisual API ⭐ **REQUIRED**

### Why We Need It
- Provides global AQI data
- Government station data
- 10,000 free calls per month

### Registration Steps
1. **Go to**: https://www.iqair.com/air-pollution-data-api
2. **Click**: "Get API Key" or "Request Access"
3. **Select**: "Community Edition" (FREE)
4. **Fill Form**:
   - Name
   - Email
   - Organization (can be "Personal Project")
   - Use case: "Air Quality Monitoring & Prediction"
5. **Wait**: Approval takes 1-2 business days
6. **Receive Email**: You'll get API key via email

### Free Tier Limits
- ✅ 10,000 calls per month (~333 calls/day)
- ✅ Enough for 10 cities (hourly checks)
- ✅ No credit card required

### Example API Call
```bash
curl "https://api.airvisual.com/v2/city?city=Delhi&state=Delhi&country=India&key=YOUR_API_KEY"
```

### Expected Response
```json
{
  "status": "success",
  "data": {
    "city": "Delhi",
    "current": {
      "pollution": {
        "aqius": 152,
        "mainus": "p2",
        "aqicn": 102
      }
    }
  }
}
```

---

## 3. CPCB Government API 🇮🇳 **OPTIONAL**

### Why We Need It
- Official Indian government data
- Station-level readings
- Free access

### Registration Steps
1. **Go to**: https://data.gov.in/
2. **Click**: "Register"
3. **Fill Form**: Name, email, organization
4. **Search**: "air quality" or "CPCB"
5. **Request API Access**: Click on dataset → "Request API Access"
6. **Wait**: Approval takes 3-7 days

### Note
- CPCB API is **optional** because OpenWeather and IQAir already provide good coverage
- Useful for redundancy and more detailed Indian station data
- API documentation varies by dataset

---

## Setting Up Your .env File

Once you have your API keys, create a `.env` file in the project root:

```env
# OpenWeather API Key
OPENWEATHER_API_KEY=your_openweather_key_here

# IQAir API Key
IQAIR_API_KEY=your_iqair_key_here

# CPCB API Key (Optional)
CPCB_API_KEY=your_cpcb_key_here

# Database Configuration
DATABASE_URL=postgresql://localhost:5432/aqi_prediction_db

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
```

---

## Testing Your API Keys

### Test OpenWeather
```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENWEATHER_API_KEY')

# Test for Delhi
url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat=28.7&lon=77.1&appid={api_key}"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(f"✓ OpenWeather API works!")
    print(f"  PM2.5: {data['list'][0]['components']['pm2_5']}")
else:
    print(f"✗ Error: {response.status_code}")
```

### Test IQAir
```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('IQAIR_API_KEY')

# Test for Delhi
url = f"https://api.airvisual.com/v2/city?city=Delhi&state=Delhi&country=India&key={api_key}"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(f"✓ IQAir API works!")
    print(f"  AQI: {data['data']['current']['pollution']['aqius']}")
else:
    print(f"✗ Error: {response.status_code}")
```

---

## Quick Test Script

Save this as `test_api_keys.py`:

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_openweather():
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key or api_key == 'your_key_here':
        print("✗ OpenWeather API key not configured")
        return False
    
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat=28.7&lon=77.1&appid={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("✓ OpenWeather API key valid")
            return True
        else:
            print(f"✗ OpenWeather API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ OpenWeather API error: {e}")
        return False

def test_iqair():
    api_key = os.getenv('IQAIR_API_KEY')
    if not api_key or api_key == 'your_key_here':
        print("✗ IQAir API key not configured")
        return False
    
    url = f"https://api.airvisual.com/v2/city?city=Delhi&state=Delhi&country=India&key={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("✓ IQAir API key valid")
            return True
        else:
            print(f"✗ IQAir API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ IQAir API error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Testing API Keys")
    print("="*50 + "\n")
    
    openweather_ok = test_openweather()
    iqair_ok = test_iqair()
    
    print("\n" + "="*50)
    if openweather_ok and iqair_ok:
        print("✓ All API keys configured correctly!")
        print("You can now run the data collector.")
    else:
        print("✗ Some API keys are missing or invalid.")
        print("Please check your .env file.")
    print("="*50 + "\n")
```

Run it:
```bash
python test_api_keys.py
```

---

## Troubleshooting

### "Invalid API key"
- ✓ Check for typos in .env file
- ✓ Remove any spaces before/after the key
- ✓ Make sure you copied the full key
- ✓ For OpenWeather, wait 10 minutes after creation

### "Rate limit exceeded"
- ✓ Wait 1 hour for limits to reset
- ✓ Reduce collection frequency
- ✓ Consider upgrading plan (paid)

### "Unauthorized"
- ✓ Verify API key is active
- ✓ Check if subscription is still valid
- ✓ For IQAir, ensure approval email was received

### "City not found"
- ✓ Use exact city names from API documentation
- ✓ For IQAir, check spelling and state name
- ✓ Use latitude/longitude for OpenWeather

---

## Cost Comparison

| Service | Free Tier | Paid Tier | Our Usage |
|---------|-----------|-----------|-----------|
| **OpenWeather** | 1,000 calls/day | $40/month (100k calls) | 240 calls/day |
| **IQAir** | 10,000 calls/month | $199/month (100k calls) | 240 calls/day |
| **CPCB** | FREE | FREE | Optional |

**Total Cost**: **$0/month** with free tiers! ✅

---

## Rate Limiting Strategy

Our system automatically handles rate limits:

```python
# OpenWeather: 60 calls/min
- Batch calls for multiple cities
- Sleep between requests if needed

# IQAir: 10,000/month (~333/day)
- Use for 10 cities hourly = 240 calls/day ✓
- Well within limit

# CPCB: Varies
- Used as fallback only
```

---

## Security Best Practices

1. **Never commit .env file**
   - Already in `.gitignore`
   
2. **Rotate keys every 6 months**
   - Set calendar reminder
   
3. **Monitor usage**
   - Check API dashboards weekly
   
4. **Use environment variables**
   - Never hardcode keys in code

---

## Summary Checklist

- [ ] Register for OpenWeather account
- [ ] Subscribe to Air Pollution API (Free)
- [ ] Copy OpenWeather API key
- [ ] Register for IQAir account
- [ ] Request Community Edition access
- [ ] Wait for IQAir approval email
- [ ] Copy IQAir API key
- [ ] Create .env file in project root
- [ ] Add both API keys to .env
- [ ] Run `python test_api_keys.py`
- [ ] Verify both APIs work

**Estimated Time**: 20 minutes + IQAir approval wait (1-2 days)

---

## Next Steps

Once you have valid API keys:

1. Run the quick start script:
   ```powershell
   .\quick-start.ps1
   ```

2. Test data collection:
   ```bash
   python real_time_collector.py
   ```

3. Check database:
   ```sql
   SELECT * FROM raw_air_quality_data ORDER BY timestamp DESC LIMIT 10;
   ```

4. Start the system:
   ```bash
   python automated_scheduler.py
   ```

---

**Questions?**

- OpenWeather Support: https://openweathermap.org/faq
- IQAir Support: https://support.iqair.com/
- CPCB Support: https://data.gov.in/help

**Ready to collect real data!** 🚀
