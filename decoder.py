#!/usr/bin/env python3
"""
Decoder for Digital Ghost Challenge
Handles Base64 and ROT-13 decoding.
"""

import argparse
import sys
import base64
import codecs


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


def decode_base64(data, verbose=False):
    """
    Decode Base64 encoded data
    
    Args:
        data: String or bytes to decode
        verbose: Enable verbose logging
    
    Returns:
        str: Decoded string or None if decoding fails
    """
    try:
        if isinstance(data, str):
            data = data.strip()
            decoded_bytes = base64.b64decode(data)
        else:
            decoded_bytes = base64.b64decode(data)
        
        # Try to decode as UTF-8
        decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
        
        if verbose:
            print_colored(f"\nBase64 Input: {str(data)[:100]}...", Colors.OKBLUE)
            print_colored(f"Decoded Output: {decoded_str[:100]}...", Colors.OKGREEN)
        
        return decoded_str
        
    except Exception as e:
        if verbose:
            print_colored(f"Base64 decoding error: {str(e)}", Colors.FAIL)
        return None


def decode_rot13(data, verbose=False):
    """
    Decode ROT-13 cipher
    
    Args:
        data: String to decode
        verbose: Enable verbose logging
    
    Returns:
        str: Decoded string
    """
    try:
        decoded = codecs.decode(data, 'rot_13')
        
        if verbose:
            print_colored(f"\nROT-13 Input: {data[:100]}...", Colors.OKBLUE)
            print_colored(f"Decoded Output: {decoded[:100]}...", Colors.OKGREEN)
        
        return decoded
        
    except Exception as e:
        if verbose:
            print_colored(f"ROT-13 decoding error: {str(e)}", Colors.FAIL)
        return None


def decode_multi_layer(data, layers, verbose=False):
    """
    Decode data through multiple encoding layers
    
    Args:
        data: Initial data to decode
        layers: List of encoding types in order (e.g., ['base64', 'rot13'])
        verbose: Enable verbose logging
    
    Returns:
        str: Final decoded string
    """
    result = data
    
    if verbose:
        print_colored("\n=== MULTI-LAYER DECODING ===", Colors.HEADER)
        print_colored(f"Initial data: {str(result)[:100]}...", Colors.OKBLUE)
    
    for i, layer in enumerate(layers):
        if verbose:
            print_colored(f"\nLayer {i+1}: {layer}", Colors.OKCYAN)
        
        if layer.lower() == 'base64':
            result = decode_base64(result, verbose=verbose)
            if result is None:
                print_colored(f"Failed at layer {i+1} ({layer})", Colors.FAIL)
                return None
        
        elif layer.lower() == 'rot13':
            result = decode_rot13(result, verbose=verbose)
            if result is None:
                print_colored(f"Failed at layer {i+1} ({layer})", Colors.FAIL)
                return None
        
        else:
            print_colored(f"Unknown encoding type: {layer}", Colors.WARNING)
    
    if verbose:
        print_colored(f"\nFinal decoded data: {result[:200]}", Colors.OKGREEN)
    
    return result


def auto_detect_and_decode(data, verbose=False):
    """
    Attempt to automatically detect and decode data
    
    Args:
        data: Data to decode
        verbose: Enable verbose logging
    
    Returns:
        dict: Results of different decoding attempts
    """
    results = {}
    
    if verbose:
        print_colored("\n=== AUTO-DETECTION ===", Colors.HEADER)
    
    # Try Base64
    if isinstance(data, str):
        # Check if it looks like base64
        base64_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
        if all(c in base64_chars or c.isspace() for c in data):
            b64_result = decode_base64(data, verbose=False)
            if b64_result:
                results['base64'] = b64_result
                if verbose:
                    print_colored("✓ Looks like Base64 data", Colors.OKGREEN)
    
    # Try ROT-13
    rot13_result = decode_rot13(str(data), verbose=False)
    if rot13_result and rot13_result != data:
        results['rot13'] = rot13_result
        if verbose:
            print_colored("✓ Applied ROT-13", Colors.OKGREEN)
    
    # Try Base64 then ROT-13
    if 'base64' in results:
        b64_rot13 = decode_rot13(results['base64'], verbose=False)
        if b64_rot13:
            results['base64_then_rot13'] = b64_rot13
            if verbose:
                print_colored("✓ Applied Base64 → ROT-13", Colors.OKGREEN)
    
    # Try ROT-13 then Base64
    if rot13_result:
        try:
            rot13_b64 = decode_base64(rot13_result, verbose=False)
            if rot13_b64:
                results['rot13_then_base64'] = rot13_b64
                if verbose:
                    print_colored("✓ Applied ROT-13 → Base64", Colors.OKGREEN)
        except:
            pass
    
    return results


def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(
        description='Decode Base64 and ROT-13 encoded data'
    )
    parser.add_argument(
        'input',
        nargs='?',
        help='Data to decode or file containing data (use - for stdin)'
    )
    parser.add_argument(
        '-f', '--file',
        help='Read input from file'
    )
    parser.add_argument(
        '-t', '--type',
        choices=['base64', 'rot13', 'auto'],
        default='auto',
        help='Decoding type (default: auto-detect)'
    )
    parser.add_argument(
        '-l', '--layers',
        help='Comma-separated list of encoding layers (e.g., "base64,rot13")'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '-o', '--output',
        help='Save decoded data to file'
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
    
    # Get input data
    data = None
    if args.file:
        with open(args.file, 'r') as f:
            data = f.read()
    elif args.input:
        if args.input == '-':
            data = sys.stdin.read()
        else:
            data = args.input
    else:
        print_colored("Error: No input provided", Colors.FAIL)
        parser.print_help()
        return 1
    
    print_colored("=== DECODER ===", Colors.HEADER)
    
    # Decode data
    result = None
    if args.layers:
        # Multi-layer decoding
        layers = [l.strip() for l in args.layers.split(',')]
        result = decode_multi_layer(data, layers, verbose=args.verbose)
    elif args.type == 'base64':
        result = decode_base64(data, verbose=args.verbose)
    elif args.type == 'rot13':
        result = decode_rot13(data, verbose=args.verbose)
    elif args.type == 'auto':
        results = auto_detect_and_decode(data, verbose=args.verbose)
        if results:
            print_colored("\n=== DECODING RESULTS ===", Colors.HEADER)
            for method, decoded in results.items():
                print_colored(f"\n{method}:", Colors.OKCYAN)
                print_colored(decoded[:500], Colors.OKGREEN)
            result = list(results.values())[0] if results else None
        else:
            print_colored("No successful decoding methods found", Colors.WARNING)
    
    # Save to file if requested
    if result and args.output:
        with open(args.output, 'w') as f:
            f.write(result)
        print_colored(f"\n✓ Decoded data saved to {args.output}", Colors.OKGREEN)
    
    if result or (args.type == 'auto' and results):
        print_colored("\n✓ Decoding complete", Colors.OKGREEN)
        return 0
    else:
        print_colored("\n✗ Decoding failed", Colors.FAIL)
        return 1


if __name__ == '__main__':
    sys.exit(main())
