#!/usr/bin/env python3
"""
Metadata Extractor for Digital Ghost Challenge
Extracts EXIF and metadata from image files.
"""

import argparse
import sys
import os
from PIL import Image
from PIL.ExifTags import TAGS
import json


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_colored(text, color=Colors.OKGREEN):
    """Print colored text to terminal"""
    print(f"{color}{text}{Colors.ENDC}")


def extract_metadata(image_path, verbose=False, output_file=None):
    """
    Extract all EXIF and metadata from the image
    
    Args:
        image_path: Path to the image file
        verbose: Enable verbose logging
        output_file: Optional file to save metadata
    
    Returns:
        dict: Metadata information
    """
    metadata = {}
    
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            print_colored(f"Error: File {image_path} not found", Colors.FAIL)
            return None
        
        # Get file properties
        file_stats = os.stat(image_path)
        metadata['file_properties'] = {
            'name': os.path.basename(image_path),
            'path': os.path.abspath(image_path),
            'size_bytes': file_stats.st_size,
            'size_readable': f"{file_stats.st_size / 1024:.2f} KB"
        }
        
        if verbose:
            print_colored("\n=== FILE PROPERTIES ===", Colors.HEADER)
            print_colored(f"Name: {metadata['file_properties']['name']}", Colors.OKBLUE)
            print_colored(f"Path: {metadata['file_properties']['path']}", Colors.OKBLUE)
            print_colored(f"Size: {metadata['file_properties']['size_readable']}", Colors.OKBLUE)
        
        # Open image and get basic info
        with Image.open(image_path) as img:
            metadata['image_properties'] = {
                'format': img.format,
                'mode': img.mode,
                'width': img.width,
                'height': img.height,
                'dimensions': f"{img.width}x{img.height}"
            }
            
            if verbose:
                print_colored("\n=== IMAGE PROPERTIES ===", Colors.HEADER)
                print_colored(f"Format: {img.format}", Colors.OKBLUE)
                print_colored(f"Mode: {img.mode}", Colors.OKBLUE)
                print_colored(f"Dimensions: {metadata['image_properties']['dimensions']}", Colors.OKBLUE)
            
            # Extract EXIF data
            exif_data = {}
            if hasattr(img, '_getexif') and img._getexif() is not None:
                exif_info = img._getexif()
                for tag_id, value in exif_info.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_data[tag] = str(value)
            
            # Try to get info dictionary (can contain hidden data)
            if img.info:
                metadata['info_dict'] = img.info
                if verbose and img.info:
                    print_colored("\n=== INFO DICTIONARY ===", Colors.HEADER)
                    for key, value in img.info.items():
                        print_colored(f"{key}: {value}", Colors.OKBLUE)
            
            if exif_data:
                metadata['exif_data'] = exif_data
                if verbose:
                    print_colored("\n=== EXIF DATA ===", Colors.HEADER)
                    for tag, value in exif_data.items():
                        print_colored(f"{tag}: {value}", Colors.OKBLUE)
            else:
                if verbose:
                    print_colored("\n=== EXIF DATA ===", Colors.HEADER)
                    print_colored("No EXIF data found", Colors.WARNING)
        
        # Look for hidden text in metadata
        hidden_text = []
        for key, value in metadata.get('info_dict', {}).items():
            if isinstance(value, str) and len(value) > 0:
                hidden_text.append(f"{key}: {value}")
        
        if hidden_text:
            metadata['potential_hidden_text'] = hidden_text
            if verbose:
                print_colored("\n=== POTENTIAL HIDDEN TEXT ===", Colors.HEADER)
                for text in hidden_text:
                    print_colored(text, Colors.OKGREEN)
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            if verbose:
                print_colored(f"\nMetadata saved to {output_file}", Colors.OKGREEN)
        
        return metadata
        
    except Exception as e:
        print_colored(f"Error extracting metadata: {str(e)}", Colors.FAIL)
        if verbose:
            import traceback
            traceback.print_exc()
        return None


def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(
        description='Extract metadata from image files for forensic analysis'
    )
    parser.add_argument(
        'image',
        help='Path to the image file'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '-o', '--output',
        help='Save metadata to JSON file'
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    args = parser.parse_args()
    
    # Disable colors if requested
    if args.no_color:
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')
    
    # Extract metadata
    print_colored("=== METADATA EXTRACTOR ===", Colors.HEADER)
    metadata = extract_metadata(args.image, verbose=args.verbose, output_file=args.output)
    
    if metadata:
        print_colored("\n✓ Metadata extraction complete", Colors.OKGREEN)
        return 0
    else:
        print_colored("\n✗ Metadata extraction failed", Colors.FAIL)
        return 1


if __name__ == '__main__':
    sys.exit(main())
