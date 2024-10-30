#!/usr/bin/env python3

"""
Utility to scan a file path for encrypted and obfuscated files.

Originally created by:
Ben Hagen (ben.hagen@neohapsis.com)
Scott Behrens (scott.behrens@neohapsis.com)

Date: 11/4/2010
Modified for Python 3 compatibility
"""

import math
import os
import re
import csv
import zlib
import time
from collections import defaultdict
import argparse

# Globals
SMALLEST = 1  # Smallest filesize to check in bytes
DEVIATION_THRESH = 1.5  # percentage deviation before alarm will sound

class Test:
    """Base class for all tests"""
    def __init__(self):
        # high_is_bad means the higher the metric, the more suspicious it is
        self.high_is_bad = True
        self.results = []
        self.mean = 0
        self.stddev = 0

    def calculate(self, file_data, file_path):
        """Calculate metric for given data. Should be overridden by child classes."""
        raise NotImplementedError("Calculate method must be implemented by child class")

    def block_calculate(self, block_size, data, filename):
        """Calculate metric for blocks of data of given size."""
        num_blocks = int(math.ceil(len(data) / block_size))
        max_entropy = -9999
        min_entropy = 9999
        j = 0
        pos = 0
        for i in range(num_blocks):
            block_data = data[j:j+block_size]
            j = j+block_size
            calc_result = self.calculate(block_data, filename)
            if self.high_is_bad:
                if max_entropy <= calc_result:
                    max_entropy = calc_result
                    pos = i * block_size
            elif min_entropy > calc_result:
                min_entropy = calc_result
                pos = i * block_size
        result = {"value": max_entropy if self.high_is_bad else min_entropy, "position": pos}
        self.results.append({"filename": filename, **result})
        return result

    def calc_mean(self):
        """Calculate mean of all results."""
        res_total = 0
        for res in self.results:
            res_total += res["value"]
        self.mean = res_total / len(self.results)

    def calc_std_dev(self):
        """Calculate standard deviation of results."""
        square_total = 0
        for res in self.results:
            square_total += math.pow(res["value"] - self.mean, 2)
        self.stddev = math.sqrt(square_total / len(self.results))

    def flag_alarm(self):
        """Flag suspicious files based on deviation from mean."""
        self.calc_mean()
        self.calc_std_dev()

        flag_list = []
        for res in self.results:
            if dist(res["value"], self.mean) > (DEVIATION_THRESH)*self.stddev:
                if (self.high_is_bad and res["value"] > self.mean) or (not self.high_is_bad and res["value"] < self.mean):
                    percentage = dist(res["value"], self.mean) / self.stddev if self.stddev > 0 else float("inf")
                    res["percentage"] = percentage
                    flag_list.append(res)

        flag_list.sort(key=lambda item: item["percentage"])
        for res in flag_list:
            print(f' {res["percentage"]:>7.4f}       {res["filename"]}')

class LanguageIC(Test):
    """Class that calculates a file's Index of Coincidence"""
    def __init__(self):
        super().__init__()
        self.char_count = defaultdict(int)
        self.total_char_count = 0
        self.results = []
        self.ic_total_results = ""
        self.high_is_bad = False

    def calculate_char_count(self, data):
        if not data:
            return 0
        for x in range(256):
            char = bytes([x])
            charcount = data.count(char)
            self.char_count[char] += charcount
            self.total_char_count += charcount
        return

    def calculate_ic(self):
        total = 0
        for val in self.char_count.values():
            if val == 0:
                continue
            total += val * (val-1)

        try:
            ic_total = float(total)/(self.total_char_count * (self.total_char_count - 1))
        except ZeroDivisionError:
            ic_total = 0
        self.ic_total_results = ic_total
        return

    def calculate(self, file_data, file_path):
        if not data or (len(data) == 1):
            return 0
        char_count = 0
        total_char_count = 0

        for x in range(256):
            char = bytes([x])
            charcount = data.count(char)
            char_count += charcount * (charcount - 1)
            total_char_count += charcount
        ic = float(char_count)/(total_char_count * (total_char_count - 1))
        if not options.block_mode:
            self.results.append({"filename": filename, "value": ic})
        self.calculate_char_count(data)
        return ic

    def sort(self):
        """Sort results by value and add ranking."""
        """Sort results by value and add ranking."""
        """Sort results by value and add ranking."""
        self.results.sort(key=lambda item: item["value"])
        self.results = results_add_rank(self.results)

    def printer(self, result_count):
        """Print top results up to specified count."""
        """Print top results up to count."""
        self.calculate_IC()
        print("\n[[ Average IC for Search ]]")
        print(self.ic_total_results)
        print(f"\n[[ Top {count} lowest IC files ]]")
        if count > len(self.results):
            count = len(self.results)
        if not options.block_mode:
            for idx in range(result_count):
                print(f' {self.results[idx]["value"]:>7.4f}        {self.results[idx]["filename"]}')
        if options.block_mode:
            for x in range(count):
                print(
                    f' {self.results[x]["value"]:>7.4f}   '
                    f'at byte number:{self.results[x]["position"]}     '
                    f'{self.results[x]["filename"]}'
                )
        return

