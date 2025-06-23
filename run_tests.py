#!/usr/bin/env python
# Test runner for Smart Home Anomaly Detection System

import os
import sys
import argparse
import subprocess
import time
import json
from datetime import datetime

# Ensure the output directory exists
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

# Run a single test module
def run_test(test_module, verbose=False):
    print(f"Running test: {test_module}")
    
    command = [sys.executable, "-m", "pytest", test_module]
    if verbose:
        command.append("-v")
    
    start_time = time.time()
    result = subprocess.run(command, capture_output=True, text=True)
    end_time = time.time()
    
    duration = end_time - start_time
    success = result.returncode == 0
    
    print(f"  {'✓ Passed' if success else '✗ Failed'} in {duration:.2f}s")
    
    if not success and verbose:
        print("\nTest output:")
        print(result.stdout)
        print("\nTest errors:")
        print(result.stderr)
    
    return {
        "module": test_module,
        "success": success,
        "duration": duration,
        "returncode": result.returncode,
        "output": result.stdout,
        "errors": result.stderr
    }

# Run all tests in the tests directory
def run_all_tests(tests_dir="tests", verbose=False):
    if not os.path.exists(tests_dir):
        print(f"Tests directory not found: {tests_dir}")
        return []
    
    test_files = []
    for root, dirs, files in os.walk(tests_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_files.append(os.path.join(root, file))
    
    if not test_files:
        print(f"No test files found in {tests_dir}")
        return []
    
    print(f"Found {len(test_files)} test files")
    
    results = []
    for test_file in sorted(test_files):
        results.append(run_test(test_file, verbose))
    
    return results

# Generate a test report
def generate_report(results, output_dir):
    if not results:
        print("No test results to report")
        return
    
    # Calculate summary statistics
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["success"])
    failed_tests = total_tests - passed_tests
    total_duration = sum(r["duration"] for r in results)
    
    report = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "total_duration": total_duration
        },
        "results": results
    }
    
    # Save the report
    output_file = os.path.join(output_dir, 'test_report.json')
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Saved test report to {output_file}")
    
    # Generate a text version of the report
    output_file_txt = os.path.join(output_dir, 'test_report.txt')
    with open(output_file_txt, 'w') as f:
        f.write(f"Test Report\n")
        f.write(f"Generated at: {report['generated_at']}\n\n")
        
        f.write(f"Summary:\n")
        f.write(f"  Total Tests: {report['summary']['total_tests']}\n")
        f.write(f"  Passed: {report['summary']['passed_tests']}\n")
        f.write(f"  Failed: {report['summary']['failed_tests']}\n")
        f.write(f"  Success Rate: {report['summary']['success_rate']:.2f}%\n")
        f.write(f"  Total Duration: {report['summary']['total_duration']:.2f}s\n\n")
        
        f.write(f"Test Results:\n")
        for result in results:
            status = "PASSED" if result["success"] else "FAILED"
            f.write(f"  {result['module']}: {status} ({result['duration']:.2f}s)\n")
        
        f.write(f"\nFailed Tests:\n")
        for result in results:
            if not result["success"]:
                f.write(f"\n{result['module']}:\n")
                f.write(f"  Return Code: {result['returncode']}\n")
                f.write(f"  Errors:\n")
                for line in result["errors"].split("\n"):
                    f.write(f"    {line}\n")
    
    print(f"Saved text report to {output_file_txt}")
    
    # Print summary to console
    print(f"\nTest Summary:")
    print(f"  Total Tests: {report['summary']['total_tests']}")
    print(f"  Passed: {report['summary']['passed_tests']}")
    print(f"  Failed: {report['summary']['failed_tests']}")
    print(f"  Success Rate: {report['summary']['success_rate']:.2f}%")
    print(f"  Total Duration: {report['summary']['total_duration']:.2f}s")

