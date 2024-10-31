# neopi

A Python utility to scan files for signs of encryption, obfuscation, and potentially malicious code patterns.

## Features

- Multiple analysis methods:
  - Entropy analysis to detect encryption/compression
  - Index of Coincidence for language detection
  - Longest word/string detection
  - Compression ratio analysis
  - Signature-based pattern matching for suspicious code
  - Specific eval() usage detection

- Flexible file selection:
  - Recursive directory scanning
  - Regex-based filename filtering
  - Optional symlink following
  - Unicode file handling

- Analysis modes:
  - Standard mode with ranked results
  - Block mode for analyzing file segments
  - Alarm mode to flag statistical outliers
  - CSV output option

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/neopi.git
cd neopi

# Install dependencies
pip install -r requirements.txt
```

## Usage

Basic usage:
```bash
python -m neopi /path/to/scan "*.php"
```

Common options:
```bash
# Run all tests
python -m neopi /path/to/scan -a

# Run specific tests
python -m neopi /path/to/scan -e -s -l  # entropy, signatures, longest word

# Block mode analysis (1024 byte blocks)
python -m neopi /path/to/scan -a -b 1024

# Generate CSV output
python -m neopi /path/to/scan -a -c results.csv

# Alarm mode (flag statistical outliers)
python -m neopi /path/to/scan -a -m 1.5
```

### Available Tests

- `-e, --entropy`: Shannon entropy analysis
- `-i, --ic`: Index of Coincidence for language detection
- `-l, --longestword`: Longest word/string detection
- `-z, --zlib`: Compression ratio analysis
- `-s, --signature`: Basic signature pattern matching
- `-S, --supersignature`: Advanced signature pattern matching
- `-E, --eval`: Specific eval() usage detection
- `-a, --all`: Run all useful tests

### Additional Options

- `-u, --unicode`: Skip files with high Unicode content
- `-f, --follow-links`: Follow symbolic links
- `-b BLOCK_SIZE, --block-mode BLOCK_SIZE`: Analyze in blocks
- `-m THRESHOLD, --alarm-mode THRESHOLD`: Flag statistical outliers
- `-c FILE, --csv FILE`: Generate CSV output

## Output

The tool provides:
- Ranked results for each test
- Cumulative rankings across all tests
- File counts and scan timing
- Optional CSV output
- Block positions for block mode
- Statistical outlier flags in alarm mode

## License

See LICENSE file for details.

## Credits

Originally created by:
- Ben Hagen (ben.hagen@neohapsis.com)
- Scott Behrens (scott.behrens@neohapsis.com)

Modified for Python 3 compatibility and enhanced features.
