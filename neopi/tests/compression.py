"""Compression test implementation."""
import zlib
from .base import Test

class Compression(Test):
    """Test data compressibility."""

    def calculate(self, input_data, filepath):
        """Calculate compression ratio."""
        if not input_data:
            return 0

        compressed = zlib.compress(input_data)
        ratio = float(len(compressed)) / float(len(input_data))
        self.results.append({"filename": filepath, "value": ratio})
        return ratio
