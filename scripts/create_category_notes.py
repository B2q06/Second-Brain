#!/usr/bin/env python3
"""
Create Category Notes - Generate parent category notes from taxonomy

This script creates intermediate parent category notes (Technology.md, Programming.md, etc.)
that serve as hub nodes in the knowledge graph, showing hierarchical relationships.
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set

try:
    from scripts.tag_path_resolver import TagPathResolver
except ImportError:
    from tag_path_resolver import TagPathResolver


class CategoryNoteGenerator:
    """Generate parent category notes from taxonomy structure"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.resolver = TagPathResolver(self.vault_path)
        self.taxonomy = self.resolver.taxonomy

    def extract_categories(self) -> Dict[Tuple[str, str], Dict]:
        """
        Extract all intermediate categories from taxonomy paths

        Returns:
            Dict mapping (name, path) tuples to category data
        """
        categories = {}

        for tag, tax_data in self.taxonomy.items():
            path = tax_data.get("path", "")
            if not path:
                continue

            # Split path into parts
            parts = [p.strip() for p in path.split(">")]

            # Extract each intermediate category
            # "Technology > Programming > Languages > Python"
            # Creates: (Technology, "Technology"), (Programming, "Technology > Programming"), etc.
            for i in range(1, len(parts)):
                cat_name = parts[i-1]
                cat_path = " > ".join(parts[:i])
                cat_key = (cat_name, cat_path)

                if cat_key not in categories:
                    categories[cat_key] = {
                        "name": cat_name,
                        "path": cat_path,
                        "root": parts[0],
                        "depth": i,
                        "children_tags": [],
                        "children_categories": set()
                    }

        return categories

    def find_children_tags(self, category_path: str) -> List[Dict]:
        """
        Find all tags that are direct children of a category

        Args:
            category_path: Full path of category (e.g., "Technology > Programming")

        Returns:
            List of dicts with tag info
        """
        children = []

        for tag, tax_data in self.taxonomy.items():
            tag_path = tax_data.get("path", "")
            if not tag_path:
                continue

            # Parse tag path
            parts = [p.strip() for p in tag_path.split(">")]

            # Build parent path (everything except last element)
            if len(parts) > 1:
                tag_parent_path = " > ".join(parts[:-1])

                # Check if this tag is a direct child
                if tag_parent_path == category_path:
                    children.append({
                        "tag": tag,
                        "canonical": tax_data.get("canonical", tag.replace('-', ' ').title()),
                        "description": tax_data.get("description", ""),
                        "path": tag_path
                    })

        return sorted(children, key=lambda x: x["canonical"])

    def find_children_categories(self, category_path: str, all_categories: Dict) -> List[str]:
        """
        Find all categories that are direct children of a category

        Args:
            category_path: Full path of parent category
            all_categories: All extracted categories

        Returns:
            List of child category names
        """
        children = []

        for (cat_name, cat_path), cat_data in all_categories.items():
            # Check if this is a direct child
            parts = [p.strip() for p in cat_path.split(">")]

            if len(parts) > 1:
                cat_parent_path = " > ".join(parts[:-1])

                if cat_parent_path == category_path:
                    children.append(cat_name)

        return sorted(children)

    def create_category_note_content(
        self,
        category_data: Dict,
        children_tags: List[Dict],
        children_categories: List[str]
    ) -> str:
        """
        Generate category note content

        Args:
            category_data: Category metadata
            children_tags: List of child tag dicts
            children_categories: List of child category names

        Returns:
            Markdown content for category note
        """
        name = category_data["name"]
        path = category_data["path"]
        root = category_data["root"]
        depth = category_data["depth"]

        # Build frontmatter
        # Create tag identifier for category (lowercase, hyphenated)
        category_tag = name.lower().replace(' ', '-')

        frontmatter = {
            "type": "category-note",
            "tags": [category_tag],  # 🔥 Add hashtag to make category visible in graph
            "canonical": name,
            "root": root,
            "path": path,
            "depth": depth,
            "created": datetime.now().strftime("%Y-%m-%d"),
            "children_count": len(children_tags) + len(children_categories)
        }

        # 🔥 Build hierarchy section (parent wikilinks)
        hierarchy_section = ""
        parts = [p.strip() for p in path.split('>')]

        if len(parts) > 1:
            # Not a root category - has parent
            parent_name = parts[-2]  # Immediate parent
            hierarchy_section = f"""## Hierarchy
**Parent**: [[{parent_name}]]
**Path**: {path}

"""

        # Build children categories section
        categories_section = ""
        if children_categories:
            categories_section = "## Child Categories\n\n"
            for child_cat in children_categories:
                categories_section += f"- [[{child_cat}]]\n"
            categories_section += "\n"

        # Build children tags section
        tags_section = ""
        if children_tags:
            tags_section = "## Child Tags\n\n"
            for child in children_tags:
                canonical = child["canonical"]
                desc = child["description"]
                desc_text = f" - {desc}" if desc else ""
                tags_section += f"- [[{canonical}]]{desc_text}\n"
            tags_section += "\n"

        # Build full content
        content = f"""---
{yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True).strip()}
---

# {name}

{hierarchy_section}{categories_section}{tags_section}## Overview

This is a category page that organizes related tags and sub-categories in the knowledge graph.

Use Obsidian's graph view or backlinks panel to explore connections.
"""

        return content

    def determine_file_location(self, category_path: str, category_name: str) -> Path:
        """
        Determine where category note file should be saved

        Args:
            category_path: Full category path (e.g., "Technology > Programming")
            category_name: Category name (e.g., "Programming")

        Returns:
            Full file path for category note
        """
        parts = [p.strip() for p in category_path.split(">")]

        if len(parts) == 1:
            # Root category: Technology.md in Technology/
            folder = self.vault_path / parts[0]
            filename = f"{parts[0]}.md"
        else:
            # Nested category: Programming.md in Technology/
            folder = self.vault_path / parts[0]
            filename = f"{parts[-1]}.md"

        return folder / filename

    def generate_all(self, dry_run: bool = False, force: bool = False) -> Tuple[int, int]:
        """
        Generate all missing category notes

        Args:
            dry_run: If True, only show what would be created
            force: If True, overwrite existing files

        Returns:
            (created_count, skipped_count)
        """
        print(f"\n{'='*60}")
        print(f"Category Note Generation")
        if dry_run:
            print(f"Mode: DRY RUN")
        if force:
            print(f"Force: Overwriting existing files")
        print(f"{'='*60}\n")

        # Extract all categories
        categories = self.extract_categories()
        print(f"[i] Found {len(categories)} unique categories in taxonomy\n")

        created = 0
        skipped = 0

        for cat_key, cat_data in sorted(categories.items(), key=lambda x: x[1]["depth"]):
            cat_name = cat_data["name"]
            cat_path = cat_data["path"]

            # Determine file location
            file_path = self.determine_file_location(cat_path, cat_name)

            # Check if already exists
            if file_path.exists() and not force:
                print(f"[SKIP] {cat_name} - already exists at {file_path.relative_to(self.vault_path)}")
                skipped += 1
                continue

            # Find children
            children_tags = self.find_children_tags(cat_path)
            children_cats = self.find_children_categories(cat_path, categories)

            # Generate content
            content = self.create_category_note_content(
                cat_data,
                children_tags,
                children_cats
            )

            if dry_run:
                print(f"[DRY RUN] Would create: {file_path.relative_to(self.vault_path)}")
                print(f"    Children: {len(children_tags)} tags, {len(children_cats)} categories")
            else:
                # Create folder if needed
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # Write file
                file_path.write_text(content, encoding='utf-8')

                print(f"[CREATE] {file_path.relative_to(self.vault_path)}")
                print(f"    Children: {len(children_tags)} tags, {len(children_cats)} categories")

                created += 1

        print(f"\n{'='*60}")
        print(f"[+] Complete")
        print(f"    Created: {created}")
        print(f"    Skipped: {skipped}")
        print(f"{'='*60}\n")

        return created, skipped


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Generate parent category notes from taxonomy")
    parser.add_argument("--vault", type=str, required=True, help="Path to Obsidian vault")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without making changes")
    parser.add_argument("--force", action="store_true", help="Overwrite existing category notes")

    args = parser.parse_args()

    vault_path = Path(args.vault)
    if not vault_path.exists():
        print(f"[X] Vault not found: {vault_path}")
        sys.exit(1)

    generator = CategoryNoteGenerator(str(vault_path))
    created, skipped = generator.generate_all(dry_run=args.dry_run, force=args.force)

    if args.dry_run:
        print(f"[i] Dry run complete. {created + skipped} category notes would be affected.")
    else:
        print(f"[✓] Generated {created} category notes")


if __name__ == "__main__":
    main()
