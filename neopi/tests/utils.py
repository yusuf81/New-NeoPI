"""Utility functions for tests."""
def decode_input(input_data):
    """Safely decode input data to UTF-8 string.
    
    Returns:
        Decoded string or None if decoding fails or input is empty
    """
    if not input_data:
        return None
        
    try:
        return input_data.decode('utf-8', errors='ignore')
    except UnicodeError:
        return None
