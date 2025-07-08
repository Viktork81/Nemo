import os

def run(*args):
    """Lists all files and directories in the current working directory."""
    try:
        # Separate files and directories for clarity
        items = os.listdir('.')
        files = [item for item in items if os.path.isfile(item)]
        dirs = [item for item in items if os.path.isdir(item)]

        output = "Directories:\n"
        if dirs:
            for d in sorted(dirs):
                output += f"- {d}/\n"
        else:
            output += "- (none)\n"

        output += "\nFiles:\n"
        if files:
            for f in sorted(files):
                output += f"- {f}\n"
        else:
            output += "- (none)\n"
            
        return output.strip()
    except Exception as e:
        return f"[ERROR] Could not list files: {e}"