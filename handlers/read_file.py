import os

def run(filename: str, *args):
    """Reads and returns the content of a specified file."""
    if not filename:
        return "[ERROR] Filename not provided."
    
    try:
        # Basic security check to prevent directory traversal
        if '..' in filename or filename.startswith('/'):
            return f"[ERROR] Invalid or insecure file path: {filename}"

        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"[ERROR] File not found: {filename}"
    except Exception as e:
        return f"[ERROR] Could not read file '{filename}': {e}"