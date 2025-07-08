# handlers/write_file.py
import os

def run(filename: str, content: str, *args):
    """Writes or overwrites a file with the given content."""
    if '..' in filename or filename.startswith('/'):
        return f"[ERROR] Invalid or insecure file path: {filename}"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File '{filename}' written successfully."
    except Exception as e:
        return f"[ERROR] Could not write to file '{filename}': {e}"