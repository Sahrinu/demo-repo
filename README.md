# Digital Ghost Forensics Toolkit

A comprehensive steganography analysis toolkit designed to solve multi-layer image forensics challenges. This toolkit provides various techniques for extracting hidden data from images including metadata extraction, LSB (Least Significant Bit) analysis, spiral pattern reading, and multi-layer decoding.

## Features

- **Metadata Extraction**: Extract EXIF and metadata from images
- **LSB Analysis**: Extract LSB from individual RGB channels
- **Spiral Pattern Reading**: Read pixel data in spiral patterns from center outward
- **Multi-Layer Decoding**: Base64 and ROT-13 cipher decryption
- **Fragment Assembly**: Collect and assemble fragments with encryption support
- **Automated Analysis**: Master script to orchestrate all techniques
- **Verbose Logging**: Track progress with detailed logging
- **Color-Coded Output**: Enhanced terminal readability

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone or download this repository
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

The following packages will be installed:
- `Pillow` - Image processing library
- `piexif` - EXIF metadata handling
- `cryptography` - Encryption/decryption support

## Usage

### Quick Start - Complete Analysis

Run the master analyzer to perform all analysis techniques automatically:

```bash
python digital_ghost_analyzer.py image.png
```

With verbose output:

```bash
python digital_ghost_analyzer.py image.png -v
```

With custom output directory:

```bash
python digital_ghost_analyzer.py image.png -o my_results
```

### Individual Module Usage

Each module can be run independently for targeted analysis:

#### 1. Metadata Extraction

Extract all metadata and EXIF data from an image:

```bash
# Basic usage
python metadata_extractor.py image.png

# Verbose output
python metadata_extractor.py image.png -v

# Save metadata to JSON file
python metadata_extractor.py image.png -o metadata.json -v
```

**What it does:**
- Extracts file properties (name, size, format)
- Retrieves image dimensions and mode
- Extracts EXIF data if available
- Looks for hidden text in metadata fields

#### 2. LSB Extraction

Extract Least Significant Bits from color channels:

```bash
# Extract from all channels
python lsb_extractor.py image.png -v

# Extract from specific channel
python lsb_extractor.py image.png --channel red -v
python lsb_extractor.py image.png --channel green -v
python lsb_extractor.py image.png --channel blue -v

# Save results to file
python lsb_extractor.py image.png --channel red -o lsb_red.txt -v
```

**What it does:**
- Extracts LSB from red, green, and blue channels separately
- Converts binary data to ASCII text
- Automatically attempts Base64 decoding
- Identifies potentially corrupted channels

#### 3. Decoder

Decode Base64 and ROT-13 encoded data:

```bash
# Auto-detect encoding
python decoder.py "SGVsbG8gV29ybGQ=" -v

# Decode from file
python decoder.py -f encoded_data.txt -v

# Specific decoding type
python decoder.py "data" --type base64 -v
python decoder.py "data" --type rot13 -v

# Multi-layer decoding
python decoder.py "data" --layers base64,rot13 -v

# Save decoded output
python decoder.py -f input.txt -o output.txt -v
```

**What it does:**
- Decodes Base64 encoded strings
- Applies ROT-13 cipher decryption
- Supports multiple encoding layers
- Auto-detects encoding types
- Handles corrupted data gracefully

#### 4. Spiral Reader

Read pixel data in spiral patterns from center outward:

```bash
# Clockwise spiral (default)
python spiral_reader.py image.png -v

# Counter-clockwise spiral
python spiral_reader.py image.png --direction counterclockwise -v

# Specific channel
python spiral_reader.py image.png --channel red -v

# Save results
python spiral_reader.py image.png -o spiral_data.txt -v
```

**What it does:**
- Generates spiral coordinates from image center
- Supports clockwise and counter-clockwise directions
- Extracts LSB from pixels in spiral order
- Converts binary data to ASCII

#### 5. Fragment Assembler

Assemble fragments and perform final decryption:

```bash
# Assemble fragments from directory
python fragment_assembler.py -d fragments/ -v

# Assemble specific fragments
python fragment_assembler.py -f fragment1.txt fragment2.txt fragment3.txt -v

# With decryption key
python fragment_assembler.py -d fragments/ -k "mykey" -v

# Specify encryption method
python fragment_assembler.py -d fragments/ -k "mykey" -m xor -v
python fragment_assembler.py -d fragments/ -k "mykey" -m aes -v

# Custom fragment order
python fragment_assembler.py -d fragments/ --order 1,3,2,4 -v

# Save result
python fragment_assembler.py -d fragments/ -k "mykey" --output final.txt -v
```

**What it does:**
- Collects fragments from files or directory
- Assembles in specified or natural order
- Supports AES and XOR decryption
- Auto-detects best decryption method
- Generates final decrypted output

## Configuration

Edit `config.json` to customize default settings:

```json
{
    "image_path": "digital_ghost_challenge.png",
    "output_directory": "output",
    "fragments_directory": "fragments",
    "verbose": true,
    "log_file": "analysis.log",
    "lsb_channels": ["red", "green", "blue"],
    "spiral_direction": "clockwise",
    "encryption_methods": ["AES", "XOR"],
    "color_output": true
}
```

## Output Structure

After running the analyzer, you'll find:

```
output/
├── analysis.log              # Detailed analysis log
├── metadata.json             # Extracted metadata
├── lsb_red.txt              # LSB data from red channel
├── lsb_green.txt            # LSB data from green channel
├── lsb_blue.txt             # LSB data from blue channel
├── spiral_clockwise.txt     # Clockwise spiral data
├── spiral_counterclockwise.txt
└── final_flag.txt           # Final assembled/decrypted result

fragments/
├── fragment_lsb_red.txt     # Fragment from red channel
├── fragment_lsb_green.txt   # Fragment from green channel
├── fragment_lsb_blue.txt    # Fragment from blue channel
├── decoded_*.txt            # Decoded fragments
└── ...
```

