#!/usr/bin/env python
# Data visualization tool for Smart Home Anomaly Detection System

import os
import sys
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime
import glob
import joblib

# Set style for plots
sns.set_style("whitegrid")
plt.rcParams.update({'font.size': 12})

# Ensure the output directory exists
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

# Load data from CSV or JSON file
def load_data(file_path):
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.json'):
        with open(file_path, 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")

# Load the latest sample data if no file is specified
def load_latest_sample():
    sample_files = glob.glob(os.path.join('samples', '*_samples.csv'))
    if not sample_files:
        sample_files = glob.glob(os.path.join('samples', '*_samples.json'))
    
    if not sample_files:
        raise FileNotFoundError("No sample data files found in 'samples' directory")
    
    latest_file = max(sample_files, key=os.path.getctime)
    print(f"Loading latest sample file: {latest_file}")
    return load_data(latest_file)

# Load event logs
def load_event_logs():
    event_files = glob.glob(os.path.join('logs', 'events_*.json'))
    
    if not event_files:
        print("No event log files found")
        return None
    
    # Load the latest event log
    latest_file = max(event_files, key=os.path.getctime)
    print(f"Loading event log: {latest_file}")
    
    with open(latest_file, 'r') as f:
        events = json.load(f)
    
    return events

# Plot time series data
def plot_time_series(df, output_dir):
    plt.figure(figsize=(12, 6))
    
    # Convert timestamp to datetime if it's not already
    if df['timestamp'].dtype == 'object':
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Create a colormap for different pattern types
    colors = {0: 'green', 1: 'red', 2: 'orange', 3: 'purple'}
    
    # Plot each pattern type with a different color
    for pattern_id in sorted(df['pattern_id'].unique()):
        pattern_data = df[df['pattern_id'] == pattern_id]
        label = f"Pattern {pattern_id}" if pattern_id > 0 else "Normal"
        plt.scatter(pattern_data['timestamp'], pattern_data['amplitude'], 
                   color=colors.get(pattern_id, 'blue'), alpha=0.7, label=label)
    
    plt.title('Sensor Data Time Series')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot
    output_file = os.path.join(output_dir, 'time_series.png')
    plt.savefig(output_file, dpi=300)
    print(f"Saved time series plot to {output_file}")
    
    # Close the plot to free memory
    plt.close()

# Plot amplitude distribution
def plot_distribution(df, output_dir):
    plt.figure(figsize=(10, 6))
    
    # Plot distribution for each pattern type
    for pattern_id in sorted(df['pattern_id'].unique()):
        pattern_data = df[df['pattern_id'] == pattern_id]
        label = f"Pattern {pattern_id}" if pattern_id > 0 else "Normal"
        sns.kdeplot(pattern_data['amplitude'], label=label, fill=True, alpha=0.3)
    
    plt.title('Amplitude Distribution by Pattern Type')
    plt.xlabel('Amplitude')
    plt.ylabel('Density')
    plt.legend()
    plt.tight_layout()
    
    # Save the plot
    output_file = os.path.join(output_dir, 'amplitude_distribution.png')
    plt.savefig(output_file, dpi=300)
    print(f"Saved distribution plot to {output_file}")
    
    # Close the plot to free memory
    plt.close()

# Plot pattern distribution
def plot_pattern_distribution(df, output_dir):
    plt.figure(figsize=(8, 6))
    
    # Count occurrences of each pattern type
    pattern_counts = df['pattern_id'].value_counts().sort_index()
    
    # Create labels
    labels = [f"Normal" if idx == 0 else f"Pattern {idx}" for idx in pattern_counts.index]
    
    # Create a pie chart
    plt.pie(pattern_counts, labels=labels, autopct='%1.1f%%', startangle=90, 
           colors=['green', 'red', 'orange', 'purple'][:len(pattern_counts)])
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title('Pattern Type Distribution')
    plt.tight_layout()
    
    # Save the plot
    output_file = os.path.join(output_dir, 'pattern_distribution.png')
    plt.savefig(output_file, dpi=300)
    print(f"Saved pattern distribution plot to {output_file}")
    
    # Close the plot to free memory
    plt.close()

# Plot event timeline
def plot_event_timeline(events, output_dir):
    if not events or len(events) == 0:
        print("No events to plot")
        return
    
    plt.figure(figsize=(12, 6))
    
    # Convert timestamps to datetime
    for event in events:
        event['start_datetime'] = pd.to_datetime(event['start_time'])
        event['end_datetime'] = pd.to_datetime(event['end_time'])
        event['duration'] = (event['end_datetime'] - event['start_datetime']).total_seconds() / 60  # minutes
    
    # Sort events by start time
    events = sorted(events, key=lambda x: x['start_datetime'])
    
    # Create a colormap for different pattern types
    colors = {1: 'red', 2: 'orange', 3: 'purple'}
    
    # Plot events as horizontal bars
    for i, event in enumerate(events):
        pattern_id = event['pattern_id']
        plt.barh(i, event['duration'], left=event['start_datetime'], 
                height=0.5, color=colors.get(pattern_id, 'blue'), alpha=0.7)
        plt.text(event['start_datetime'], i, f" Pattern {pattern_id}", va='center')
    
    plt.title('Event Timeline')
    plt.xlabel('Time')
    plt.ylabel('Event')
    plt.yticks([])
    plt.grid(axis='x')
    plt.tight_layout()
    
    # Save the plot
    output_file = os.path.join(output_dir, 'event_timeline.png')
    plt.savefig(output_file, dpi=300)
    print(f"Saved event timeline plot to {output_file}")
    
    # Close the plot to free memory
    plt.close()

# Generate a summary report
def generate_report(df, events, output_dir):
    report = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_summary": {
            "total_samples": len(df),
            "normal_samples": len(df[df['pattern_id'] == 0]),
            "anomaly_samples": len(df[df['pattern_id'] > 0]),
            "pattern_distribution": df['pattern_id'].value_counts().to_dict(),
            "amplitude_stats": {
                "min": float(df['amplitude'].min()),
                "max": float(df['amplitude'].max()),
                "mean": float(df['amplitude'].mean()),
                "median": float(df['amplitude'].median()),
                "std": float(df['amplitude'].std())
            }
        }
    }
    
    # Add event summary if available
    if events and len(events) > 0:
        report["event_summary"] = {
            "total_events": len(events),
            "pattern_distribution": {}
        }
        
        # Count events by pattern type
        for event in events:
            pattern_id = event['pattern_id']
            if pattern_id not in report["event_summary"]["pattern_distribution"]:
                report["event_summary"]["pattern_distribution"][pattern_id] = 0
            report["event_summary"]["pattern_distribution"][pattern_id] += 1
    
    # Save the report
    output_file = os.path.join(output_dir, 'data_report.json')
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"Saved data report to {output_file}")
    
    # Generate a text version of the report
    output_file_txt = os.path.join(output_dir, 'data_report.txt')
    with open(output_file_txt, 'w') as f:
        f.write(f"Data Visualization Report\n")
        f.write(f"Generated at: {report['generated_at']}\n\n")
        
        f.write(f"Data Summary:\n")
        f.write(f"  Total samples: {report['data_summary']['total_samples']}\n")
        f.write(f"  Normal samples: {report['data_summary']['normal_samples']} ({report['data_summary']['normal_samples']/report['data_summary']['total_samples']*100:.1f}%)\n")
        f.write(f"  Anomaly samples: {report['data_summary']['anomaly_samples']} ({report['data_summary']['anomaly_samples']/report['data_summary']['total_samples']*100:.1f}%)\n\n")
        
        f.write(f"Pattern Distribution:\n")
        for pattern_id, count in sorted(report['data_summary']['pattern_distribution'].items()):
            pattern_name = "Normal" if int(pattern_id) == 0 else f"Pattern {pattern_id}"
            f.write(f"  {pattern_name}: {count} ({count/report['data_summary']['total_samples']*100:.1f}%)\n")
        
        f.write(f"\nAmplitude Statistics:\n")
        f.write(f"  Minimum: {report['data_summary']['amplitude_stats']['min']:.2f}\n")
        f.write(f"  Maximum: {report['data_summary']['amplitude_stats']['max']:.2f}\n")
        f.write(f"  Mean: {report['data_summary']['amplitude_stats']['mean']:.2f}\n")
        f.write(f"  Median: {report['data_summary']['amplitude_stats']['median']:.2f}\n")
        f.write(f"  Standard Deviation: {report['data_summary']['amplitude_stats']['std']:.2f}\n")
        
        if "event_summary" in report:
            f.write(f"\nEvent Summary:\n")
            f.write(f"  Total events: {report['event_summary']['total_events']}\n")
            f.write(f"  Events by pattern type:\n")
            for pattern_id, count in sorted(report['event_summary']['pattern_distribution'].items()):
                f.write(f"    Pattern {pattern_id}: {count} ({count/report['event_summary']['total_events']*100:.1f}%)\n")
    
    print(f"Saved text report to {output_file_txt}")

