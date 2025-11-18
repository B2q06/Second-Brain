"""
Backfill Tag Notes - Create tag notes for all existing processed conversations

This script processes all conversations in 00-Inbox/processed/ and creates/updates
tag notes retroactively, building the initial semantic memory layer.
"""

import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import sys

# Import our modules (try both relative and absolute)
try:
    from scripts.tag_note_manager import TagNoteManager
    from scripts.extract_tag_knowledge import TagKnowledgeExtractor, extract_conversation_body
except ImportError:
    from tag_note_manager import TagNoteManager
    from extract_tag_knowledge import TagKnowledgeExtractor, extract_conversation_body


class TagNoteBackfill:
    """Backfill tag notes from existing conversations"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.processed_folder = self.vault_path / "00-Inbox" / "processed"
        self.manager = TagNoteManager(str(vault_path))
        self.extractor = TagKnowledgeExtractor()

        # Statistics
        self.stats = {
            'conversations_processed': 0,
            'conversations_skipped': 0,
            'tag_notes_created': 0,
            'tag_notes_updated': 0,
            'entities_processed': 0,
            'errors': 0
        }

    def find_processed_conversations(self) -> List[Path]:
        """Find all processed conversation files"""
        if not self.processed_folder.exists():
            print(f"[!] Processed folder not found: {self.processed_folder}")
            return []

        conversations = list(self.processed_folder.glob("conversation_*.md"))
        conversations += list(self.processed_folder.glob("processed_conversation_*.md"))

        return sorted(conversations)

    def extract_frontmatter(self, conversation_file: Path) -> Dict:
        """Extract YAML frontmatter from conversation file"""
        content = conversation_file.read_text(encoding='utf-8')

        # Extract frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            print(f"[!] No frontmatter found in {conversation_file.name}")
            return {}

        try:
            frontmatter = yaml.safe_load(match.group(1))
            return frontmatter
        except Exception as e:
            print(f"[!] Error parsing frontmatter in {conversation_file.name}: {e}")
            return {}

    def extract_all_entities(self, frontmatter: Dict) -> List[str]:
        """Extract all entities from conversation frontmatter"""
        entities = []

        # Extract from various fields
        for field in ['topics', 'skills', 'concepts', 'projects', 'entities']:
            if field in frontmatter:
                values = frontmatter[field]

                # Handle both lists and single values
                if isinstance(values, list):
                    entities.extend(values)
                elif isinstance(values, str):
                    entities.append(values)

        # Also check for graph entities
        if 'graph' in frontmatter and 'entities' in frontmatter['graph']:
            graph_entities = frontmatter['graph']['entities']
            if isinstance(graph_entities, list):
                for entity_dict in graph_entities:
                    if isinstance(entity_dict, dict) and 'name' in entity_dict:
                        entities.append(entity_dict['name'])

        # Remove duplicates and empty strings
        entities = [e.strip() for e in entities if e and isinstance(e, str)]
        entities = list(set(entities))

        return entities

    def parse_timestamp(self, frontmatter: Dict, conversation_file: Path) -> datetime:
        """Parse timestamp from frontmatter"""
        # Try different timestamp fields
        for field in ['captured', 'created', 'timestamp', 'date']:
            if field in frontmatter:
                timestamp_str = frontmatter[field]

                # Parse various formats
                try:
                    # ISO format: 2025-11-11T16:30:00Z
                    if 'T' in str(timestamp_str):
                        return datetime.fromisoformat(str(timestamp_str).replace('Z', '+00:00'))

                    # Date only: 2025-11-11
                    return datetime.strptime(str(timestamp_str)[:10], '%Y-%m-%d')
                except Exception as e:
                    print(f"[!] Error parsing timestamp '{timestamp_str}': {e}")

        # Fallback: Use file modification time
        return datetime.fromtimestamp(conversation_file.stat().st_mtime)

    def extract_duration(self, frontmatter: Dict) -> int:
        """Extract conversation duration in minutes from frontmatter"""
        # Try different duration fields
        for field in ['duration_minutes', 'total_time_minutes', 'duration']:
            if field in frontmatter:
                try:
                    return int(frontmatter[field])
                except (ValueError, TypeError):
                    pass

        # Try to calculate from timestamps if available
        if 'captured' in frontmatter and 'completed' in frontmatter:
            try:
                start = datetime.fromisoformat(str(frontmatter['captured']).replace('Z', '+00:00'))
                end = datetime.fromisoformat(str(frontmatter['completed']).replace('Z', '+00:00'))
                duration = (end - start).total_seconds() / 60
                return int(duration)
            except:
                pass

        # Default estimate: 15 minutes per conversation
        return 15

    def process_conversation(self, conversation_file: Path) -> Tuple[int, int]:
        """
        Process a single conversation and create/update tag notes

        Returns:
            (created_count, updated_count)
        """
        try:
            print(f"\n[*] Processing: {conversation_file.name}")

            # Extract frontmatter
            frontmatter = self.extract_frontmatter(conversation_file)
            if not frontmatter:
                print(f"[-] Skipping (no frontmatter)")
                self.stats['conversations_skipped'] += 1
                return (0, 0)

            # Extract entities
            entities = self.extract_all_entities(frontmatter)
            if not entities:
                print(f"[-] Skipping (no entities found)")
                self.stats['conversations_skipped'] += 1
                return (0, 0)

            print(f"[+] Found {len(entities)} entities: {', '.join(entities[:5])}{'...' if len(entities) > 5 else ''}")

            # Extract conversation body
            conversation_text = extract_conversation_body(conversation_file)

            # Parse timestamp
            timestamp = self.parse_timestamp(frontmatter, conversation_file)
            print(f"[+] Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M')}")

            # Extract duration
            duration = self.extract_duration(frontmatter)
            print(f"[+] Duration: {duration} minutes")

            # Generate conversation link
            conversation_link = f"[[{conversation_file.stem}]]"

            # Process each entity
            created_count = 0
            updated_count = 0

            for entity in entities:
                try:
                    # Extract what user discussed about this entity
                    discussion = self.extractor.extract_tag_discussion(entity, conversation_text)

                    if not discussion or len(discussion.strip()) < 20:
                        print(f"  [-] {entity}: No substantial discussion found")
                        continue

                    # Get related tags (other entities from same conversation)
                    related_tags = self.manager.extract_related_tags(entities, entity)

                    # Create or update tag note
                    tag_path, created_new = self.manager.create_or_update_tag_note(
                        tag_name=entity,
                        discussion_text=discussion,
                        timestamp=timestamp,
                        conversation_link=conversation_link,
                        related_tags=related_tags,
                        conversation_duration_minutes=duration
                    )

                    if created_new:
                        created_count += 1
                        print(f"  [+] {entity}: Created -> {tag_path.name}")
                    else:
                        updated_count += 1
                        print(f"  [~] {entity}: Updated -> {tag_path.name}")

                    self.stats['entities_processed'] += 1

                except Exception as e:
                    print(f"  [X] {entity}: Error - {e}")
                    self.stats['errors'] += 1

            self.stats['conversations_processed'] += 1
            return (created_count, updated_count)

        except Exception as e:
            print(f"[X] Error processing {conversation_file.name}: {e}")
            import traceback
            traceback.print_exc()
            self.stats['errors'] += 1
            self.stats['conversations_skipped'] += 1
            return (0, 0)

    def run(self, dry_run: bool = False, limit: int = None):
        """
        Run backfill for all processed conversations

        Args:
            dry_run: If True, only show what would be processed
            limit: Maximum number of conversations to process
        """
        print(f"\n{'='*60}")
        print(f"Tag Note Backfill")
        print(f"Vault: {self.vault_path}")
        if dry_run:
            print(f"Mode: DRY RUN (no files will be modified)")
        if limit:
            print(f"Limit: {limit} conversations")
        print(f"{'='*60}\n")

        # Find all conversations
        conversations = self.find_processed_conversations()
        print(f"[i] Found {len(conversations)} processed conversation(s)\n")

        if not conversations:
            print("[!] No conversations to process")
            return

        # Apply limit if specified
        if limit:
            conversations = conversations[:limit]

        # Dry run mode
        if dry_run:
            for conv in conversations:
                print(f"[~] Would process: {conv.name}")
                frontmatter = self.extract_frontmatter(conv)
                entities = self.extract_all_entities(frontmatter)
                print(f"    Entities: {', '.join(entities)}")
            print(f"\n[i] Dry run complete. {len(conversations)} conversations would be processed.")
            return

        # Process each conversation
        total_created = 0
        total_updated = 0

        for conv in conversations:
            created, updated = self.process_conversation(conv)
            total_created += created
            total_updated += updated
            self.stats['tag_notes_created'] += created
            self.stats['tag_notes_updated'] += updated

        # Print summary
        print(f"\n{'='*60}")
        print(f"[+] Backfill Complete")
        print(f"{'='*60}")
        print(f"Conversations processed: {self.stats['conversations_processed']}")
        print(f"Conversations skipped: {self.stats['conversations_skipped']}")
        print(f"Entities processed: {self.stats['entities_processed']}")
        print(f"Tag notes created: {self.stats['tag_notes_created']}")
        print(f"Tag notes updated: {self.stats['tag_notes_updated']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"{'='*60}\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Backfill tag notes from existing conversations")
    parser.add_argument("--vault", type=str, required=True, help="Path to Obsidian vault")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed without making changes")
    parser.add_argument("--limit", type=int, help="Limit number of conversations to process (for testing)")

    args = parser.parse_args()

    vault_path = Path(args.vault)
    if not vault_path.exists():
        print(f"[X] Vault not found: {vault_path}")
        sys.exit(1)

    backfill = TagNoteBackfill(str(vault_path))
    backfill.run(dry_run=args.dry_run, limit=args.limit)


if __name__ == '__main__':
    main()