class Entropy(Test):
    """Class that calculates a file's Entropy"""
    def __init__(self):
        super().__init__()
        self.results = []
        self.high_is_bad = True

    def calculate(self, data, filename):
        if not data:
            return 0
        entropy = 0
        for x in range(256):
            p_x = float(data.count(bytes([x]))) / len(data)
            if p_x > 0:
                entropy += - p_x * math.log(p_x, 2)
        if not options.block_mode:
            self.results.append({"filename": filename, "value": entropy})
        return entropy

    def sort(self):
        self.results.sort(key=lambda item: item["value"], reverse=True)
        self.results = results_add_rank(self.results)

    def printer(self, count):
        print(f"\n[[ Top {count} entropic files for a given search ]]")
        if count > len(self.results):
            count = len(self.results)
        if not options.block_mode:
            for x in range(count):
                print(f' {self.results[x]["value"]:>7.4f}        {self.results[x]["filename"]}')
        if options.block_mode:
            for x in range(count):
                print(
                    f' {self.results[x]["value"]:>7.4f}   '
                    f'at byte number:{self.results[x]["position"]}     '
                    f'{self.results[x]["filename"]}'
                )
        return

class LongestWord(Test):
    """Class that determines the longest word for a particular file"""
    def __init__(self):
        super().__init__()
        self.results = []
        self.high_is_bad = True

    def calculate(self, data, filename):
        if not data:
            return 0
        try:
            text_data = data.decode('utf-8', errors='ignore')
        except (UnicodeDecodeError, ValueError):
            return 0
        longest = 0
        words = re.split(r"[\s,\n,\r]", text_data)
        if words:
            longest = max(len(word) for word in words)
        if not options.block_mode:
            self.results.append({"filename": filename, "value": longest})
        return longest

    def sort(self):
        self.results.sort(key=lambda item: item["value"], reverse=True)
        self.results = results_add_rank(self.results)

    def printer(self, count):
        print(f"\n[[ Top {count} longest word files ]]")
        if count > len(self.results):
            count = len(self.results)
        if not options.block_mode:
            for x in range(count):
                print(f' {self.results[x]["value"]:>7.4f}        {self.results[x]["filename"]}')
        if options.block_mode:
            for x in range(count):
                print(f' {self.results[x]["value"]:>7.4f}   at byte number:{self.results[x]["position"]}     {self.results[x]["filename"]}')
        return

class SignatureNasty(Test):
    """Generator that searches a given file for nasty expressions"""
    def __init__(self):
        super().__init__()
        self.results = []
        self.high_is_bad = True

    def calculate(self, data, filename):
        if not data:
            return 0
        try:
            text_data = data.decode('utf-8', errors='ignore')
        except (UnicodeDecodeError, ValueError):
            return 0
        valid_regex = re.compile(
            r'(eval\(|file_put_contents|base64_decode|python_eval|exec\(|'
            r'passthru|popen|proc_open|pcntl|assert\(|system\(|shell)',
            re.I)
        matches = re.findall(valid_regex, text_data)
        if not options.block_mode:
            self.results.append({"filename": filename, "value": len(matches)})
        return len(matches)

    def sort(self):
        self.results.sort(key=lambda item: item["value"], reverse=True)
        self.results = results_add_rank(self.results)

    def printer(self, count):
        print(f"\n[[ Top {count} signature match counts ]]")
        if count > len(self.results):
            count = len(self.results)
        if not options.block_mode:
            for x in range(count):
                print(f' {self.results[x]["value"]:>7.4f}        {self.results[x]["filename"]}')
        if options.block_mode:
            for x in range(count):
                print(f' {self.results[x]["value"]:>7.4f}   at byte number:{self.results[x]["position"]}     {self.results[x]["filename"]}')
        return

