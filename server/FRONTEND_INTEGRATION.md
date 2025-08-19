# 🚀 Frontend Integration Guide

This guide helps frontend developers connect to the Smart Energy Management System backend API.

## 🌐 Server Information

- **Base URL**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

## 📡 Available Endpoints

### Core Endpoints
- `GET /` - Root endpoint with system overview
- `GET /health` - Health check
- `GET /status` - System status
- `GET /docs` - Interactive API documentation

### Web Application Endpoints
- `GET /web/dashboard` - Unified dashboard data
- `POST /web/preferences` - Update user preferences
- `POST /web/export` - Export data
- `GET /web/integration-status` - System integration status
- `GET /web/config` - Frontend configuration
- `GET /web/health` - Web routes health check

### Development Helper Endpoints
- `GET /web/dev/endpoints` - All available endpoints
- `GET /web/dev/sample-data` - Sample data for development
- `POST /web/dev/test-connection` - Test frontend connection
- `GET /web/dev/error-test` - Test error handling

### Energy Management System Endpoints
- `GET /appliance-health/*` - Appliance health prediction
- `GET /solar-calculator/*` - Solar feasibility & ROI calculator
- `GET /smart-analysis/*` - Automated smart analysis
- `GET /bill-simulation/*` - Bill simulation & forecasting
- `GET /carbon-tracker/*` - Carbon footprint tracking

## 🔧 Frontend Setup

### 1. Basic Connection Test

```javascript
// Test server connection
async function testConnection() {
    try {
        const response = await fetch('http://localhost:8000/health');
        const data = await response.json();
        console.log('Server status:', data.status);
        return true;
    } catch (error) {
        console.error('Connection failed:', error);
        return false;
    }
}
```

### 2. Dashboard Data Fetching

```javascript
// Get dashboard data
async function getDashboardData() {
    try {
        const response = await fetch('http://localhost:8000/web/dashboard');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Failed to fetch dashboard:', error);
        throw error;
    }
}

// Usage
getDashboardData().then(dashboard => {
    console.log('Solar insights:', dashboard.solar_insights);
    console.log('Appliance health:', dashboard.appliance_health);
    console.log('Bill forecast:', dashboard.bill_forecast);
    console.log('Carbon footprint:', dashboard.carbon_footprint);
});
```

### 3. User Preferences Management

```javascript
// Update user preferences
async function updatePreferences(preferences) {
    try {
        const response = await fetch('http://localhost:8000/web/preferences', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(preferences)
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Failed to update preferences:', error);
        throw error;
    }
}

// Usage
const userPrefs = {
    location: 'New York, NY',
    energy_company: 'ConEdison',
    monthly_budget: 150.0,
    solar_interest: true,
    appliance_monitoring: true,
    carbon_tracking: true
};

updatePreferences(userPrefs).then(result => {
    console.log('Preferences updated:', result);
});
```

### 4. Data Export

```javascript
// Export user data
async function exportData(format = 'json', dataTypes = ['all']) {
    try {
        const response = await fetch('http://localhost:8000/web/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                format: format,
                data_type: dataTypes.join(','),
                date_range: '30d'
            })
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Failed to export data:', error);
        throw error;
    }
}

// Usage
exportData('json', ['analytics', 'appliances']).then(exportInfo => {
    console.log('Export ready:', exportInfo.download_url);
});
```

## 🎯 React Integration Example

```jsx
import React, { useState, useEffect } from 'react';

const Dashboard = () => {
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:8000/web/dashboard');
            const data = await response.json();
            setDashboardData(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div>Loading dashboard...</div>;
    if (error) return <div>Error: {error}</div>;
    if (!dashboardData) return <div>No data available</div>;

    return (
        <div className="dashboard">
            <h1>Energy Management Dashboard</h1>
            
            {/* Solar Insights */}
            <div className="card">
                <h2>☀️ Solar Insights</h2>
                <p>Potential Savings: {dashboardData.solar_insights.potential_savings}</p>
                <p>ROI: {dashboardData.solar_insights.roi_percentage}</p>
                <p>Payback Period: {dashboardData.solar_insights.payback_period}</p>
            </div>

            {/* Appliance Health */}
            <div className="card">
                <h2>⚡ Appliance Health</h2>
                <p>Total Appliances: {dashboardData.appliance_health.total_appliances}</p>
                <p>Healthy: {dashboardData.appliance_health.healthy}</p>
                <p>Warning: {dashboardData.appliance_health.warning}</p>
                <p>Critical: {dashboardData.appliance_health.critical}</p>
            </div>

            {/* Bill Forecast */}
            <div className="card">
                <h2>💰 Bill Forecast</h2>
                <p>Next Month: {dashboardData.bill_forecast.next_month}</p>
                <p>Trend: {dashboardData.bill_forecast.trend}</p>
                <p>Seasonal Factor: {dashboardData.bill_forecast.seasonal_factor}</p>
            </div>

            {/* Carbon Footprint */}
            <div className="card">
                <h2>🌍 Carbon Footprint</h2>
                <p>Current Month: {dashboardData.carbon_footprint.current_month}</p>
                <p>Trend: {dashboardData.carbon_footprint.trend}</p>
                <p>Offset Progress: {dashboardData.carbon_footprint.offset_progress}</p>
            </div>
        </div>
    );
};

export default Dashboard;
```

