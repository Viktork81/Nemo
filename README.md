Nemo: Modular AI CLI Agent
Author: Viktor Kirschner

First working(ish) version: July 2025
Project type: AI-powered command-line assistant (Python)

🤖 What is Nemo?

Nemo is a modular, locally-executing AI assistant that runs directly on your computer via CLI. It's powered by an LLM (e.g. OpenAI GPT-4o), which receives structured prompts from Python, interacts with your file system, runs commands, and modifies its own codebase when necessary. Nemo is not just an assistant — it's a living process on your machine that can analyze its environment and act accordingly. It is an autonomous, programmable, expandable command-line intelligence. Think of it as a hybrid between a CLI tool, a Python framework, and a self-aware script engine.

📌 Name Meaning

Nemo = "Neural Executor for Modular Operations"
And also: Latin for “no one” — an assistant that doesn’t speak unless needed, just acts. 🙂


🧠 Core Features

AI Command Execution: Parses your tasks and translates them into modular commands
Multiline Prompting: Supports complex, multi-step tasks
PowerShell + Python runtime: Executes native scripts directly on your system
Memory + log.txt: Tracks recent context, decisions, and goals
Autonomous reasoning loop: Can decide to generate new commands if needed
Modular command system: Each instruction is a standalone Python file
Priming prompt: Includes all current tools, instructions, and system role
Human-like autonomy: Detects failed steps and retries/fixes them automatically

🛠️ Project Structure

/handlers           <- Contains all modular commands (e.g. read_file.py, browse_folders.py)

log.txt             <- History of recent prompts and reasoning

priming_prompt.txt  <- Initial memory, current tools, instructions for LLM

cli_tool.py             <- CLI interface and execution loop

ai_connector.py     <- Switchable backend (OpenAI, Gemini, Claude, etc)


🧪 What Makes Nemo Unique

Designed for true system-level agency, not chatting. (Although it can be chatting as well)
Fully local — runs directly on your device.
Capable of autonomous goal decomposition, not just instruction execution.
Modular, extensible, and customizable by anyone with Python knowledge.
Can be dropped into any project folder (e.g. Unity project) and made to analyze/edit files contextually.

🔐 Attribution

Developed by Viktor Kirschner
Powered by OpenAI GPT-4o (initial implementation)
Future support planned for Gemini, Claude, and open-source models.

💬 License

MIT License
Viktor Kirschner - 2025

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Version 1: 
07/07/2025: Works fine as intended, but only uses Openai's 4o model at the moment. 
There is a known issue: When it finishes a high level goal successfully it may deem it failed, delete and re-do it. I am working on that.

