#!/usr/bin/env python
# Maintenance script for Smart Home Anomaly Detection System

import os
import sys
import shutil
import argparse
from datetime import datetime, timedelta
import glob
import json

def clean_logs(days=7, dry_run=False):
    """Clean log files older than specified days"""
    print(f"Cleaning log files older than {days} days...")
    
    # Server logs
    server_log_path = os.path.join('server', 'logs', 'server.log')
    if os.path.exists(server_log_path):
        log_size = os.path.getsize(server_log_path) / 1024  # KB
        if log_size > 1024:  # If larger than 1MB
            print(f"Server log file size: {log_size:.2f} KB")
            if not dry_run:
                # Backup the log file
                backup_path = f"{server_log_path}.{datetime.now().strftime('%Y%m%d')}"
                shutil.copy2(server_log_path, backup_path)
                # Truncate the log file
                with open(server_log_path, 'w') as f:
                    f.write(f"Log file truncated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                print(f"Server log backed up to {backup_path} and truncated")
            else:
                print("[DRY RUN] Would backup and truncate server log")
    
    # Event logs
    cutoff_date = datetime.now() - timedelta(days=days)
    event_logs = glob.glob(os.path.join('logs', 'events_*.json'))
    
    for log_file in event_logs:
        try:
            # Extract date from filename (events_YYYYMMDD.json)
            filename = os.path.basename(log_file)
            date_str = filename.replace('events_', '').replace('.json', '')
            log_date = datetime.strptime(date_str, '%Y%m%d')
            
            if log_date < cutoff_date:
                print(f"Found old event log: {filename} ({log_date.strftime('%Y-%m-%d')})")
                if not dry_run:
                    # Archive the log file
                    archive_dir = os.path.join('logs', 'archive')
                    os.makedirs(archive_dir, exist_ok=True)
                    shutil.move(log_file, os.path.join(archive_dir, filename))
                    print(f"Moved to archive: {os.path.join('logs', 'archive', filename)}")
                else:
                    print(f"[DRY RUN] Would move {filename} to archive")
        except Exception as e:
            print(f"Error processing {log_file}: {str(e)}")

def clean_cache(dry_run=False):
    """Clean cache files and __pycache__ directories"""
    print("Cleaning cache files...")
    
    # Find all __pycache__ directories
    pycache_dirs = []
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_dirs.append(os.path.join(root, '__pycache__'))
    
    for cache_dir in pycache_dirs:
        print(f"Found cache directory: {cache_dir}")
        if not dry_run:
            try:
                shutil.rmtree(cache_dir)
                print(f"Removed: {cache_dir}")
            except Exception as e:
                print(f"Error removing {cache_dir}: {str(e)}")
        else:
            print(f"[DRY RUN] Would remove {cache_dir}")
    
    # Find all .pyc files
    pyc_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                pyc_files.append(os.path.join(root, file))
    
    for pyc_file in pyc_files:
        print(f"Found .pyc file: {pyc_file}")
        if not dry_run:
            try:
                os.remove(pyc_file)
                print(f"Removed: {pyc_file}")
            except Exception as e:
                print(f"Error removing {pyc_file}: {str(e)}")
        else:
            print(f"[DRY RUN] Would remove {pyc_file}")

def backup_data(backup_dir=None, dry_run=False):
    """Backup important data files"""
    if backup_dir is None:
        backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"Backing up important data to {backup_dir}...")
    
    # Create backup directory
    if not dry_run:
        os.makedirs(backup_dir, exist_ok=True)
    
    # Files to backup
    backup_files = [
        os.path.join('model', 'sound_classifier.pkl'),
        os.path.join('server', 'config.py')
    ]
    
    # Directories to backup
    backup_dirs = [
        'logs',
        'samples'
    ]
    
    # Backup files
    for file_path in backup_files:
        if os.path.exists(file_path):
            dest_path = os.path.join(backup_dir, file_path)
            dest_dir = os.path.dirname(dest_path)
            print(f"Backing up file: {file_path}")
            
            if not dry_run:
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(file_path, dest_path)
                print(f"Backed up to: {dest_path}")
            else:
                print(f"[DRY RUN] Would backup {file_path} to {dest_path}")
    
    # Backup directories
    for dir_path in backup_dirs:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            dest_path = os.path.join(backup_dir, dir_path)
            print(f"Backing up directory: {dir_path}")
            
            if not dry_run:
                shutil.copytree(dir_path, dest_path, dirs_exist_ok=True)
                print(f"Backed up to: {dest_path}")
            else:
                print(f"[DRY RUN] Would backup {dir_path} to {dest_path}")
    
    print(f"Backup completed to {backup_dir}")
    return backup_dir

def main():
    parser = argparse.ArgumentParser(description='Maintenance script for Smart Home Anomaly Detection System')
    parser.add_argument('--clean-logs', action='store_true', help='Clean old log files')
    parser.add_argument('--days', type=int, default=7, help='Number of days to keep logs (default: 7)')
    parser.add_argument('--clean-cache', action='store_true', help='Clean cache files and __pycache__ directories')
    parser.add_argument('--backup', action='store_true', help='Backup important data')
    parser.add_argument('--backup-dir', type=str, help='Backup directory (default: backup_YYYYMMDD_HHMMSS)')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no changes will be made)')
    parser.add_argument('--all', action='store_true', help='Perform all maintenance tasks')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    print(f"Smart Home Anomaly Detection System - Maintenance")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    if args.dry_run:
        print("DRY RUN MODE: No changes will be made")
        print("-" * 60)
    
    if args.clean_logs or args.all:
        clean_logs(args.days, args.dry_run)
        print("-" * 60)
    
    if args.clean_cache or args.all:
        clean_cache(args.dry_run)
        print("-" * 60)
    
    if args.backup or args.all:
        backup_data(args.backup_dir, args.dry_run)
        print("-" * 60)
    
    print("Maintenance completed!")

if __name__ == "__main__":
    main()