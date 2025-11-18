#!/usr/bin/env python3
"""
Detect New Roots - Intelligent detection of new knowledge domains

This system analyzes entity patterns to detect when you're exploring
entirely new areas of knowledge that deserve their own root category.

Uses semantic pattern matching and clustering to suggest new roots automatically.
"""

import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Set
from collections import defaultdict, Counter

try:
    from scripts.tag_path_resolver import TagPathResolver
except ImportError:
    from tag_path_resolver import TagPathResolver


class NewRootDetector:
    """Detect when entities suggest creation of new root category"""

    # Known existing roots
    EXISTING_ROOTS = ["Technology", "Language", "History", "Culture", "Projects"]

    # Semantic keyword patterns for common knowledge domains
    ROOT_PATTERNS = {
        "Science": [
            "biology", "physics", "chemistry", "astronomy", "geology",
            "genetics", "dna", "evolution", "molecular", "cellular",
            "quantum", "particle", "atom", "molecule", "research",
            "experiment", "hypothesis", "theory", "scientific-method"
        ],
        "Art": [
            "painting", "sculpture", "music", "theater", "design",
            "drawing", "illustration", "photography", "film", "cinema",
            "dance", "performance", "creative", "aesthetic", "visual-art",
            "fine-art", "contemporary-art"
        ],
        "Business": [
            "finance", "marketing", "sales", "management", "economics",
            "accounting", "revenue", "profit", "business-model", "startup",
            "entrepreneur", "commerce", "trade", "market", "customer",
            "business-strategy", "leadership"
        ],
        "Health": [
            "medicine", "fitness", "nutrition", "mental-health", "wellness",
            "exercise", "diet", "healthcare", "therapy", "treatment",
            "diagnosis", "symptoms", "disease", "health", "medical",
            "pharmaceutical", "clinical"
        ],
        "Philosophy": [
            "ethics", "logic", "metaphysics", "epistemology", "philosophy",
            "reasoning", "argument", "truth", "knowledge", "existence",
            "morality", "virtue", "justice", "consciousness", "mind"
        ],
        "Mathematics": [
            "algebra", "geometry", "calculus", "statistics", "probability",
            "mathematics", "math", "equation", "theorem", "proof",
            "arithmetic", "numbers", "computation", "mathematical"
        ],
        "Education": [
            "pedagogy", "curriculum", "learning", "teaching", "education",
            "instruction", "training", "academic", "school", "university",
            "student", "teacher", "educational", "learning-theory"
        ],
        "Sports": [
            "football", "basketball", "athletics", "training", "sports",
            "competition", "athlete", "fitness", "game", "match",
            "tournament", "championship", "physical-activity"
        ],
        "Media": [
            "journalism", "broadcasting", "publishing", "content-creation",
            "media", "news", "press", "reporter", "editor", "blog",
            "podcast", "video", "streaming", "social-media"
        ],
        "Social Sciences": [
            "sociology", "psychology", "anthropology", "political-science",
            "social", "society", "culture", "behavior", "community",
            "identity", "relationships", "human-behavior"
        ]
    }

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.resolver = TagPathResolver(self.vault_path)
        self.taxonomy = self.resolver.taxonomy

        # Track suggestions
        self.suggestions = []

    def detect_root_for_entity(self, entity_name: str) -> Optional[str]:
        """
        Determine which root category an orphaned entity should belong to

        Args:
            entity_name: Entity/tag name (may include spaces or hyphens)

        Returns:
            Suggested root name, or None if can't determine
        """
        # First check if already in taxonomy
        normalized = entity_name.lower().replace(' ', '-').replace('_', '-')
        if normalized in self.taxonomy:
            return self.taxonomy[normalized].get('root')

        # Semantic matching against patterns
        entity_lower = entity_name.lower().replace('-', ' ').replace('_', ' ')
        entity_words = set(entity_lower.split())

        best_match = None
        best_score = 0

        for root, keywords in self.ROOT_PATTERNS.items():
            score = 0

            # Check for keyword matches
            for keyword in keywords:
                if keyword in entity_lower:
                    score += 2  # Exact phrase match
                elif any(word in keyword or keyword in word for word in entity_words):
                    score += 1  # Partial word match

            if score > best_score:
                best_score = score
                best_match = root

        # Require minimum confidence
        if best_score >= 2:
            return best_match

        return None

    def analyze_entity_cluster(self, entities: List[str]) -> Optional[Dict]:
        """
        Analyze a cluster of uncategorized entities to suggest new root

        Args:
            entities: List of entity names

        Returns:
            Suggestion dict with root name, confidence, and entities, or None
        """
        if len(entities) < 3:
            # Not enough for a cluster
            return None

        # Count root suggestions
        root_votes = Counter()

        for entity in entities:
            suggested_root = self.detect_root_for_entity(entity)
            if suggested_root:
                root_votes[suggested_root] += 1

        if not root_votes:
            # No clear suggestions
            return None

        # Get most common suggestion
        suggested_root, vote_count = root_votes.most_common(1)[0]

        # Calculate confidence
        confidence = vote_count / len(entities)

        # Require reasonable threshold
        if confidence >= 0.4 and vote_count >= 3:
            return {
                "suggested_root": suggested_root,
                "entities": entities,
                "vote_count": vote_count,
                "total_entities": len(entities),
                "confidence": round(confidence, 2),
                "confidence_level": "high" if confidence >= 0.7 else "medium"
            }

        return None

    def scan_uncategorized_entities(self) -> List[str]:
        """
        Scan vault for entities that don't belong to any existing root

        Returns:
            List of uncategorized entity names
        """
        uncategorized = []

        # Find all tag notes
        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                content = md_file.read_text(encoding='utf-8')

                if 'type: tag-note' not in content[:500]:
                    continue

                # Extract frontmatter
                match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
                if match:
                    import yaml
                    fm = yaml.safe_load(match.group(1))

                    root = fm.get('root', '')
                    tag = fm.get('tag', '')

                    # Check if uncategorized
                    if root in ['Uncategorized', 'Resources', 'Unknown', ''] and tag:
                        uncategorized.append(tag)

            except Exception:
                pass

        return uncategorized

    def generate_report(self, dry_run: bool = False) -> Dict:
        """
        Generate report of uncategorized entities and root suggestions

        Args:
            dry_run: If True, don't save report

        Returns:
            Report dict
        """
        print(f"\n{'='*60}")
        print(f"New Root Detection Analysis")
        print(f"{'='*60}\n")

        # Find uncategorized entities
        uncategorized = self.scan_uncategorized_entities()

        print(f"[i] Found {len(uncategorized)} uncategorized entities\n")

        if not uncategorized:
            print("[OK] All entities are categorized!")
            return {"uncategorized": [], "suggestion": None}

        # Analyze for clustering
        suggestion = self.analyze_entity_cluster(uncategorized)

        # Print results
        print(f"Uncategorized entities:")
        for entity in sorted(uncategorized):
            detected_root = self.detect_root_for_entity(entity)
            if detected_root:
                print(f"  - {entity} → suggested: {detected_root}")
            else:
                print(f"  - {entity} → no suggestion")

        print(f"\n")

        if suggestion:
            print(f"[SUGGESTION] Create new root category: '{suggestion['suggested_root']}'")
            print(f"  Confidence: {suggestion['confidence_level'].upper()} ({suggestion['confidence']*100:.0f}%)")
            print(f"  Supporting entities: {suggestion['vote_count']}/{suggestion['total_entities']}")
            print(f"  Entities: {', '.join(suggestion['entities'][:5])}{'...' if len(suggestion['entities']) > 5 else ''}")
            print(f"\n")
            print(f"[ACTION] To create this root:")
            print(f"  python scripts/create_root_category.py --vault . --root \"{suggestion['suggested_root']}\"")
        else:
            print(f"[INFO] No clear clustering detected")
            print(f"  Entities may need manual categorization")

        return {
            "uncategorized": uncategorized,
            "suggestion": suggestion
        }


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Detect new root categories from uncategorized entities")
    parser.add_argument("--vault", type=str, required=True, help="Path to Obsidian vault")
    parser.add_argument("--dry-run", action="store_true", help="Don't save report")

    args = parser.parse_args()

    vault_path = Path(args.vault)
    if not vault_path.exists():
        print(f"[X] Vault not found: {vault_path}")
        sys.exit(1)

    detector = NewRootDetector(str(vault_path))
    report = detector.generate_report(dry_run=args.dry_run)

    if report['suggestion']:
        print(f"\n[!] ACTION REQUIRED: Review suggestion and decide whether to create new root")


if __name__ == "__main__":
    main()
