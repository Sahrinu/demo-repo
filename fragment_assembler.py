#!/usr/bin/env python3
"""
Fragment Assembler for Digital Ghost Challenge
Collects and assembles fragments, performs final decryption.
"""

import argparse
import sys
import os
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64
import hashlib


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


def xor_decrypt(data, key):
    """
    XOR decryption
    
    Args:
        data: Data to decrypt (bytes or string)
        key: Encryption key (bytes or string)
    
    Returns:
        bytes: Decrypted data
    """
    if isinstance(data, str):
        data = data.encode()
    if isinstance(key, str):
        key = key.encode()
    
    # Repeat key to match data length
    key_repeated = (key * (len(data) // len(key) + 1))[:len(data)]
    
    # XOR operation
    decrypted = bytes([d ^ k for d, k in zip(data, key_repeated)])
    return decrypted


def aes_decrypt(encrypted_data, key, iv=None):
    """
    AES decryption
    
    Args:
        encrypted_data: Encrypted data (bytes)
        key: Encryption key (bytes or string)
        iv: Initialization vector (optional, will be derived from key if not provided)
    
    Returns:
        bytes: Decrypted data
    """
    if isinstance(key, str):
        key = key.encode()
    
    # Ensure key is correct length (16, 24, or 32 bytes for AES)
    if len(key) < 16:
        key = key.ljust(16, b'\0')
    elif len(key) < 24:
        key = key[:16]
    elif len(key) < 32:
        key = key.ljust(24, b'\0')
    else:
        key = key[:32]
    
    # Use provided IV or generate from key using SHA-256 (more secure than MD5)
    if iv is None:
        import hashlib
        iv = hashlib.sha256(key).digest()[:16]  # AES block size is 16 bytes
    
    # Decrypt
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
    
    # Remove padding
    try:
        unpadder = padding.PKCS7(128).unpadder()
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
        return decrypted
    except:
        # If unpadding fails, return as is
        return decrypted_padded


def assemble_fragments(fragments, order=None, verbose=False):
    """
    Assemble fragments in correct order
    
    Args:
        fragments: List of fragment strings or dict with fragment names
        order: Optional list specifying the order of fragments
        verbose: Enable verbose logging
    
    Returns:
        str: Assembled string
    """
    if verbose:
        print_colored("\n=== ASSEMBLING FRAGMENTS ===", Colors.HEADER)
    
    # If fragments is a dict, extract values
    if isinstance(fragments, dict):
        if order:
            # Use specified order
            ordered_fragments = [fragments.get(key, '') for key in order]
        else:
            # Use natural order of keys
            ordered_fragments = [fragments[key] for key in sorted(fragments.keys())]
    else:
        # Fragments is already a list
        ordered_fragments = fragments
    
    # Assemble
    assembled = ''.join(str(f) for f in ordered_fragments if f)
    
    if verbose:
        print_colored(f"Assembled {len(ordered_fragments)} fragments", Colors.OKBLUE)
        print_colored(f"Total length: {len(assembled)} characters", Colors.OKBLUE)
        print_colored(f"Preview: {assembled[:200]}", Colors.OKGREEN)
    
    return assembled


def decrypt_final(encrypted_data, key, method='auto', verbose=False):
    """
    Perform final decryption using specified method
    
    Args:
        encrypted_data: Encrypted data (string or bytes)
        key: Encryption key
        method: Encryption method ('aes', 'xor', 'auto')
        verbose: Enable verbose logging
    
    Returns:
        str: Decrypted string or None if decryption fails
    """
    if verbose:
        print_colored("\n=== FINAL DECRYPTION ===", Colors.HEADER)
        print_colored(f"Method: {method}", Colors.OKBLUE)
        print_colored(f"Key: {key}", Colors.OKBLUE)
    
    results = {}
    
    # Convert encrypted_data to bytes if needed
    if isinstance(encrypted_data, str):
        try:
            # Try to decode as base64 first
            encrypted_bytes = base64.b64decode(encrypted_data)
        except:
            encrypted_bytes = encrypted_data.encode()
    else:
        encrypted_bytes = encrypted_data
    
    if method == 'xor' or method == 'auto':
        try:
            decrypted = xor_decrypt(encrypted_bytes, key)
            decrypted_str = decrypted.decode('utf-8', errors='ignore')
            results['xor'] = decrypted_str
            if verbose:
                print_colored(f"\nXOR decryption result: {decrypted_str[:200]}", Colors.OKGREEN)
        except Exception as e:
            if verbose:
                print_colored(f"XOR decryption failed: {str(e)}", Colors.WARNING)
    
    if method == 'aes' or method == 'auto':
        try:
            decrypted = aes_decrypt(encrypted_bytes, key)
            decrypted_str = decrypted.decode('utf-8', errors='ignore')
            results['aes'] = decrypted_str
            if verbose:
                print_colored(f"\nAES decryption result: {decrypted_str[:200]}", Colors.OKGREEN)
        except Exception as e:
            if verbose:
                print_colored(f"AES decryption failed: {str(e)}", Colors.WARNING)
    
    # Return best result
    if method == 'auto':
        # Return the result that looks most like readable text
        for method_name, result in results.items():
            if result and any(c.isalpha() for c in result):
                if verbose:
                    print_colored(f"\nBest result from {method_name}", Colors.OKGREEN)
                return result
        # If no good result, return first available
        return list(results.values())[0] if results else None
    else:
        return results.get(method)


def load_fragments_from_directory(directory, verbose=False):
    """
    Load all fragment files from a directory
    
    Args:
        directory: Path to fragments directory
        verbose: Enable verbose logging
    
    Returns:
        dict: Fragment name to content mapping
    """
    fragments = {}
    
    if not os.path.exists(directory):
        if verbose:
            print_colored(f"Directory {directory} not found", Colors.WARNING)
        return fragments
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            try:
                with open(filepath, 'r', errors='replace') as f:
                    content = f.read()
                    fragments[filename] = content
                    if verbose:
                        print_colored(f"Loaded fragment: {filename} ({len(content)} chars)", Colors.OKBLUE)
            except Exception as e:
                if verbose:
                    print_colored(f"Warning: Failed to load {filename}: {str(e)}", Colors.WARNING)
    
    return fragments


def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(
        description='Assemble fragments and perform final decryption'
    )
    parser.add_argument(
        '-f', '--fragments',
        nargs='+',
        help='Fragment strings or file paths'
    )
    parser.add_argument(
        '-d', '--directory',
        help='Directory containing fragment files'
    )
    parser.add_argument(
        '-k', '--key',
        help='Decryption key'
    )
    parser.add_argument(
        '-m', '--method',
        choices=['aes', 'xor', 'auto'],
        default='auto',
        help='Decryption method (default: auto)'
    )
    parser.add_argument(
        '-o', '--order',
        help='Comma-separated fragment order (e.g., "1,3,2,4")'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--output',
        help='Save decrypted result to file'
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
    
    print_colored("=== FRAGMENT ASSEMBLER ===", Colors.HEADER)
    
    # Load fragments
    fragments = []
    if args.directory:
        fragment_dict = load_fragments_from_directory(args.directory, verbose=args.verbose)
        fragments = list(fragment_dict.values())
    elif args.fragments:
        for frag in args.fragments:
            if os.path.isfile(frag):
                with open(frag, 'r') as f:
                    fragments.append(f.read())
            else:
                fragments.append(frag)
    else:
        print_colored("Error: No fragments provided", Colors.FAIL)
        parser.print_help()
        return 1
    
    if not fragments:
        print_colored("Error: No fragments found", Colors.FAIL)
        return 1
    
    # Parse order if provided
    order = None
    if args.order:
        order = [int(x.strip()) for x in args.order.split(',')]
    
    # Assemble fragments
    assembled = assemble_fragments(fragments, order=order, verbose=args.verbose)
    
    if not assembled:
        print_colored("Error: Assembly failed", Colors.FAIL)
        return 1
    
    # Decrypt if key provided
    result = assembled
    if args.key:
        result = decrypt_final(assembled, args.key, method=args.method, verbose=args.verbose)
        if not result:
            print_colored("Warning: Decryption failed, returning assembled data", Colors.WARNING)
            result = assembled
    
    # Display result
    print_colored("\n=== FINAL RESULT ===", Colors.HEADER)
    print_colored(result, Colors.OKGREEN)
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            f.write(result)
        print_colored(f"\n✓ Result saved to {args.output}", Colors.OKGREEN)
    
    print_colored("\n✓ Assembly complete", Colors.OKGREEN)
    return 0


if __name__ == '__main__':
    sys.exit(main())
