"""
Extract Tag Knowledge - Extract what the USER discussed about each tag

CRITICAL CONSTRAINT: Only extract what the user ACTUALLY discussed in the conversation.
Do NOT add external knowledge, definitions, or information not present in the conversation.

This ensures tag notes reflect the user's personal knowledge base, not a Wikipedia clone.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional


class TagKnowledgeExtractor:
    """Extract user's discussion about specific tags from conversation text"""

    def __init__(self):
        pass

    def extract_tag_discussion(
        self,
        tag_name: str,
        conversation_text: str,
        max_sentences: int = 4
    ) -> Optional[str]:
        """
        Extract what the user discussed about a specific tag from conversation

        Args:
            tag_name: Tag to find discussion about (e.g., "FastAPI", "Python")
            conversation_text: Full conversation text
            max_sentences: Maximum sentences to include (default 4)

        Returns:
            Concise summary of what user discussed about tag, or None if not discussed
        """
        # Find all paragraphs/sentences mentioning this tag
        relevant_segments = self._find_relevant_segments(tag_name, conversation_text)

        if not relevant_segments:
            return None

        # Extract key points
        discussion = self._consolidate_discussion(relevant_segments, max_sentences)

        return discussion

    def _find_relevant_segments(self, tag_name: str, text: str) -> List[str]:
        """
        Find text segments discussing the tag

        Args:
            tag_name: Tag to search for
            text: Full conversation text

        Returns:
            List of relevant text segments
        """
        segments = []

        # Normalize tag name for matching
        tag_lower = tag_name.lower()
        tag_variations = self._generate_tag_variations(tag_name)

        # Split into paragraphs
        paragraphs = text.split('\n\n')

        for para in paragraphs:
            # Check if paragraph mentions tag
            para_lower = para.lower()

            if any(var in para_lower for var in tag_variations):
                # Clean up markdown formatting
                clean_para = self._clean_markdown(para)

                if clean_para and len(clean_para.strip()) > 20:  # Ignore very short segments
                    segments.append(clean_para)

        return segments

    def _generate_tag_variations(self, tag_name: str) -> List[str]:
        """
        Generate variations of tag name for matching

        Args:
            tag_name: Original tag name

        Returns:
            List of variations (lowercase, with/without spaces, etc.)
        """
        variations = [tag_name.lower()]

        # Add hyphenated version
        variations.append(tag_name.replace(' ', '-').lower())
        variations.append(tag_name.replace('-', ' ').lower())

        # Add underscore version
        variations.append(tag_name.replace(' ', '_').lower())
        variations.append(tag_name.replace('-', '_').lower())

        # Remove duplicates
        return list(set(variations))

    def _clean_markdown(self, text: str) -> str:
        """
        Remove markdown formatting from text

        Args:
            text: Text with markdown

        Returns:
            Plain text
        """
        # Remove code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

        # Remove inline code
        text = re.sub(r'`[^`]+`', '', text)

        # Remove bold/italic
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)

        # Remove links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # Remove headers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)

        # Remove list markers
        text = re.sub(r'^\s*[\-\*\+]\s+', '', text, flags=re.MULTILINE)

        # Clean up whitespace
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def _consolidate_discussion(self, segments: List[str], max_sentences: int) -> str:
        """
        Consolidate multiple segments into concise discussion summary

        Args:
            segments: List of relevant text segments
            max_sentences: Maximum sentences to include

        Returns:
            Consolidated discussion text
        """
        # Split all segments into sentences
        all_sentences = []

        for segment in segments:
            # Simple sentence split (handles most cases)
            sentences = re.split(r'(?<=[.!?])\s+', segment)
            all_sentences.extend([s.strip() for s in sentences if s.strip()])

        # Take most relevant sentences (prioritize those with tag references)
        # For now, take first max_sentences (in future could use more sophisticated ranking)
        selected = all_sentences[:max_sentences]

        # Join into paragraph
        discussion = ' '.join(selected)

        # Ensure proper ending
        if discussion and not discussion[-1] in '.!?':
            discussion += '.'

        return discussion

    def extract_all_tag_discussions(
        self,
        conversation_text: str,
        tags: List[str]
    ) -> Dict[str, str]:
        """
        Extract discussions for multiple tags from conversation

        Args:
            conversation_text: Full conversation text
            tags: List of tag names to extract

        Returns:
            Dict mapping tag_name -> discussion_text
        """
        discussions = {}

        for tag in tags:
            discussion = self.extract_tag_discussion(tag, conversation_text)

            if discussion:
                discussions[tag] = discussion

        return discussions


def extract_conversation_body(conversation_file: Path) -> str:
    """
    Extract conversation body text from processed conversation file

    Args:
        conversation_file: Path to conversation markdown file

    Returns:
        Conversation text (without frontmatter)
    """
    content = conversation_file.read_text(encoding='utf-8')

    # Remove frontmatter
    match = re.match(r'^---\n.*?\n---\n', content, re.DOTALL)
    if match:
        body = content[match.end():]
    else:
        body = content

    return body


def main():
    """CLI interface for tag knowledge extraction"""
    import argparse

    parser = argparse.ArgumentParser(description='Extract tag knowledge from conversations')
    parser.add_argument('--conversation', required=True, help='Path to conversation file')
    parser.add_argument('--tags', nargs='+', required=True, help='Tags to extract knowledge about')
    parser.add_argument('--max-sentences', type=int, default=4, help='Max sentences per tag')

    args = parser.parse_args()

    # Load conversation
    conv_path = Path(args.conversation)
    if not conv_path.exists():
        print(f"[!] Error: Conversation file not found: {conv_path}")
        return

    conversation_text = extract_conversation_body(conv_path)

    # Extract knowledge
    extractor = TagKnowledgeExtractor()

    for tag in args.tags:
        print(f"\n[*] Extracting knowledge about: {tag}")
        discussion = extractor.extract_tag_discussion(tag, conversation_text, args.max_sentences)

        if discussion:
            print(f"[+] Found discussion:\n{discussion}\n")
        else:
            print(f"[-] No discussion found about {tag}")


if __name__ == '__main__':
    main()