## Digital Ghost Challenge - Solving Guide

The Digital Ghost challenge involves multiple layers of hidden data:

### Layer 1: Metadata
- Check image metadata and EXIF data for hidden clues
- Look for suspicious text in metadata fields

### Layer 2: LSB Steganography
- Extract LSB from RGB channels separately
- Red, green, or blue channel may contain different fragments
- One channel might be corrupted (incomplete data)

### Layer 3: Base64 Encoding
- Extracted data is likely Base64 encoded
- Decode to reveal intermediate fragments

### Layer 4: ROT-13 Cipher
- Decoded Base64 data may use ROT-13 cipher
- Apply ROT-13 decryption to reveal readable text

### Layer 5: Spiral Pattern
- Hidden data might be arranged in spiral pattern
- Read from center outward in clockwise/counter-clockwise direction

### Layer 6: Final Assembly
- Collect all fragments from different techniques
- Assemble in correct order
- Decrypt using key (often image filename + discovered word)

### Typical Workflow:

```bash
# Step 1: Run complete analysis
python digital_ghost_analyzer.py digital_ghost_challenge.png -v

# Step 2: Check output directory for discovered fragments
ls output/
ls fragments/

# Step 3: If needed, manually assemble specific fragments
python fragment_assembler.py -d fragments/ -k "digital_ghost_challenge" -v

# Step 4: Review final_flag.txt for the solution
cat output/final_flag.txt
```

## Command-Line Options

### Common Options (All Scripts)

- `-v, --verbose`: Enable verbose output with detailed information
- `--no-color`: Disable colored terminal output
- `-o, --output`: Specify output file path

### Script-Specific Options

**metadata_extractor.py:**
- `image`: Path to image file (required)

**lsb_extractor.py:**
- `image`: Path to image file (required)
- `-c, --channel {red,green,blue,all}`: Channel to extract (default: all)

**decoder.py:**
- `input`: Data to decode or '-' for stdin
- `-f, --file`: Read input from file
- `-t, --type {base64,rot13,auto}`: Decoding type (default: auto)
- `-l, --layers`: Comma-separated encoding layers (e.g., "base64,rot13")

**spiral_reader.py:**
- `image`: Path to image file (required)
- `-d, --direction {clockwise,counterclockwise}`: Spiral direction
- `-c, --channel {red,green,blue,all}`: Channel to extract (default: all)

**fragment_assembler.py:**
- `-f, --fragments`: Fragment strings or file paths
- `-d, --directory`: Directory containing fragment files
- `-k, --key`: Decryption key
- `-m, --method {aes,xor,auto}`: Decryption method (default: auto)
- `-o, --order`: Comma-separated fragment order

**digital_ghost_analyzer.py:**
- `image`: Path to image file (required)
- `-c, --config`: Configuration file path (default: config.json)
- `-o, --output-dir`: Output directory (overrides config)

## Examples

### Example 1: Complete Analysis

```bash
python digital_ghost_analyzer.py challenge.png -v
```

### Example 2: Manual Step-by-Step Analysis

```bash
# Extract metadata
python metadata_extractor.py challenge.png -v -o metadata.json

# Extract LSB from each channel
python lsb_extractor.py challenge.png --channel red -v -o lsb_red.txt
python lsb_extractor.py challenge.png --channel green -v -o lsb_green.txt
python lsb_extractor.py challenge.png --channel blue -v -o lsb_blue.txt

# Try spiral patterns
python spiral_reader.py challenge.png -v -o spiral.txt

# Decode any Base64 data found
python decoder.py -f lsb_red.txt -t base64 -v -o decoded_red.txt

# Assemble and decrypt
python fragment_assembler.py -f decoded_red.txt decoded_green.txt -k "challenge" -v
```

### Example 3: Testing Different Spiral Directions

```bash
python spiral_reader.py image.png --direction clockwise --channel red -v
python spiral_reader.py image.png --direction counterclockwise --channel red -v
```

## Troubleshooting

**Issue: "Module not found" error**
- Ensure all dependencies are installed: `pip install -r requirements.txt`

**Issue: "File not found" error**
- Check that the image path is correct
- Use absolute paths if relative paths don't work

**Issue: No fragments discovered**
- The image may not contain steganographic data
- Try different channels and patterns
- Check metadata for clues

**Issue: Decryption fails**
- Verify the decryption key is correct
- Try different encryption methods (AES vs XOR)
- Check if fragments are in correct order

## Technical Details

### LSB Extraction Algorithm
- Extracts the least significant bit from each pixel's color channel
- Assembles bits into bytes (8 bits per byte)
- Converts bytes to ASCII text when possible
- Identifies null terminators as potential end markers

### Spiral Pattern Algorithm
- Starts from center pixel (width/2, height/2)
- Moves outward in expanding square spiral
- Supports both clockwise and counter-clockwise directions
- Covers all pixels in the image

### Supported Image Formats
- PNG (recommended for lossless steganography)
- JPG/JPEG (may lose hidden data due to compression)
- BMP (lossless, good for steganography)
- Other formats supported by Pillow

### Encryption Support
- **XOR**: Simple XOR cipher with key repetition
- **AES**: AES-CBC with key derivation and PKCS7 padding
- **Auto**: Attempts both methods and selects best result

## Contributing

Feel free to extend this toolkit with additional steganography techniques:
- Implement additional LSB patterns
- Add support for more encryption algorithms
- Implement frequency analysis
- Add visual analysis tools

## License

This toolkit is provided for educational and forensics analysis purposes.

## Author

Digital Ghost Forensics Toolkit
Created for steganography analysis and CTF challenges.
