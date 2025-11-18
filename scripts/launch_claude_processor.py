#!/usr/bin/env python3
"""
Launch Claude Code Processor with wexpect

Uses wexpect (Windows expect) to spawn Claude Code and send activation message
directly to the process. No GUI automation, no clicking, no focus issues!

This approach:
- Spawns Claude in interactive mode (uses Max subscription, not API)
- Sends input directly to stdin (no pyautogui)
- Waits for process responses (reliable)
- Works in background while you use other apps
"""

import wexpect
import time
import os
from pathlib import Path


def launch_claude_with_wexpect(vault_path: str, activation_message: str = "file watcher summons you"):
    """
    Launch Claude Code and send activation message using wexpect

    Args:
        vault_path: Absolute path to Obsidian vault
        activation_message: Message to send to agent (default: "file watcher summons you")

    Returns:
        wexpect child process handle
    """

    # Ensure absolute path
    vault_path = str(Path(vault_path).resolve())

    print(f"\n{'='*60}")
    print(f"[*] Launching Claude Code with wexpect")
    print(f"{'='*60}")
    print(f"    Vault: {vault_path}")
    print(f"    Activation: '{activation_message}'")
    print()

    # Change to vault directory
    original_dir = os.getcwd()
    os.chdir(vault_path)

    try:
        # Spawn Claude Code interactively
        print(f"[*] Spawning Claude Code...")

        child = wexpect.spawn(
            'claude --dangerously-skip-permissions',
            encoding='utf-8',
            timeout=30,
            maxread=8192
        )

        print(f"[+] Process spawned successfully")
        print(f"[*] Waiting for Claude to initialize (this takes ~5-10 seconds)...")

        # Wait for Claude prompt
        # Claude Code shows "> " when ready for input
        try:
            # Try to detect the input prompt
            child.expect(['>', 'bypass permissions'], timeout=15)
            print(f"[+] Claude ready - prompt detected")

        except wexpect.TIMEOUT:
            # If timeout, Claude might still be loading
            print(f"[!] Prompt not detected yet, waiting 3 more seconds...")
            time.sleep(3)
            print(f"[i] Proceeding anyway...")

        # Give it a moment to settle
        time.sleep(1)

        # Send activation message directly to Claude's stdin
        print(f"\n[*] Sending activation message to agent...")
        child.sendline(activation_message)

        print(f"[+] Message sent: '{activation_message}'")
        print(f"[+] Agent should now be processing")
        print(f"\n[i] Waiting 15 seconds for agent to create success.txt...")

        # Wait and check for success.txt (test file)
        success_file = Path(vault_path) / "success.txt"
        if success_file.exists():
            success_file.unlink()  # Delete old one if exists

        time.sleep(15)  # Give agent time to respond

        if success_file.exists():
            print(f"[+] SUCCESS! Agent received message and created file!")
            print(f"[+] wexpect communication WORKS!")
            with open(success_file, 'r') as f:
                content = f.read()
            print(f"    File content: {content}")
            success_file.unlink()  # Clean up
        else:
            print(f"[!] FAILED - success.txt not created")
            print(f"[!] Agent may not have received the message")
            print(f"[i] Check the Claude terminal window manually")

        print(f"{'='*60}\n")

        # Return child for monitoring
        return child

    except wexpect.ExceptionPexpect as e:
        print(f"\n[X] wexpect error: {e}")
        print(f"[i] Fallback: Manually run 'claude --dangerously-skip-permissions'")
        print(f"[i] Then type: {activation_message}\n")
        return None

    except Exception as e:
        print(f"\n[X] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        # Restore original directory
        os.chdir(original_dir)


def monitor_completion(child, vault_path: str, timeout: int = 600):
    """
    Monitor for completion signal while keeping process alive

    Args:
        child: wexpect child process
        vault_path: Vault directory path
        timeout: Max seconds to wait (default 600 = 10 minutes)
    """

    signal_file = Path(vault_path) / "_system" / "agent_completion_signal.txt"
    start_time = time.time()

    print(f"[*] Monitoring completion signal...")
    print(f"    Signal file: {signal_file}")
    print(f"    Timeout: {timeout}s\n")

    while time.time() - start_time < timeout:
        # Check for completion signal
        if signal_file.exists():
            try:
                with open(signal_file, 'r') as f:
                    signal = f.read().strip()

                print(f"\n{'='*60}")
                print(f"[✓] PROCESSING COMPLETE!")
                print(f"    Signal: {signal}")
                print(f"{'='*60}\n")

                # Delete signal file
                signal_file.unlink()

                return True

            except Exception as e:
                print(f"[!] Error reading signal: {e}")

        # Check if process is still alive
        if child and not child.isalive():
            print(f"\n[!] Claude process exited")
            print(f"[i] Check if completion signal was written")

            if signal_file.exists():
                print(f"[✓] Completion signal found - processing finished")
                signal_file.unlink()
                return True
            else:
                print(f"[X] No completion signal - agent may have failed")
                return False

        time.sleep(2)  # Poll every 2 seconds

    print(f"\n[!] Timeout waiting for completion ({timeout}s)")
    print(f"[i] Processing may still be ongoing")
    return False


def main():
    """CLI interface for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Launch Claude Code processor with wexpect")
    parser.add_argument("--vault", type=str, default="C:/obsidian-memory-vault", help="Vault path")
    parser.add_argument("--message", type=str, default="file watcher summons you", help="Activation message")
    parser.add_argument("--wait", action="store_true", help="Wait for completion")

    args = parser.parse_args()

    # Launch Claude
    child = launch_claude_with_wexpect(args.vault, args.message)

    if child and args.wait:
        # Monitor for completion
        monitor_completion(child, args.vault)

    print(f"\n[i] Claude Code session active")
    print(f"[i] Process will continue in background")


if __name__ == "__main__":
    main()
