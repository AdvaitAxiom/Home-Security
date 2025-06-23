#!/usr/bin/env python
# Benchmark tool for Smart Home Anomaly Detection System

import os
import sys
import argparse
import time
import json
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import requests
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for plots
sns.set_style("whitegrid")
plt.rcParams.update({'font.size': 12})

# Ensure the output directory exists
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

# Generate random test data
def generate_test_data(num_samples):
    data = []
    timestamp = datetime.now() - timedelta(hours=num_samples)
    
    for i in range(num_samples):
        pattern_id = random.choices([0, 1, 2, 3], weights=[0.7, 0.1, 0.1, 0.1])[0]
        
        if pattern_id == 0:  # Normal
            amplitude = random.uniform(0.1, 0.9)
        elif pattern_id == 1:  # Anomaly type 1
            amplitude = random.uniform(1.5, 2.5)
        elif pattern_id == 2:  # Anomaly type 2
            amplitude = random.uniform(0.02, 0.05)
        else:  # Anomaly type 3
            amplitude = random.uniform(3.0, 5.0)
        
        data.append({
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "amplitude": round(amplitude, 2),
            "pattern_id": pattern_id
        })
        
        timestamp += timedelta(minutes=1)
    
    return data

# Benchmark API endpoints
def benchmark_api(base_url, num_requests, endpoint, payload=None, method="GET"):
    print(f"Benchmarking {endpoint} endpoint...")
    
    url = f"{base_url}{endpoint}"
    response_times = []
    status_codes = []
    errors = 0
    
    for i in range(num_requests):
        try:
            start_time = time.time()
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=payload, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            response_times.append(response_time)
            status_codes.append(response.status_code)
            
            if response.status_code != 200:
                errors += 1
                print(f"  Request {i+1}/{num_requests} failed with status code {response.status_code}")
            elif i % 10 == 0 and i > 0:
                print(f"  Completed {i}/{num_requests} requests")
                
        except Exception as e:
            errors += 1
            print(f"  Request {i+1}/{num_requests} failed with error: {str(e)}")
    
    # Calculate statistics
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        p95_response_time = np.percentile(response_times, 95)
        success_rate = ((num_requests - errors) / num_requests) * 100
        
        result = {
            "endpoint": endpoint,
            "method": method,
            "requests": num_requests,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "min_response_time": min_response_time,
            "max_response_time": max_response_time,
            "p95_response_time": p95_response_time,
            "errors": errors
        }
        
        print(f"  Results for {endpoint}:")
        print(f"    Success Rate: {success_rate:.2f}%")
        print(f"    Avg Response Time: {avg_response_time:.2f} ms")
        print(f"    Min Response Time: {min_response_time:.2f} ms")
        print(f"    Max Response Time: {max_response_time:.2f} ms")
        print(f"    95th Percentile: {p95_response_time:.2f} ms")
        print(f"    Errors: {errors}")
        
        return result, response_times
    else:
        print(f"  No successful requests for {endpoint}")
        return None, []

# Plot response time distribution
def plot_response_times(results, output_dir):
    plt.figure(figsize=(12, 6))
    
    for endpoint, times in results.items():
        if times:
            sns.kdeplot(times, label=endpoint, fill=True, alpha=0.3)
    
    plt.title('API Response Time Distribution')
    plt.xlabel('Response Time (ms)')
    plt.ylabel('Density')
    plt.legend()
    plt.tight_layout()
    
    # Save the plot
    output_file = os.path.join(output_dir, 'response_time_distribution.png')
    plt.savefig(output_file, dpi=300)
    print(f"Saved response time distribution plot to {output_file}")
    plt.close()

