# 🚀 Smart Energy Management System - Server Backend

This folder contains the backend server implementation for the Smart Energy Management System web application. The server provides a comprehensive API that integrates all the energy management systems and communicates with the frontend.

## 📁 Folder Structure

```
server/
├── __init__.py              # Package initialization
├── main.py                  # Main FastAPI application
├── web_routes.py            # Web-specific API routes
├── data_service.py          # Data aggregation service
├── test_server.py           # Server testing script
└── README.md                # This file
```

## 🏗️ Architecture

### Main Application (`main.py`)
- **FastAPI Application**: Main server with CORS middleware
- **System Integration**: Loads all energy management system routers
- **Status Tracking**: Monitors system health and availability
- **Error Handling**: Comprehensive error handling for 404 and 500 errors

### Web Routes (`web_routes.py`)
- **Dashboard API**: Unified dashboard data endpoint
- **User Preferences**: User settings and configuration management
- **Data Export**: Export functionality for various data formats
- **Integration Status**: Real-time system status monitoring
- **Frontend Configuration**: Feature flags and UI configuration

### Data Service (`data_service.py`)
- **Data Aggregation**: Combines data from all systems
- **Caching**: Intelligent caching for performance optimization
- **Analytics**: User-specific analytics and insights
- **Export Services**: Data export in multiple formats

## 🚀 Quick Start

### 1. Start the Server
```bash
# From the root directory
python server/main.py
```

### 2. Access the API
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **System Status**: http://localhost:8000/status

### 3. Test the Server
```bash
# Run the test suite
python server/test_server.py
```

## 📡 API Endpoints

### Core Endpoints
- `GET /` - Root endpoint with system overview
- `GET /health` - Health check for load balancers
- `GET /status` - Detailed system status

### Web Application Endpoints
- `GET /web/dashboard` - Unified dashboard data
- `POST /web/preferences` - Update user preferences
- `POST /web/export` - Export data in various formats
- `GET /web/integration-status` - System integration status
- `GET /web/config` - Frontend configuration
- `GET /web/health` - Web routes health check

### Energy Management System Endpoints
- `GET /appliance-health/*` - Appliance health prediction
- `GET /solar-calculator/*` - Solar feasibility & ROI calculator
- `GET /smart-analysis/*` - Automated smart analysis
- `GET /bill-simulation/*` - Bill simulation & forecasting
- `GET /carbon-tracker/*` - Carbon footprint tracking

## 🔧 Configuration

### CORS Settings
The server is configured with CORS middleware for frontend communication:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### System Loading
The server automatically loads all available energy management systems:
- Appliance Health Prediction
- Solar Feasibility Calculator
- Smart Automated Analysis
- Bill Simulation Engine
- Carbon Footprint Tracker

## 📊 Data Flow

```
Frontend Request → Web Routes → Data Service → System Routers → Response
     ↓              ↓            ↓            ↓
  Dashboard    User Prefs   Aggregation   ML Models
  Analytics    Settings     Caching       Calculations
  Export       Config       Analytics     Reports
```

## 🧪 Testing

### Test Server Setup
```bash
python server/test_server.py
```

The test suite verifies:
- ✅ Server component imports
- ✅ Data service functionality
- ✅ System integration status
- ✅ API endpoint availability

### Manual Testing
1. Start the server: `python server/main.py`
2. Open browser: http://localhost:8000/docs
3. Test endpoints using the interactive Swagger UI

## 🔍 Monitoring

### Health Checks
- **Overall Health**: `/health` - Basic health status
- **System Status**: `/status` - Detailed system information
- **Integration Status**: `/web/integration-status` - System availability

### Logging
The server provides detailed logging for:
- System loading status
- Router integration success/failure
- Error handling and debugging

## 🚨 Error Handling

### HTTP Status Codes
- `200` - Success
- `404` - Endpoint not found
- `500` - Internal server error

### Error Responses
All errors return structured JSON responses with:
- Error type and message
- Timestamp
- Available endpoints (for 404 errors)

## 🔮 Future Enhancements

### Planned Features
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] User authentication and authorization
- [ ] Real-time WebSocket connections
- [ ] Advanced caching with Redis
- [ ] Rate limiting and API quotas
- [ ] Comprehensive logging and monitoring
- [ ] Docker containerization
- [ ] Kubernetes deployment support

### Integration Possibilities
- [ ] Smart home device APIs (Philips Hue, Nest, etc.)
- [ ] Utility company APIs for real-time data
- [ ] Weather service integration
- [ ] IoT sensor data ingestion
- [ ] Machine learning model serving

## 📚 Dependencies

### Core Dependencies
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `pandas` - Data manipulation
- `numpy` - Numerical computing

### Optional Dependencies
- `scikit-learn` - Machine learning models
- `requests` - HTTP client
- `python-dotenv` - Environment variables

## 🆘 Troubleshooting

### Common Issues

#### Import Errors
If you see import errors for energy management systems:
```bash
# Check if all required files exist
ls -la *.py

# Verify Python path
python -c "import sys; print(sys.path)"
```

#### Port Already in Use
```bash
# Check what's using port 8000
netstat -an | grep 8000

# Kill the process or use a different port
python server/main.py --port 8001
```

#### CORS Issues
If the frontend can't connect:
1. Verify CORS settings in `main.py`
2. Check frontend origin configuration
3. Ensure proper headers are sent

### Getting Help
1. Check the logs for error messages
2. Run the test suite: `python server/test_server.py`
3. Verify all dependencies are installed
4. Check file permissions and paths

## 📄 License

This server implementation is part of the Smart Energy Management System project.

---

**Ready to get started?** Run `python server/main.py` and visit http://localhost:8000/docs to explore the API!
