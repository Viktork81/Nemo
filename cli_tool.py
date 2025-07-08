import os
import sys
import shlex
import importlib.util
from pathlib import Path
import getpass
import subprocess

from ai_connector import get_ai_response_with_history, initialize_client

# --- Custom Exceptions for Flow Control ---
class TaskComplete(Exception):
    """Custom exception to signal the AI has finished the entire task."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class UserInputRequired(Exception):
    """Custom exception to signal the AI needs input from the user to continue."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# --- Constants ---
HANDLERS_DIR = "handlers"
PRIMING_PROMPT_FILE = "priming_prompt.txt"
LOG_FILE = "log.txt"
START_MARKER = "░"
END_MARKER = "█"

# --- State Variables ---
in_code_mode = False
new_command_name = ""

# --- Core Functions ---

def setup_environment():
    """Ensures necessary directories and files exist."""
    Path(HANDLERS_DIR).mkdir(exist_ok=True)
    if not Path(PRIMING_PROMPT_FILE).exists():
        with open(PRIMING_PROMPT_FILE, 'w', encoding='utf-8') as f:
            f.write("# Add your command documentation here for the AI to read.")
    if not Path(LOG_FILE).exists():
        Path(LOG_FILE).touch()

def parse_ai_command(response: str):
    """Extracts a command from the AI's response string."""
    start_index = response.find(START_MARKER)
    end_index = response.find(END_MARKER)
    if start_index != -1 and end_index != -1 and start_index < end_index:
        return response[start_index + 1:end_index].strip()
    return None

def save_new_command(name: str, code: str) -> str:
    """Saves a new command, cleaning it of all common AI-generated artifacts."""
    lines = code.strip().split('\n')
    
    # Clean Markdown Fences (e.g., ```python)
    if lines and lines[0].strip().startswith('```'):
        lines.pop(0)
    if lines and lines[-1].strip() == '```':
        lines.pop(-1)
        
    # Filter out any line that is just the END_MARKER
    temp_lines = [line for line in lines if line.strip() != END_MARKER]
    
    # Filter out any lines that look like command invocations
    temp_lines_2 = [line for line in temp_lines if not (START_MARKER in line and END_MARKER in line)]
    
    # Find the first actual line of code, discarding conversational preamble.
    first_code_line_index = 0
    python_starters = ('import ', 'from ', 'def ', 'class ', '#', '"""', "'''")
    for i, line in enumerate(temp_lines_2):
        if line.strip().startswith(python_starters):
            first_code_line_index = i
            break
    
    cleaned_lines = temp_lines_2[first_code_line_index:]
    cleaned_code = '\n'.join(cleaned_lines)

    final_path = Path(HANDLERS_DIR) / f"{name}.py"
    if final_path.exists():
        return f"[ERROR] Command '{name}' already exists."
    try:
        with open(final_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_code)
        return f"[SUCCESS] Command '{name}' created and cleaned successfully."
    except Exception as e:
        return f"[ERROR] Failed to save command '{name}': {e}"

def execute_command(command_str: str) -> str:
    """Parses and executes a command, raising exceptions for flow control."""
    global in_code_mode, new_command_name
    try:
        parts = shlex.split(command_str)
        if not parts: return "[ERROR] Empty command."
        command_name = parts[0]
        args = parts[1:]
    except (ValueError, IndexError):
        return f"[ERROR] Invalid command syntax: '{command_str}'"

    # --- Internal commands that control the loop's state ---
    if command_name == 'create_command_begin':
        if not args:
            return "[ERROR] 'create_command_begin' requires a command name."
        new_command_name = args[0]
        in_code_mode = True
        return f"[INFO] Entering multi-line code mode for new command '{new_command_name}'. Awaiting AI's code block."

    if command_name == 'task_complete':
        final_message = " ".join(args) if args else "Task completed."
        raise TaskComplete(final_message)

    if command_name == 'request_user_input':
        question = " ".join(args) if args else "What is your next step?"
        raise UserInputRequired(question)

    # --- Other internal and external commands ---
    internal_handlers = {
        'run_powershell': handle_run_powershell
    }
    if command_name in internal_handlers:
        return internal_handlers[command_name](*args)
    
    return handle_run_command(command_name, *args)

# --- Command Handlers ---

def handle_run_powershell(command_to_run: str = None, *args):
    """Executes a PowerShell command."""
    if not command_to_run: return "[ERROR] No command provided to run_powershell."
    full_command = command_to_run + " " + " ".join(args)
    try:
        result = subprocess.run(["powershell", "-NoProfile", "-Command", full_command], capture_output=True, text=True, timeout=30, check=False)
        if result.returncode != 0:
            return f"[POWERSHELL ERROR] Exit Code: {result.returncode}\n{result.stderr}"
        return result.stdout if result.stdout else "[INFO] PowerShell command ran with no output."
    except Exception as e:
        return f"[POWERSHELL ERROR] Failed to execute command: {e}"

