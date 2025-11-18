#!/usr/bin/env python3
"""
Error Recovery Utilities
Handles failures gracefully and provides recovery mechanisms across the pipeline
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from logger_setup import get_logger


class ErrorRecovery:
    """Error recovery and backup utilities"""

    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path)
        self.logger = get_logger(__name__, str(vault_path))
        self.backup_dir = self.vault_path / "_system" / "backups"
        self.error_log = self.vault_path / "_system" / "error-log.json"
        self.recovery_queue = self.vault_path / "_system" / "recovery-queue.json"

        # Create directories
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def backup_file(self, file_path: Path, label: str = "") -> Optional[Path]:
        """Create timestamped backup of a file"""
        try:
            if not file_path.exists():
                self.logger.warning(f"Cannot backup non-existent file: {file_path}")
                return None

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            label_suffix = f"_{label}" if label else ""
            backup_name = f"{file_path.stem}_{timestamp}{label_suffix}{file_path.suffix}"
            backup_path = self.backup_dir / backup_name

            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Backed up: {file_path.name} -> {backup_path.name}")

            return backup_path

        except Exception as e:
            self.logger.error(f"Failed to backup {file_path}: {e}", exc_info=True)
            return None

    def restore_backup(self, backup_path: Path, target_path: Optional[Path] = None) -> bool:
        """Restore a file from backup"""
        try:
            if not backup_path.exists():
                self.logger.error(f"Backup file not found: {backup_path}")
                return False

            if target_path is None:
                # Infer target from backup name (remove timestamp)
                target_name = backup_path.stem.split("_")[0] + backup_path.suffix
                target_path = self.vault_path / target_name

            shutil.copy2(backup_path, target_path)
            self.logger.info(f"Restored: {backup_path.name} -> {target_path}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to restore {backup_path}: {e}", exc_info=True)
            return False

    def log_error(self, operation: str, error: str, context: Dict = None):
        """Log error to persistent error log"""
        try:
            # Load existing log
            if self.error_log.exists():
                with open(self.error_log, 'r', encoding='utf-8') as f:
                    errors = json.load(f)
            else:
                errors = []

            # Add new error
            error_entry = {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "error": error,
                "context": context or {}
            }

            errors.append(error_entry)

            # Keep only last 1000 errors
            if len(errors) > 1000:
                errors = errors[-1000:]

            # Save log
            with open(self.error_log, 'w', encoding='utf-8') as f:
                json.dump(errors, f, indent=2)

            self.logger.error(f"Logged error: {operation} - {error}")

        except Exception as e:
            self.logger.error(f"Failed to log error: {e}", exc_info=True)

    def add_to_recovery_queue(self, file_path: Path, reason: str, metadata: Dict = None):
        """Add file to recovery queue for later processing"""
        try:
            # Load queue
            if self.recovery_queue.exists():
                with open(self.recovery_queue, 'r', encoding='utf-8') as f:
                    queue = json.load(f)
            else:
                queue = []

            # Add entry
            entry = {
                "file": str(file_path),
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {},
                "attempts": 0
            }

            queue.append(entry)

            # Save queue
            with open(self.recovery_queue, 'w', encoding='utf-8') as f:
                json.dump(queue, f, indent=2)

            self.logger.info(f"Added to recovery queue: {file_path.name} - {reason}")

        except Exception as e:
            self.logger.error(f"Failed to add to recovery queue: {e}", exc_info=True)

    def get_recovery_queue(self) -> List[Dict]:
        """Get list of files in recovery queue"""
        try:
            if not self.recovery_queue.exists():
                return []

            with open(self.recovery_queue, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Failed to read recovery queue: {e}", exc_info=True)
            return []

    def remove_from_recovery_queue(self, file_path: Path):
        """Remove file from recovery queue after successful processing"""
        try:
            queue = self.get_recovery_queue()

            # Filter out the file
            new_queue = [e for e in queue if Path(e["file"]) != file_path]

            # Save updated queue
            with open(self.recovery_queue, 'w', encoding='utf-8') as f:
                json.dump(new_queue, f, indent=2)

            self.logger.info(f"Removed from recovery queue: {file_path.name}")

        except Exception as e:
            self.logger.error(f"Failed to remove from recovery queue: {e}", exc_info=True)

    def retry_with_backoff(self,
                          func: Callable,
                          max_attempts: int = 3,
                          backoff_seconds: List[int] = None,
                          operation_name: str = "operation") -> Optional[Any]:
        """Retry a function with exponential backoff"""
        import time

        if backoff_seconds is None:
            backoff_seconds = [1, 5, 15]

        for attempt in range(max_attempts):
            try:
                self.logger.info(f"{operation_name}: Attempt {attempt + 1}/{max_attempts}")
                result = func()
                self.logger.info(f"{operation_name}: Success on attempt {attempt + 1}")
                return result

            except Exception as e:
                self.logger.warning(f"{operation_name}: Failed attempt {attempt + 1}: {e}")

                if attempt < max_attempts - 1:
                    sleep_time = backoff_seconds[min(attempt, len(backoff_seconds) - 1)]
                    self.logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    self.logger.error(f"{operation_name}: All attempts failed", exc_info=True)
                    self.log_error(operation_name, str(e), {"attempts": max_attempts})
                    return None

    def safe_json_write(self, file_path: Path, data: Dict, backup: bool = True) -> bool:
        """Safely write JSON with backup and atomic write"""
        try:
            # Create backup if requested
            if backup and file_path.exists():
                self.backup_file(file_path, label="pre_write")

            # Write to temporary file first
            temp_path = file_path.with_suffix(".tmp")

            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            # Atomic rename
            temp_path.replace(file_path)

            self.logger.info(f"Safely wrote JSON: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to safely write JSON {file_path}: {e}", exc_info=True)
            self.log_error("safe_json_write", str(e), {"file": str(file_path)})
            return False

    def safe_file_move(self, source: Path, dest: Path, backup: bool = True) -> bool:
        """Safely move file with backup"""
        try:
            if not source.exists():
                self.logger.error(f"Source file not found: {source}")
                return False

            # Backup destination if exists
            if backup and dest.exists():
                self.backup_file(dest, label="pre_move")

            # Ensure destination directory exists
            dest.parent.mkdir(parents=True, exist_ok=True)

            # Move file
            shutil.move(str(source), str(dest))

            self.logger.info(f"Safely moved: {source} -> {dest}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to move {source} -> {dest}: {e}", exc_info=True)
            self.log_error("safe_file_move", str(e), {"source": str(source), "dest": str(dest)})
            return False

    def cleanup_old_backups(self, keep_count: int = 50):
        """Clean up old backup files, keeping only most recent N"""
        try:
            backups = sorted(self.backup_dir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)

            if len(backups) > keep_count:
                for backup in backups[keep_count:]:
                    backup.unlink()
                    self.logger.info(f"Deleted old backup: {backup.name}")

                self.logger.info(f"Cleaned up {len(backups) - keep_count} old backups")

        except Exception as e:
            self.logger.error(f"Failed to cleanup old backups: {e}", exc_info=True)

    def get_recent_errors(self, limit: int = 20) -> List[Dict]:
        """Get recent errors from error log"""
        try:
            if not self.error_log.exists():
                return []

            with open(self.error_log, 'r', encoding='utf-8') as f:
                errors = json.load(f)

            return errors[-limit:]

        except Exception as e:
            self.logger.error(f"Failed to read error log: {e}", exc_info=True)
            return []

    def generate_recovery_report(self) -> str:
        """Generate recovery status report"""
        try:
            queue = self.get_recovery_queue()
            errors = self.get_recent_errors(limit=50)

            report = f"# Error Recovery Report\n\n"
            report += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            report += f"## Recovery Queue\n\n"
            report += f"**Items in queue**: {len(queue)}\n\n"

            if queue:
                for entry in queue:
                    report += f"- `{Path(entry['file']).name}` - {entry['reason']} (attempts: {entry.get('attempts', 0)})\n"
            else:
                report += "No items in recovery queue ✅\n"

            report += f"\n## Recent Errors (Last 50)\n\n"

            if errors:
                # Group by operation
                by_operation = {}
                for error in errors:
                    op = error["operation"]
                    if op not in by_operation:
                        by_operation[op] = []
                    by_operation[op].append(error)

                for op, op_errors in by_operation.items():
                    report += f"\n### {op} ({len(op_errors)} errors)\n\n"
                    for err in op_errors[-10:]:  # Show last 10 per operation
                        timestamp = err["timestamp"][:19]  # Truncate to seconds
                        report += f"- `{timestamp}`: {err['error']}\n"
            else:
                report += "No recent errors ✅\n"

            return report

        except Exception as e:
            self.logger.error(f"Failed to generate recovery report: {e}", exc_info=True)
            return f"# Error Recovery Report\n\nFailed to generate report: {e}\n"


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Error recovery utilities")
    parser.add_argument("--vault", type=str, default="C:/obsidian-memory-vault",
                       help="Path to vault")
    parser.add_argument("--queue", action="store_true",
                       help="Show recovery queue")
    parser.add_argument("--errors", action="store_true",
                       help="Show recent errors")
    parser.add_argument("--report", action="store_true",
                       help="Generate recovery report")
    parser.add_argument("--cleanup", action="store_true",
                       help="Cleanup old backups")

    args = parser.parse_args()

    recovery = ErrorRecovery(Path(args.vault))

    if args.queue:
        queue = recovery.get_recovery_queue()
        print(f"\n[OK] Recovery Queue ({len(queue)} items)")
        if queue:
            for entry in queue:
                print(f"\n   File: {Path(entry['file']).name}")
                print(f"   Reason: {entry['reason']}")
                print(f"   Attempts: {entry.get('attempts', 0)}")
        else:
            print("   No items in queue")

    elif args.errors:
        errors = recovery.get_recent_errors(limit=20)
        print(f"\n[OK] Recent Errors ({len(errors)} shown)")
        for error in errors:
            print(f"\n   Time: {error['timestamp'][:19]}")
            print(f"   Operation: {error['operation']}")
            print(f"   Error: {error['error']}")

    elif args.report:
        report = recovery.generate_recovery_report()
        report_path = Path(args.vault) / "_system" / "recovery-report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n[OK] Recovery Report Generated")
        print(f"   Report: {report_path}")

    elif args.cleanup:
        recovery.cleanup_old_backups(keep_count=50)
        print(f"\n[OK] Backup Cleanup Complete")
        print(f"   Keeping most recent 50 backups")

    else:
        print(f"\n[OK] Error Recovery Status")
        queue = recovery.get_recovery_queue()
        errors = recovery.get_recent_errors(limit=10)
        print(f"\n   Recovery queue: {len(queue)} items")
        print(f"   Recent errors: {len(errors)} in last 10")

    print()


if __name__ == "__main__":
    main()
