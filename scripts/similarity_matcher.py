#!/usr/bin/env python3
"""
Similarity Matcher
Find similar entities based on co-occurrence patterns and shared contexts
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict
from logger_setup import get_logger, TimedOperation


class SimilarityMatcher:
    """Find similar entities based on patterns"""

    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path)
        self.logger = get_logger(__name__, str(vault_path))

    def find_similar_entities(self, entity: str, limit: int = 10) -> List[Dict]:
        """Find entities similar to the given entity"""
        self.logger.info(f"Finding entities similar to: {entity}")

        # Get conversations mentioning this entity
        entity_convs = self._get_entity_conversations(entity)

        if not entity_convs:
            self.logger.warning(f"No conversations found for entity: {entity}")
            return []

        # Count co-occurrences with other entities
        co_occurrence = defaultdict(int)

        for conv in entity_convs:
            entities = self._get_conversation_entities(conv)
            for other in entities:
                if other != entity:
                    co_occurrence[other] += 1

        # Calculate similarity scores
        similarities = []

        for other_entity, count in co_occurrence.items():
            # Co-occurrence score
            cooc_score = count

            # Jaccard similarity (shared conversations / total conversations)
            other_convs = self._get_entity_conversations(other_entity)
            shared = len(entity_convs & other_convs)
            total = len(entity_convs | other_convs)
            jaccard = shared / total if total > 0 else 0

            # Combined score
            similarity_score = (cooc_score * 10) + (jaccard * 100)

            similarities.append({
                "entity": other_entity,
                "similarity_score": round(similarity_score, 2),
                "co_occurrences": count,
                "jaccard_similarity": round(jaccard, 3),
                "shared_conversations": shared
            })

        # Sort by similarity
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)

        return similarities[:limit]

    def find_similar_by_tags(self, entity: str, limit: int = 10) -> List[Dict]:
        """Find similar entities based on shared taxonomy tags"""
        self.logger.info(f"Finding similar entities by tags: {entity}")

        # Get entity's parent tags
        entity_parents = self._get_parent_tags(entity)

        if not entity_parents:
            return []

        # Find entities with overlapping parent tags
        similarities = []

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

                other_entity = tag_match.group(1).strip()
                if other_entity == entity:
                    continue

                # Get other entity's parent tags
                other_parents = self._get_parent_tags(other_entity)

                # Calculate overlap
                shared = len(set(entity_parents) & set(other_parents))
                total = len(set(entity_parents) | set(other_parents))

                if shared > 0:
                    similarity = shared / total if total > 0 else 0

                    similarities.append({
                        "entity": other_entity,
                        "similarity": round(similarity, 3),
                        "shared_tags": shared,
                        "total_tags": total
                    })

            except:
                pass

        similarities.sort(key=lambda x: x["similarity"], reverse=True)

        return similarities[:limit]

    def find_cross_domain_similarities(self, limit: int = 20) -> List[Dict]:
        """Find surprising cross-domain similarities"""
        self.logger.info("Finding cross-domain similarities")

        # Get all entities by domain
        by_domain = defaultdict(list)

        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                    if 'type: tag-note' not in content:
                        continue

                tag_match = re.search(r'^tag:\s*(.+)$', content, re.MULTILINE)
                root_match = re.search(r'root:\s*(\w+)', content)

                if tag_match and root_match:
                    entity = tag_match.group(1).strip()
                    root = root_match.group(1)
                    by_domain[root].append(entity)

            except:
                pass

        # Find co-occurrences across domains
        cross_domain = []

        for domain1, entities1 in by_domain.items():
            for entity1 in entities1:
                entity1_convs = self._get_entity_conversations(entity1)

                for domain2, entities2 in by_domain.items():
                    if domain1 >= domain2:  # Avoid duplicates
                        continue

                    for entity2 in entities2:
                        entity2_convs = self._get_entity_conversations(entity2)

                        shared = len(entity1_convs & entity2_convs)
                        if shared > 0:
                            cross_domain.append({
                                "entity1": entity1,
                                "domain1": domain1,
                                "entity2": entity2,
                                "domain2": domain2,
                                "shared_conversations": shared
                            })

        # Sort by shared conversations
        cross_domain.sort(key=lambda x: x["shared_conversations"], reverse=True)

        return cross_domain[:limit]

    def build_similarity_matrix(self) -> Dict:
        """Build full similarity matrix for all entities"""
        with TimedOperation(self.logger, "Building similarity matrix"):
            entities = self._get_all_entities()

            matrix = {}

            for entity in entities:
                similar = self.find_similar_entities(entity, limit=5)
                matrix[entity] = similar

            self.logger.info(f"Built similarity matrix for {len(entities)} entities")

            return matrix

    def suggest_connections(self, entity: str, threshold: float = 0.3) -> List[str]:
        """Suggest entities that should be connected to this one"""
        similar = self.find_similar_entities(entity, limit=20)

        # Filter by threshold
        suggestions = [
            s["entity"] for s in similar
            if s["jaccard_similarity"] >= threshold
        ]

        return suggestions

    def _get_entity_conversations(self, entity: str) -> Set[str]:
        """Get set of conversation files mentioning entity"""
        conversations = set()

        processed_dir = self.vault_path / "00-Inbox" / "processed"
        if not processed_dir.exists():
            return conversations

        for conv_file in processed_dir.glob("*.md"):
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    content = f.read(1000)

                entities_match = re.search(r'entities:\s*\[(.*?)\]', content, re.DOTALL)
                if entities_match:
                    entities = [e.strip().strip('"').strip("'") for e in entities_match.group(1).split(',')]
                    if entity in entities:
                        conversations.add(conv_file.name)

            except:
                pass

        return conversations

    def _get_conversation_entities(self, conv_file_name: str) -> List[str]:
        """Get all entities in a conversation"""
        conv_file = self.vault_path / "00-Inbox" / "processed" / conv_file_name

        if not conv_file.exists():
            return []

        try:
            with open(conv_file, 'r', encoding='utf-8') as f:
                content = f.read(1000)

            entities_match = re.search(r'entities:\s*\[(.*?)\]', content, re.DOTALL)
            if entities_match:
                return [e.strip().strip('"').strip("'") for e in entities_match.group(1).split(',') if e.strip()]

        except:
            pass

        return []

    def _get_parent_tags(self, entity: str) -> List[str]:
        """Get parent tags for entity"""
        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                    if 'type: tag-note' not in content:
                        continue

                tag_match = re.search(r'^tag:\s*(.+)$', content, re.MULTILINE)
                if not tag_match or tag_match.group(1).strip() != entity:
                    continue

                parent_match = re.search(r'parent_tags:\s*\[(.*?)\]', content)
                if parent_match:
                    return [p.strip() for p in parent_match.group(1).split(',') if p.strip()]

            except:
                pass

        return []

    def _get_all_entities(self) -> List[str]:
        """Get list of all entities"""
        entities = []

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
                    entities.append(tag_match.group(1).strip())

            except:
                pass

        return entities


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Entity similarity matcher")
    parser.add_argument("--vault", type=str, default="C:/obsidian-memory-vault",
                       help="Path to vault")
    parser.add_argument("--entity", type=str,
                       help="Find similar entities to this one")
    parser.add_argument("--by-tags", action="store_true",
                       help="Use taxonomy tags for similarity")
    parser.add_argument("--cross-domain", action="store_true",
                       help="Find cross-domain similarities")
    parser.add_argument("--matrix", action="store_true",
                       help="Build full similarity matrix")

    args = parser.parse_args()

    matcher = SimilarityMatcher(Path(args.vault))

    if args.entity:
        if args.by_tags:
            similar = matcher.find_similar_by_tags(args.entity, limit=10)
            print(f"\n[OK] Similar Entities by Tags: {args.entity}")
            for sim in similar:
                print(f"\n   {sim['entity']}")
                print(f"      Similarity: {sim['similarity']}")
                print(f"      Shared tags: {sim['shared_tags']}/{sim['total_tags']}")

        else:
            similar = matcher.find_similar_entities(args.entity, limit=10)
            print(f"\n[OK] Similar Entities: {args.entity}")
            for sim in similar:
                print(f"\n   {sim['entity']}")
                print(f"      Score: {sim['similarity_score']}")
                print(f"      Co-occurrences: {sim['co_occurrences']}")
                print(f"      Jaccard: {sim['jaccard_similarity']}")

    elif args.cross_domain:
        cross = matcher.find_cross_domain_similarities(limit=20)
        print(f"\n[OK] Cross-Domain Similarities")
        for c in cross:
            print(f"\n   {c['entity1']} ({c['domain1']}) <-> {c['entity2']} ({c['domain2']})")
            print(f"      Shared conversations: {c['shared_conversations']}")

    elif args.matrix:
        matrix = matcher.build_similarity_matrix()
        output_file = Path(args.vault) / "_system" / "similarity-matrix.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(matrix, f, indent=2)

        print(f"\n[OK] Similarity Matrix Built")
        print(f"   Entities: {len(matrix)}")
        print(f"   Output: {output_file}")

    else:
        print(f"\n[INFO] Similarity Matcher")
        print(f"   Use --entity, --cross-domain, or --matrix")

    print()


if __name__ == "__main__":
    main()
