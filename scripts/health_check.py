#!/usr/bin/env python3
"""
System Health Check
Comprehensive health check for the Second Brain pipeline
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from logger_setup import get_logger, TimedOperation


class HealthChecker:
    """Perform system health checks"""

    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path)
        self.logger = get_logger(__name__, str(vault_path))
        self.checks = []

    def run_all_checks(self) -> Dict:
        """Run all health checks"""
        with TimedOperation(self.logger, "Running health checks"):
            results = {
                "timestamp": datetime.now().isoformat(),
                "status": "healthy",
                "checks": []
            }

            # Run checks
            self.check_directory_structure()
            self.check_config_file()
            self.check_taxonomy()
            self.check_tag_notes()
            self.check_conversations()
            self.check_scripts()
            self.check_logs()
            self.check_disk_space()

            # Compile results
            results["checks"] = self.checks

            # Determine overall status
            failed = [c for c in self.checks if c["status"] == "failed"]
            warnings = [c for c in self.checks if c["status"] == "warning"]

            if failed:
                results["status"] = "unhealthy"
            elif warnings:
                results["status"] = "degraded"

            results["summary"] = {
                "total_checks": len(self.checks),
                "passed": len([c for c in self.checks if c["status"] == "passed"]),
                "warnings": len(warnings),
                "failed": len(failed)
            }

            self.logger.info(f"Health check complete: {results['status']}")

            return results

    def check_directory_structure(self):
        """Check required directories exist"""
        self.logger.info("Checking directory structure")

        required_dirs = [
            "_system",
            "_system/logs",
            "_system/backups",
            "00-Inbox",
            "00-Inbox/raw-conversations",
            "00-Inbox/processed",
            "scripts"
        ]

        missing = []
        for dir_path in required_dirs:
            full_path = self.vault_path / dir_path
            if not full_path.exists():
                missing.append(dir_path)

        if missing:
            self.checks.append({
                "name": "Directory Structure",
                "status": "warning",
                "message": f"Missing directories: {', '.join(missing)}"
            })
        else:
            self.checks.append({
                "name": "Directory Structure",
                "status": "passed",
                "message": "All required directories present"
            })

    def check_config_file(self):
        """Check config.json is valid"""
        self.logger.info("Checking config file")

        config_path = self.vault_path / "_system" / "config.json"

        if not config_path.exists():
            self.checks.append({
                "name": "Config File",
                "status": "failed",
                "message": "config.json not found"
            })
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Check required fields
            required_fields = ["version", "system_name", "file_watcher", "taxonomy", "neo4j"]
            missing = [f for f in required_fields if f not in config]

            if missing:
                self.checks.append({
                    "name": "Config File",
                    "status": "warning",
                    "message": f"Missing fields: {', '.join(missing)}"
                })
            else:
                self.checks.append({
                    "name": "Config File",
                    "status": "passed",
                    "message": "Config valid"
                })

        except json.JSONDecodeError as e:
            self.checks.append({
                "name": "Config File",
                "status": "failed",
                "message": f"Invalid JSON: {e}"
            })

    def check_taxonomy(self):
        """Check taxonomy file"""
        self.logger.info("Checking taxonomy")

        taxonomy_path = self.vault_path / "_system" / "tag-taxonomy.md"

        if not taxonomy_path.exists():
            self.checks.append({
                "name": "Taxonomy",
                "status": "failed",
                "message": "tag-taxonomy.md not found"
            })
            return

        try:
            with open(taxonomy_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Count tags
            import re
            yaml_blocks = re.findall(r'```yaml\n(.*?)\n```', content, re.DOTALL)

            tag_count = 0
            for block in yaml_blocks:
                import yaml
                try:
                    data = yaml.safe_load(block)
                    if isinstance(data, dict):
                        tag_count += len(data)
                except:
                    pass

            if tag_count == 0:
                self.checks.append({
                    "name": "Taxonomy",
                    "status": "warning",
                    "message": "No tags found in taxonomy"
                })
            else:
                self.checks.append({
                    "name": "Taxonomy",
                    "status": "passed",
                    "message": f"{tag_count} tags defined"
                })

        except Exception as e:
            self.checks.append({
                "name": "Taxonomy",
                "status": "failed",
                "message": f"Error reading taxonomy: {e}"
            })

    def check_tag_notes(self):
        """Check tag notes"""
        self.logger.info("Checking tag notes")

        tag_notes = []
        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                    if 'type: tag-note' in content:
                        tag_notes.append(md_file)
            except:
                pass

        self.checks.append({
            "name": "Tag Notes",
            "status": "passed",
            "message": f"{len(tag_notes)} tag notes found"
        })

    def check_conversations(self):
        """Check conversations"""
        self.logger.info("Checking conversations")

        processed_dir = self.vault_path / "00-Inbox" / "processed"

        if not processed_dir.exists():
            self.checks.append({
                "name": "Conversations",
                "status": "warning",
                "message": "Processed directory not found"
            })
            return

        conv_count = len(list(processed_dir.glob("*.md")))

        self.checks.append({
            "name": "Conversations",
            "status": "passed",
            "message": f"{conv_count} conversations processed"
        })

    def check_scripts(self):
        """Check all utility scripts exist"""
        self.logger.info("Checking scripts")

        required_scripts = [
            "logger_setup.py",
            "export_brain_data.py",
            "brain_space_calculator.py",
            "config_validator.py",
            "migrate_tag_notes.py",
            "error_recovery.py",
            "canvas_generator.py",
            "timeline_generator.py",
            "batch_neo4j_helper.py",
            "tag_path_resolver.py",
            "entity_prominence.py",
            "frontmatter_parser.py",
            "similarity_matcher.py",
            "health_check.py"
        ]

        scripts_dir = self.vault_path / "scripts"
        missing = []

        for script in required_scripts:
            script_path = scripts_dir / script
            if not script_path.exists():
                missing.append(script)

        if missing:
            self.checks.append({
                "name": "Scripts",
                "status": "warning",
                "message": f"Missing scripts: {', '.join(missing)}"
            })
        else:
            self.checks.append({
                "name": "Scripts",
                "status": "passed",
                "message": f"All {len(required_scripts)} scripts present"
            })

    def check_logs(self):
        """Check log files"""
        self.logger.info("Checking logs")

        logs_dir = self.vault_path / "_system" / "logs"

        if not logs_dir.exists():
            self.checks.append({
                "name": "Logs",
                "status": "warning",
                "message": "Logs directory not found"
            })
            return

        log_count = len(list(logs_dir.glob("*.log")))

        self.checks.append({
            "name": "Logs",
            "status": "passed",
            "message": f"{log_count} log files"
        })

    def check_disk_space(self):
        """Check available disk space"""
        self.logger.info("Checking disk space")

        try:
            import shutil
            stat = shutil.disk_usage(self.vault_path)

            free_gb = stat.free / (1024**3)
            total_gb = stat.total / (1024**3)
            percent_free = (stat.free / stat.total) * 100

            if percent_free < 10:
                status = "failed"
                message = f"Low disk space: {free_gb:.1f}GB free ({percent_free:.1f}%)"
            elif percent_free < 20:
                status = "warning"
                message = f"Disk space getting low: {free_gb:.1f}GB free ({percent_free:.1f}%)"
            else:
                status = "passed"
                message = f"{free_gb:.1f}GB free ({percent_free:.1f}%)"

            self.checks.append({
                "name": "Disk Space",
                "status": status,
                "message": message
            })

        except Exception as e:
            self.checks.append({
                "name": "Disk Space",
                "status": "warning",
                "message": f"Unable to check: {e}"
            })

    def generate_report(self, output_file: Path = None) -> str:
        """Generate health check report"""
        if output_file is None:
            output_file = self.vault_path / "_system" / "health-report.md"

        results = self.run_all_checks()

        report = "# System Health Report\n\n"
        report += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"**Overall Status**: {results['status'].upper()}\n\n"
        report += "---\n\n"

        # Summary
        summary = results["summary"]
        report += "## Summary\n\n"
        report += f"- **Total Checks**: {summary['total_checks']}\n"
        report += f"- **Passed**: {summary['passed']}\n"
        report += f"- **Warnings**: {summary['warnings']}\n"
        report += f"- **Failed**: {summary['failed']}\n\n"

        # Check details
        report += "## Check Details\n\n"

        for check in results["checks"]:
            status_icon = {
                "passed": "✅",
                "warning": "⚠️",
                "failed": "❌"
            }.get(check["status"], "❓")

            report += f"### {status_icon} {check['name']}\n\n"
            report += f"**Status**: {check['status'].upper()}\n\n"
            report += f"{check['message']}\n\n"

        # Save
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        self.logger.info(f"Health report generated: {output_file}")

        return report


def main():
    import argparse

    parser = argparse.ArgumentParser(description="System health check")
    parser.add_argument("--vault", type=str, default="C:/obsidian-memory-vault",
                       help="Path to vault")
    parser.add_argument("--report", action="store_true",
                       help="Generate health report")
    parser.add_argument("--json", action="store_true",
                       help="Output as JSON")

    args = parser.parse_args()

    checker = HealthChecker(Path(args.vault))

    if args.report:
        report = checker.generate_report()
        print(f"\n[OK] Health Report Generated")
        print(f"   File: {checker.vault_path / '_system' / 'health-report.md'}")

    else:
        results = checker.run_all_checks()

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            status_icon = {
                "healthy": "[OK]",
                "degraded": "[WARNING]",
                "unhealthy": "[ERROR]"
            }.get(results["status"], "[?]")

            print(f"\n{status_icon} System Health: {results['status'].upper()}")
            print(f"\n   Passed: {results['summary']['passed']}/{results['summary']['total_checks']}")
            print(f"   Warnings: {results['summary']['warnings']}")
            print(f"   Failed: {results['summary']['failed']}")

            # Show failures and warnings
            for check in results["checks"]:
                if check["status"] in ["warning", "failed"]:
                    print(f"\n   [{check['status'].upper()}] {check['name']}")
                    print(f"      {check['message']}")

    print()


if __name__ == "__main__":
    main()
