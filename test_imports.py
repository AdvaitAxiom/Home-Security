#!/usr/bin/env python
# Test script to verify imports

import sys
import os

print("Python version:", sys.version)
print("Testing imports...")

try:
    import flask
    print(f"Flask version: {flask.__version__}")
    
    import werkzeug
    print(f"Werkzeug version: {werkzeug.__version__}")
    
    # Test the specific import that was failing
    from werkzeug.urls import url_quote
    print("Successfully imported url_quote from werkzeug.urls")
    
    # Try importing the app module
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'server')))
    import app
    print("Successfully imported app module")
    
    print("\nAll imports successful!")
    print("You can now run the server using run_server.ps1 or run_server.sh")
    
 except Exception as e:
    print(f"\nError: {e}")
    print("\nPlease run update_dependencies.ps1 (Windows) or update_dependencies.sh (Linux/macOS) to fix dependency issues.")