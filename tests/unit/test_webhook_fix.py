#!/usr/bin/env python3
"""
Test script to verify webhook functionality in generated mock servers.
This script will generate a new mock server and test the webhook registration.
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mockloop_mcp.parser import load_api_specification
from mockloop_mcp.generator import generate_mock_api

async def test_webhook_functionality():
    """Test webhook functionality by generating a mock server and testing webhook registration."""
    
    print("🧪 Testing webhook functionality...")
    
    # Use the existing test API spec
    spec_path = "test_api_spec.json"
    
    try:
        # Load the API specification
        print(f"📖 Loading API specification from {spec_path}")
        spec_data = load_api_specification(spec_path)
        
        # Generate a mock server with webhooks enabled
        print("🏗️  Generating mock server with webhooks enabled...")
        mock_server_name = f"webhook_test_{int(time.time())}"
        generated_path = generate_mock_api(
            spec_data=spec_data,
            mock_server_name=mock_server_name,
            auth_enabled=True,
            webhooks_enabled=True,
            admin_ui_enabled=True,
            storage_enabled=True
        )
        
        print(f"✅ Mock server generated at: {generated_path}")
        
        # Check that the webhook handler was created
        webhook_handler_path = generated_path / "webhook_handler.py"
        if webhook_handler_path.exists():
            print("✅ webhook_handler.py was created")
        else:
            print("❌ webhook_handler.py was NOT created")
            return False
        
        # Check that the main.py contains webhook endpoints
        main_py_path = generated_path / "main.py"
        if main_py_path.exists():
            with open(main_py_path, 'r') as f:
                main_content = f.read()
                
            if "/admin/api/webhooks" in main_content:
                print("✅ Webhook API endpoints found in main.py")
            else:
                print("❌ Webhook API endpoints NOT found in main.py")
                return False
                
            if "webhook_data: dict = Body(...)" in main_content:
                print("✅ Fixed webhook endpoint signature found")
            else:
                print("❌ Fixed webhook endpoint signature NOT found")
                return False
        else:
            print("❌ main.py was NOT created")
            return False
        
        # Check that the admin UI template contains webhook JavaScript
        admin_template_path = generated_path / "templates" / "admin.html"
        if admin_template_path.exists():
            with open(admin_template_path, 'r') as f:
                admin_content = f.read()
                
            if "webhook-form" in admin_content:
                print("✅ Webhook form found in admin UI")
            else:
                print("❌ Webhook form NOT found in admin UI")
                return False
                
            if "loadWebhooks" in admin_content:
                print("✅ Webhook JavaScript functions found in admin UI")
            else:
                print("❌ Webhook JavaScript functions NOT found in admin UI")
                return False
        else:
            print("❌ Admin UI template was NOT created")
            return False
        
        print("\n🎉 All webhook functionality tests passed!")
        print(f"📁 Generated mock server location: {generated_path}")
        print("\n🚀 To test the webhook functionality:")
        print(f"   1. cd {generated_path}")
        print("   2. pip install -r requirements_mock.txt")
        print("   3. python main.py")
        print("   4. Open http://localhost:8000/admin")
        print("   5. Go to the Webhooks tab and try registering a webhook")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during webhook test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_webhook_functionality())
    sys.exit(0 if success else 1)