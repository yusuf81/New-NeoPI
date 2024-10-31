"""Command line interface for neopi."""

import argparse
import os
import re
import time
import csv
from .search import SearchFile
from .tests import (
    LanguageIC, Entropy, LongestWord, 
    SignatureNasty, SignatureSuperNasty, UsesEval,
    Compression
)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Utility to scan a file path for encrypted and obfuscated files"
    )
    parser.add_argument("directory", help="Start directory")
    parser.add_argument("regex", nargs="?", help="Filename regex", default=".*")
    parser.add_argument("-c", "--csv", help="Generate CSV outfile", metavar="FILECSV")
    parser.add_argument("-a", "--all", action="store_true",
                       help="Run all (useful) tests [Entropy, Longest Word, IC, Signature]")
    parser.add_argument("-z", "--zlib", action="store_true", help="Run compression Test")
    parser.add_argument("-e", "--entropy", action="store_true", help="Run entropy Test")
    parser.add_argument("-E", "--eval", action="store_true", help="Run signature test for the eval")
    parser.add_argument("-l", "--longestword", action="store_true", help="Run longest word test")
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

def get_tests(args):
    """Get list of tests to run based on arguments."""
    tests = []
    if args.all:
        tests.extend([
            LanguageIC(), Entropy(), LongestWord(),
            SignatureNasty(), SignatureSuperNasty()
        ])
    else:
        if args.entropy:
            tests.append(Entropy())
        if args.longestword:
            tests.append(LongestWord())
        if args.ic:
            tests.append(LanguageIC())
        if args.signature:
            tests.append(SignatureNasty())
        if args.supersignature:
            tests.append(SignatureSuperNasty())
        if args.eval:
            tests.append(UsesEval())
        if args.zlib:
            tests.append(Compression())
    return tests

def write_csv(filename, header, rows):
    """Write results to CSV file."""
    with open(filename, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

def main():
    """Main entry point for CLI."""
    print("""
   yusuf81-modified-neopi
   """)

    args = parse_args()

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

    locator = SearchFile(args.follow_links)
    csv_array = []
    csv_header = ["filename"]

    file_count = 0
    file_ignore_count = 0
    time_start = time.time()

    for test in tests:
        csv_header.append(test.__class__.__name__)
        if args.block_mode:
            csv_header.append("position")

    for data, filename in locator.search_file_path([args.directory], valid_regex):
        if not data:
            continue

        csv_row = [filename]
        
        if args.unicode:
            try:
                text_data = data.decode('utf-8')
                ascii_high_count = sum(1 for c in text_data if ord(c) > 127)
                file_ascii_ratio = float(ascii_high_count) / float(len(text_data))
                if file_ascii_ratio >= 0.1:
                    file_ignore_count += 1
                    continue
            except (UnicodeDecodeError, ValueError):
                pass

        for test in tests:
            if args.block_mode:
                result = test.block_calculate(args.block_mode, data, filename)
                csv_row.extend([result["value"], result["position"]])
            else:
                result = test.calculate(data, filename)
                csv_row.append(result)
        
        csv_array.append(csv_row)
        file_count += 1

    if args.csv:
        write_csv(args.csv, csv_header, csv_array)

    time_finish = time.time()
    scan_time = time_finish - time_start

    print(f"\n[[ Total files scanned: {file_count} ]]")
    print(f"[[ Total files ignored: {file_ignore_count} ]]")
    print(f"[[ Scan Time: {scan_time:.2f} seconds ]]")

    rank_list = {}
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
        for x in range(count):
            print(f' {rank_sorted[x][1]:>7}        {rank_sorted[x][0]}')

    return 0
