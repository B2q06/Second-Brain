#!/usr/bin/env python3
"""
Tag Path Resolver
Resolves taxonomy paths and determines optimal file locations for tag notes
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from scripts.logger_setup import get_logger
except ImportError:
    try:
        from logger_setup import get_logger
    except ImportError:
        # Fallback if logger not available
        import logging
        def get_logger(name, path):
            return logging.getLogger(name)


class TagPathResolver:
    """Resolve tag taxonomy paths and file locations"""

    def __init__(self, vault_path: Path, taxonomy_path: Path = None):
        self.vault_path = Path(vault_path)
        self.logger = get_logger(__name__, str(vault_path))

        if taxonomy_path is None:
            taxonomy_path = self.vault_path / "_system" / "tag-taxonomy.md"

        self.taxonomy_path = Path(taxonomy_path)
        self.taxonomy = self._load_taxonomy()

    def _load_taxonomy(self) -> Dict:
        """Load taxonomy from tag-taxonomy.md"""
        self.logger.info(f"Loading taxonomy from {self.taxonomy_path}")

        if not self.taxonomy_path.exists():
            self.logger.error(f"Taxonomy file not found: {self.taxonomy_path}")
            return {}

        with open(self.taxonomy_path, 'r', encoding='utf-8') as f:
            content = f.read()

        taxonomy = {}
        yaml_blocks = re.findall(r'```yaml\n(.*?)\n```', content, re.DOTALL)

        for block in yaml_blocks:
            try:
                data = yaml.safe_load(block)
                if isinstance(data, dict):
                    taxonomy.update(data)
            except yaml.YAMLError as e:
                self.logger.warning(f"Failed to parse YAML block: {e}")

        self.logger.info(f"Loaded {len(taxonomy)} tags from taxonomy")
        return taxonomy

    def resolve_path(self, tag: str) -> Optional[str]:
        """Resolve full taxonomy path for a tag"""
        if tag not in self.taxonomy:
            self.logger.warning(f"Tag '{tag}' not in taxonomy")
            return None

        return self.taxonomy[tag].get("path", None)

    def resolve_file_location(self, tag: str) -> Optional[Path]:
        """Resolve optimal file system location for a tag note"""
        if tag not in self.taxonomy:
            return None

        tax_entry = self.taxonomy[tag]
        path = tax_entry.get("path", "")
        root = tax_entry.get("root", "Unknown")

        if not path:
            return None

        # Parse path into components
        # Example: "Technology > Programming > Languages > Python > Frameworks > Web > FastAPI"
        parts = [p.strip() for p in path.split(">")]

        # Determine folder depth based on taxonomy structure
        # Root only: vault_path / root /
        # 2-3 levels: vault_path / root /
        # 4+ levels: vault_path / root / category /

        if len(parts) <= 2:
            # Root level: Technology/
            folder = self.vault_path / parts[0]
        elif len(parts) <= 3:
            # One level deep: Technology/
            folder = self.vault_path / parts[0]
        else:
            # Two levels deep: Technology/Programming/
            folder = self.vault_path / parts[0] / parts[1]

        return folder

    def resolve_parent_tags(self, tag: str) -> List[str]:
        """Resolve parent tags for a tag"""
        if tag not in self.taxonomy:
            return []

        return self.taxonomy[tag].get("parent_tags", [])

    def resolve_children_tags(self, tag: str) -> List[str]:
        """Find all children of a tag"""
        children = []

        for other_tag, tax_entry in self.taxonomy.items():
            parent_tags = tax_entry.get("parent_tags", [])
            if tag in parent_tags:
                children.append(other_tag)

        return children

    def resolve_root(self, tag: str) -> Optional[str]:
        """Resolve root area for a tag"""
        if tag not in self.taxonomy:
            return None

        return self.taxonomy[tag].get("root", None)

    def resolve_depth(self, tag: str) -> Optional[int]:
        """Resolve taxonomy depth for a tag"""
        if tag not in self.taxonomy:
            return None

        return self.taxonomy[tag].get("depth", None)

    def find_tag_by_alias(self, alias: str) -> Optional[str]:
        """Find canonical tag name by alias"""
        for tag, tax_entry in self.taxonomy.items():
            aliases = tax_entry.get("aliases", [])
            if alias in aliases:
                return tag

        return None

    def suggest_tags_by_path(self, partial_path: str) -> List[str]:
        """Suggest tags matching a partial path"""
        suggestions = []

        for tag, tax_entry in self.taxonomy.items():
            path = tax_entry.get("path", "")
            if partial_path.lower() in path.lower():
                suggestions.append({
                    "tag": tag,
                    "path": path,
                    "root": tax_entry.get("root", "Unknown")
                })

        return suggestions

    def get_tags_by_root(self, root: str) -> List[str]:
        """Get all tags in a specific root area"""
        tags = []

        for tag, tax_entry in self.taxonomy.items():
            if tax_entry.get("root", "") == root:
                tags.append(tag)

        return tags

    def get_tags_by_depth(self, depth: int) -> List[str]:
        """Get all tags at a specific depth"""
        tags = []

        for tag, tax_entry in self.taxonomy.items():
            if tax_entry.get("depth", 0) == depth:
                tags.append(tag)

        return tags

    def validate_tag_hierarchy(self) -> List[Dict]:
        """Validate taxonomy hierarchy for issues"""
        issues = []

        for tag, tax_entry in self.taxonomy.items():
            # Check parent tags exist
            parent_tags = tax_entry.get("parent_tags", [])
            for parent in parent_tags:
                if parent not in self.taxonomy:
                    issues.append({
                        "tag": tag,
                        "issue": "missing_parent",
                        "details": f"Parent '{parent}' not in taxonomy"
                    })

            # Check path consistency
            path = tax_entry.get("path", "")
            root = tax_entry.get("root", "")
            if path and not path.startswith(root):
                issues.append({
                    "tag": tag,
                    "issue": "path_mismatch",
                    "details": f"Path doesn't start with root '{root}'"
                })

            # Check depth consistency
            depth = tax_entry.get("depth", 0)
            if path:
                actual_depth = len([p for p in path.split(">")]) - 1
                if actual_depth != depth:
                    issues.append({
                        "tag": tag,
                        "issue": "depth_mismatch",
                        "details": f"Stated depth {depth} != actual depth {actual_depth}"
                    })

        return issues

    def generate_path_report(self) -> str:
        """Generate path resolution report"""
        report = "# Tag Path Resolution Report\n\n"
        report += f"**Total tags**: {len(self.taxonomy)}\n\n"

        # Group by root
        by_root = {}
        for tag, tax_entry in self.taxonomy.items():
            root = tax_entry.get("root", "Unknown")
            if root not in by_root:
                by_root[root] = []
            by_root[root].append(tag)

        report += "## Tags by Root\n\n"
        for root in sorted(by_root.keys()):
            tags = by_root[root]
            report += f"### {root} ({len(tags)} tags)\n\n"

            for tag in sorted(tags):
                path = self.resolve_path(tag)
                depth = self.resolve_depth(tag)
                file_loc = self.resolve_file_location(tag)

                report += f"- **{tag}**\n"
                report += f"  - Path: `{path}`\n"
                report += f"  - Depth: {depth}\n"
                if file_loc:
                    report += f"  - File location: `{file_loc.relative_to(self.vault_path)}/`\n"
                report += "\n"

        # Validation issues
        issues = self.validate_tag_hierarchy()
        report += f"## Validation Issues\n\n"

        if issues:
            report += f"Found {len(issues)} issue(s):\n\n"
            for issue in issues:
                report += f"- **{issue['tag']}**: {issue['issue']} - {issue['details']}\n"
        else:
            report += "No issues found ✅\n"

        return report


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Tag path resolver")
    parser.add_argument("--vault", type=str, default="C:/obsidian-memory-vault",
                       help="Path to vault")
    parser.add_argument("--tag", type=str,
                       help="Resolve path for specific tag")
    parser.add_argument("--root", type=str,
                       help="List all tags in root area")
    parser.add_argument("--validate", action="store_true",
                       help="Validate taxonomy hierarchy")
    parser.add_argument("--report", action="store_true",
                       help="Generate path resolution report")

    args = parser.parse_args()

    resolver = TagPathResolver(Path(args.vault))

    if args.tag:
        path = resolver.resolve_path(args.tag)
        file_loc = resolver.resolve_file_location(args.tag)
        parents = resolver.resolve_parent_tags(args.tag)
        children = resolver.resolve_children_tags(args.tag)

        print(f"\n[OK] Tag Resolution: {args.tag}")
        print(f"\n   Path: {path}")
        print(f"   File location: {file_loc.relative_to(resolver.vault_path) if file_loc else 'N/A'}")
        print(f"   Parents: {', '.join(parents) if parents else 'None'}")
        print(f"   Children: {', '.join(children) if children else 'None'}")

    elif args.root:
        tags = resolver.get_tags_by_root(args.root)
        print(f"\n[OK] Tags in {args.root} ({len(tags)} tags)")
        for tag in sorted(tags):
            print(f"   - {tag}")

    elif args.validate:
        issues = resolver.validate_tag_hierarchy()
        print(f"\n[OK] Taxonomy Validation")
        if issues:
            print(f"\n   Found {len(issues)} issue(s):")
            for issue in issues:
                print(f"\n   Tag: {issue['tag']}")
                print(f"   Issue: {issue['issue']}")
                print(f"   Details: {issue['details']}")
        else:
            print(f"\n   No issues found")

    elif args.report:
        report = resolver.generate_path_report()
        report_file = Path(args.vault) / "_system" / "tag-path-report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n[OK] Path Report Generated")
        print(f"   File: {report_file}")

    else:
        print(f"\n[INFO] Tag Path Resolver")
        print(f"   Use --tag, --root, --validate, or --report")

    print()


if __name__ == "__main__":
    main()
