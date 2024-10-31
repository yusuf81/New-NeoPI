"""Test implementations for neopi.

This module provides various test classes for analyzing files:
- Entropy tests for detecting encryption/compression
- Language tests for identifying obfuscation
- Signature tests for finding suspicious patterns
- Word tests for unusual string patterns
"""

from .base import Test
from .entropy import Entropy
from .language import LanguageIC
from .compression import Compression
from .signatures import SignatureNasty, SignatureSuperNasty, UsesEval
from .words import LongestWord

__all__ = [
    'Test',
    'Entropy',
    'LanguageIC', 
    'Compression',
    'SignatureNasty',
    'SignatureSuperNasty',
    'UsesEval',
    'LongestWord'
]