# Try to load and visualize model information
def visualize_model(output_dir):
    model_path = os.path.join('model', 'sound_classifier.pkl')
    if not os.path.exists(model_path):
        print(f"Model file not found at {model_path}")
        return
    
    try:
        # Load the model
        model = joblib.load(model_path)
        print(f"Loaded model from {model_path}")
        
        # Check if it's a scikit-learn model
        if hasattr(model, 'feature_importances_'):
            # Plot feature importances if available
            plt.figure(figsize=(10, 6))
            feature_names = [f"Feature {i}" for i in range(len(model.feature_importances_))]
            
            # Sort features by importance
            indices = np.argsort(model.feature_importances_)[::-1]
            sorted_importances = model.feature_importances_[indices]
            sorted_features = [feature_names[i] for i in indices]
            
            # Plot top 10 features or all if less than 10
            num_features = min(10, len(sorted_features))
            plt.barh(range(num_features), sorted_importances[:num_features], align='center')
            plt.yticks(range(num_features), sorted_features[:num_features])
            plt.xlabel('Importance')
            plt.title('Feature Importances')
            plt.tight_layout()
            
            # Save the plot
            output_file = os.path.join(output_dir, 'feature_importances.png')
            plt.savefig(output_file, dpi=300)
            print(f"Saved feature importances plot to {output_file}")
            plt.close()
        else:
            print("Model does not have feature importances attribute")
    except Exception as e:
        print(f"Error visualizing model: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Data visualization tool for Smart Home Anomaly Detection System')
    parser.add_argument('--input', type=str, help='Input data file (CSV or JSON)')
    parser.add_argument('--output-dir', type=str, default='visualizations', help='Output directory for visualizations')
    parser.add_argument('--events', action='store_true', help='Include event log visualization')
    parser.add_argument('--model', action='store_true', help='Include model visualization if available')
    parser.add_argument('--report', action='store_true', help='Generate summary report')
    parser.add_argument('--all', action='store_true', help='Generate all visualizations and reports')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # Ensure output directory exists
    ensure_dir(args.output_dir)
    
    # Load data
    try:
        if args.input:
            df = load_data(args.input)
        else:
            df = load_latest_sample()
        
        print(f"Loaded {len(df)} data points")
        
        # Basic data preprocessing
        if 'timestamp' in df.columns and df['timestamp'].dtype == 'object':
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Load events if requested
        events = None
        if args.events or args.all:
            events = load_event_logs()
        
        # Generate visualizations
        plot_time_series(df, args.output_dir)
        plot_distribution(df, args.output_dir)
        plot_pattern_distribution(df, args.output_dir)
        
        if events and len(events) > 0:
            plot_event_timeline(events, args.output_dir)
        
        # Generate report if requested
        if args.report or args.all:
            generate_report(df, events, args.output_dir)
        
        # Visualize model if requested
        if args.model or args.all:
            visualize_model(args.output_dir)
        
        print(f"Visualization completed! Output saved to {args.output_dir}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())