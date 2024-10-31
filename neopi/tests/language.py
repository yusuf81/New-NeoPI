"""Language test implementation."""
from collections import Counter
from .base import Test

class LanguageIC(Test):
    """Calculate Index of Coincidence for language detection."""
    def __init__(self):
        super().__init__()
        self.high_is_bad = False

    def calculate(self, input_data, filepath):
        """Calculate Index of Coincidence."""
        if not input_data:
            return 0

        # Only process ASCII range
        filtered = bytes(x for x in input_data if x < 128)
        if not filtered:
            return 0

        length = len(filtered)
        counts = Counter(filtered)

        # Calculate IC
        index_coincidence = 0
        for count in counts.values():
            index_coincidence += count * (count - 1)

        index_coincidence = float(index_coincidence) / (length * (length - 1)) if length > 1 else 0
        self.results.append({"filename": filepath, "value": index_coincidence})
        return index_coincidence