## 🎨 Vue.js Integration Example

```vue
<template>
    <div class="dashboard">
        <h1>Energy Management Dashboard</h1>
        
        <div v-if="loading" class="loading">Loading dashboard...</div>
        <div v-else-if="error" class="error">Error: {{ error }}</div>
        <div v-else-if="dashboardData" class="dashboard-content">
            <!-- Solar Insights -->
            <div class="card">
                <h2>☀️ Solar Insights</h2>
                <p>Potential Savings: {{ dashboardData.solar_insights.potential_savings }}</p>
                <p>ROI: {{ dashboardData.solar_insights.roi_percentage }}</p>
                <p>Payback Period: {{ dashboardData.solar_insights.payback_period }}</p>
            </div>

            <!-- Appliance Health -->
            <div class="card">
                <h2>⚡ Appliance Health</h2>
                <p>Total Appliances: {{ dashboardData.appliance_health.total_appliances }}</p>
                <p>Healthy: {{ dashboardData.appliance_health.healthy }}</p>
                <p>Warning: {{ dashboardData.appliance_health.warning }}</p>
                <p>Critical: {{ dashboardData.appliance_health.critical }}</p>
            </div>

            <!-- Bill Forecast -->
            <div class="card">
                <h2>💰 Bill Forecast</h2>
                <p>Next Month: {{ dashboardData.bill_forecast.next_month }}</p>
                <p>Trend: {{ dashboardData.bill_forecast.trend }}</p>
                <p>Seasonal Factor: {{ dashboardData.bill_forecast.seasonal_factor }}</p>
            </div>

            <!-- Carbon Footprint -->
            <div class="card">
                <h2>🌍 Carbon Footprint</h2>
                <p>Current Month: {{ dashboardData.carbon_footprint.current_month }}</p>
                <p>Trend: {{ dashboardData.carbon_footprint.trend }}</p>
                <p>Offset Progress: {{ dashboardData.carbon_footprint.offset_progress }}</p>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'Dashboard',
    data() {
        return {
            dashboardData: null,
            loading: true,
            error: null
        };
    },
    async mounted() {
        await this.fetchDashboardData();
    },
    methods: {
        async fetchDashboardData() {
            try {
                this.loading = true;
                const response = await fetch('http://localhost:8000/web/dashboard');
                const data = await response.json();
                this.dashboardData = data;
            } catch (err) {
                this.error = err.message;
            } finally {
                this.loading = false;
            }
        }
    }
};
</script>
```

## 🔒 CORS Configuration

The backend is configured with CORS middleware that allows all origins for development:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, restrict `allow_origins` to your specific frontend domain.

## 📊 Error Handling

The API returns structured error responses:

```javascript
// Error handling example
async function handleApiCall(endpoint) {
    try {
        const response = await fetch(`http://localhost:8000${endpoint}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API call failed for ${endpoint}:`, error);
        // Handle error in your UI
        throw error;
    }
}
```

## 🧪 Testing Your Integration

1. **Start the backend server**:
   ```bash
   python server/main.py
   ```

2. **Open the test page**:
   - Open `server/frontend_test.html` in your browser
   - This will test all endpoints and show responses

3. **Check the API docs**:
   - Visit `http://localhost:8000/docs`
   - Test endpoints interactively

4. **Monitor server logs**:
   - Watch the terminal for any errors
   - Check for successful endpoint calls

## 🚀 Next Steps

1. **Test basic connectivity** with the health check endpoint
2. **Fetch dashboard data** to display in your UI
3. **Implement user preferences** for customization
4. **Add data export functionality** for user convenience
5. **Integrate with energy management systems** for full functionality

## 📞 Support

If you encounter issues:

1. Check the server logs for error messages
2. Verify the server is running on port 8000
3. Test endpoints using the interactive test page
4. Check the API documentation at `/docs`
5. Ensure CORS is properly configured for your frontend domain

---

**Happy coding! 🎉** Your frontend should now be able to connect to the Smart Energy Management System backend.
