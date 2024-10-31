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
