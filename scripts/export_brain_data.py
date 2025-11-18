#!/usr/bin/env python3
"""
Brain Space Data Exporter
Exports metrics and statistics for dashboard visualization
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict
from logger_setup import get_logger, TimedOperation


class BrainDataExporter:
    """Export brain space metrics to JSON for visualization"""

    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path)
        self.logger = get_logger(__name__, str(vault_path))
        self.output_file = self.vault_path / "_system" / "brain-space-data.json"

    def export_all(self) -> Dict:
        """Export all metrics"""
        with TimedOperation(self.logger, "Exporting brain space data"):
            data = {
                "generated_at": datetime.now().isoformat(),
                "metrics": self.get_basic_metrics(),
                "time_distribution": self.get_time_distribution(),
                "growth_trends": self.get_growth_trends(),
                "hub_entities": self.get_hub_entities(),
                "recent_activity": self.get_recent_conversations(limit=10),
                "tag_statistics": self.get_tag_statistics()
            }

            # Write to file
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            self.logger.info(f"Exported data to {self.output_file}")
            return data

    def get_basic_metrics(self) -> Dict:
        """Get high-level metrics"""
        self.logger.info("Calculating basic metrics")

        processed_dir = self.vault_path / "00-Inbox" / "processed"
        conversation_count = len(list(processed_dir.glob("*.md"))) if processed_dir.exists() else 0

        # Count tag notes (any .md file with type: tag-note)
        tag_note_count = 0
        total_time_minutes = 0

        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # Read first 1000 chars
                    if 'type: tag-note' in content:
                        tag_note_count += 1

                        # Extract time from frontmatter
                        time_match = re.search(r'total_time_minutes:\s*(\d+(?:\.\d+)?)', content)
                        if time_match:
                            total_time_minutes += float(time_match.group(1))
            except:
                pass

        # Count areas (unique root categories from tag notes)
        areas = self._count_areas()

        return {
            "total_conversations": conversation_count,
            "total_tag_notes": tag_note_count,
            "total_areas": len(areas),
            "total_time_hours": round(total_time_minutes / 60, 1),
            "total_time_minutes": round(total_time_minutes, 1)
        }

    def _count_areas(self) -> set:
        """Count unique root areas"""
        areas = set()

        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                    if 'type: tag-note' in content:
                        root_match = re.search(r'root:\s*(\w+)', content)
                        if root_match:
                            areas.add(root_match.group(1))
            except:
                pass

        return areas

    def get_time_distribution(self) -> List[Dict]:
        """Get time spent per area/root"""
        self.logger.info("Calculating time distribution by area")

        area_time = defaultdict(float)

        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(1000)
                    if 'type: tag-note' not in content:
                        continue

                    # Extract root and time
                    root_match = re.search(r'root:\s*(\w+)', content)
                    time_match = re.search(r'total_time_minutes:\s*(\d+(?:\.\d+)?)', content)

                    if root_match and time_match:
                        root = root_match.group(1)
                        time_min = float(time_match.group(1))
                        area_time[root] += time_min
            except:
                pass

        # Convert to list format for treemap
        result = [
            {
                "name": area,
                "time_hours": round(minutes / 60, 1),
                "time_minutes": round(minutes, 1),
                "color": self._get_area_color(area)
            }
            for area, minutes in sorted(area_time.items(), key=lambda x: x[1], reverse=True)
        ]

        return result

    def _get_area_color(self, area: str) -> str:
        """Get color for area"""
        colors = {
            "Technology": "#1f77b4",
            "Language": "#2ca02c",
            "History": "#d62728",
            "Culture": "#9467bd",
            "Science": "#ff7f0e",
            "Art": "#8c564b",
        }
        return colors.get(area, "#7f7f7f")

    def get_growth_trends(self) -> List[Dict]:
        """Get entity/conversation growth over time"""
        self.logger.info("Calculating growth trends")

        # Group conversations by week
        weekly_counts = defaultdict(int)

        processed_dir = self.vault_path / "00-Inbox" / "processed"
        if not processed_dir.exists():
            return []

        for conv_file in processed_dir.glob("*.md"):
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)

                    # Extract created date
                    date_match = re.search(r'created:\s*(\d{4}-\d{2}-\d{2})', content)
                    if date_match:
                        date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                        week = date.strftime("%Y-W%W")
                        weekly_counts[week] += 1
            except:
                pass

        # Convert to list
        result = [
            {"week": week, "count": count}
            for week, count in sorted(weekly_counts.items())
        ]

        return result

    def get_hub_entities(self, limit: int = 10) -> List[Dict]:
        """Get most connected entities (by conversation count)"""
        self.logger.info("Finding hub entities")

        entity_stats = defaultdict(lambda: {"count": 0, "time": 0, "root": "Unknown"})

        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(1000)
                    if 'type: tag-note' not in content:
                        continue

                    # Extract tag name, root, conversations, time
                    tag_match = re.search(r'^tag:\s*(.+)$', content, re.MULTILINE)
                    root_match = re.search(r'root:\s*(\w+)', content)
                    conv_match = re.search(r'total_conversations:\s*(\d+)', content)
                    time_match = re.search(r'total_time_minutes:\s*(\d+(?:\.\d+)?)', content)

                    if tag_match:
                        tag = tag_match.group(1).strip()
                        entity_stats[tag]["count"] = int(conv_match.group(1)) if conv_match else 0
                        entity_stats[tag]["time"] = float(time_match.group(1)) if time_match else 0
                        entity_stats[tag]["root"] = root_match.group(1) if root_match else "Unknown"
            except:
                pass

        # Sort by connection count
        sorted_entities = sorted(
            entity_stats.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )[:limit]

        result = [
            {
                "name": tag,
                "connections": stats["count"],
                "time_hours": round(stats["time"] / 60, 1),
                "root": stats["root"]
            }
            for tag, stats in sorted_entities
        ]

        return result

    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get most recent conversations"""
        self.logger.info(f"Getting {limit} recent conversations")

        conversations = []
        processed_dir = self.vault_path / "00-Inbox" / "processed"

        if not processed_dir.exists():
            return []

        for conv_file in processed_dir.glob("*.md"):
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    content = f.read(1000)

                    title_match = re.search(r'^title:\s*"?(.+?)"?$', content, re.MULTILINE)
                    date_match = re.search(r'created:\s*(\d{4}-\d{2}-\d{2})', content)
                    tags_match = re.search(r'tags:\s*\[([^\]]+)\]', content)

                    if date_match:
                        conversations.append({
                            "title": title_match.group(1) if title_match else conv_file.stem,
                            "date": date_match.group(1),
                            "tags": [t.strip() for t in tags_match.group(1).split(',')] if tags_match else [],
                            "file": conv_file.name
                        })
            except:
                pass

        # Sort by date, most recent first
        conversations.sort(key=lambda x: x["date"], reverse=True)
        return conversations[:limit]

    def get_tag_statistics(self) -> Dict:
        """Get tag-level statistics"""
        self.logger.info("Calculating tag statistics")

        stats = {
            "by_root": defaultdict(int),
            "by_depth": defaultdict(int),
            "total_tags": 0
        }

        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                    if 'type: tag-note' not in content:
                        continue

                    stats["total_tags"] += 1

                    root_match = re.search(r'root:\s*(\w+)', content)
                    depth_match = re.search(r'depth:\s*(\d+)', content)

                    if root_match:
                        stats["by_root"][root_match.group(1)] += 1
                    if depth_match:
                        depth = depth_match.group(1)
                        stats["by_depth"][f"depth_{depth}"] += 1
            except:
                pass

        # Convert defaultdicts to regular dicts
        return {
            "by_root": dict(stats["by_root"]),
            "by_depth": dict(stats["by_depth"]),
            "total_tags": stats["total_tags"]
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Export brain space data for visualization")
    parser.add_argument("--vault", type=str, default="C:/obsidian-memory-vault",
                       help="Path to vault")
    parser.add_argument("--output", type=str, help="Override output file")

    args = parser.parse_args()

    exporter = BrainDataExporter(Path(args.vault))
    data = exporter.export_all()

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(data, f, indent=2)

    # Print summary
    metrics = data["metrics"]
    print(f"\n[OK] Brain Space Data Exported")
    print(f"   Conversations: {metrics['total_conversations']}")
    print(f"   Tag Notes: {metrics['total_tag_notes']}")
    print(f"   Areas: {metrics['total_areas']}")
    print(f"   Total Time: {metrics['total_time_hours']} hours")
    print(f"\n   Output: {exporter.output_file}\n")


if __name__ == "__main__":
    main()
