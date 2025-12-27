#!/usr/bin/env python3
"""
Digital Ghost Analyzer - Master orchestration script
Runs all analysis techniques to solve the Digital Ghost challenge.
"""

import argparse
import sys
import os
import json
from datetime import datetime

# Import our modules
import metadata_extractor
import lsb_extractor
import decoder
import spiral_reader
import fragment_assembler


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


def print_banner():
    """Print ASCII banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          DIGITAL GHOST FORENSICS ANALYZER                ║
║          Multi-Layer Steganography Toolkit               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    print_colored(banner, Colors.HEADER)


def setup_output_directory(output_dir):
    """Create output directory if it doesn't exist"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        return True
    return False


def log_message(message, log_file=None, verbose=False):
    """Log message to file and optionally print"""
    if verbose:
        print_colored(message, Colors.OKBLUE)
    
    if log_file:
        with open(log_file, 'a') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] {message}\n")


def run_complete_analysis(image_path, config, verbose=False):
    """
    Run complete analysis on the image
    
    Args:
        image_path: Path to the image file
        config: Configuration dictionary
        verbose: Enable verbose logging
    
    Returns:
        dict: Results from all analysis techniques
    """
    results = {
        'metadata': None,
        'lsb': {},
        'spiral': {},
        'fragments': [],
        'final_flag': None
    }
    
    output_dir = config.get('output_directory', 'output')
    fragments_dir = config.get('fragments_directory', 'fragments')
    log_file = os.path.join(output_dir, config.get('log_file', 'analysis.log'))
    
    # Setup directories
    setup_output_directory(output_dir)
    setup_output_directory(fragments_dir)
    
    # Clear log file
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # Step 1: Extract Metadata
    print_colored("\n" + "="*60, Colors.HEADER)
    print_colored("STEP 1: METADATA EXTRACTION", Colors.HEADER)
    print_colored("="*60, Colors.HEADER)
    
    log_message("Starting metadata extraction...", log_file, verbose)
    metadata_output = os.path.join(output_dir, 'metadata.json')
    results['metadata'] = metadata_extractor.extract_metadata(
        image_path,
        verbose=verbose,
        output_file=metadata_output
    )
    
    if results['metadata']:
        log_message("✓ Metadata extraction complete", log_file, verbose)
    else:
        log_message("✗ Metadata extraction failed", log_file, verbose)
    
    # Step 2: LSB Extraction from RGB channels
    print_colored("\n" + "="*60, Colors.HEADER)
    print_colored("STEP 2: LSB EXTRACTION (RGB CHANNELS)", Colors.HEADER)
    print_colored("="*60, Colors.HEADER)
    
    for channel in ['red', 'green', 'blue']:
        log_message(f"Extracting LSB from {channel.upper()} channel...", log_file, verbose)
        lsb_output = os.path.join(output_dir, f'lsb_{channel}.txt')
        
        channel_results = lsb_extractor.extract_lsb_from_channel(
            image_path,
            channel=channel,
            verbose=verbose,
            output_file=lsb_output
        )
        
        if channel_results and channel in channel_results:
            results['lsb'][channel] = channel_results[channel]
            
            # Save as potential fragment
            ascii_text = channel_results[channel].get('ascii_text', '')
            if ascii_text and len(ascii_text) > 10:
                fragment_file = os.path.join(fragments_dir, f'fragment_lsb_{channel}.txt')
                with open(fragment_file, 'w') as f:
                    f.write(ascii_text)
                results['fragments'].append({
                    'source': f'lsb_{channel}',
                    'data': ascii_text,
                    'file': fragment_file
                })
                log_message(f"✓ Fragment saved from {channel} channel", log_file, verbose)
    
    # Step 3: Spiral Pattern Reading
    print_colored("\n" + "="*60, Colors.HEADER)
    print_colored("STEP 3: SPIRAL PATTERN READING", Colors.HEADER)
    print_colored("="*60, Colors.HEADER)
    
    spiral_directions = ['clockwise', 'counterclockwise']
    for direction in spiral_directions:
        log_message(f"Reading spiral pattern ({direction})...", log_file, verbose)
        spiral_output = os.path.join(output_dir, f'spiral_{direction}.txt')
        
        spiral_results = spiral_reader.read_spiral_lsb(
            image_path,
            clockwise=(direction == 'clockwise'),
            channel='all',
            verbose=verbose,
            output_file=spiral_output
        )
        
        if spiral_results:
            results['spiral'][direction] = spiral_results
            
            # Check each channel for potential fragments
            for channel, data in spiral_results.items():
                ascii_text = data.get('ascii_text', '')
                if ascii_text and len(ascii_text) > 10:
                    fragment_file = os.path.join(fragments_dir, f'fragment_spiral_{direction}_{channel}.txt')
                    with open(fragment_file, 'w') as f:
                        f.write(ascii_text)
                    results['fragments'].append({
                        'source': f'spiral_{direction}_{channel}',
                        'data': ascii_text,
                        'file': fragment_file
                    })
    
    # Step 4: Decode fragments (Base64, ROT-13)
    print_colored("\n" + "="*60, Colors.HEADER)
    print_colored("STEP 4: DECODING FRAGMENTS", Colors.HEADER)
    print_colored("="*60, Colors.HEADER)
    
    decoded_fragments = []
    for fragment in results['fragments']:
        log_message(f"Decoding fragment from {fragment['source']}...", log_file, verbose)
        
        # Try auto-detection
        decode_results = decoder.auto_detect_and_decode(fragment['data'], verbose=verbose)
        
        if decode_results:
            for method, decoded in decode_results.items():
                decoded_file = os.path.join(fragments_dir, f"decoded_{fragment['source']}_{method}.txt")
                with open(decoded_file, 'w') as f:
                    f.write(decoded)
                decoded_fragments.append({
                    'source': fragment['source'],
                    'method': method,
                    'data': decoded,
                    'file': decoded_file
                })
                log_message(f"✓ Decoded using {method}", log_file, verbose)
    
    # Step 5: Fragment Assembly
    print_colored("\n" + "="*60, Colors.HEADER)
    print_colored("STEP 5: FRAGMENT ASSEMBLY", Colors.HEADER)
    print_colored("="*60, Colors.HEADER)
    
    if decoded_fragments or results['fragments']:
        # Combine all fragment data
        all_fragment_data = [f['data'] for f in decoded_fragments]
        if not all_fragment_data:
            all_fragment_data = [f['data'] for f in results['fragments']]
        
        assembled = fragment_assembler.assemble_fragments(all_fragment_data, verbose=verbose)
        
        # Try to decrypt using image name as key
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        log_message(f"Attempting decryption with key: {image_name}", log_file, verbose)
        
        final_result = fragment_assembler.decrypt_final(
            assembled,
            image_name,
            method='auto',
            verbose=verbose
        )
        
        if final_result:
            results['final_flag'] = final_result
            final_output = os.path.join(output_dir, 'final_flag.txt')
            with open(final_output, 'w') as f:
                f.write(final_result)
            log_message(f"✓ Final flag saved to {final_output}", log_file, verbose)
    
    return results


