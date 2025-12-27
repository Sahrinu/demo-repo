#!/usr/bin/env python3
"""
Spiral Reader for Digital Ghost Challenge
Reads pixel data in spiral pattern from center outward.
"""

import argparse
import sys
import os
from PIL import Image


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


def generate_spiral_coordinates(width, height, clockwise=True):
    """
    Generate coordinates for spiral pattern from center outward
    
    Args:
        width: Image width
        height: Image height
        clockwise: Direction of spiral (True for clockwise, False for counter-clockwise)
    
    Returns:
        list: List of (x, y) coordinates in spiral order
    """
    coordinates = []
    
    # Start from center
    x = width // 2
    y = height // 2
    coordinates.append((x, y))
    
    # Spiral outward
    step = 1
    while len(coordinates) < width * height:
        # Move in spiral pattern
        # Right/Left
        dx = 1 if clockwise else -1
        for _ in range(step):
            x += dx
            if 0 <= x < width and 0 <= y < height:
                coordinates.append((x, y))
            if len(coordinates) >= width * height:
                break
        
        if len(coordinates) >= width * height:
            break
        
        # Down/Up
        dy = 1 if clockwise else -1
        for _ in range(step):
            y += dy
            if 0 <= x < width and 0 <= y < height:
                coordinates.append((x, y))
            if len(coordinates) >= width * height:
                break
        
        if len(coordinates) >= width * height:
            break
        
        step += 1
        
        # Left/Right
        dx = -1 if clockwise else 1
        for _ in range(step):
            x += dx
            if 0 <= x < width and 0 <= y < height:
                coordinates.append((x, y))
            if len(coordinates) >= width * height:
                break
        
        if len(coordinates) >= width * height:
            break
        
        # Up/Down
        dy = -1 if clockwise else 1
        for _ in range(step):
            y += dy
            if 0 <= x < width and 0 <= y < height:
                coordinates.append((x, y))
            if len(coordinates) >= width * height:
                break
        
        if len(coordinates) >= width * height:
            break
        
        step += 1
    
    return coordinates


def read_spiral_lsb(image_path, clockwise=True, channel='all', verbose=False, output_file=None):
    """
    Read pixel data in spiral pattern and extract LSB
    
    Args:
        image_path: Path to the image file
        clockwise: Direction of spiral
        channel: Color channel to extract from ('red', 'green', 'blue', or 'all')
        verbose: Enable verbose logging
        output_file: Optional file to save extracted data
    
    Returns:
        dict: Extracted data from spiral pattern
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
            print_colored(f"\n=== SPIRAL READER ===", Colors.HEADER)
            print_colored(f"Image size: {width}x{height}", Colors.OKBLUE)
            print_colored(f"Direction: {'Clockwise' if clockwise else 'Counter-clockwise'}", Colors.OKBLUE)
        
        # Generate spiral coordinates
        spiral_coords = generate_spiral_coordinates(width, height, clockwise)
        
        if verbose:
            print_colored(f"Generated {len(spiral_coords)} spiral coordinates", Colors.OKGREEN)
        
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
        
        # Extract LSB from each channel in spiral order
        for ch_name in channels:
            if ch_name not in channels_to_extract:
                print_colored(f"Warning: Invalid channel '{ch_name}'", Colors.WARNING)
                continue
            
            ch_index = channels_to_extract[ch_name]
            bits = []
            
            if verbose:
                print_colored(f"\nExtracting from {ch_name.upper()} channel in spiral pattern...", Colors.OKCYAN)
            
            # Extract LSB from pixels in spiral order
            for x, y in spiral_coords:
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
            byte_data = []
            
            for i in range(0, len(binary_string), 8):
                byte = binary_string[i:i+8]
                if len(byte) < 8:
                    # Skip incomplete byte at the end
                    break
                byte_value = int(byte, 2)
                byte_data.append(byte_value)
                
                # Try to decode as ASCII
                if 32 <= byte_value <= 126 or byte_value in [10, 13, 9]:
                    ascii_text += chr(byte_value)
                elif byte_value == 0:
                    # Null terminator might indicate end of data
                    break
            
            # Store results
            results[ch_name] = {
                'total_bits': len(binary_string),
                'total_bytes': len(byte_data),
                'binary': binary_string[:100] + '...' if len(binary_string) > 100 else binary_string,
                'ascii_text': ascii_text,
                'raw_bytes': byte_data
            }
            
            if verbose:
                print_colored(f"Extracted {len(binary_string)} bits ({len(byte_data)} bytes)", Colors.OKBLUE)
                if ascii_text:
                    print_colored(f"ASCII preview (first 200 chars): {ascii_text[:200]}", Colors.OKGREEN)
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                f.write(f"Spiral Direction: {'Clockwise' if clockwise else 'Counter-clockwise'}\n")
                for ch_name, data in results.items():
                    f.write(f"\n=== {ch_name.upper()} CHANNEL ===\n")
                    f.write(f"Total bits: {data['total_bits']}\n")
                    f.write(f"Total bytes: {data['total_bytes']}\n")
                    if data['ascii_text']:
                        f.write(f"\nASCII Text:\n{data['ascii_text']}\n")
            if verbose:
                print_colored(f"\nResults saved to {output_file}", Colors.OKGREEN)
        
        img.close()
        return results
        
    except Exception as e:
        print_colored(f"Error reading spiral pattern: {str(e)}", Colors.FAIL)
        if verbose:
            import traceback
            traceback.print_exc()
        return None


def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(
        description='Read pixel data in spiral pattern and extract LSB'
    )
    parser.add_argument(
        'image',
        help='Path to the image file'
    )
    parser.add_argument(
        '-d', '--direction',
        choices=['clockwise', 'counterclockwise'],
        default='clockwise',
        help='Spiral direction (default: clockwise)'
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
    
    # Read spiral pattern
    print_colored("=== SPIRAL READER ===", Colors.HEADER)
    results = read_spiral_lsb(
        args.image,
        clockwise=(args.direction == 'clockwise'),
        channel=args.channel,
        verbose=args.verbose,
        output_file=args.output
    )
    
    if results:
        print_colored("\n✓ Spiral reading complete", Colors.OKGREEN)
        
        # Summary
        for ch_name, data in results.items():
            print_colored(f"\n{ch_name.upper()} channel: {data['total_bytes']} bytes extracted", Colors.OKCYAN)
        
        return 0
    else:
        print_colored("\n✗ Spiral reading failed", Colors.FAIL)
        return 1


if __name__ == '__main__':
    sys.exit(main())
