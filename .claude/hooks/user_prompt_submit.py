#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

"""
User Prompt Submit Hook - Auto-inject next command from workflow

This hook is triggered when the user submits a prompt.
It checks for next_prompt.json and auto-injects the next command if available.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from utils.constants import ensure_session_log_dir

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def log_user_prompt(session_id, input_data):
    """Log user prompt to session directory."""
    log_dir = ensure_session_log_dir(session_id)
    log_file = log_dir / 'user_prompt_submit.json'

    if log_file.exists():
        with open(log_file, 'r') as f:
            try:
                log_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                log_data = []
    else:
        log_data = []

    log_data.append(input_data)

    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)


def check_next_prompt():
    """Check if next_prompt.json exists and return command."""
    next_prompt_file = Path(".claude/next_prompt.json")

    if not next_prompt_file.exists():
        return None

    try:
        with open(next_prompt_file, 'r') as f:
            next_prompt = json.load(f)

        # Check if auto_start is enabled
        auto_start = next_prompt.get("auto_start", False)
        command = next_prompt.get("command", "")
        args = next_prompt.get("args", [])

        if not auto_start:
            # Manual mode - don't inject, just return info
            return None

        if not command:
            return None

        # Build full command with args
        full_command = command
        if args:
            full_command = f"{command} {' '.join(str(arg) for arg in args)}"

        # Delete the next_prompt file after reading (one-time use)
        next_prompt_file.unlink()

        return full_command

    except (json.JSONDecodeError, FileNotFoundError):
        return None


def should_clear_context():
    """Check if context should be cleared before next command."""
    # Read environment variable or workflow state
    clear_enabled = os.getenv("AUTO_CLEAR_CONTEXT", "false").lower() == "true"

    if not clear_enabled:
        return False

    # Check workflow state for phase transitions
    state_file = Path("state/workflow_state.json")
    if not state_file.exists():
        return False

    try:
        with open(state_file, 'r') as f:
            state = json.load(f)

        # Clear context on major phase transitions
        phase = state.get("phase", "")
        next_action = state.get("next_action", "")

        # Clear between major phases to reduce context
        major_phases = ["plan", "build", "test", "review", "document"]

        if phase in major_phases and next_action in major_phases:
            return True

        return False

    except (json.JSONDecodeError, FileNotFoundError):
        return False


def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--validate', action='store_true',
                          help='Enable prompt validation')
        parser.add_argument('--log-only', action='store_true',
                          help='Only log prompts, no injection')
        parser.add_argument('--auto-inject', action='store_true',
                          help='Enable auto-injection of next command')
        args = parser.parse_args()

        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())

        # Extract session_id and prompt
        session_id = input_data.get('session_id', 'unknown')
        prompt = input_data.get('prompt', '')

        # Log the user prompt
        log_user_prompt(session_id, input_data)

        # Check for next command injection (if enabled)
        if args.auto_inject or os.getenv("AUTO_INJECT_COMMANDS", "false").lower() == "true":
            next_command = check_next_prompt()

            if next_command:
                # Check if we should clear context first
                if should_clear_context():
                    # Print /clear followed by the command
                    print(f"/clear")
                    print(f"{next_command}")
                else:
                    # Just print the next command
                    print(f"{next_command}")

                # Exit with code 1 to replace user's prompt
                sys.exit(1)

        # If no injection, process user's prompt normally
        # Can add context information here
        # Example: print(f"[Context] Current time: {datetime.now()}")

        # Success - prompt will be processed as-is
        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == '__main__':
    main()
