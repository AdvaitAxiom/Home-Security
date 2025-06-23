#!/usr/bin/env python
# System check script for Smart Home Anomaly Detection System

import os
import sys
import importlib.util
import platform
import json
from datetime import datetime

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Check if running on Windows and adjust colors if needed
if platform.system() == 'Windows':
    # Windows terminal might not support ANSI colors
    try:
        import colorama
        colorama.init()
    except ImportError:
        # If colorama is not available, disable colors
        for attr in dir(Colors):
            if not attr.startswith('__'):
                setattr(Colors, attr, '')

def print_status(message, status, details=None):
    """Print a status message with color coding"""
    if status == 'OK':
        status_str = f"{Colors.OKGREEN}[OK]{Colors.ENDC}"
    elif status == 'WARNING':
        status_str = f"{Colors.WARNING}[WARNING]{Colors.ENDC}"
    elif status == 'ERROR':
        status_str = f"{Colors.FAIL}[ERROR]{Colors.ENDC}"
    else:
        status_str = f"[{status}]"
    
    print(f"{status_str} {message}")
    if details:
        print(f"     {details}")

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print_status(f"Python version: {sys.version.split()[0]}", "OK")
        return True
    else:
        print_status(f"Python version: {sys.version.split()[0]}", "ERROR", 
                    "Python 3.7 or higher is required")
        return False

def check_virtual_env():
    """Check if running in a virtual environment"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_status("Virtual environment", "OK", f"Active: {sys.prefix}")
        return True
    else:
        print_status("Virtual environment", "WARNING", 
                    "Not activated. Run 'venv\Scripts\activate' (Windows) or 'source venv/bin/activate' (Linux/macOS)")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'werkzeug',
        'numpy',
        'pandas',
        'scikit-learn',
        'requests'
    ]
    
    all_installed = True
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is None:
            print_status(f"Package: {package}", "ERROR", "Not installed")
            all_installed = False
        else:
            try:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', 'unknown')
                print_status(f"Package: {package}", "OK", f"Version: {version}")
            except ImportError:
                print_status(f"Package: {package}", "ERROR", "Installed but cannot be imported")
                all_installed = False
    
    return all_installed

def check_flask_werkzeug_compatibility():
    """Check if Flask and Werkzeug versions are compatible"""
    try:
        import flask
        import werkzeug
        
        flask_version = getattr(flask, '__version__', 'unknown')
        werkzeug_version = getattr(werkzeug, '__version__', 'unknown')
        
        # Check for the specific url_quote import
        try:
            from werkzeug.urls import url_quote
            print_status("Flask-Werkzeug compatibility", "OK", 
                        f"Flask {flask_version}, Werkzeug {werkzeug_version}")
            return True
        except ImportError:
            print_status("Flask-Werkzeug compatibility", "ERROR", 
                        f"Flask {flask_version}, Werkzeug {werkzeug_version} - url_quote import fails")
            return False
    except ImportError as e:
        print_status("Flask-Werkzeug compatibility", "ERROR", str(e))
        return False

def check_model_file():
    """Check if the model file exists"""
    model_path = os.path.join('model', 'sound_classifier.pkl')
    if os.path.exists(model_path):
        size = os.path.getsize(model_path) / 1024  # KB
        modified = datetime.fromtimestamp(os.path.getmtime(model_path)).strftime('%Y-%m-%d %H:%M:%S')
        print_status("Model file", "OK", f"Size: {size:.2f} KB, Last modified: {modified}")
        return True
    else:
        print_status("Model file", "ERROR", 
                    "Not found. Run setup script or generate_model.py to create it")
        return False

def check_directory_structure():
    """Check if required directories exist"""
    required_dirs = [
        'logs',
        'model',
        'samples',
        'server',
        'server/logs',
        'server/static',
        'server/templates'
    ]
    
    all_exist = True
    for directory in required_dirs:
        if os.path.exists(directory) and os.path.isdir(directory):
            print_status(f"Directory: {directory}", "OK")
        else:
            print_status(f"Directory: {directory}", "ERROR", "Not found")
            all_exist = False
    
    return all_exist

def check_sample_data():
    """Check if sample data files exist"""
    sample_files = [
        'samples/normal_samples.csv',
        'samples/glass_break_samples.csv',
        'samples/fire_crackle_samples.csv',
        'samples/human_scream_samples.csv',
        'samples/dog_bark_samples.csv'
    ]
    
    all_exist = True
    for file in sample_files:
        if os.path.exists(file) and os.path.isfile(file):
            size = os.path.getsize(file) / 1024  # KB
            print_status(f"Sample file: {file}", "OK", f"Size: {size:.2f} KB")
        else:
            print_status(f"Sample file: {file}", "ERROR", "Not found")
            all_exist = False
    
    return all_exist

def check_config_file():
    """Check if config file exists and has required settings"""
    config_path = os.path.join('server', 'config.py')
    if not os.path.exists(config_path):
        print_status("Config file", "ERROR", "Not found")
        return False
    
    try:
        sys.path.append(os.path.abspath('server'))
        import config
        
        required_settings = [
            'THINGSPEAK_CHANNEL_ID',
            'THINGSPEAK_READ_API_KEY',
            'SERVER_HOST',
            'SERVER_PORT',
            'MODEL_PATH'
        ]
        
        missing_settings = []
        for setting in required_settings:
            if not hasattr(config, setting):
                missing_settings.append(setting)
        
        if missing_settings:
            print_status("Config file", "WARNING", 
                        f"Missing settings: {', '.join(missing_settings)}")
            return False
        else:
            print_status("Config file", "OK", "All required settings present")
            return True
    except Exception as e:
        print_status("Config file", "ERROR", f"Error importing: {str(e)}")
        return False

def main():
    """Run all checks and print summary"""
    print(f"{Colors.HEADER}{Colors.BOLD}Smart Home Anomaly Detection System - System Check{Colors.ENDC}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"System: {platform.system()} {platform.release()}")
    print("-" * 60)
    
    checks = [
        ("Python version", check_python_version()),
        ("Virtual environment", check_virtual_env()),
        ("Dependencies", check_dependencies()),
        ("Flask-Werkzeug compatibility", check_flask_werkzeug_compatibility()),
        ("Model file", check_model_file()),
        ("Directory structure", check_directory_structure()),
        ("Sample data", check_sample_data()),
        ("Configuration", check_config_file())
    ]
    
    print("\n" + "-" * 60)
    print(f"{Colors.BOLD}Summary:{Colors.ENDC}")
    
    all_passed = True
    for name, result in checks:
        if result:
            status = f"{Colors.OKGREEN}PASS{Colors.ENDC}"
        else:
            status = f"{Colors.FAIL}FAIL{Colors.ENDC}"
            all_passed = False
        print(f"{status} - {name}")
    
    print("-" * 60)
    if all_passed:
        print(f"{Colors.OKGREEN}{Colors.BOLD}All checks passed! The system is ready to run.{Colors.ENDC}")
        print("Run the server with: .\run_server.ps1 (Windows) or ./run_server.sh (Linux/macOS)")
    else:
        print(f"{Colors.WARNING}{Colors.BOLD}Some checks failed. Please fix the issues before running the system.{Colors.ENDC}")
        print("For troubleshooting, refer to the README.md file.")

if __name__ == "__main__":
    main()