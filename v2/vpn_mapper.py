#!/usr/bin/env python3
import os
import json
import glob
from datetime import datetime
from collections import OrderedDict

def load_existing_mapping(filename="vpn_mapping.json"):
    """Load existing mapping if file exists"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f, object_pairs_hook=OrderedDict)
    except Exception as e:
        print(f"Warning: Failed to load existing mapping: {e}")
    return OrderedDict()

def parse_filename(filename):
    """Parse the OVPN filename to extract meaningful information"""
    name = os.path.splitext(filename)[0]
    
    # Get file modification time
    file_time = os.path.getmtime(filename)
    formatted_time = datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S')
    
    info = {
        "filename": filename,
        "user": name,
        "location": None,
        "file_date": formatted_time
    }
    

    if name.startswith("sad-"):
        info["location"] = "sd"
        info["user"] = name[3:]  
            
    return info

def update_vpn_mapping():
    """Update mapping of OVPN files, preserving existing entries"""
    # Load existing mapping
    existing_mapping = load_existing_mapping()
    
    # Get current .ovpn files
    current_files = set(glob.glob("*.ovpn"))
    
    # Track new entries
    new_entries = OrderedDict()
    
    # Process new files first
    for filename in current_files:
        if filename not in existing_mapping:
            info = parse_filename(filename)
            new_entries[filename] = info
            print(f"Adding new mapping: {filename}")
    
    # Combine new and existing entries
    updated_mapping = OrderedDict()
    
    # Add new entries at the beginning
    updated_mapping.update(new_entries)
    
    # Add existing entries, preserving their data
    for filename, info in existing_mapping.items():
        if filename in current_files:  # File still exists
            updated_mapping[filename] = info
        else:  # File no longer exists, mark as inactive but keep the mapping
            info['active'] = False
            updated_mapping[filename] = info
            print(f"Marking as inactive: {filename}")
    
    return updated_mapping

def main():
    # Update the mapping
    vpn_mapping = update_vpn_mapping()
    
    # Write to JSON file
    output_file = "vpn_mapping.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(vpn_mapping, f, indent=2, ensure_ascii=False)
    
    # Count active mappings
    active_count = sum(1 for info in vpn_mapping.values() if info.get('active', True))
    print(f"Mapping file updated: {output_file}")
    print(f"Total mappings: {len(vpn_mapping)} (Active: {active_count})")

if __name__ == "__main__":
    main() 