class SignatureSuperNasty(Test):
    """Generator that searches a given file for SUPER-nasty expressions"""
    def __init__(self):
        super().__init__()
        self.results = []
        self.high_is_bad = True

    def calculate(self, data, filename):
        if not data:
            return 0
        try:
            text_data = data.decode('utf-8', errors='ignore')
        except UnicodeDecodeError:
            return 0
        valid_regex = re.compile(r'(@\$_\[\]=|\$_=@\$_GET|\$_\[\+""\]=)', re.I)
        matches = re.findall(valid_regex, text_data)
        if not options.block_mode:
            self.results.append({"filename": filename, "value": len(matches)})
        return len(matches)

    def sort(self):
        self.results.sort(key=lambda item: item["value"], reverse=True)
        self.results = results_add_rank(self.results)

    def printer(self, count):
        print(f"\n[[ Top {count} SUPER-signature match counts (These are usually bad!) ]]")
        if count > len(self.results):
            count = len(self.results)
        if not options.block_mode:
            for x in range(count):
                print(f' {self.results[x]["value"]:>7.4f}        {self.results[x]["filename"]}')
        if options.block_mode:
            for x in range(count):
                print(f' {self.results[x]["value"]:>7.4f}   at byte number:{self.results[x]["position"]}     {self.results[x]["filename"]}')
        return

class UsesEval(Test):
    """Generator that searches a given file for nasty eval with variable"""
    def __init__(self):
        super().__init__()
        self.results = []
        self.highIsBad = True

    def calculate(self, data, filename):
        if not data:
            return 0
        try:
            text_data = data.decode('utf-8', errors='ignore')
        except (UnicodeDecodeError, ValueError):
            return 0
        valid_regex = re.compile(r'(eval\(\$(\w|\d))', re.I)
        matches = re.findall(valid_regex, text_data)
        if not options.block_mode:
            self.results.append({"filename": filename, "value": len(matches)})
        return len(matches)

    def sort(self):
        self.results.sort(key=lambda item: item["value"], reverse=True)
        self.results = results_add_rank(self.results)

    def printer(self, count):
        print(f"\n[[ Top {count} eval match counts ]]")
        if count > len(self.results):
            count = len(self.results)
        if not options.block_mode:
            for x in range(count):
                print(f' {self.results[x]["value"]:>7.4f}        {self.results[x]["filename"]}')
        if options.block_mode:
            for x in range(count):
                print(f' {self.results[x]["value"]:>7.4f}   at byte number:{self.results[x]["position"]}     {self.results[x]["filename"]}')
        return

class Compression(Test):
    """Generator finds compression ratio"""
    def __init__(self):
        super().__init__()
        self.results = []
        self.highIsBad = True

    def calculate(self, data, filename):
        if not data:
            return 0
        compressed = zlib.compress(data)
        ratio = float(len(compressed)) / float(len(data))
        if not options.block_mode:
            self.results.append({"filename": filename, "value": ratio})
        return ratio

    def sort(self):
        self.results.sort(key=lambda item: item["value"], reverse=True)
        self.results = results_add_rank(self.results)

    def printer(self, count):
        print(f"\n[[ Top {count} compression match counts ]]")
        if count > len(self.results):
            count = len(self.results)
        if not options.block_mode:
            for x in range(count):
                print(f' {self.results[x]["value"]:>7.4f}        {self.results[x]["filename"]}')
        if options.block_mode:
            for x in range(count):
                print(f' {self.results[x]["value"]:>7.4f}   at byte number:{self.results[x]["position"]}     {self.results[x]["filename"]}')
        return

def results_add_rank(results):
    """Add ranking to sorted results list."""
    rank = 1
    offset = 1
    previous_value = False
    new_list = []
    for file in results:
        if previous_value and previous_value != file["value"]:
            rank = offset
        file["rank"] = rank
        new_list.append(file)
        previous_value = file["value"]
        offset = offset + 1
    return new_list

def calculate_distance(value1, value2):
    """Calculate absolute distance between two numbers."""
    return math.fabs(value1 - value2)

class SearchFile:
    """Generator that searches a given filepath with an optional regular
    expression and returns the filepath and filename"""

    def __init__(self, follow_symlinks):
        self.follow_symlinks = follow_symlinks
    def is_valid_file(self, filepath, regex):
        """Check if file matches search criteria."""
        return (os.path.exists(filepath) and
                regex.search(os.path.basename(filepath)) and
                os.path.getsize(filepath) > SMALLEST)

    def search_file_path(self, args, valid_regex):
        """Search files in path matching regex pattern."""
        for root, _, files in os.walk(args[0], followlinks=self.follow_symlinks):
            for file in files:
                filename = os.path.join(root, file)
                if not valid_regex.search(file) or os.path.getsize(filename) <= SMALLEST:
                    continue
                try:
                    with open(filename, 'rb') as f:
                        data = f.read()
                    yield data, filename
                except (OSError, IOError):
                    print(f"Could not read file :: {root}/{file}")

