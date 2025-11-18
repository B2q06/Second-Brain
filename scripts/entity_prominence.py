#!/usr/bin/env python3
"""
Entity Prominence Calculator
Calculates prominence scores and rankings for entities based on multiple metrics
"""

import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict
from logger_setup import get_logger, TimedOperation


class EntityProminenceCalculator:
    """Calculate entity prominence scores"""

    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path)
        self.logger = get_logger(__name__, str(vault_path))

    def calculate_prominence(self, entity: str) -> Dict:
        """Calculate comprehensive prominence metrics for an entity"""
        self.logger.info(f"Calculating prominence for: {entity}")

        # Find tag note
        tag_file = self._find_tag_note(entity)
        if not tag_file:
            self.logger.warning(f"Tag note not found for: {entity}")
            return {}

        with open(tag_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract metrics from frontmatter
        conv_match = re.search(r'total_conversations:\s*(\d+)', content)
        time_match = re.search(r'total_time_minutes:\s*(\d+(?:\.\d+)?)', content)
        depth_match = re.search(r'depth:\s*(\d+)', content)
        root_match = re.search(r'root:\s*(\w+)', content)

        conversations = int(conv_match.group(1)) if conv_match else 0
        time_minutes = float(time_match.group(1)) if time_match else 0
        depth = int(depth_match.group(1)) if depth_match else 1
        root = root_match.group(1) if root_match else "Unknown"

        # Calculate prominence score (weighted)
        # - 10 points per conversation
        # - 5 points per hour
        # - Depth bonus: (8 - depth) * 2 (shallower = more fundamental)
        conv_score = conversations * 10
        time_score = (time_minutes / 60) * 5
        depth_score = (8 - min(depth, 8)) * 2

        total_score = conv_score + time_score + depth_score

        # Calculate recency score (recent activity = more prominence)
        recency_score = self._calculate_recency_score(entity)

        # Calculate connection score (more connections = more central)
        connection_score = self._calculate_connection_score(entity)

        prominence = {
            "entity": entity,
            "total_score": round(total_score + recency_score + connection_score, 2),
            "breakdown": {
                "conversations": conversations,
                "time_hours": round(time_minutes / 60, 2),
                "depth": depth,
                "root": root,
                "conversation_score": round(conv_score, 2),
                "time_score": round(time_score, 2),
                "depth_score": round(depth_score, 2),
                "recency_score": round(recency_score, 2),
                "connection_score": round(connection_score, 2)
            },
            "rank_category": self._categorize_prominence(total_score + recency_score + connection_score)
        }

        return prominence

    def calculate_all_prominence(self) -> List[Dict]:
        """Calculate prominence for all entities"""
        with TimedOperation(self.logger, "Calculating prominence for all entities"):
            entities = []

            # Find all tag notes
            for md_file in self.vault_path.rglob("*.md"):
                if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                    continue

                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read(500)
                        if 'type: tag-note' not in content:
                            continue

                    tag_match = re.search(r'^tag:\s*(.+)$', content, re.MULTILINE)
                    if tag_match:
                        entity = tag_match.group(1).strip()
                        prominence = self.calculate_prominence(entity)
                        if prominence:
                            entities.append(prominence)

                except Exception as e:
                    self.logger.warning(f"Failed to process {md_file.name}: {e}")

            # Sort by total score
            entities.sort(key=lambda x: x["total_score"], reverse=True)

            self.logger.info(f"Calculated prominence for {len(entities)} entities")
            return entities

    def get_top_entities(self, limit: int = 20, root: str = None) -> List[Dict]:
        """Get top N entities by prominence"""
        all_entities = self.calculate_all_prominence()

        # Filter by root if specified
        if root:
            all_entities = [e for e in all_entities if e["breakdown"]["root"] == root]

        return all_entities[:limit]

    def get_rising_entities(self, days: int = 30, limit: int = 10) -> List[Dict]:
        """Get entities with recent activity (rising stars)"""
        self.logger.info(f"Finding rising entities in last {days} days")

        entities_with_recency = []

        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                    if 'type: tag-note' not in content:
                        continue

                tag_match = re.search(r'^tag:\s*(.+)$', content, re.MULTILINE)
                if not tag_match:
                    continue

                entity = tag_match.group(1).strip()

                # Check recent activity
                recent_mentions = self._get_recent_mentions(entity, days)

                if recent_mentions > 0:
                    prominence = self.calculate_prominence(entity)
                    if prominence:
                        prominence["recent_mentions"] = recent_mentions
                        entities_with_recency.append(prominence)

            except:
                pass

        # Sort by recent mentions then total score
        entities_with_recency.sort(
            key=lambda x: (x["recent_mentions"], x["total_score"]),
            reverse=True
        )

        return entities_with_recency[:limit]

    def get_foundational_entities(self, limit: int = 10) -> List[Dict]:
        """Get most fundamental entities (shallow depth + high prominence)"""
        all_entities = self.calculate_all_prominence()

        # Filter to depth 1-2 only
        foundational = [e for e in all_entities if e["breakdown"]["depth"] <= 2]

        return foundational[:limit]

    def _find_tag_note(self, entity: str) -> Path:
        """Find tag note file for entity"""
        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                    if 'type: tag-note' not in content:
                        continue

                    tag_match = re.search(r'^tag:\s*(.+)$', content, re.MULTILINE)
                    if tag_match and tag_match.group(1).strip() == entity:
                        return md_file
            except:
                pass

        return None

    def _calculate_recency_score(self, entity: str) -> float:
        """Calculate recency score (recent activity = higher score)"""
        recent_mentions = self._get_recent_mentions(entity, days=30)

        # 2 points per mention in last 30 days
        return recent_mentions * 2.0

    def _get_recent_mentions(self, entity: str, days: int) -> int:
        """Count mentions in recent conversations"""
        cutoff = datetime.now() - timedelta(days=days)
        count = 0

        processed_dir = self.vault_path / "00-Inbox" / "processed"
        if not processed_dir.exists():
            return 0

        for conv_file in processed_dir.glob("*.md"):
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    content = f.read(1000)

                # Check date
                date_match = re.search(r'created:\s*(\d{4}-\d{2}-\d{2})', content)
                if not date_match:
                    continue

                conv_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                if conv_date < cutoff:
                    continue

                # Check if entity mentioned
                entities_match = re.search(r'entities:\s*\[(.*?)\]', content, re.DOTALL)
                if entities_match:
                    entities = [e.strip().strip('"').strip("'") for e in entities_match.group(1).split(',')]
                    if entity in entities:
                        count += 1

            except:
                pass

        return count

    def _calculate_connection_score(self, entity: str) -> float:
        """Calculate connection score (how connected to other entities)"""
        # Count parent and child connections
        tag_file = self._find_tag_note(entity)
        if not tag_file:
            return 0

        try:
            with open(tag_file, 'r', encoding='utf-8') as f:
                content = f.read(1000)

            parent_match = re.search(r'parent_tags:\s*\[(.*?)\]', content)
            parent_count = 0
            if parent_match:
                parents = [p.strip() for p in parent_match.group(1).split(',') if p.strip()]
                parent_count = len(parents)

            # Count children (entities that list this as parent)
            child_count = 0
            for md_file in self.vault_path.rglob("*.md"):
                if md_file == tag_file:
                    continue

                if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                    continue

                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        child_content = f.read(500)
                        if 'type: tag-note' not in child_content:
                            continue

                        child_parent_match = re.search(r'parent_tags:\s*\[(.*?)\]', child_content)
                        if child_parent_match:
                            child_parents = [p.strip() for p in child_parent_match.group(1).split(',')]
                            if entity in child_parents:
                                child_count += 1
                except:
                    pass

            # Score: 1 point per parent, 3 points per child (being a parent is more central)
            return (parent_count * 1.0) + (child_count * 3.0)

        except:
            return 0

    def _categorize_prominence(self, score: float) -> str:
        """Categorize prominence level"""
        if score >= 100:
            return "Core"
        elif score >= 50:
            return "Major"
        elif score >= 20:
            return "Notable"
        elif score >= 5:
            return "Emerging"
        else:
            return "New"

    def generate_prominence_report(self, output_file: Path = None) -> str:
        """Generate prominence report"""
        if output_file is None:
            output_file = self.vault_path / "_system" / "entity-prominence-report.md"

        with TimedOperation(self.logger, "Generating prominence report"):
            all_entities = self.calculate_all_prominence()

            report = "# Entity Prominence Report\n\n"
            report += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            report += f"**Total entities**: {len(all_entities)}\n\n"
            report += "---\n\n"

            # Top 20
            report += "## Top 20 Entities\n\n"
            report += "| Rank | Entity | Score | Conversations | Time | Category |\n"
            report += "|------|--------|-------|--------------|------|----------|\n"

            for i, entity in enumerate(all_entities[:20], 1):
                report += f"| {i} | **{entity['entity']}** | {entity['total_score']} | "
                report += f"{entity['breakdown']['conversations']} | "
                report += f"{entity['breakdown']['time_hours']}h | "
                report += f"{entity['rank_category']} |\n"

            report += "\n"

            # Rising entities
            rising = self.get_rising_entities(days=30, limit=10)
            if rising:
                report += "## Rising Entities (Last 30 Days)\n\n"
                for entity in rising:
                    report += f"- **{entity['entity']}** - {entity['recent_mentions']} recent mentions, "
                    report += f"score: {entity['total_score']}\n"
                report += "\n"

            # Foundational entities
            foundational = self.get_foundational_entities(limit=10)
            if foundational:
                report += "## Foundational Entities\n\n"
                for entity in foundational:
                    report += f"- **{entity['entity']}** (depth {entity['breakdown']['depth']}) - "
                    report += f"score: {entity['total_score']}\n"
                report += "\n"

            # By category
            report += "## Entities by Category\n\n"
            by_category = defaultdict(list)
            for entity in all_entities:
                category = entity['rank_category']
                by_category[category].append(entity)

            for category in ["Core", "Major", "Notable", "Emerging", "New"]:
                entities = by_category[category]
                if entities:
                    report += f"### {category} ({len(entities)} entities)\n\n"
                    for entity in entities[:10]:  # Show top 10 per category
                        report += f"- **{entity['entity']}** - {entity['total_score']}\n"
                    report += "\n"

            # Save
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)

            self.logger.info(f"Prominence report generated: {output_file}")
            return report


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Calculate entity prominence")
    parser.add_argument("--vault", type=str, default="C:/obsidian-memory-vault",
                       help="Path to vault")
    parser.add_argument("--entity", type=str,
                       help="Calculate prominence for specific entity")
    parser.add_argument("--top", type=int, default=20,
                       help="Show top N entities")
    parser.add_argument("--rising", action="store_true",
                       help="Show rising entities")
    parser.add_argument("--report", action="store_true",
                       help="Generate full prominence report")

    args = parser.parse_args()

    calculator = EntityProminenceCalculator(Path(args.vault))

    if args.entity:
        prominence = calculator.calculate_prominence(args.entity)
        if prominence:
            print(f"\n[OK] Prominence: {args.entity}")
            print(f"\n   Total Score: {prominence['total_score']}")
            print(f"   Category: {prominence['rank_category']}")
            print(f"\n   Breakdown:")
            for key, value in prominence['breakdown'].items():
                print(f"      {key}: {value}")

    elif args.rising:
        rising = calculator.get_rising_entities(days=30, limit=10)
        print(f"\n[OK] Rising Entities (Last 30 Days)")
        for i, entity in enumerate(rising, 1):
            print(f"\n   {i}. {entity['entity']}")
            print(f"      Recent mentions: {entity['recent_mentions']}")
            print(f"      Score: {entity['total_score']}")

    elif args.report:
        report = calculator.generate_prominence_report()
        print(f"\n[OK] Prominence Report Generated")
        print(f"   File: {calculator.vault_path / '_system' / 'entity-prominence-report.md'}")

    else:
        # Default: show top N
        top = calculator.get_top_entities(limit=args.top)
        print(f"\n[OK] Top {args.top} Entities by Prominence")
        for i, entity in enumerate(top, 1):
            print(f"\n   {i}. {entity['entity']} - {entity['total_score']}")
            print(f"      Conversations: {entity['breakdown']['conversations']}, "
                  f"Time: {entity['breakdown']['time_hours']}h, "
                  f"Category: {entity['rank_category']}")

    print()


if __name__ == "__main__":
    main()
