#!/usr/bin/env python3
"""
LSB Extractor for Digital Ghost Challenge
Extracts Least Significant Bits from image channels.
"""

import argparse
import sys
import os
from PIL import Image
import base64


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


def extract_lsb_from_channel(image_path, channel='red', verbose=False, output_file=None):
    """
    Extract LSB from a specific color channel
    
    Args:
        image_path: Path to the image file
        channel: Color channel to extract from ('red', 'green', 'blue', or 'all')
        verbose: Enable verbose logging
        output_file: Optional file to save extracted data
    
    Returns:
        dict: Extracted LSB data from channel(s)
    """
    results = {}
    
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            print_colored(f"Error: File {image_path} not found", Colors.FAIL)
            return None
        
        # Open image
        img = Image.open(image_path)
        pixels = img.load()
        width, height = img.size
        
        if verbose:
            print_colored(f"\n=== LSB EXTRACTION ===", Colors.HEADER)
            print_colored(f"Image size: {width}x{height}", Colors.OKBLUE)
            print_colored(f"Total pixels: {width * height}", Colors.OKBLUE)
        
        # Define channel indices
        channels_to_extract = {
            'red': 0,
            'green': 1,
            'blue': 2
        }
        
        # Determine which channels to process
        if channel == 'all':
            channels = ['red', 'green', 'blue']
        else:
            channels = [channel.lower()]
        
        # Extract LSB from each channel
        for ch_name in channels:
            if ch_name not in channels_to_extract:
                print_colored(f"Warning: Invalid channel '{ch_name}'", Colors.WARNING)
                continue
            
            ch_index = channels_to_extract[ch_name]
            bits = []
            
            if verbose:
                print_colored(f"\nExtracting from {ch_name.upper()} channel...", Colors.OKCYAN)
            
            # Extract LSB from each pixel
            for y in range(height):
                for x in range(width):
                    pixel = pixels[x, y]
                    # Get the channel value and extract LSB
                    if isinstance(pixel, tuple) and len(pixel) > ch_index:
                        channel_value = pixel[ch_index]
                        lsb = channel_value & 1
                        bits.append(str(lsb))
            
            # Convert bits to bytes
            binary_string = ''.join(bits)
            
            # Try to convert to ASCII
            ascii_text = ""
            corrupted = False
            byte_data = []
            
            for i in range(0, len(binary_string) - 7, 8):
                byte = binary_string[i:i+8]
                byte_value = int(byte, 2)
                byte_data.append(byte_value)
                
                # Try to decode as ASCII
                if 32 <= byte_value <= 126 or byte_value in [10, 13, 9]:  # Printable ASCII + newline, CR, tab
                    ascii_text += chr(byte_value)
                elif byte_value == 0:
                    # Null terminator might indicate end of data
                    break
                else:
                    # Non-printable character
                    corrupted = True
            
            # Store results
            results[ch_name] = {
                'total_bits': len(binary_string),
                'total_bytes': len(byte_data),
                'binary': binary_string[:100] + '...' if len(binary_string) > 100 else binary_string,
                'raw_bytes': byte_data,
                'ascii_text': ascii_text,
                'possibly_corrupted': corrupted
            }
            
            if verbose:
                print_colored(f"Extracted {len(binary_string)} bits ({len(byte_data)} bytes)", Colors.OKBLUE)
                if ascii_text:
                    print_colored(f"ASCII preview (first 200 chars): {ascii_text[:200]}", Colors.OKGREEN)
                if corrupted:
                    print_colored("Warning: Channel may contain corrupted or binary data", Colors.WARNING)
            
            # Try Base64 decoding
            if ascii_text and len(ascii_text) > 10:
                try:
                    # Check if it looks like base64
                    if all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\n\r' for c in ascii_text.strip()):
                        decoded = base64.b64decode(ascii_text.strip())
                        results[ch_name]['base64_decoded'] = decoded.decode('utf-8', errors='ignore')
                        if verbose:
                            print_colored(f"Base64 decoded: {results[ch_name]['base64_decoded'][:200]}", Colors.OKGREEN)
                except Exception as e:
                    if verbose:
                        print_colored(f"Base64 decoding failed: {str(e)}", Colors.WARNING)
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                for ch_name, data in results.items():
                    f.write(f"\n=== {ch_name.upper()} CHANNEL ===\n")
                    f.write(f"Total bits: {data['total_bits']}\n")
                    f.write(f"Total bytes: {data['total_bytes']}\n")
                    if data['ascii_text']:
                        f.write(f"\nASCII Text:\n{data['ascii_text']}\n")
                    if 'base64_decoded' in data:
                        f.write(f"\nBase64 Decoded:\n{data['base64_decoded']}\n")
            if verbose:
                print_colored(f"\nResults saved to {output_file}", Colors.OKGREEN)
        
        img.close()
        return results
        
    except Exception as e:
        print_colored(f"Error extracting LSB: {str(e)}", Colors.FAIL)
        if verbose:
            import traceback
            traceback.print_exc()
        return None


def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(
        description='Extract LSB data from image color channels'
    )
    parser.add_argument(
        'image',
        help='Path to the image file'
    )
    parser.add_argument(
        '-c', '--channel',
        choices=['red', 'green', 'blue', 'all'],
        default='all',
        help='Color channel to extract from (default: all)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '-o', '--output',
        help='Save extracted data to file'
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
    
    # Extract LSB data
    print_colored("=== LSB EXTRACTOR ===", Colors.HEADER)
    results = extract_lsb_from_channel(
        args.image,
        channel=args.channel,
        verbose=args.verbose,
        output_file=args.output
    )
    
    if results:
        print_colored("\n✓ LSB extraction complete", Colors.OKGREEN)
        
        # Summary
        for ch_name, data in results.items():
            print_colored(f"\n{ch_name.upper()} channel: {data['total_bytes']} bytes extracted", Colors.OKCYAN)
            if data.get('base64_decoded'):
                print_colored("  Contains Base64-encoded data ✓", Colors.OKGREEN)
        
        return 0
    else:
        print_colored("\n✗ LSB extraction failed", Colors.FAIL)
        return 1


if __name__ == '__main__':
    sys.exit(main())