def handle_run_command(name: str = None, *args):
    """Executes a command script in a separate process and captures its output."""
    if not name:
        return "[ERROR] Command name not provided."
    module_path = Path(HANDLERS_DIR) / f"{name}.py"
    if not module_path.exists():
        return f"[ERROR] Unknown command: '{name}'"
    try:
        command_to_execute = [sys.executable, str(module_path)] + list(args)
        result = subprocess.run(
            command_to_execute, capture_output=True, text=True, timeout=30, check=False
        )
        if result.returncode != 0:
            error_output = result.stderr if result.stderr else "The script failed but produced no error message."
            return f"[EXECUTION ERROR] Command '{name}' failed with exit code {result.returncode}:\n{error_output}"
        return result.stdout if result.stdout else f"[INFO] Command '{name}' ran successfully with no output."
    except subprocess.TimeoutExpired:
        return f"[EXECUTION ERROR] Command '{name}' timed out after 30 seconds."
    except Exception as e:
        return f"[EXECUTION ERROR] An unexpected error occurred while running '{name}': {e}"

# --- Main REPL Loop ---

def main():
    """The main Read-Eval-Print Loop for the autonomous agent."""
    global in_code_mode, new_command_name
    
    setup_environment()
    
    print("--- AI Agent Tool Initialization ---")
    api_key = os.getenv("OPENAI_API_KEY") 
    if not api_key:
        print("INFO: API key environment variable not found.")
        try: api_key = getpass.getpass("Please enter your API key and press Enter: ")
        except (KeyboardInterrupt, EOFError): print("\nOperation cancelled. Exiting."); return
    if not initialize_client(api_key):
        print("Could not start the tool. Exiting."); return
        
    print("\nAI Agent CLI Tool v9.0 (Interactive Pausing)")
    print("Enter your high-level goal.")
    try:
        with open(PRIMING_PROMPT_FILE, 'r', encoding='utf-8') as f: system_prompt = f.read()
    except FileNotFoundError:
        print(f"[FATAL] Priming prompt '{PRIMING_PROMPT_FILE}' not found. Exiting."); return

    conversation_history = []
    
    while True:
        try:
            if not conversation_history:
                user_query = input("\n👤 You: ")
                if user_query.lower() in ['exit', 'quit']: break
                conversation_history.append({"role": "user", "content": user_query})
            
            print(f"\n--- Autonomous Step ---")
            
            ai_response_text = get_ai_response_with_history(system_prompt, conversation_history)
            
            if in_code_mode:
                print(f"🤖 AI intends to write the following code for '{new_command_name}':")
                print(f"```python\n{ai_response_text}\n```")
                result = save_new_command(new_command_name, ai_response_text)
                print(f"🛠️ Tool Output:\n{result}")
                in_code_mode = False
                new_command_name = ""
                tool_feedback = f"The result of your 'create_command_begin' action was: {result}. What is your next step?"
                conversation_history.append({"role": "assistant", "content": ai_response_text})
                conversation_history.append({"role": "user", "content": tool_feedback})
                continue

            print(f"🤖 AI: {ai_response_text}")
            conversation_history.append({"role": "assistant", "content": ai_response_text})
            
            command_to_run = parse_ai_command(ai_response_text)
            
            if command_to_run:
                execution_result = execute_command(command_to_run)
                if execution_result is None: execution_result = "[INFO] Command ran with no output."
                print("-" * 20)
                print(f"🛠️ Tool Output:\n{execution_result}")
                print("-" * 20)
                tool_feedback = f"The result of your last command was:\n\n{execution_result}\n\nBased on this, what is your next action?"
                conversation_history.append({"role": "user", "content": tool_feedback})
            else:
                print("[INFO] AI provided a thought process without a command. Prompting for next action...")
                feedback_for_ai = "Your last response did not contain a command. Please state your next action to proceed with the goal."
                conversation_history.append({"role": "user", "content": feedback_for_ai})

        except UserInputRequired as e:
            print("-" * 20)
            print(f"🤖 AI: {e.message}")
            user_response = input("\n👤 You: ")
            if user_response.lower() in ['exit', 'quit']:
                print("\nOperation cancelled. Exiting..."); break
            # Add user's response to history so the AI sees it next
            conversation_history.append({"role": "user", "content": user_response})
            print("-" * 20)
            continue

        except TaskComplete as e:
            print("-" * 20)
            print(f"✅ AI: {e.message}")
            print("[INFO] AI has marked the task as complete. Awaiting new user input.")
            print("-" * 20)
            conversation_history = []
            continue

        except KeyboardInterrupt:
            print("\nOperation cancelled. Exiting..."); break
        except Exception as e:
            print(f"\n[FATAL] An unexpected error occurred in the main loop: {e}")
            break

if __name__ == "__main__":
    main()
