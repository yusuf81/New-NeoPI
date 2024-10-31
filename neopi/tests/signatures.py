"""Signature-based tests implementation."""
import re
from .base import Test

class SignatureNasty(Test):
    """Test for suspicious code patterns."""

    def calculate(self, input_data, filepath):
        """Check for suspicious patterns."""
        if not input_data:
            return 0

        try:
            data = input_data.decode('utf-8', errors='ignore')
        except UnicodeError:
            return 0

        score = 0
        patterns = [
            r'chr\(.*?\)',
            r'base64',
            r'eval\(',
            r'exec\(',
            r'str\.replace',
            r'\\x[0-9a-fA-F]{2}'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, data)
            score += len(matches)
        self.results.append({"filename": filepath, "value": score})
        self.results.append({"filename": filepath, "value": score})
        return score

class SignatureSuperNasty(Test):
    """Test for highly suspicious code patterns."""
    def calculate(self, input_data, filepath):
        """Check for highly suspicious patterns."""
        if not input_data:
            return 0

        try:
            data = input_data.decode('utf-8', errors='ignore')
        except UnicodeError:
            return 0

        score = 0
        patterns = [
            r'system\(',
            r'shell_exec',
            r'passthru\(',
            r'eval\(base64_decode',
            r'assert\(',
            r'preg_replace.*\/e'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, data)
            score += len(matches) * 2
        return score

class UsesEval(Test):
    """Test specifically for eval() usage."""
    def calculate(self, input_data, filepath):
        """Check for eval() usage."""
        if not input_data:
            return 0

        try:
            data = input_data.decode('utf-8', errors='ignore')
        except UnicodeError:
            return 0

        matches = re.findall(r'eval\s*\(', data)
        score = len(matches)
        self.results.append({"filename": filepath, "value": score})
        return score
