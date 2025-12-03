def make_32_hash(input_string: str) -> str:
    """Generate a 32-character hash for the given input string."""
    import hashlib
    hash_object = hashlib.md5(input_string.encode())
    return hash_object.hexdigest()