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
        ic = 0
        for count in counts.values():
            ic += count * (count - 1)
            
        ic = float(ic) / (length * (length - 1)) if length > 1 else 0
        return ic
