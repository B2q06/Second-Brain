#!/usr/bin/env python3
"""
Brain Space Calculator
Computes knowledge space metrics, growth analytics, and cognitive patterns
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict
from logger_setup import get_logger, TimedOperation


class BrainSpaceCalculator:
    """Calculate comprehensive brain space metrics"""

    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path)
        self.logger = get_logger(__name__, str(vault_path))

    def calculate_all_metrics(self) -> Dict:
        """Calculate all brain space metrics"""
        with TimedOperation(self.logger, "Calculating all brain space metrics"):
            metrics = {
                "knowledge_coverage": self.calculate_knowledge_coverage(),
                "learning_velocity": self.calculate_learning_velocity(),
                "cognitive_depth": self.calculate_cognitive_depth(),
                "connection_density": self.calculate_connection_density(),
                "domain_diversity": self.calculate_domain_diversity(),
                "temporal_patterns": self.calculate_temporal_patterns(),
                "entity_prominence": self.calculate_entity_prominence(),
                "growth_trajectory": self.calculate_growth_trajectory()
            }

            self.logger.info("All metrics calculated successfully")
            return metrics

    def calculate_knowledge_coverage(self) -> Dict:
        """Calculate knowledge coverage across domains"""
        self.logger.info("Calculating knowledge coverage")

        coverage = {
            "total_entities": 0,
            "total_conversations": 0,
            "total_time_hours": 0,
            "areas": {},
            "depth_distribution": defaultdict(int)
        }

        # Count conversations
        processed_dir = self.vault_path / "00-Inbox" / "processed"
        if processed_dir.exists():
            coverage["total_conversations"] = len(list(processed_dir.glob("*.md")))

        # Analyze tag notes
        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(1000)
                    if 'type: tag-note' not in content:
                        continue

                    coverage["total_entities"] += 1

                    # Extract root area
                    root_match = re.search(r'root:\s*(\w+)', content)
                    if root_match:
                        root = root_match.group(1)
                        if root not in coverage["areas"]:
                            coverage["areas"][root] = {"count": 0, "time": 0}
                        coverage["areas"][root]["count"] += 1

                    # Extract time
                    time_match = re.search(r'total_time_minutes:\s*(\d+(?:\.\d+)?)', content)
                    if time_match:
                        time_min = float(time_match.group(1))
                        coverage["total_time_hours"] += time_min / 60
                        if root_match:
                            coverage["areas"][root]["time"] += time_min / 60

                    # Extract depth
                    depth_match = re.search(r'depth:\s*(\d+)', content)
                    if depth_match:
                        depth = int(depth_match.group(1))
                        coverage["depth_distribution"][depth] += 1
            except:
                pass

        # Round time
        coverage["total_time_hours"] = round(coverage["total_time_hours"], 1)
        for area in coverage["areas"]:
            coverage["areas"][area]["time"] = round(coverage["areas"][area]["time"], 1)

        # Convert defaultdict to dict
        coverage["depth_distribution"] = dict(coverage["depth_distribution"])

        return coverage

    def calculate_learning_velocity(self) -> Dict:
        """Calculate learning velocity over time windows"""
        self.logger.info("Calculating learning velocity")

        velocity = {
            "entities_per_week": 0,
            "conversations_per_week": 0,
            "time_per_week_hours": 0,
            "acceleration": 0  # Change in velocity over time
        }

        # Collect timestamps
        entity_dates = []
        conversation_dates = []

        # Get entity creation dates
        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                    if 'type: tag-note' in content:
                        date_match = re.search(r'created:\s*(\d{4}-\d{2}-\d{2})', content)
                        if date_match:
                            entity_dates.append(datetime.strptime(date_match.group(1), "%Y-%m-%d"))
            except:
                pass

        # Get conversation dates
        processed_dir = self.vault_path / "00-Inbox" / "processed"
        if processed_dir.exists():
            for conv_file in processed_dir.glob("*.md"):
                try:
                    with open(conv_file, 'r', encoding='utf-8') as f:
                        content = f.read(500)
                        date_match = re.search(r'created:\s*(\d{4}-\d{2}-\d{2})', content)
                        if date_match:
                            conversation_dates.append(datetime.strptime(date_match.group(1), "%Y-%m-%d"))
                except:
                    pass

        # Calculate velocity if we have data
        if entity_dates or conversation_dates:
            all_dates = entity_dates + conversation_dates
            if all_dates:
                earliest = min(all_dates)
                latest = max(all_dates)
                weeks = max((latest - earliest).days / 7, 1)

                velocity["entities_per_week"] = round(len(entity_dates) / weeks, 2)
                velocity["conversations_per_week"] = round(len(conversation_dates) / weeks, 2)

                # Calculate acceleration (compare first half vs second half)
                if len(conversation_dates) >= 4:
                    sorted_dates = sorted(conversation_dates)
                    midpoint_idx = len(sorted_dates) // 2
                    midpoint_date = sorted_dates[midpoint_idx]

                    first_half_weeks = max((midpoint_date - earliest).days / 7, 1)
                    second_half_weeks = max((latest - midpoint_date).days / 7, 1)

                    first_half_velocity = midpoint_idx / first_half_weeks
                    second_half_velocity = (len(sorted_dates) - midpoint_idx) / second_half_weeks

                    velocity["acceleration"] = round(second_half_velocity - first_half_velocity, 2)

        return velocity

    def calculate_cognitive_depth(self) -> Dict:
        """Calculate cognitive depth metrics"""
        self.logger.info("Calculating cognitive depth")

        depth = {
            "average_depth": 0,
            "max_depth": 0,
            "depth_by_area": {},
            "shallow_vs_deep": {"shallow": 0, "medium": 0, "deep": 0}
        }

        depths = []
        area_depths = defaultdict(list)

        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                    if 'type: tag-note' not in content:
                        continue

                    depth_match = re.search(r'depth:\s*(\d+)', content)
                    root_match = re.search(r'root:\s*(\w+)', content)

                    if depth_match:
                        d = int(depth_match.group(1))
                        depths.append(d)

                        if root_match:
                            area_depths[root_match.group(1)].append(d)

                        # Categorize depth
                        if d <= 2:
                            depth["shallow_vs_deep"]["shallow"] += 1
                        elif d <= 4:
                            depth["shallow_vs_deep"]["medium"] += 1
                        else:
                            depth["shallow_vs_deep"]["deep"] += 1
            except:
                pass

        if depths:
            depth["average_depth"] = round(sum(depths) / len(depths), 2)
            depth["max_depth"] = max(depths)

        # Calculate average depth per area
        for area, area_depth_list in area_depths.items():
            depth["depth_by_area"][area] = round(sum(area_depth_list) / len(area_depth_list), 2)

        return depth

    def calculate_connection_density(self) -> Dict:
        """Calculate connection density (entities per conversation)"""
        self.logger.info("Calculating connection density")

        density = {
            "entities_per_conversation": 0,
            "cross_area_connections": 0,
            "hub_concentration": 0  # What % of entities are in top 10%
        }

        # Get total entities
        total_entities = 0
        entity_conversation_counts = []

        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                    if 'type: tag-note' not in content:
                        continue

                    total_entities += 1

                    conv_match = re.search(r'total_conversations:\s*(\d+)', content)
                    if conv_match:
                        entity_conversation_counts.append(int(conv_match.group(1)))
            except:
                pass

        # Calculate density
        processed_dir = self.vault_path / "00-Inbox" / "processed"
        total_conversations = 0
        if processed_dir.exists():
            total_conversations = len(list(processed_dir.glob("*.md")))

        if total_conversations > 0:
            density["entities_per_conversation"] = round(total_entities / total_conversations, 2)

        # Calculate hub concentration
        if entity_conversation_counts:
            entity_conversation_counts.sort(reverse=True)
            top_10_percent = max(1, len(entity_conversation_counts) // 10)
            top_entities_total = sum(entity_conversation_counts[:top_10_percent])
            all_entities_total = sum(entity_conversation_counts)

            if all_entities_total > 0:
                density["hub_concentration"] = round(top_entities_total / all_entities_total, 2)

        return density

    def calculate_domain_diversity(self) -> Dict:
        """Calculate domain diversity metrics"""
        self.logger.info("Calculating domain diversity")

        diversity = {
            "total_areas": 0,
            "gini_coefficient": 0,  # Measure of inequality in time distribution
            "area_balance": {}
        }

        area_time = defaultdict(float)

        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(1000)
                    if 'type: tag-note' not in content:
                        continue

                    root_match = re.search(r'root:\s*(\w+)', content)
                    time_match = re.search(r'total_time_minutes:\s*(\d+(?:\.\d+)?)', content)

                    if root_match and time_match:
                        area_time[root_match.group(1)] += float(time_match.group(1))
            except:
                pass

        diversity["total_areas"] = len(area_time)

        # Calculate Gini coefficient
        if area_time:
            times = sorted(area_time.values())
            n = len(times)
            total = sum(times)

            if total > 0:
                cumsum = 0
                gini_sum = 0
                for i, t in enumerate(times):
                    cumsum += t
                    gini_sum += (n - i) * t

                diversity["gini_coefficient"] = round(1 - (2 * gini_sum) / (n * total), 2)

            # Calculate balance (percentage of total time per area)
            for area, time_min in area_time.items():
                diversity["area_balance"][area] = round((time_min / total) * 100, 1)

        return diversity

    def calculate_temporal_patterns(self) -> Dict:
        """Calculate temporal patterns in learning"""
        self.logger.info("Calculating temporal patterns")

        patterns = {
            "active_days": 0,
            "longest_streak": 0,
            "current_streak": 0,
            "preferred_time_of_day": None,
            "weekly_distribution": defaultdict(int)
        }

        # Collect all conversation dates
        conversation_dates = []
        processed_dir = self.vault_path / "00-Inbox" / "processed"

        if processed_dir.exists():
            for conv_file in processed_dir.glob("*.md"):
                try:
                    with open(conv_file, 'r', encoding='utf-8') as f:
                        content = f.read(500)
                        date_match = re.search(r'created:\s*(\d{4}-\d{2}-\d{2})', content)
                        if date_match:
                            conversation_dates.append(datetime.strptime(date_match.group(1), "%Y-%m-%d"))
                except:
                    pass

        if conversation_dates:
            # Count active days
            unique_dates = set(d.date() for d in conversation_dates)
            patterns["active_days"] = len(unique_dates)

            # Calculate streaks
            sorted_dates = sorted(unique_dates)
            current_streak = 1
            longest_streak = 1

            for i in range(1, len(sorted_dates)):
                if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                    current_streak += 1
                    longest_streak = max(longest_streak, current_streak)
                else:
                    current_streak = 1

            patterns["longest_streak"] = longest_streak

            # Check current streak
            if sorted_dates:
                last_date = sorted_dates[-1]
                today = datetime.now().date()
                if (today - last_date).days <= 1:
                    patterns["current_streak"] = current_streak

            # Weekly distribution
            for date in conversation_dates:
                day = date.strftime("%A")
                patterns["weekly_distribution"][day] += 1

        # Convert defaultdict to dict
        patterns["weekly_distribution"] = dict(patterns["weekly_distribution"])

        return patterns

    def calculate_entity_prominence(self, limit: int = 20) -> List[Dict]:
        """Calculate entity prominence scores"""
        self.logger.info(f"Calculating entity prominence (top {limit})")

        entities = []

        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(1000)
                    if 'type: tag-note' not in content:
                        continue

                    tag_match = re.search(r'^tag:\s*(.+)$', content, re.MULTILINE)
                    conv_match = re.search(r'total_conversations:\s*(\d+)', content)
                    time_match = re.search(r'total_time_minutes:\s*(\d+(?:\.\d+)?)', content)
                    root_match = re.search(r'root:\s*(\w+)', content)
                    depth_match = re.search(r'depth:\s*(\d+)', content)

                    if tag_match:
                        conversations = int(conv_match.group(1)) if conv_match else 0
                        time_hours = float(time_match.group(1)) / 60 if time_match else 0

                        # Calculate prominence score (weighted combination)
                        prominence = (conversations * 10) + (time_hours * 5)

                        entities.append({
                            "name": tag_match.group(1).strip(),
                            "conversations": conversations,
                            "time_hours": round(time_hours, 1),
                            "prominence_score": round(prominence, 2),
                            "root": root_match.group(1) if root_match else "Unknown",
                            "depth": int(depth_match.group(1)) if depth_match else 0
                        })
            except:
                pass

        # Sort by prominence and return top N
        entities.sort(key=lambda x: x["prominence_score"], reverse=True)
        return entities[:limit]

    def calculate_growth_trajectory(self) -> Dict:
        """Calculate growth trajectory and projections"""
        self.logger.info("Calculating growth trajectory")

        trajectory = {
            "weekly_growth": [],
            "projected_entities_30d": 0,
            "projected_conversations_30d": 0,
            "growth_phase": "Unknown"  # Exponential, Linear, Plateau
        }

        # Collect weekly data
        weekly_entities = defaultdict(int)
        weekly_conversations = defaultdict(int)

        # Entities by week
        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                    if 'type: tag-note' in content:
                        date_match = re.search(r'created:\s*(\d{4}-\d{2}-\d{2})', content)
                        if date_match:
                            date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                            week = date.strftime("%Y-W%W")
                            weekly_entities[week] += 1
            except:
                pass

        # Conversations by week
        processed_dir = self.vault_path / "00-Inbox" / "processed"
        if processed_dir.exists():
            for conv_file in processed_dir.glob("*.md"):
                try:
                    with open(conv_file, 'r', encoding='utf-8') as f:
                        content = f.read(500)
                        date_match = re.search(r'created:\s*(\d{4}-\d{2}-\d{2})', content)
                        if date_match:
                            date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                            week = date.strftime("%Y-W%W")
                            weekly_conversations[week] += 1
                except:
                    pass

        # Merge weekly data
        all_weeks = sorted(set(list(weekly_entities.keys()) + list(weekly_conversations.keys())))

        for week in all_weeks:
            trajectory["weekly_growth"].append({
                "week": week,
                "entities": weekly_entities.get(week, 0),
                "conversations": weekly_conversations.get(week, 0)
            })

        # Calculate projections (simple moving average of last 4 weeks)
        if len(trajectory["weekly_growth"]) >= 4:
            recent_4 = trajectory["weekly_growth"][-4:]
            avg_entities = sum(w["entities"] for w in recent_4) / 4
            avg_conversations = sum(w["conversations"] for w in recent_4) / 4

            trajectory["projected_entities_30d"] = round(avg_entities * 4, 0)
            trajectory["projected_conversations_30d"] = round(avg_conversations * 4, 0)

            # Determine growth phase
            if len(trajectory["weekly_growth"]) >= 8:
                first_half = trajectory["weekly_growth"][:len(trajectory["weekly_growth"])//2]
                second_half = trajectory["weekly_growth"][len(trajectory["weekly_growth"])//2:]

                first_avg = sum(w["conversations"] for w in first_half) / len(first_half)
                second_avg = sum(w["conversations"] for w in second_half) / len(second_half)

                growth_rate = (second_avg - first_avg) / first_avg if first_avg > 0 else 0

                if growth_rate > 0.5:
                    trajectory["growth_phase"] = "Exponential"
                elif growth_rate > 0.1:
                    trajectory["growth_phase"] = "Linear"
                else:
                    trajectory["growth_phase"] = "Plateau"

        return trajectory

    def export_metrics(self, output_file: Path = None) -> Dict:
        """Export all metrics to JSON"""
        if output_file is None:
            output_file = self.vault_path / "_system" / "brain-space-metrics.json"

        metrics = self.calculate_all_metrics()

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2)

        self.logger.info(f"Metrics exported to {output_file}")
        return metrics


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Calculate brain space metrics")
    parser.add_argument("--vault", type=str, default="C:/obsidian-memory-vault",
                       help="Path to vault")
    parser.add_argument("--output", type=str, help="Override output file")

    args = parser.parse_args()

    calculator = BrainSpaceCalculator(Path(args.vault))

    output_path = Path(args.output) if args.output else None
    metrics = calculator.export_metrics(output_path)

    # Print summary
    coverage = metrics["knowledge_coverage"]
    velocity = metrics["learning_velocity"]
    depth = metrics["cognitive_depth"]

    print(f"\n[OK] Brain Space Metrics Calculated")
    print(f"\n   Knowledge Coverage:")
    print(f"      Entities: {coverage['total_entities']}")
    print(f"      Conversations: {coverage['total_conversations']}")
    print(f"      Time: {coverage['total_time_hours']} hours")
    print(f"      Areas: {len(coverage['areas'])}")

    print(f"\n   Learning Velocity:")
    print(f"      Entities/week: {velocity['entities_per_week']}")
    print(f"      Conversations/week: {velocity['conversations_per_week']}")
    print(f"      Acceleration: {velocity['acceleration']}")

    print(f"\n   Cognitive Depth:")
    print(f"      Average depth: {depth['average_depth']}")
    print(f"      Max depth: {depth['max_depth']}")
    print(f"      Deep entities: {depth['shallow_vs_deep']['deep']}")

    print(f"\n   Output: {output_path if output_path else calculator.vault_path / '_system' / 'brain-space-metrics.json'}\n")


if __name__ == "__main__":
    main()
