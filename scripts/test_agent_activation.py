#!/usr/bin/env python3
"""
Test Agent Activation Loop

Iterates launching Claude, sending activation message, and checking for success.txt
Closes and retries until agent responds correctly.
"""

import subprocess
import time
import os
from pathlib import Path

def test_agent_activation(vault_path: str = "C:/obsidian-memory-vault", max_attempts: int = 10):
    """Iterate until agent creates success.txt"""

    vault_path = Path(vault_path).resolve()
    os.chdir(vault_path)

    # Clean up any existing success file
    success_file = vault_path / "success.txt"
    if success_file.exists():
        success_file.unlink()
        print("[i] Deleted existing success.txt\n")

    for attempt in range(1, max_attempts + 1):
        print(f"\n{'='*60}")
        print(f"ATTEMPT {attempt}/{max_attempts}")
        print(f"{'='*60}\n")

        try:
            # Launch Claude with wexpect
            print(f"[*] Launching Claude and sending activation...")
            result = subprocess.run(
                ['python', 'scripts/launch_claude_processor.py',
                 '--vault', str(vault_path),
                 '--message', 'file watcher summons you'],
                timeout=35,
                capture_output=True,
                text=True,
                cwd=str(vault_path)
            )

            print(f"[+] Launch completed")

            # Wait a bit for agent to process
            print(f"[*] Waiting 3 seconds for agent...")
            time.sleep(3)

            # Check for success file
            if success_file.exists():
                print(f"\n{'='*60}")
                print(f"[SUCCESS] Agent activated on attempt {attempt}!")
                print(f"{'='*60}\n")

                with open(success_file, 'r') as f:
                    content = f.read()
                print(f"File content: {content}\n")

                print(f"[+] wexpect automation WORKS!")
                print(f"[+] Agent responds to triggers!")
                print(f"[i] Ready to restore full pipeline instructions\n")

                return True
            else:
                print(f"[!] No success.txt found")
                print(f"[!] Stopping iteration - check Claude window manually")
                return False

        except subprocess.TimeoutExpired:
            print(f"[!] Timeout on attempt {attempt}")
            return False

        except Exception as e:
            print(f"[X] Error on attempt {attempt}: {e}")
            return False

    print(f"\n{'='*60}")
    print(f"[FAILED] Agent didn't respond after {max_attempts} attempts")
    print(f"{'='*60}\n")
    print(f"[i] Possible issues:")
    print(f"    - Agent not configured correctly in Claude UI")
    print(f"    - Agent instructions file not being read")
    print(f"    - Message not reaching agent")
    print(f"    - Agent asking questions instead of executing\n")

    return False


if __name__ == "__main__":
    import sys

    vault = sys.argv[1] if len(sys.argv) > 1 else "C:/obsidian-memory-vault"
    attempts = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    success = test_agent_activation(vault, attempts)
    sys.exit(0 if success else 1)
