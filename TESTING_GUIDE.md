# UI Features Testing Guide

## ✅ Status: Frontend Running Successfully

**Server:** http://localhost:3000  
**Status:** ✅ Vite development server running  
**Compilation:** ✅ No errors  

---

## 🧪 Testing Checklist

### 1. Interactive AQI Map (`AQIMap.jsx`)

**Test Steps:**
1. ✅ Navigate to Dashboard (http://localhost:3000)
2. ✅ Scroll down to "Real-Time AQI Map" section
3. ✅ Verify map loads with OpenStreetMap tiles
4. ✅ Check if station markers appear as colored circles
5. ✅ Click on any marker to open popup
6. ✅ Verify popup shows:
   - Station name
   - City
   - AQI value with colored badge
   - PM2.5, PM10, NO2 values
   - Last update timestamp
7. ✅ Check if legend is visible (bottom-right corner)
8. ✅ Verify auto-refresh works (60 seconds)

**Expected Colors:**
- Green (0-50): Good
- Yellow (51-100): Satisfactory
- Orange (101-200): Moderate
- Red (201-300): Poor
- Purple (301-400): Very Poor
- Maroon (400+): Severe

---

### 2. Multi-City Comparison (`CityComparison.jsx`)

**Test Steps:**
1. ✅ Click "Compare Cities" in navigation
2. ✅ URL should be http://localhost:3000/comparison
3. ✅ Select 2-10 cities from dropdown
4. ✅ Test Bar Chart view:
   - Verify bars show PM2.5, PM10, NO2, AQI
   - Check if colors match (green/orange/red/purple)
   - Hover to see values
5. ✅ Test Radar Chart view:
   - Click "Radar" button
   - Verify multi-pollutant visualization
   - Check if all 6 metrics visible
6. ✅ Test Table view:
   - Click "Table" button
   - Verify all pollutants listed
   - Check AQI color coding
   - Try sorting by clicking column headers
7. ✅ Check Best/Worst rankings cards
   - Verify top 3 best cities (green)
   - Verify top 3 worst cities (red)

---

### 3. Health Impact & Recommendations (`HealthImpact.jsx`)

**Test Steps:**
1. ✅ Go to Dashboard
2. ✅ Scroll to "Health Advisory" section
3. ✅ Verify it shows the worst affected city
4. ✅ Check AQI summary card:
   - AQI value displayed prominently
   - Correct emoji for level (😊/🙂/😐/😷/😨/☠️)
   - Category badge with correct color
5. ✅ Verify Health Implications section:
   - General public advice visible
   - Sensitive groups warning (if applicable)
6. ✅ Check Activity Recommendations grid:
   - 4 recommendation cards
   - Icons displayed correctly
   - Color-coded backgrounds
7. ✅ Verify Additional Health Tips:
   - 8 bullet points
   - Color-coded icon
8. ✅ Check Emergency Alert (if AQI > 300):
   - Red alert card visible
   - Warning icon and message
   - Emergency contact info

**Test Different AQI Levels:**
- Test with AQI 30 (Good) - Should show positive messages
- Test with AQI 150 (Moderate) - Should show caution
- Test with AQI 350 (Very Poor) - Should show emergency alert

---

### 4. Email Alert System (`AlertSettings.jsx`)

**Test Steps:**
1. ✅ Click "Alerts" in navigation (Bell icon)
2. ✅ URL should be http://localhost:3000/alerts
3. ✅ Test Email Configuration:
   - Enter email address
   - Click "Save Email"
   - Verify success toast notification
4. ✅ Test Create Alert:
   - Select city from dropdown
   - Set AQI threshold (e.g., 200)
   - Choose frequency (Once/Hourly/Daily)
   - Click "Add Alert"
   - Verify alert appears in "Active Alerts" list
5. ✅ Test Alert Management:
   - Toggle enable/disable switch
   - Click "Test Alert" button
   - Verify test toast notification
   - Click "Delete" button
   - Confirm deletion
   - Verify alert removed from list
6. ✅ Test Threshold Color Coding:
   - Set threshold 50 - Should be green (Good)
   - Set threshold 150 - Should be orange (Moderate)
   - Set threshold 300 - Should be red (Poor)
7. ✅ Test Multiple Alerts:
   - Create alerts for different cities
   - Verify all show in list
   - Test managing multiple alerts

---

### 5. Enhanced Dashboard Integration

**Test Steps:**
1. ✅ Go to Dashboard home page
2. ✅ Verify layout structure:
   - Stats grid (4 cards) at top
   - Real-Time AQI Map in middle
   - Health Advisory card below map
   - PM2.5 Trends chart
   - Latest Readings table at bottom
3. ✅ Test City Filter:
   - Select specific city from dropdown
   - Verify all components update
   - Check map centers on city
   - Health advisory updates to selected city
4. ✅ Test Data Refresh:
   - Click refresh button (if visible)
   - Verify all components reload
   - Check timestamps update

---

### 6. Navigation & Routing

**Test Steps:**
1. ✅ Test all navigation links:
   - Dashboard (Home icon)
   - Stations (Map icon)
   - Predictions (TrendingUp icon)
   - Analytics (BarChart icon)
   - Compare Cities (GitCompare icon) - **NEW**
   - Alerts (Bell icon) - **NEW**
2. ✅ Verify URLs:
   - `/` - Dashboard
   - `/stations` - Stations
   - `/predictions` - Predictions
   - `/analytics` - Analytics
   - `/comparison` - City Comparison **NEW**
   - `/alerts` - Alert Settings **NEW**
3. ✅ Test browser back/forward buttons
4. ✅ Verify active link highlighting
5. ✅ Test direct URL navigation (copy/paste URLs)

---

## 🔧 Backend Testing (Optional)

If backend is running on http://localhost:5000:

### Alert Endpoints

**Test with curl or Postman:**

```bash
# 1. Get alert settings
GET http://localhost:5000/api/alerts/settings

# 2. Update email
POST http://localhost:5000/api/alerts/email
Body: {"email": "test@example.com"}

# 3. Create alert
POST http://localhost:5000/api/alerts
Body: {
  "city": "Delhi",
  "threshold": 200,
  "frequency": "daily"
}

# 4. Update alert
PUT http://localhost:5000/api/alerts/1
Body: {"enabled": false}

# 5. Delete alert
DELETE http://localhost:5000/api/alerts/1

# 6. Test alert email
POST http://localhost:5000/api/alerts/1/test
```

---

## 📊 Data Requirements

For full functionality, ensure backend provides:

### 1. Station Data (for Map)
```json
{
  "stations": [
    {
      "id": 1,
      "name": "Station Name",
      "city": "City Name",
      "latitude": 28.7041,
      "longitude": 77.1025,
      "aqi": 150,
      "pm25": 88.5,
      "pm10": 120.3,
      "no2": 45.2,
      "last_updated": "2025-10-28T10:30:00"
    }
  ]
}
```

### 2. City Data (for Comparison)
```json
{
  "cities": [
    {
      "name": "Delhi",
      "avg_aqi": 250,
      "avg_pm25": 120,
      "avg_pm10": 180,
      "avg_no2": 60,
      "avg_so2": 15,
      "avg_co": 1.2,
      "avg_o3": 40
    }
  ]
}
```

### 3. Historical Data (for Trends)
```json
{
  "trends": [
    {
      "date": "2025-10-21",
      "pm25": 85.5
    }
  ]
}
```

---

## 🐛 Known Issues & Limitations

### Current Implementation
- ✅ Alert storage is in-memory (resets on server restart)
- ✅ Email sending is mocked (logs only, no actual emails)
- ✅ No user authentication (single user only)
- ✅ No alert history tracking
- ✅ No database persistence for alerts

### For Production
- [ ] Migrate alerts to PostgreSQL database
- [ ] Implement actual email sending (SendGrid/AWS SES)
- [ ] Add user authentication & multi-user support
- [ ] Create background worker for alert monitoring
- [ ] Add alert history & analytics
- [ ] Implement rate limiting for alerts
- [ ] Add email verification

---

## 🔍 Debugging Tips

### If Map Doesn't Load
1. Check browser console for errors
2. Verify Leaflet CSS is imported in `AQIMap.jsx`
3. Check if `data` prop contains `latitude` and `longitude`
4. Ensure OpenStreetMap tiles are accessible (internet required)

### If Charts Don't Render
1. Verify recharts is installed: `npm list recharts`
2. Check data format matches expected structure
3. Look for console errors in browser DevTools
4. Verify parent container has defined dimensions

### If Alerts Don't Save
1. Check backend API is running on port 5000
2. Verify CORS is enabled in backend
3. Check Network tab in DevTools for API responses
4. Look for error toasts in UI

### If Components Don't Update
1. Check auto-refresh is enabled
2. Verify API endpoints return fresh data
3. Check if data fetching has errors
4. Look for console warnings about stale data

---

## 📱 Browser Testing

### Recommended Browsers
- ✅ Chrome 90+ (Recommended)
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

### Mobile Responsive Testing
1. Open DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test on different screen sizes:
   - Mobile: 375px × 667px
   - Tablet: 768px × 1024px
   - Desktop: 1920px × 1080px

---

## ✅ Success Criteria

**All features working if:**
- ✅ Map loads with colored markers
- ✅ Clicking markers shows popups with data
- ✅ City comparison shows 3 view modes
- ✅ Health advisory updates based on AQI
- ✅ Alerts can be created, edited, deleted
- ✅ Toast notifications appear for actions
- ✅ Navigation works smoothly
- ✅ All charts render correctly
- ✅ No console errors (except expected API warnings)

---

## 🚀 Quick Start

```bash
# Terminal 1: Start Frontend
cd frontend
npm run dev
# Opens at http://localhost:3000

# Terminal 2: Start Backend (optional)
cd backend
python api.py
# Runs at http://localhost:5000

# Terminal 3: Open Browser
# Navigate to http://localhost:3000
```

---

## 📞 Need Help?

**If you encounter issues:**
1. Check browser console for errors (F12)
2. Verify all dependencies installed: `npm list`
3. Ensure backend API is running
4. Check network requests in DevTools
5. Review `UI_FEATURES_COMPLETE.md` for implementation details

---

**Last Updated:** October 28, 2025  
**Status:** ✅ Ready for Testing  
**Server:** ✅ Running on http://localhost:3000
