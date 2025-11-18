#!/usr/bin/env python3
"""
Frontmatter Parser Utility
Robust YAML frontmatter parser and writer for markdown files
"""

import yaml
import re
from pathlib import Path
from typing import Dict, Tuple, Optional
from logger_setup import get_logger


class FrontmatterParser:
    """Parse and manipulate YAML frontmatter in markdown files"""

    def __init__(self, vault_path: Path = None):
        self.vault_path = Path(vault_path) if vault_path else None
        self.logger = get_logger(__name__, str(vault_path) if vault_path else ".")

    def parse(self, file_path: Path) -> Tuple[Dict, str]:
        """
        Parse markdown file into frontmatter dict and body string

        Returns:
            (frontmatter_dict, body_string)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Match frontmatter
            fm_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)

            if not fm_match:
                self.logger.warning(f"No frontmatter found in {file_path.name}")
                return {}, content

            frontmatter_str = fm_match.group(1)
            body = fm_match.group(2)

            # Parse YAML
            try:
                frontmatter = yaml.safe_load(frontmatter_str)
                if frontmatter is None:
                    frontmatter = {}
            except yaml.YAMLError as e:
                self.logger.error(f"Failed to parse YAML in {file_path.name}: {e}")
                return {}, content

            return frontmatter, body

        except Exception as e:
            self.logger.error(f"Failed to parse {file_path.name}: {e}", exc_info=True)
            return {}, ""

    def write(self, file_path: Path, frontmatter: Dict, body: str):
        """
        Write frontmatter and body back to markdown file
        """
        try:
            # Serialize frontmatter to YAML
            frontmatter_str = yaml.dump(
                frontmatter,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )

            # Construct content
            content = f"---\n{frontmatter_str}---\n{body}"

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.logger.info(f"Written frontmatter to {file_path.name}")

        except Exception as e:
            self.logger.error(f"Failed to write {file_path.name}: {e}", exc_info=True)

    def get_field(self, file_path: Path, field: str) -> Optional[any]:
        """Get single frontmatter field value"""
        frontmatter, _ = self.parse(file_path)
        return frontmatter.get(field, None)

    def set_field(self, file_path: Path, field: str, value: any):
        """Set single frontmatter field value"""
        frontmatter, body = self.parse(file_path)
        frontmatter[field] = value
        self.write(file_path, frontmatter, body)
        self.logger.info(f"Set {field} = {value} in {file_path.name}")

    def update_fields(self, file_path: Path, fields: Dict):
        """Update multiple frontmatter fields"""
        frontmatter, body = self.parse(file_path)
        frontmatter.update(fields)
        self.write(file_path, frontmatter, body)
        self.logger.info(f"Updated {len(fields)} fields in {file_path.name}")

    def delete_field(self, file_path: Path, field: str):
        """Delete frontmatter field"""
        frontmatter, body = self.parse(file_path)
        if field in frontmatter:
            del frontmatter[field]
            self.write(file_path, frontmatter, body)
            self.logger.info(f"Deleted field '{field}' from {file_path.name}")

    def ensure_field(self, file_path: Path, field: str, default_value: any):
        """Ensure field exists with default value if missing"""
        frontmatter, body = self.parse(file_path)
        if field not in frontmatter:
            frontmatter[field] = default_value
            self.write(file_path, frontmatter, body)
            self.logger.info(f"Added default field '{field}' to {file_path.name}")

    def validate_frontmatter(self, file_path: Path, required_fields: list) -> Tuple[bool, list]:
        """
        Validate frontmatter has required fields

        Returns:
            (is_valid, missing_fields)
        """
        frontmatter, _ = self.parse(file_path)

        missing = [field for field in required_fields if field not in frontmatter]

        is_valid = len(missing) == 0

        if not is_valid:
            self.logger.warning(f"{file_path.name} missing fields: {missing}")

        return is_valid, missing

    def bulk_update_field(self, pattern: str, field: str, value: any):
        """Bulk update field across all matching files"""
        if not self.vault_path:
            self.logger.error("vault_path not set for bulk operations")
            return

        count = 0

        for md_file in self.vault_path.rglob(pattern):
            try:
                self.set_field(md_file, field, value)
                count += 1
            except Exception as e:
                self.logger.error(f"Failed to update {md_file.name}: {e}")

        self.logger.info(f"Bulk updated {count} files")

    def bulk_ensure_field(self, pattern: str, field: str, default_value: any):
        """Bulk ensure field exists across all matching files"""
        if not self.vault_path:
            self.logger.error("vault_path not set for bulk operations")
            return

        count = 0

        for md_file in self.vault_path.rglob(pattern):
            try:
                self.ensure_field(md_file, field, default_value)
                count += 1
            except Exception as e:
                self.logger.error(f"Failed to process {md_file.name}: {e}")

        self.logger.info(f"Bulk ensured field in {count} files")

    def extract_to_dict(self, file_path: Path, fields: list) -> Dict:
        """Extract specific fields to dict"""
        frontmatter, _ = self.parse(file_path)

        extracted = {}
        for field in fields:
            if field in frontmatter:
                extracted[field] = frontmatter[field]

        return extracted

    def merge_frontmatter(self, file_path: Path, new_data: Dict, overwrite: bool = False):
        """
        Merge new data into frontmatter

        Args:
            overwrite: If True, overwrite existing values. If False, only add new fields.
        """
        frontmatter, body = self.parse(file_path)

        if overwrite:
            frontmatter.update(new_data)
        else:
            for key, value in new_data.items():
                if key not in frontmatter:
                    frontmatter[key] = value

        self.write(file_path, frontmatter, body)

    def validate_yaml_syntax(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate YAML syntax without parsing entire file

        Returns:
            (is_valid, error_message)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if not fm_match:
                return False, "No frontmatter found"

            frontmatter_str = fm_match.group(1)

            try:
                yaml.safe_load(frontmatter_str)
                return True, None
            except yaml.YAMLError as e:
                return False, str(e)

        except Exception as e:
            return False, str(e)

    def generate_frontmatter_report(self) -> Dict:
        """Generate report on frontmatter usage across vault"""
        if not self.vault_path:
            self.logger.error("vault_path not set")
            return {}

        report = {
            "total_files": 0,
            "files_with_frontmatter": 0,
            "files_without_frontmatter": 0,
            "invalid_yaml": 0,
            "field_usage": {},
            "missing_required": []
        }

        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in [".obsidian"]):
                continue

            report["total_files"] += 1

            # Check YAML syntax
            is_valid, error = self.validate_yaml_syntax(md_file)

            if not is_valid:
                if "No frontmatter found" in error:
                    report["files_without_frontmatter"] += 1
                else:
                    report["invalid_yaml"] += 1
                    self.logger.warning(f"Invalid YAML in {md_file.name}: {error}")
                continue

            report["files_with_frontmatter"] += 1

            # Parse frontmatter
            frontmatter, _ = self.parse(md_file)

            # Track field usage
            for field in frontmatter.keys():
                if field not in report["field_usage"]:
                    report["field_usage"][field] = 0
                report["field_usage"][field] += 1

        return report


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Frontmatter parser utility")
    parser.add_argument("--file", type=str,
                       help="File to parse")
    parser.add_argument("--vault", type=str, default="C:/obsidian-memory-vault",
                       help="Vault path for bulk operations")
    parser.add_argument("--get", type=str,
                       help="Get field value")
    parser.add_argument("--set", nargs=2, metavar=('FIELD', 'VALUE'),
                       help="Set field value")
    parser.add_argument("--validate", action="store_true",
                       help="Validate YAML syntax")
    parser.add_argument("--report", action="store_true",
                       help="Generate frontmatter usage report")

    args = parser.parse_args()

    parser_obj = FrontmatterParser(Path(args.vault))

    if args.file:
        file_path = Path(args.file)

        if args.get:
            value = parser_obj.get_field(file_path, args.get)
            print(f"\n[OK] Field: {args.get}")
            print(f"   Value: {value}")

        elif args.set:
            field, value = args.set
            parser_obj.set_field(file_path, field, value)
            print(f"\n[OK] Field Set: {field} = {value}")

        elif args.validate:
            is_valid, error = parser_obj.validate_yaml_syntax(file_path)
            print(f"\n[{'OK' if is_valid else 'ERROR'}] YAML Validation")
            if not is_valid:
                print(f"   Error: {error}")

        else:
            # Default: show all frontmatter
            frontmatter, _ = parser_obj.parse(file_path)
            print(f"\n[OK] Frontmatter:")
            for key, value in frontmatter.items():
                print(f"   {key}: {value}")

    elif args.report:
        report = parser_obj.generate_frontmatter_report()
        print(f"\n[OK] Frontmatter Report")
        print(f"\n   Total files: {report['total_files']}")
        print(f"   With frontmatter: {report['files_with_frontmatter']}")
        print(f"   Without frontmatter: {report['files_without_frontmatter']}")
        print(f"   Invalid YAML: {report['invalid_yaml']}")
        print(f"\n   Top 10 fields:")
        sorted_fields = sorted(report['field_usage'].items(), key=lambda x: x[1], reverse=True)
        for field, count in sorted_fields[:10]:
            print(f"      {field}: {count} files")

    else:
        print(f"\n[INFO] Frontmatter Parser")
        print(f"   Use --file with --get, --set, or --validate")
        print(f"   Use --report for vault-wide analysis")

    print()


if __name__ == "__main__":
    main()
