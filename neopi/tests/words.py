"""Word length test implementation."""
import re
from .base import Test

class LongestWord(Test):
    """Find longest word/string in data."""
    def calculate(self, input_data, filepath):
        """Calculate longest contiguous string of printable chars."""
        if not input_data:
            return 0

        try:
            data = input_data.decode('utf-8', errors='ignore')
        except UnicodeError:
            return 0

        # Find longest string of printable chars
        words = re.findall(r'[A-Za-z0-9_]+', data)
        if not words:
            return 0

        longest = len(max(words, key=len)) if words else 0
        self.results.append({"filename": filepath, "value": longest})
        return longest
