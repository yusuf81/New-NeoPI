"""Command line interface for neopi."""

import argparse
import os
import re
import time
import csv
from typing import List, Dict, Any
from .search import SearchFile
from .tests import (
    Test,
    LanguageIC, Entropy, LongestWord,
    SignatureNasty, SignatureSuperNasty, UsesEval,
    Compression
)

def create_arg_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Utility to scan a file path for encrypted and obfuscated files"
    )

    # Required arguments
    parser.add_argument(
        "directory",
        help="Start directory"
    )
    parser.add_argument(
        "regex",
        nargs="?",
        help="Filename regex",
        default=".*"
    )
    parser.add_argument(
        "-c",
        "--csv",
        help="Generate CSV outfile",
        metavar="FILECSV"
    )
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Run all (useful) tests [Entropy, Longest Word, IC, Signature]"
    )
    parser.add_argument(
        "-z", "--zlib",
        action="store_true",
        help="Run compression Test"
    )
    parser.add_argument(
        "-e", "--entropy",
        action="store_true",
        help="Run entropy Test"
    )
    parser.add_argument(
        "-E", "--eval",
        action="store_true",
        help="Run signature test for the eval"
    )
    parser.add_argument(
        "-l", "--longestword",
        action="store_true",
        help="Run longest word test"
    )
    parser.add_argument("-i", "--ic", action="store_true", help="Run IC test")
    parser.add_argument("-s", "--signature", action="store_true", help="Run signature test")
    parser.add_argument("-S", "--supersignature", action="store_true", help="Run SUPER-signature test")
    parser.add_argument("-u", "--unicode", action="store_true", help="Skip over unicode-y/UTF'y files")
    parser.add_argument("-f", "--follow-links", action="store_true", help="Follow symbolic links")
    parser.add_argument(
        "-m", "--alarm-mode",
        type=float,
        help="Alarm mode outputs flags only files with high deviation"
    )
    parser.add_argument(
        "-b", "--block-mode",
        type=int,
        help="Block mode calculates the tests selected for the specified block sizes in each file"
    )
    return parser.parse_args()

def get_tests(args: argparse.Namespace) -> List[Test]:
    """Get list of tests to run based on arguments."""
    test_map = {
        'entropy': Entropy,
        'longestword': LongestWord,
        'ic': LanguageIC,
        'signature': SignatureNasty,
        'supersignature': SignatureSuperNasty,
        'eval': UsesEval,
        'zlib': Compression
    }

    tests = []
    if args.all:
        tests.extend([
            LanguageIC(), Entropy(), LongestWord(),
            SignatureNasty(), SignatureSuperNasty()
        ])
        return tests

    for arg_name, test_class in test_map.items():
        if getattr(args, arg_name, False):
            tests.append(test_class())

    return tests

def write_csv(filename: str, header: List[str], rows: List[List[Any]]) -> None:
    """Write results to CSV file."""
    with open(filename, "w", newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(rows)

def process_file(data: bytes, filename: str, tests: List[Test], args: argparse.Namespace) -> List[Any]:
    """Process a single file with all tests."""
    if args.unicode:
        try:
            text_data = data.decode('utf-8')
            ascii_high_count = sum(1 for c in text_data if ord(c) > 127)
            file_ascii_ratio = float(ascii_high_count) / float(len(text_data))
            if file_ascii_ratio >= 0.1:
                return []
        except (UnicodeDecodeError, ValueError):
            pass

    csv_row = [filename]

    for test in tests:
        if args.block_mode:
            result = test.block_calculate(args.block_mode, data, filename)
            csv_row.extend([result["value"], result["position"]])
        else:
            result = test.calculate(data, filename)
            csv_row.append(result)

    return csv_row

def print_summary(file_count: int, file_ignore_count: int, scan_time: float) -> None:
    """Print summary statistics."""
    print(f"\n[[ Total files scanned: {file_count} ]]")
    print(f"[[ Total files ignored: {file_ignore_count} ]]")
    print(f"[[ Scan Time: {scan_time:.2f} seconds ]]")

def print_results(tests: List[Test], rank_list: Dict[str, float], args: argparse.Namespace) -> None:
    """Print test results and rankings."""
    for test in tests:
        if args.alarm_mode:
            print(f"Flagged files for: {test.__class__.__name__}")
            test.flag_alarm(args.alarm_mode)
        else:
            test.sort()
            test.printer(10, args.block_mode)
            for file in test.results:
                rank_list[file["filename"]] = rank_list.get(file["filename"], 0) + file["rank"]

    if not args.alarm_mode:
        rank_sorted = sorted(rank_list.items(), key=lambda x: x[1])
        print("\n[[ Top cumulative ranked files ]]")
        count = min(10, len(rank_sorted))
        for idx in range(count):
            print(f' {rank_sorted[idx][1]:>7}        {rank_sorted[idx][0]}')

def process_files(args, tests, valid_regex) -> tuple:
    """Process all files and collect results."""
    locator = SearchFile(args.follow_links)
    csv_array = []
    csv_header = ["filename"]
    file_count = 0
    file_ignore_count = 0

    # Setup CSV headers
    for test in tests:
        csv_header.append(test.__class__.__name__)
        if args.block_mode:
            csv_header.append("position")

    # Process files
    for data, filename in locator.search_file_path([args.directory], valid_regex):
        if not data:
            continue

        csv_row = process_file(data, filename, tests, args)
        if csv_row:
            csv_array.append(csv_row)
            file_count += 1
        else:
            file_ignore_count += 1

    return csv_array, csv_header, file_count, file_ignore_count

def main() -> int:
    """Main entry point for CLI."""
    print("""
   yusuf81-modified-neopi
   """)

    args = create_arg_parser()

    # Validate inputs
    if not os.path.exists(args.directory):
        print("Error: Invalid path")
        return 1

    try:
        valid_regex = re.compile(args.regex)
    except re.error:
        print("Error: Invalid regular expression")
        return 1

    tests = get_tests(args)
    if not tests:
        print("Error: No tests specified")
        return 1

    rank_list: Dict[str, float] = {}
    time_start = time.time()
    
    # Process all files
    csv_array, csv_header, file_count, file_ignore_count = process_files(
        args, tests, valid_regex
    )

    # Write results
    if args.csv:
        write_csv(args.csv, csv_header, csv_array)

    # Print results
    scan_time = time.time() - time_start
    print_summary(file_count, file_ignore_count, scan_time)
    print_results(tests, rank_list, args)

    return 0
