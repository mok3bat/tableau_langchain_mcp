#!/usr/bin/env python3
"""
Simple test script for the Tableau LangChain MCP Server
This version avoids accessing internal MCP server attributes
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path for importing
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported"""
    print("=== Import Test ===")
    
    imports_to_test = [
        ("mcp", "MCP framework"),
        ("mcp.server", "MCP server components"),
        ("mcp.server.stdio", "MCP stdio server"),
        ("mcp.types", "MCP types"),
        ("httpx", "HTTP client"),
    ]
    
    optional_imports = [
        ("langchain_tableau", "LangChain Tableau integration"),
        ("langchain_tableau.tools.simple_datasource_qa", "Tableau QA tool"),
        ("langchain_openai", "LangChain OpenAI integration"),
    ]
    
    all_core_ok = True
    all_optional_ok = True
    
    # Test core imports
    for module_name, description in imports_to_test:
        try:
            __import__(module_name)
            print(f"✓ {module_name}: {description}")
        except ImportError as e:
            print(f"✗ {module_name}: {description} - FAILED ({e})")
            all_core_ok = False
    
    # Test optional imports
    for module_name, description in optional_imports:
        try:
            __import__(module_name)
            print(f"✓ {module_name}: {description}")
        except ImportError as e:
            print(f"⚠ {module_name}: {description} - NOT AVAILABLE ({e})")
            all_optional_ok = False
    
    return all_core_ok, all_optional_ok

def test_server_creation():
    """Test that the server can be created"""
    print("\n=== Server Creation Test ===")
    
    try:
        from tableau_langchain_mcp.server import TableauMCPServer
        server = TableauMCPServer()
        print("✓ TableauMCPServer created successfully")
        
        # Test that server has expected attributes
        if hasattr(server, 'server'):
            print("✓ MCP server instance created")
        else:
            print("✗ MCP server instance not found")
            return False
            
        if hasattr(server, 'tableau_config'):
            print("✓ Tableau configuration loaded")
        else:
            print("✗ Tableau configuration not loaded")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Failed to create server: {str(e)}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n=== Configuration Test ===")
    
    # Load environment variables from .env file if it exists
    try:
        from dotenv import load_dotenv
        if os.path.exists('.env'):
            load_dotenv()
            print("✓ Loaded .env file")
        else:
            print("ℹ No .env file found")
    except ImportError:
        print("ℹ python-dotenv not available")
    
    try:
        from tableau_langchain_mcp.server import TableauMCPServer
        server = TableauMCPServer()
        config = server.tableau_config
        
        required_env_vars = [
            "TABLEAU_DOMAIN",
            "TABLEAU_JWT_CLIENT_ID", 
            "TABLEAU_JWT_SECRET_ID",
            "TABLEAU_JWT_SECRET",
            "TABLEAU_USER",
            "TABLEAU_DATASOURCE_LUID",
            "OPENAI_API_KEY"
        ]
        
        config_ok = True
        for var in required_env_vars:
            # Convert to config key
            config_key = var.lower().replace('tableau_', '').replace('openai_', 'openai_')
            value = config.get(config_key)
            
            if value:
                # Mask sensitive values
                if 'secret' in config_key or 'key' in config_key:
                    display = f"{'*' * 8}...{value[-4:] if len(value) > 4 else '***'}"
                else:
                    display = value
                print(f"✓ {var}: {display}")
            else:
                print(f"✗ {var}: Not set")
                config_ok = False
        
        return config_ok
        
    except Exception as e:
        print(f"✗ Configuration test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Tableau LangChain MCP Server - Simple Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test imports
    core_imports_ok, optional_imports_ok = test_imports()
    results['Core Imports'] = core_imports_ok
    results['Optional Imports'] = optional_imports_ok
    
    if not core_imports_ok:
        print("\n❌ Core imports failed. Install missing dependencies:")
        print("pip install mcp httpx")
        return False
    
    # Test server creation
    results['Server Creation'] = test_server_creation()
    
    # Test configuration
    results['Configuration'] = test_configuration()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    
    all_critical_passed = True
    for test_name, passed in results.items():
        if test_name == 'Optional Imports':
            status = "✅ OK" if passed else "⚠️  PARTIAL"
            if not passed:
                print(f"  {test_name}: {status} (langchain-tableau may need to be installed)")
        else:
            status = "✅ PASS" if passed else "❌ FAIL"
            if not passed and test_name != 'Configuration':
                all_critical_passed = False
        print(f"  {test_name}: {status}")
    
    if not results.get('Configuration', False):
        print(f"\n⚠️  Configuration incomplete but server structure is OK")
        print(f"   Set up your .env file with Tableau and OpenAI credentials to enable full functionality")
    
    if all_critical_passed:
        print(f"\n🎉 Core functionality tests passed!")
        if results.get('Optional Imports') and results.get('Configuration'):
            print(f"✨ All tests passed - your MCP server is ready!")
        else:
            if not results.get('Optional Imports'):
                print(f"📝 Next: Install langchain-tableau with: pip install langchain-tableau")
            if not results.get('Configuration'):
                print(f"📝 Next: Set up your .env file with credentials")
    else:
        print(f"\n❌ Some critical tests failed. Please fix the issues above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
