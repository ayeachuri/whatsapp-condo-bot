#!/usr/bin/env python3
import os
import sys
import argparse

def print_directory_structure(startpath, prefix=''):
    """
    Print the directory structure starting from startpath in a tree-like format.
    
    Args:
        startpath (str): The root directory to start from
        prefix (str): Prefix to add before each line (used for recursion)
    """
    # Get items in the current directory
    items = os.listdir(startpath)
    items.sort()
    
    # Handle files and directories
    for i, item in enumerate(items):
        path = os.path.join(startpath, item)
        is_last = i == len(items) - 1
        
        # Create the connector symbol
        connector = '└── ' if is_last else '├── '
        
        # Print the current item
        print(f"{prefix}{connector}{item}")
        
        # If it's a directory, recursively process it
        if os.path.isdir(path):
            # Create the new prefix for subdirectories
            extension = '    ' if is_last else '│   '
            print_directory_structure(path, prefix + extension)

def main():
    parser = argparse.ArgumentParser(description='Print directory structure in a tree-like format.')
    parser.add_argument('path', nargs='?', default='.', help='Path to the directory (default: current directory)')
    parser.add_argument('-d', '--max-depth', type=int, help='Maximum depth to traverse')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.")
        return 1
    
    if not os.path.isdir(args.path):
        print(f"Error: Path '{args.path}' is not a directory.")
        return 1
    
    print(os.path.abspath(args.path))
    print_directory_structure(args.path)
    return 0

if __name__ == '__main__':
    sys.exit(main())