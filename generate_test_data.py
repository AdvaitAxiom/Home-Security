#!/usr/bin/env python
# Test data generator for Smart Home Anomaly Detection System

import os
import sys
import argparse
import random
import csv
import json
from datetime import datetime, timedelta

# Ensure the samples directory exists
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

# Generate random amplitude value based on pattern type
def generate_amplitude(pattern_id):
    base_amplitude = random.uniform(0.1, 0.9)
    
    if pattern_id == 0:  # Normal
        return round(base_amplitude, 2)
    elif pattern_id == 1:  # Anomaly type 1
        return round(base_amplitude * random.uniform(1.5, 2.5), 2)
    elif pattern_id == 2:  # Anomaly type 2
        return round(base_amplitude * random.uniform(0.2, 0.5), 2)
    elif pattern_id == 3:  # Anomaly type 3
        return round(base_amplitude * random.uniform(3.0, 5.0), 2)
    else:  # Unknown pattern
        return round(base_amplitude, 2)

# Generate a sequence of timestamps
def generate_timestamps(count, interval_seconds=60, start_time=None):
    if start_time is None:
        start_time = datetime.now() - timedelta(days=1)
    
    timestamps = []
    current_time = start_time
    
    for _ in range(count):
        timestamps.append(current_time.strftime("%Y-%m-%d %H:%M:%S"))
        current_time += timedelta(seconds=interval_seconds)
    
    return timestamps

# Generate test data for a specific pattern distribution
def generate_test_data(total_samples, normal_ratio=0.7, anomaly_ratios=None, output_file=None):
    if anomaly_ratios is None:
        # Default distribution of anomaly types
        anomaly_ratios = {1: 0.1, 2: 0.1, 3: 0.1}  # pattern_id: ratio
    
    # Calculate sample counts
    normal_count = int(total_samples * normal_ratio)
    anomaly_counts = {}
    for pattern_id, ratio in anomaly_ratios.items():
        anomaly_counts[pattern_id] = int(total_samples * ratio)
    
    # Adjust for rounding errors
    total_allocated = normal_count + sum(anomaly_counts.values())
    if total_allocated < total_samples:
        normal_count += (total_samples - total_allocated)
    
    # Generate timestamps
    timestamps = generate_timestamps(total_samples)
    
    # Create data with the specified distribution
    data = []
    
    # Add normal samples
    for i in range(normal_count):
        data.append({
            "timestamp": timestamps[i],
            "amplitude": generate_amplitude(0),
            "pattern_id": 0
        })
    
    # Add anomaly samples
    current_index = normal_count
    for pattern_id, count in anomaly_counts.items():
        for i in range(count):
            if current_index < len(timestamps):
                data.append({
                    "timestamp": timestamps[current_index],
                    "amplitude": generate_amplitude(pattern_id),
                    "pattern_id": pattern_id
                })
                current_index += 1
    
    # Shuffle the data to mix normal and anomaly samples
    random.shuffle(data)
    
    # Sort by timestamp
    data.sort(key=lambda x: x["timestamp"])
    
    return data

# Write data to CSV file
def write_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['timestamp', 'amplitude', 'pattern_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"Generated CSV file: {filename}")

# Write data to JSON file
def write_json(data, filename):
    with open(filename, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=2)
    print(f"Generated JSON file: {filename}")

# Generate a test event log
def generate_event_log(data, filename):
    events = []
    
    # Group consecutive anomalies of the same type
    current_event = None
    for entry in data:
        if entry["pattern_id"] > 0:  # This is an anomaly
            if current_event is None or current_event["pattern_id"] != entry["pattern_id"]:
                # Start a new event
                current_event = {
                    "start_time": entry["timestamp"],
                    "end_time": entry["timestamp"],
                    "pattern_id": entry["pattern_id"],
                    "confidence": round(random.uniform(0.7, 0.99), 2),
                    "amplitude": entry["amplitude"],
                    "recommendations": [
                        f"Check sensor {random.randint(1, 5)}",
                        f"Verify power supply",
                        f"Inspect for physical damage"
                    ]
                }
                events.append(current_event)
            else:
                # Update the end time of the current event
                current_event["end_time"] = entry["timestamp"]
                # Update amplitude if higher
                if entry["amplitude"] > current_event["amplitude"]:
                    current_event["amplitude"] = entry["amplitude"]
    
    # Write events to file
    with open(filename, 'w') as jsonfile:
        json.dump(events, jsonfile, indent=2)
    print(f"Generated event log: {filename}")

def main():
    parser = argparse.ArgumentParser(description='Generate test data for Smart Home Anomaly Detection System')
    parser.add_argument('--samples', type=int, default=100, help='Number of samples to generate (default: 100)')
    parser.add_argument('--normal-ratio', type=float, default=0.7, help='Ratio of normal samples (default: 0.7)')
    parser.add_argument('--anomaly1-ratio', type=float, default=0.1, help='Ratio of anomaly type 1 (default: 0.1)')
    parser.add_argument('--anomaly2-ratio', type=float, default=0.1, help='Ratio of anomaly type 2 (default: 0.1)')
    parser.add_argument('--anomaly3-ratio', type=float, default=0.1, help='Ratio of anomaly type 3 (default: 0.1)')
    parser.add_argument('--output-dir', type=str, default='samples', help='Output directory (default: samples)')
    parser.add_argument('--format', type=str, choices=['csv', 'json', 'both'], default='both', help='Output format (default: both)')
    parser.add_argument('--generate-events', action='store_true', help='Generate event log')
    
    args = parser.parse_args()
    
    # Validate ratios
    total_ratio = args.normal_ratio + args.anomaly1_ratio + args.anomaly2_ratio + args.anomaly3_ratio
    if abs(total_ratio - 1.0) > 0.01:
        print(f"Warning: The sum of ratios ({total_ratio}) is not 1.0. Adjusting normal ratio.")
        args.normal_ratio = 1.0 - (args.anomaly1_ratio + args.anomaly2_ratio + args.anomaly3_ratio)
        print(f"Adjusted normal ratio: {args.normal_ratio}")
    
    # Ensure output directory exists
    ensure_dir(args.output_dir)
    
    # Set up anomaly ratios
    anomaly_ratios = {
        1: args.anomaly1_ratio,
        2: args.anomaly2_ratio,
        3: args.anomaly3_ratio
    }
    
    # Generate data
    print(f"Generating {args.samples} samples with {args.normal_ratio*100:.1f}% normal data...")
    data = generate_test_data(args.samples, args.normal_ratio, anomaly_ratios)
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Write output files
    if args.format in ['csv', 'both']:
        csv_filename = os.path.join(args.output_dir, f"test_data_{timestamp}_samples.csv")
        write_csv(data, csv_filename)
    
    if args.format in ['json', 'both']:
        json_filename = os.path.join(args.output_dir, f"test_data_{timestamp}_samples.json")
        write_json(data, json_filename)
    
    # Generate event log if requested
    if args.generate_events:
        ensure_dir('logs')
        event_filename = os.path.join('logs', f"events_{datetime.now().strftime('%Y%m%d')}.json")
        generate_event_log(data, event_filename)
    
    print("Data generation completed!")
    print(f"Generated {args.samples} samples with the following distribution:")
    print(f"  - Normal: {args.normal_ratio*100:.1f}% ({int(args.samples * args.normal_ratio)} samples)")
    for pattern_id, ratio in anomaly_ratios.items():
        print(f"  - Anomaly type {pattern_id}: {ratio*100:.1f}% ({int(args.samples * ratio)} samples)")

if __name__ == "__main__":
    main()