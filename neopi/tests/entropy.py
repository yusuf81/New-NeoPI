"""Entropy test implementation."""
import math
from collections import Counter
from .base import Test

class Entropy(Test):
    """Calculate entropy of input data."""

    def calculate(self, input_data, filepath):
        """Calculate Shannon entropy of data."""
        if not input_data:
            return 0

        entropy = 0
        length = len(input_data)

        # Count byte frequencies
        counts = Counter(input_data)

        # Calculate Shannon entropy
        for count in counts.values():
            probability = float(count) / length
            entropy -= probability * math.log2(probability)

        # Append result
        self.results.append({"filename": filepath, "value": entropy})
        return entropy
