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
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


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

        print(f"[#] Configuration loaded:")
        print(f"    - Batch threshold: {self.config['batch_processing']['min_file_count']} files")
        print(f"    - Large file threshold: {self.config['batch_processing']['large_file_threshold_chars']:,} chars")
        print(f"    - Batch timeout: {self.batch_timeout}s")

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

        # Only process files starting with "unprocessed_" and ending with ".md"
        if file_path.name.startswith("unprocessed_") and file_path.suffix == ".md":
            print(f"\n[+] Detected new file: {file_path.name}")

            # Wait briefly for file write to complete
            time.sleep(0.5)

            # Add to batch and set timer
            self.processing_batch.append(file_path)
            self.last_file_time = time.time()

            # Start monitoring for batch
            print(f"    Added to batch (currently {len(self.processing_batch)} file(s))")
            print(f"    Waiting {self.batch_timeout}s for more files...")

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
        renamed_files = []

        for file_path in self.processing_batch:
            try:
                # Get file size
                file_size = file_path.stat().st_size
                total_size += file_size

                # Rename file from unprocessed_ to processing_
                new_name = file_path.name.replace("unprocessed_", "processing_")
                new_path = file_path.parent / new_name

                file_path.rename(new_path)
                renamed_files.append(new_path)

                print(f"[>] Renamed: {file_path.name} -> {new_name}")

            except Exception as e:
                print(f"[X] Error processing {file_path.name}: {e}")

        if not renamed_files:
            print("[!] No files were successfully renamed")
            self.processing_batch = []
            self.last_file_time = None
            return

        # Determine batch mode
        batch_mode = self.determine_batch_mode(renamed_files, total_size)

        # Update processing queue
        self.update_processing_queue(renamed_files, batch_mode, total_size)

        # Clear batch
        self.processing_batch = []
        self.last_file_time = None

        print(f"\n[✓] Batch processing complete!")
        print(f"    Mode: {batch_mode}")
        print(f"    Files: {len(renamed_files)}")
        print(f"    Total size: {total_size:,} bytes ({total_size/1000:.1f} KB)")
        print(f"\n[i] Files are now in the processing queue.")
        print(f"    The Processing Pipeline Agent will pick them up automatically.")
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
                f"**Total Size**: {total_size:,} characters\n",
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
        """Spawn the processing-pipeline-agent to handle queued files."""
        try:
            print("\n[~] Spawning processing-pipeline-agent...")

            # Change to vault directory for agent context
            vault_dir = self.raw_conversations_path.parent.parent

            cmd = [
                'claude', '-p',  # Headless/print mode
                'Use the processing-pipeline-agent subagent to process all files in the queue.',
                '--output-format', 'json',
                '--max-turns', '20'  # Allow enough turns for full pipeline
            ]

            # Run agent in background (non-blocking)
            process = subprocess.Popen(
                cmd,
                cwd=str(vault_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            print(f"[✓] Agent spawned (PID: {process.pid})")
            print("    Processing will happen in background...")
            print("    Check processing-queue.md for status updates")

        except FileNotFoundError:
            print("[X] 'claude' command not found")
            print("    Make sure Claude Code is installed and in PATH")
            print("    You can manually run: claude 'Use processing-pipeline-agent'")
        except Exception as e:
            print(f"[X] Error spawning agent: {e}")
            print("    You can manually run: claude 'Use processing-pipeline-agent'")


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

    print()
    print("[✓] File watcher is running!")
    print(f"    Press Ctrl+C to stop")
    print()
    print("Monitoring for new conversation files...")
    print("-" * 60)

    try:
        while True:
            time.sleep(1)
            # Check if batch needs processing
            event_handler.check_and_process_batch()

    except KeyboardInterrupt:
        print("\n\n[-] Stopping file watcher...")
        observer.stop()
        observer.join()
        print("[✓] File watcher stopped.")


if __name__ == "__main__":
    main()