def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(
        description='Digital Ghost Forensics Analyzer - Master orchestration script',
        epilog='For detailed usage of individual modules, run them separately with --help'
    )
    parser.add_argument(
        'image',
        help='Path to the image file to analyze'
    )
    parser.add_argument(
        '-c', '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '-o', '--output-dir',
        help='Output directory (overrides config)'
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
    
    # Load configuration
    config = {
        'output_directory': 'output',
        'fragments_directory': 'fragments',
        'log_file': 'analysis.log',
        'verbose': False
    }
    
    if os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config.update(json.load(f))
    
    # Override with command line args
    if args.output_dir:
        config['output_directory'] = args.output_dir
    if args.verbose:
        config['verbose'] = True
    
    # Print banner
    print_banner()
    
    # Check if image exists
    if not os.path.exists(args.image):
        print_colored(f"Error: Image file '{args.image}' not found", Colors.FAIL)
        return 1
    
    print_colored(f"\nAnalyzing: {args.image}", Colors.OKCYAN)
    print_colored(f"Output directory: {config['output_directory']}", Colors.OKCYAN)
    
    # Run analysis
    try:
        results = run_complete_analysis(args.image, config, verbose=args.verbose)
        
        # Print summary
        print_colored("\n" + "="*60, Colors.HEADER)
        print_colored("ANALYSIS SUMMARY", Colors.HEADER)
        print_colored("="*60, Colors.HEADER)
        
        print_colored(f"\n✓ Metadata extracted: {'Yes' if results['metadata'] else 'No'}", Colors.OKGREEN)
        print_colored(f"✓ LSB channels analyzed: {len(results['lsb'])}", Colors.OKGREEN)
        print_colored(f"✓ Spiral patterns read: {len(results['spiral'])}", Colors.OKGREEN)
        print_colored(f"✓ Fragments collected: {len(results['fragments'])}", Colors.OKGREEN)
        
        if results['final_flag']:
            print_colored("\n" + "="*60, Colors.HEADER)
            print_colored("FINAL FLAG DISCOVERED!", Colors.HEADER)
            print_colored("="*60, Colors.HEADER)
            print_colored(f"\n{results['final_flag']}\n", Colors.BOLD + Colors.OKGREEN)
        
        print_colored(f"\nResults saved to: {config['output_directory']}/", Colors.OKCYAN)
        print_colored("\n✓ Analysis complete!", Colors.OKGREEN)
        
        return 0
        
    except Exception as e:
        print_colored(f"\n✗ Analysis failed: {str(e)}", Colors.FAIL)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