# Plot response time comparison
def plot_response_time_comparison(summary, output_dir):
    plt.figure(figsize=(10, 6))
    
    endpoints = []
    avg_times = []
    p95_times = []
    
    for result in summary:
        if result:
            endpoints.append(result["endpoint"])
            avg_times.append(result["avg_response_time"])
            p95_times.append(result["p95_response_time"])
    
    x = range(len(endpoints))
    width = 0.35
    
    plt.bar([i - width/2 for i in x], avg_times, width, label='Average')
    plt.bar([i + width/2 for i in x], p95_times, width, label='95th Percentile')
    
    plt.xlabel('Endpoint')
    plt.ylabel('Response Time (ms)')
    plt.title('API Response Time Comparison')
    plt.xticks(x, endpoints)
    plt.legend()
    plt.tight_layout()
    
    # Save the plot
    output_file = os.path.join(output_dir, 'response_time_comparison.png')
    plt.savefig(output_file, dpi=300)
    print(f"Saved response time comparison plot to {output_file}")
    plt.close()

# Generate a benchmark report
def generate_report(summary, output_dir):
    report = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": summary
    }
    
    # Save the report
    output_file = os.path.join(output_dir, 'benchmark_report.json')
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Saved benchmark report to {output_file}")
    
    # Generate a text version of the report
    output_file_txt = os.path.join(output_dir, 'benchmark_report.txt')
    with open(output_file_txt, 'w') as f:
        f.write(f"API Benchmark Report\n")
        f.write(f"Generated at: {report['generated_at']}\n\n")
        
        f.write(f"Summary:\n")
        for result in summary:
            if result:
                f.write(f"\nEndpoint: {result['endpoint']} ({result['method']})\n")
                f.write(f"  Requests: {result['requests']}\n")
                f.write(f"  Success Rate: {result['success_rate']:.2f}%\n")
                f.write(f"  Avg Response Time: {result['avg_response_time']:.2f} ms\n")
                f.write(f"  Min Response Time: {result['min_response_time']:.2f} ms\n")
                f.write(f"  Max Response Time: {result['max_response_time']:.2f} ms\n")
                f.write(f"  95th Percentile: {result['p95_response_time']:.2f} ms\n")
                f.write(f"  Errors: {result['errors']}\n")
    
    print(f"Saved text report to {output_file_txt}")

def main():
    parser = argparse.ArgumentParser(description='Benchmark tool for Smart Home Anomaly Detection System')
    parser.add_argument('--url', type=str, default='http://localhost:5000', help='Base URL of the API server')
    parser.add_argument('--requests', type=int, default=100, help='Number of requests per endpoint')
    parser.add_argument('--output-dir', type=str, default='benchmark_results', help='Output directory for results')
    parser.add_argument('--endpoints', nargs='+', default=['/', '/status', '/api', '/analyze'], help='Endpoints to benchmark')
    parser.add_argument('--simulate', action='store_true', help='Include simulation endpoint in benchmark')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # Ensure output directory exists
    ensure_dir(args.output_dir)
    
    print(f"Smart Home Anomaly Detection System - Benchmark")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Server URL: {args.url}")
    print(f"Requests per endpoint: {args.requests}")
    print("-" * 60)
    
    # Prepare for benchmarking
    summary = []
    response_times = {}
    
    # Benchmark each endpoint
    for endpoint in args.endpoints:
        result, times = benchmark_api(args.url, args.requests, endpoint)
        if result:
            summary.append(result)
            response_times[endpoint] = times
        print("-" * 60)
    
    # Benchmark simulation endpoint if requested
    if args.simulate:
        # Generate test data for simulation
        test_data = generate_test_data(1)[0]  # Just one sample
        result, times = benchmark_api(args.url, args.requests, '/simulate', payload=test_data, method="POST")
        if result:
            summary.append(result)
            response_times["/simulate"] = times
        print("-" * 60)
    
    # Generate visualizations and report
    if summary:
        plot_response_times(response_times, args.output_dir)
        plot_response_time_comparison(summary, args.output_dir)
        generate_report(summary, args.output_dir)
        print(f"Benchmark completed! Results saved to {args.output_dir}")
    else:
        print("No successful benchmark results to report.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())