"""File search functionality."""

import os
import re
from functools import lru_cache
from multiprocessing import Pool

SMALLEST = 1  # Smallest filesize to check in bytes

class SearchFile:
    """Generator that searches a given filepath with an optional regular
    expression and returns the filepath and filename"""

    def __init__(self, follow_symlinks=False):
        self.follow_symlinks = follow_symlinks

    def is_valid_file(self, filepath, regex):
        """Check if file matches search criteria."""
        return (os.path.exists(filepath) and
                regex.search(os.path.basename(filepath)) and
                os.path.getsize(filepath) > SMALLEST
            )

    @lru_cache(maxsize=1024)
    def read_file(self, filepath):
        """Read file contents with caching."""
        try:
            with open(filepath, 'rb') as file_handle:
                return file_handle.read()
        except (OSError, IOError):
            print(f"Could not read file :: {filepath}")
            return None

    def process_file(self, filepath, pattern):
        """Process a single file."""
        if not pattern.search(os.path.basename(filepath)) or os.path.getsize(filepath) <= SMALLEST:
            return None
        file_data = self.read_file(filepath)
        if file_data:
            return file_data, filepath
        return None

    def _process_file_wrapper(self, args):
        """Wrapper function for process_file to make it pickleable"""
        filepath, pattern = args
        return self.process_file(filepath, pattern)

    def search_file_path(self, args, pattern):
        """Search files in path matching regex pattern."""
        with Pool() as pool:
            for root, _, files in os.walk(args[0], followlinks=self.follow_symlinks):
                filepaths = [os.path.join(root, f) for f in files]
                # Create tuples of (filepath, pattern) for each file
                work_items = [(f, pattern) for f in filepaths]
                for result in pool.imap_unordered(self._process_file_wrapper, work_items):
                    if result:
                        yield result