if __name__ == "__main__":
    print("""
   yusuf81-modified-neopi
   """)

    parser = argparse.ArgumentParser(description="Utility to scan a file path for encrypted and obfuscated files")
    parser.add_argument("directory", help="Start directory")
    parser.add_argument("regex", nargs="?", help="Filename regex", default=".*")
    parser.add_argument("-c", "--csv", help="Generate CSV outfile", metavar="FILECSV")
    parser.add_argument("-a", "--all", action="store_true", help="Run all (useful) tests [Entropy, Longest Word, IC, Signature]")
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

    options = parser.parse_args()

    if not os.path.exists(options.directory):
        parser.error("Invalid path")

    try:
        valid_regex = re.compile(options.regex)
    except re.error:
        parser.error("Invalid regular expression")

    tests = []

    if options.all:
        tests.extend([LanguageIC(), Entropy(), LongestWord(), SignatureNasty(), SignatureSuperNasty()])
    else:
        if options.entropy:
            tests.append(Entropy())
        if options.longestword:
            tests.append(LongestWord())
        if options.ic:
            tests.append(LanguageIC())
        if options.signature:
            tests.append(SignatureNasty())
        if options.supersignature:
            tests.append(SignatureSuperNasty())
        if options.eval:
            tests.append(UsesEval())
        if options.zlib:
            tests.append(Compression())

    locator = SearchFile(options.follow_links)

    csv_array = []
    csv_header = ["filename"]

    FILE_COUNT = 0 
    FILE_IGNORE_COUNT = 0
    time_start = time.time()

    for test in tests:
        csv_header.append(test.__class__.__name__)
        if options.block_mode:
            csv_header.append("position")

    for data, filename in locator.search_file_path([options.directory], valid_regex):
        if data:
            csv_row = []
            csv_row.append(filename)

            if options.unicode:
                try:
                    text_data = data.decode('utf-8')
                    ascii_high_count = sum(1 for c in text_data if ord(c) > 127)
                    FILE_ASCII_HIGH_RATIO = (float(ascii_high_count) / 
                                           float(len(text_data)))
                except (UnicodeDecodeError, ValueError):
                    FILE_ASCII_HIGH_RATIO = 0

            if not options.unicode or FILE_ASCII_HIGH_RATIO < 0.1:
                for test in tests:
                    if options.block_mode:
                        calculated_value = test.blockCalculate(options.block_mode, data, filename)
                    else:
                        calculated_value = test.calculate(data, filename)
                    if not options.block_mode:
                        csv_row.append(calculated_value)
                    else:
                        csv_row.append(calculated_value["value"])
                        csv_row.append(calculated_value["position"])
                    FILE_COUNT = FILE_COUNT + 1
                csv_array.append(csv_row)
            else:
                FILE_IGNORE_COUNT = FILE_IGNORE_COUNT + 1

    if options.csv:
        csv_array.insert(0, csv_header)
        with open(options.csv, "w", newline='', encoding='utf-8') as f:
            fileOutput = csv.writer(f)
            fileOutput.writerows(csv_array)

    time_finish = time.time()

    print(f"\n[[ Total files scanned: {FILE_COUNT} ]]")
    print(f"[[ Total files ignored: {FILE_IGNORE_COUNT} ]]")
    print(f"[[ Scan Time: {time_finish - time_start:.2f} seconds ]]")

    rank_list = {}
    for test in tests:
        if options.alarm_mode:
            DEVIATION_THRESH = options.alarm_mode
            print(f"Flagged files for: {test.__class__.__name__}")
            test.flagAlarm()
        else:
            test.sort()
            test.printer(10)
            for file in test.results:
                rank_list[file["filename"]] = rank_list.setdefault(file["filename"], 0) + file["rank"]

    if not options.alarm_mode:
        rank_sorted = sorted(rank_list.items(), key=lambda x: x[1])

        print("\n[[ Top cumulative ranked files ]]")
        count = min(10, len(rank_sorted))
        for x in range(count):
            print(f' {rank_sorted[x][1]:>7}        {rank_sorted[x][0]}')