# Create a basic test file if none exists
def create_sample_tests(tests_dir="tests"):
    ensure_dir(tests_dir)
    
    # Create a basic test for the server
    server_test_file = os.path.join(tests_dir, "test_server.py")
    if not os.path.exists(server_test_file):
        with open(server_test_file, 'w') as f:
            f.write("""import os
import sys
import pytest

# Add the parent directory to the path so we can import the server modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Basic tests for the server

def test_server_imports():
    """Test that server modules can be imported"""
    try:
        from server import app
        assert True
    except ImportError as e:
        pytest.skip(f"Server import failed: {str(e)}")

def test_config_exists():
    """Test that the config file exists"""
    config_path = os.path.join('server', 'config.py')
    assert os.path.exists(config_path), f"Config file not found at {config_path}"

def test_model_exists():
    """Test that the model file exists"""
    model_path = os.path.join('model', 'sound_classifier.pkl')
    assert os.path.exists(model_path), f"Model file not found at {model_path}"

def test_sample_data_exists():
    """Test that sample data exists"""
    samples_dir = 'samples'
    assert os.path.exists(samples_dir), f"Samples directory not found at {samples_dir}"
    
    # Check for at least one sample file
    sample_files = [f for f in os.listdir(samples_dir) if f.endswith('_samples.csv') or f.endswith('_samples.json')]
    assert len(sample_files) > 0, f"No sample files found in {samples_dir}"
""")
        print(f"Created sample test file: {server_test_file}")
    
    # Create a basic test for the model
    model_test_file = os.path.join(tests_dir, "test_model.py")
    if not os.path.exists(model_test_file):
        with open(model_test_file, 'w') as f:
            f.write("""import os
import sys
import pytest
import numpy as np

# Add the parent directory to the path so we can import the server modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Basic tests for the model

def test_model_loading():
    """Test that the model can be loaded"""
    try:
        import joblib
        model_path = os.path.join('model', 'sound_classifier.pkl')
        if not os.path.exists(model_path):
            pytest.skip(f"Model file not found at {model_path}")
        
        model = joblib.load(model_path)
        assert model is not None, "Model could not be loaded"
    except ImportError as e:
        pytest.skip(f"Joblib import failed: {str(e)}")
    except Exception as e:
        pytest.fail(f"Error loading model: {str(e)}")

def test_model_prediction():
    """Test that the model can make predictions"""
    try:
        import joblib
        model_path = os.path.join('model', 'sound_classifier.pkl')
        if not os.path.exists(model_path):
            pytest.skip(f"Model file not found at {model_path}")
        
        model = joblib.load(model_path)
        
        # Create a simple test input (adjust based on your model's expected input)
        test_input = np.array([[0.5]])  # Simple amplitude value
        
        # Try to make a prediction
        try:
            prediction = model.predict(test_input)
            assert prediction is not None, "Model prediction returned None"
        except Exception as e:
            pytest.fail(f"Error making prediction: {str(e)}")
    except ImportError as e:
        pytest.skip(f"Required import failed: {str(e)}")
    except Exception as e:
        pytest.skip(f"Error in test setup: {str(e)}")
""")
        print(f"Created sample test file: {model_test_file}")
    
    # Create a basic test for utilities
    utils_test_file = os.path.join(tests_dir, "test_utils.py")
    if not os.path.exists(utils_test_file):
        with open(utils_test_file, 'w') as f:
            f.write("""import os
import sys
import pytest
from datetime import datetime

# Add the parent directory to the path so we can import the server modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Basic utility tests

def test_directory_structure():
    """Test that the required directories exist"""
    required_dirs = ['server', 'model', 'samples', 'logs']
    for directory in required_dirs:
        assert os.path.exists(directory), f"Required directory not found: {directory}"

def test_log_directory_writable():
    """Test that the log directory is writable"""
    log_dir = os.path.join('server', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    test_file = os.path.join(log_dir, 'test_write.tmp')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        assert os.path.exists(test_file), "Failed to write to log directory"
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

def test_timestamp_parsing():
    """Test timestamp parsing functionality"""
    # Test a few timestamp formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y%m%d%H%M%S"
    ]
    
    test_time = datetime.now()
    for fmt in formats:
        time_str = test_time.strftime(fmt)
        try:
            parsed_time = datetime.strptime(time_str, fmt)
            assert parsed_time is not None, f"Failed to parse timestamp with format {fmt}"
        except ValueError as e:
            pytest.fail(f"Error parsing timestamp with format {fmt}: {str(e)}")
""")
        print(f"Created sample test file: {utils_test_file}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Test runner for Smart Home Anomaly Detection System')
    parser.add_argument('--tests-dir', type=str, default='tests', help='Directory containing test files')
    parser.add_argument('--output-dir', type=str, default='test_results', help='Output directory for test results')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--create-tests', action='store_true', help='Create sample test files if none exist')
    parser.add_argument('--test-file', type=str, help='Run a specific test file')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # Create sample tests if requested
    if args.create_tests:
        create_sample_tests(args.tests_dir)
    
    # Ensure output directory exists
    ensure_dir(args.output_dir)
    
    print(f"Smart Home Anomaly Detection System - Test Runner")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # Run tests
    if args.test_file:
        results = [run_test(args.test_file, args.verbose)]
    else:
        results = run_all_tests(args.tests_dir, args.verbose)
    
    # Generate report
    if results:
        generate_report(results, args.output_dir)
    else:
        print("No tests were run. Use --create-tests to create sample tests.")
    
    # Return non-zero exit code if any tests failed
    failed_tests = sum(1 for r in results if not r["success"])
    return 1 if failed_tests > 0 else 0

if __name__ == "__main__":
    sys.exit(main())