#!/usr/bin/env python3
"""
Test script for the server setup
Verifies that all components can be imported and basic functionality works
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_server_imports():
    """Test that all server components can be imported"""
    print("🧪 Testing Server Component Imports...")
    
    try:
        from server.main import app
        print("✅ Main server app imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import main server app: {e}")
        return False
    
    try:
        from server.web_routes import web_router
        print("✅ Web routes imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import web routes: {e}")
        return False
    
    try:
        from server.data_service import data_service
        print("✅ Data service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import data service: {e}")
        return False
    
    return True

def test_data_service():
    """Test data service functionality"""
    print("\n🧪 Testing Data Service...")
    
    try:
        from server.data_service import data_service
        
        # Test dashboard data
        dashboard = data_service.get_unified_dashboard_data()
        print(f"✅ Dashboard data generated: {len(dashboard)} sections")
        
        # Test user analytics
        analytics = data_service.get_user_analytics("test_user", "30d")
        print(f"✅ User analytics generated: {len(analytics)} metrics")
        
        # Test data export
        export = data_service.export_user_data("test_user", "json", ["analytics"])
        print(f"✅ Data export generated: {export['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data service test failed: {e}")
        return False

def test_system_integration():
    """Test integration with main systems"""
    print("\n🧪 Testing System Integration...")
    
    systems = [
        "appliance_health_router",
        "solar_calculator_router", 
        "smart_automated_router",
        "bill_simulation_router",
        "carbon_tracker_router"
    ]
    
    active_systems = 0
    for system in systems:
        try:
            if system == "appliance_health_router":
                from appliance_health_router import appliance_health_router
            elif system == "solar_calculator_router":
                from solar_calculator_router import solar_calculator_router
            elif system == "smart_automated_router":
                from smart_automated_router import smart_automated_router
            elif system == "bill_simulation_router":
                from bill_simulation_router import bill_simulation_router
            elif system == "carbon_tracker_router":
                from carbon_tracker_router import carbon_tracker_router
            
            print(f"✅ {system} imported successfully")
            active_systems += 1
            
        except ImportError as e:
            print(f"⚠️  {system} not available: {e}")
    
    print(f"\n📊 System Status: {active_systems}/{len(systems)} systems active")
    return active_systems > 0

def main():
    """Run all tests"""
    print("🚀 Smart Energy Management System - Server Test Suite")
    print("=" * 60)
    
    # Test imports
    if not test_server_imports():
        print("\n❌ Server import tests failed")
        return False
    
    # Test data service
    if not test_data_service():
        print("\n❌ Data service tests failed")
        return False
    
    # Test system integration
    if not test_system_integration():
        print("\n⚠️  System integration tests failed (some systems may be optional)")
    
    print("\n🎉 Server test suite completed!")
    print("\n📋 Next steps:")
    print("1. Start the server: python server/main.py")
    print("2. Access API docs: http://localhost:8000/docs")
    print("3. Test endpoints: http://localhost:8000/web/dashboard")
    
    return True

if __name__ == "__main__":
    main()
