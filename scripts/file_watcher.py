#!/usr/bin/env python3
"""
The Second Brain - File Watcher
Monitors raw-conversations folder for new unprocessed files and prepares them for processing.

Version: 1.2
Updated: 2025-11-08
"""

import os
import sys
import json
import time
import subprocess
import re
import threading
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class QueueMonitor(threading.Thread):
    """Monitors the processing queue and displays real-time agent status."""

    def __init__(self, queue_path):
        super().__init__(daemon=True)
        self.queue_path = Path(queue_path)
        self.running = True
        self.last_status = None
        self.last_mtime = 0

    def run(self):
        """Monitor queue file for changes and display updates."""
        while self.running:
            try:
                # Check if queue file was modified
                current_mtime = self.queue_path.stat().st_mtime

                if current_mtime != self.last_mtime:
                    self.last_mtime = current_mtime
                    self._check_queue_status()

                time.sleep(2)  # Check every 2 seconds

            except Exception as e:
                # Queue file might not exist yet
                time.sleep(5)

    def _check_queue_status(self):
        """Parse queue file and display current status."""
        try:
            with open(self.queue_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract "Currently Processing" section
            processing_match = re.search(
                r'## Currently Processing\s*\n\s*<!--.*?-->\s*\n(.*?)(?=\n---|\n##|$)',
                content,
                re.DOTALL
            )

            if processing_match and processing_match.group(1).strip():
                processing_text = processing_match.group(1).strip()

                # Parse processing details
                file_match = re.search(r'^-\s+(\S+)', processing_text, re.MULTILINE)
                stage_match = re.search(r'^\s*-\s*\*\*Stage\*\*:\s*(.+?)$', processing_text, re.MULTILINE)
                started_match = re.search(r'^\s*-\s*\*\*Started\*\*:\s*(.+?)$', processing_text, re.MULTILINE)

                if file_match:
                    filename = file_match.group(1)
                    stage = stage_match.group(1) if stage_match else "Unknown"
                    started = started_match.group(1) if started_match else "Unknown"

                    status_msg = f"📋 AGENT STATUS: Processing {filename}\n    Stage: {stage}\n    Started: {started}"

                    if status_msg != self.last_status:
                        print(f"\n{'─'*60}")
                        print(status_msg)
                        print(f"{'─'*60}\n")
                        self.last_status = status_msg

            # Check for completed files (new completions)
            completed_section = re.search(
                r'## Completed \(Last 24 Hours\)(.*?)(?=\n---|\n##|$)',
                content,
                re.DOTALL
            )

            if completed_section:
                # Look for very recent completions (within last minute)
                recent_pattern = r'- \[x\]\s+(\S+)\s+\n\s+- \*\*Completed\*\*:\s+([^\n]+)\n\s+.*?\*\*Status\*\*:\s+(✅[^\n]+)'
                for match in re.finditer(recent_pattern, completed_section.group(1)):
                    filename = match.group(1)
                    completed_time = match.group(2)
                    status = match.group(3)

                    completion_msg = f"✅ COMPLETED: {filename}\n    Time: {completed_time}\n    {status}"

                    # Only show if this is new (not in last_status)
                    if self.last_status and filename not in str(self.last_status):
                        print(f"\n{'═'*60}")
                        print(completion_msg)
                        print(f"{'═'*60}\n")

        except Exception as e:
            # Silently ignore parsing errors
            pass

    def stop(self):
        """Stop the monitor thread."""
        self.running = False


class ConversationFileHandler(FileSystemEventHandler):
    """Handler for detecting new conversation files."""

    def __init__(self, config_path, queue_path, raw_conversations_path):
        self.config_path = Path(config_path)
        self.queue_path = Path(queue_path)
        self.raw_conversations_path = Path(raw_conversations_path)
        self.config = self.load_config()
        self.processing_batch = []
        self.batch_timeout = 5  # Wait 5 seconds for more files before processing batch
        self.last_file_time = None
        self.seen_files = set()  # Track files we've already seen (for polling)

        print(f"[#] Configuration loaded:")
        print(f"    - Batch threshold: {self.config['batch_processing']['min_file_count']} files")
        print(f"    - Large file threshold: {self.config['batch_processing']['large_file_threshold_chars']:,} chars")
        print(f"    - Batch timeout: {self.batch_timeout}s")

        # Initialize seen_files with existing files
        self._scan_existing_files()

    def load_config(self):
        """Load configuration from config.json."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Warning: Could not load config.json: {e}")
            print("    Using default configuration...")
            return {
                "batch_processing": {
                    "min_file_count": 5,
                    "large_file_threshold_chars": 100000,
                    "total_batch_threshold_chars": 500000
                }
            }

    def on_created(self, event):
        """Called when a file is created."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        print(f"[DEBUG] on_created event: {file_path.name}")

        # Only process files starting with "unprocessed_" and ending with ".md"
        if file_path.name.startswith("unprocessed_") and file_path.suffix == ".md":
            self._add_file_to_batch(file_path)

    def on_modified(self, event):
        """Called when a file is modified (Windows fallback)."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        print(f"[DEBUG] on_modified event: {file_path.name}")

        # Only process files starting with "unprocessed_" and ending with ".md"
        # Check if already in batch to avoid duplicates
        if file_path.name.startswith("unprocessed_") and file_path.suffix == ".md":
            if file_path not in self.processing_batch:
                self._add_file_to_batch(file_path)

    def _add_file_to_batch(self, file_path):
        """Add a file to the processing batch."""
        print(f"\n[+] Detected new file: {file_path.name}")

        # Wait briefly for file write to complete
        time.sleep(0.5)

        # Add to batch and set timer
        self.processing_batch.append(file_path)
        self.last_file_time = time.time()

        # Start monitoring for batch
        print(f"    Added to batch (currently {len(self.processing_batch)} file(s))")
        print(f"    Waiting {self.batch_timeout}s for more files...")

    def _scan_existing_files(self):
        """Scan directory for existing files to avoid reprocessing."""
        try:
            for file_path in self.raw_conversations_path.glob("*.md"):
                self.seen_files.add(file_path.name)
            print(f"[i] Initialized with {len(self.seen_files)} existing files")
        except Exception as e:
            print(f"[!] Error scanning existing files: {e}")

    def poll_for_new_files(self):
        """Manually poll for new files (Windows fallback)."""
        try:
            for file_path in self.raw_conversations_path.glob("unprocessed_*.md"):
                if file_path.name not in self.seen_files:
                    print(f"[POLL] Found new file: {file_path.name}")
                    self.seen_files.add(file_path.name)
                    if file_path not in self.processing_batch:
                        self._add_file_to_batch(file_path)
        except Exception as e:
            print(f"[!] Error polling for files: {e}")

    def check_and_process_batch(self):
        """Check if batch is ready to process."""
        if not self.processing_batch:
            return

        if self.last_file_time is None:
            return

        # Check if timeout has passed
        time_since_last = time.time() - self.last_file_time
        if time_since_last >= self.batch_timeout:
            self.process_batch()

    def process_batch(self):
        """Process the current batch of files."""
        if not self.processing_batch:
            return

        print(f"\n{'='*60}")
        print(f"[~] Processing batch of {len(self.processing_batch)} file(s)...")
        print(f"{'='*60}")

        # Calculate batch statistics
        total_size = 0
        files_to_queue = []

        for file_path in self.processing_batch:
            try:
                # Get file size
                file_size = file_path.stat().st_size
                total_size += file_size
                files_to_queue.append(file_path)

                print(f"[+] Queued: {file_path.name} ({file_size:,} bytes)")

            except Exception as e:
                print(f"[X] Error processing {file_path.name}: {e}")

        if not files_to_queue:
            print("[!] No files were successfully queued")
            self.processing_batch = []
            self.last_file_time = None
            return

        # Determine batch mode
        batch_mode = self.determine_batch_mode(files_to_queue, total_size)

        # Update processing queue
        self.update_processing_queue(files_to_queue, batch_mode, total_size)

        # Clear batch
        self.processing_batch = []
        self.last_file_time = None

        print(f"\n[✓] Batch queuing complete!")
        print(f"    Mode: {batch_mode}")
        print(f"    Files: {len(files_to_queue)}")
        print(f"    Total size: {total_size:,} bytes ({total_size/1000:.1f} KB)")
        print(f"\n[i] Files remain as 'unprocessed_*.md' until agent starts processing.")
        print(f"    The Processing Pipeline Agent will rename them when it begins.")
        print(f"{'='*60}\n")

    def determine_batch_mode(self, files, total_size):
        """Determine if batch processing should be used."""
        config = self.config.get("batch_processing", {})

        min_file_count = config.get("min_file_count", 5)
        large_file_threshold = config.get("large_file_threshold_chars", 100000)
        total_threshold = config.get("total_batch_threshold_chars", 500000)

        # Check conditions
        if len(files) >= min_file_count:
            return "Batch (5+ files)"

        if total_size >= total_threshold:
            return "Batch (total size > 500k)"

        for file_path in files:
            try:
                if file_path.stat().st_size >= large_file_threshold:
                    return "Batch (large file detected)"
            except:
                pass

        return "Single"

    def update_processing_queue(self, files, mode, total_size):
        """Update the processing-queue.md file."""
        try:
            timestamp = datetime.now().isoformat()

            # Read current queue
            with open(self.queue_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find the marker
            marker = "<!-- File watcher will add entries here automatically -->"

            if marker not in content:
                print("[!] Warning: Could not find marker in processing-queue.md")
                print("    Files renamed but queue not updated.")
                return

            # Build the new entry
            entry_lines = [
                f"\n\n### Batch Added: {timestamp}\n",
                f"**Mode**: {mode}",
                f"**File count**: {len(files)}",
                f"**Total Size**: {total_size:,} bytes\n",
                "**Files**:"
            ]

            for file_path in files:
                entry_lines.append(f"- [ ] {file_path.name}")

            entry = "\n".join(entry_lines) + "\n"

            # Insert entry after marker
            parts = content.split(marker, 1)
            content = parts[0] + marker + entry + (parts[1] if len(parts) > 1 else "")

            # Update queue status
            content = content.replace(
                '**Queue Status**: Empty ✅',
                f'**Queue Status**: {len(files)} file(s) awaiting processing ⏳'
            )

            # Update last check timestamp
            if '**Last Check**: Never' in content:
                content = content.replace(
                    '**Last Check**: Never',
                    f'**Last Check**: {timestamp}'
                )
            else:
                # Find and replace any existing timestamp
                import re
                content = re.sub(
                    r'\*\*Last Check\*\*: [^\n]+',
                    f'**Last Check**: {timestamp}',
                    content
                )

            # Write back to queue
            with open(self.queue_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"[*] Updated processing queue: {len(files)} file(s) added")

            # Spawn the processing pipeline agent
            self.spawn_processing_agent()

        except Exception as e:
            print(f"[X] Error updating processing queue: {e}")
            import traceback
            traceback.print_exc()

    def spawn_processing_agent(self):
        """Open Claude Code terminal for manual activation (simple & reliable)."""
        vault_dir = self.raw_conversations_path.parent.parent

        print(f"\n{'='*60}")
        print(f"[!] NEW CONVERSATIONS READY")
        print(f"{'='*60}\n")

        # Open Claude in terminal (no automation, just open it)
        cmd = [
            'wt.exe', '-w', '-1', '--title', 'Claude - Process Queue',
            '--', 'cmd.exe', '/k',
            f'cd /d "{vault_dir}" && claude --dangerously-skip-permissions'
        ]

        subprocess.Popen(cmd)

        print(f"[+] Claude opened in: {vault_dir}")
        print(f"\n[i] In the Claude terminal, type:")
        print(f"      file watcher summons you")
        print(f"\n{'='*60}\n")

        # Beep to alert
        try:
            import winsound
            winsound.MessageBeep()
        except:
            pass

        # Monitor for completion
        threading.Thread(target=self._wait_for_signal, args=(vault_dir,), daemon=True).start()

    def spawn_processing_agent_simple(self):
        """Simple version - just open Claude, user types activation."""
        vault_dir = self.raw_conversations_path.parent.parent

        print(f"\n{'='*60}")
        print(f"[!] NEW CONVERSATIONS DETECTED")
        print(f"{'='*60}\n")

        # Open terminal with Claude
        cmd = [
            'wt.exe', '-w', '-1', '--title', 'Claude - Process Queue',
            '--', 'cmd.exe', '/k',
            f'cd /d "{vault_dir}" && claude --dangerously-skip-permissions'
        ]

        subprocess.Popen(cmd)

        print(f"[+] Claude terminal opened")
        print(f"\n[i] Type in the Claude window:")
        print(f"      file watcher summons you\n")

        # Beep
        try:
            import winsound
            winsound.MessageBeep()
        except:
            pass

        # Monitor completion
        threading.Thread(target=self._wait_for_signal, args=(vault_dir,), daemon=True).start()

    def _fallback_manual_prompt(self, vault_dir):
        """Fallback: Prompt user to run Claude manually"""
        print(f"\n{'='*60}")
        print(f"[!] MANUAL ACTION REQUIRED")
        print(f"{'='*60}")
        print(f"\n1. Open terminal in: {vault_dir}")
        print(f"2. Run: claude --dangerously-skip-permissions")
        print(f"3. Type: /process-queue")
        print(f"\n{'='*60}\n")

        # Alert sound
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONINFORMATION)
        except:
            pass

    def _wait_for_signal(self, vault_dir):
        """Wait for completion signal (infinite - agent will run until done)"""
        try:
            signal_file = vault_dir / "_system" / "agent_completion_signal.txt"

            print(f"\n[i] Monitoring completion signal (no timeout)...")
            print(f"    Signal file: {signal_file}\n")

            # Infinite loop - agent will complete when it's done
            while True:
                if signal_file.exists():
                    try:
                        with open(signal_file, 'r') as f:
                            signal = f.read().strip()

                        print(f"\n{'='*70}")
                        print(f"✅ PROCESSING PIPELINE COMPLETE!")
                        print(f"{'='*70}")
                        print(f"Signal received: {signal}\n")

                        # Find and display the latest processing log
                        self._display_latest_log(vault_dir)

                        # Remove the completion signal file
                        signal_file.unlink()
                        print(f"\n[✓] Completion signal removed")

                        # Notify user to close Claude session
                        print(f"\n{'─'*70}")
                        print(f"[!] PLEASE CLOSE THE CLAUDE TERMINAL WINDOW")
                        print(f"    The processing agent has finished and should be terminated.")
                        print(f"    Press Ctrl+C in the Claude window or close it manually.")
                        print(f"{'─'*70}\n")

                        # Alert beep
                        try:
                            import winsound
                            winsound.MessageBeep(winsound.MB_ICONASTERISK)
                            time.sleep(0.3)
                            winsound.MessageBeep(winsound.MB_ICONASTERISK)
                        except:
                            pass

                        return

                    except Exception as e:
                        print(f"[!] Error reading signal: {e}")

                time.sleep(2)  # Poll every 2 seconds

        except Exception as e:
            print(f"[X] Error monitoring signal: {e}")

    def _display_latest_log(self, vault_dir):
        """Display summary from the latest processing log."""
        try:
            log_dir = vault_dir / "docs" / "pipeline_agent"

            if not log_dir.exists():
                print(f"[!] Log directory not found: {log_dir}")
                return

            # Find all processing log files
            log_files = sorted(log_dir.glob("processing_log_*.md"), reverse=True)

            if not log_files:
                print(f"[!] No processing logs found in {log_dir}")
                return

            # Read the latest log
            latest_log = log_files[0]
            print(f"\n{'─'*70}")
            print(f"📋 PROCESSING LOG: {latest_log.name}")
            print(f"{'─'*70}\n")

            with open(latest_log, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract key sections to display
            import re

            # Extract summary statistics
            summary_match = re.search(r'## Summary Statistics\s+(.*?)(?=\n##|\Z)', content, re.DOTALL)
            if summary_match:
                print("SUMMARY STATISTICS:")
                summary_lines = summary_match.group(1).strip().split('\n')
                for line in summary_lines:
                    if line.strip().startswith('-'):
                        print(f"  {line.strip()}")
                print()

            # Extract errors/warnings section
            errors_match = re.search(r'## Errors & Warnings\s+(.*?)(?=\n##|\Z)', content, re.DOTALL)
            if errors_match:
                errors_text = errors_match.group(1).strip()
                if "No errors" not in errors_text and errors_text:
                    print("⚠️  ERRORS & WARNINGS:")
                    print(f"  {errors_text}\n")

            # Extract next actions
            actions_match = re.search(r'## Next Actions\s+(.*?)(?=\n##|\Z)', content, re.DOTALL)
            if actions_match:
                actions_text = actions_match.group(1).strip()
                if actions_text and not re.search(r'\{\{.*?\}\}', actions_text):  # Skip if template placeholders remain
                    print("📌 NEXT ACTIONS:")
                    actions_lines = actions_text.split('\n')
                    for line in actions_lines:
                        if line.strip().startswith('-'):
                            print(f"  {line.strip()}")
                    print()

            print(f"{'─'*70}")
            print(f"Full log available at: {latest_log.relative_to(vault_dir)}")
            print(f"{'─'*70}")

        except Exception as e:
            print(f"[!] Error displaying log: {e}")
            import traceback
            traceback.print_exc()

    def _wait_and_embed(self, process, vault_dir):
        """Wait for agent to complete, then trigger embedding of new notes."""
        try:
            # Monitor completion signal file instead of just waiting for process
            signal_file = vault_dir / "_system" / "agent_completion_signal.txt"
            timeout = 600  # 10 minutes max
            start_time = time.time()

            print(f"\n[i] Monitoring agent completion signal...")
            print(f"    Signal file: {signal_file}")
            print(f"    Timeout: {timeout} seconds\n")

            # Poll for completion signal
            while time.time() - start_time < timeout:
                if signal_file.exists():
                    # Read signal
                    try:
                        with open(signal_file, 'r') as f:
                            signal = f.read().strip()
                        print(f"\n{'─'*60}")
                        print(f"[✓] Agent completion signal received: {signal}")
                        print(f"{'─'*60}\n")

                        # Delete signal file
                        signal_file.unlink()
                        break
                    except Exception as e:
                        print(f"[!] Error reading signal file: {e}")

                # Check if process exited prematurely
                if process.poll() is not None:
                    print(f"\n[!] Agent process exited with code: {process.returncode}")
                    if not signal_file.exists():
                        print(f"[!] No completion signal found - agent may have failed")
                    break

                time.sleep(2)  # Check every 2 seconds
            else:
                # Timeout reached
                print(f"\n[!] Agent timeout - exceeded {timeout} seconds")
                print(f"[!] Terminating agent process...")
                process.terminate()
                process.wait(timeout=10)
                return

            # Wait for process to fully exit
            return_code = process.wait(timeout=10)
            print(f"[i] Agent process exited with return code: {return_code}\n")

            # Trigger embedding of newly created processed notes
            print("[~] Embedding new processed notes with Ollama...")
            print("    Model: nomic-embed-text:latest")
            print("    Target: 00-Inbox/processed/\n")

            embed_script = vault_dir / "scripts" / "embed_notes_ollama.py"

            # Run embedding script
            embed_process = subprocess.run(
                [
                    sys.executable,  # Use same Python interpreter
                    str(embed_script),
                    "--vault", str(vault_dir),
                    "--folder", "00-Inbox/processed"
                ],
                cwd=str(vault_dir),
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for embedding
            )

            if embed_process.returncode == 0:
                print(f"[OK] Embedding complete!")
                # Parse output for statistics
                if "Files processed:" in embed_process.stdout:
                    # Extract stats from output
                    for line in embed_process.stdout.split('\n'):
                        if any(key in line for key in ["Files processed:", "Files skipped:", "Chunks embedded:"]):
                            print(f"    {line.strip()}")
            else:
                print(f"[X] Embedding failed with return code: {embed_process.returncode}")
                if embed_process.stderr:
                    print(f"    Error: {embed_process.stderr}")

        except subprocess.TimeoutExpired:
            print("[X] Embedding timed out after 10 minutes")
        except Exception as e:
            print(f"[X] Error during embedding: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point."""
    print("="*60)
    print("The Second Brain - File Watcher")
    print("="*60)
    print()

    # Determine paths
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    else:
        vault_path = Path(__file__).parent.parent

    config_path = vault_path / "_system" / "config.json"
    queue_path = vault_path / "_system" / "processing-queue.md"
    raw_conversations_path = vault_path / "00-Inbox" / "raw-conversations"

    print(f"[.] Vault path: {vault_path}")
    print(f"[.] Watching: {raw_conversations_path}")
    print()

    # Verify paths exist
    if not raw_conversations_path.exists():
        print(f"[!] Directory not found: {raw_conversations_path}")
        print(f"    Creating directory...")
        raw_conversations_path.mkdir(parents=True, exist_ok=True)
        print(f"    [✓] Directory created")

    if not config_path.exists():
        print(f"[!] Warning: config.json not found at {config_path}")
        print(f"    Using default configuration...")

    if not queue_path.exists():
        print(f"[X] Error: processing-queue.md not found at {queue_path}")
        print(f"    Please ensure the vault structure is set up correctly.")
        return

    print()

    # Set up file system observer
    event_handler = ConversationFileHandler(config_path, queue_path, raw_conversations_path)
    observer = Observer()
    observer.schedule(event_handler, str(raw_conversations_path), recursive=False)
    observer.start()

    # Check for existing unprocessed files on startup
    print("[*] Checking for existing unprocessed files...")
    existing_unprocessed = list(raw_conversations_path.glob("unprocessed_*.md"))

    if existing_unprocessed:
        print(f"[!] Found {len(existing_unprocessed)} unprocessed file(s):")
        for f in existing_unprocessed:
            print(f"    - {f.name}")

        print(f"\n[*] Triggering agent to process existing files...")
        # Add to batch and trigger processing
        for f in existing_unprocessed:
            event_handler._add_file_to_batch(f)

        # Force immediate processing (don't wait for timeout)
        if event_handler.processing_batch:
            event_handler.process_batch()
    else:
        print(f"[i] No existing unprocessed files found")

    # Start queue monitor for real-time agent status
    queue_monitor = QueueMonitor(queue_path)
    queue_monitor.start()

    print()
    print("[✓] File watcher is running!")
    print(f"    Press Ctrl+C to stop")
    print()
    print("Monitoring for new conversation files...")
    print("    (Using both file system events + polling for Windows compatibility)")
    print("    (Monitoring processing queue for agent status updates)")
    print("-" * 60)

    try:
        poll_counter = 0
        while True:
            time.sleep(1)
            poll_counter += 1

            # Poll for new files every 3 seconds (Windows fallback)
            if poll_counter >= 3:
                event_handler.poll_for_new_files()
                poll_counter = 0

            # Check if batch needs processing
            event_handler.check_and_process_batch()

    except KeyboardInterrupt:
        print("\n\n[-] Stopping file watcher...")
        queue_monitor.stop()
        observer.stop()
        observer.join()
        print("[✓] File watcher stopped.")


if __name__ == "__main__":
    main()
