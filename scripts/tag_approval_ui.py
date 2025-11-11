#!/usr/bin/env python3
"""
Terminal UI for Tag Approval
Interactive interface for human-in-the-loop tag confirmation during processing
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class TagApprovalUI:
    """Terminal-based UI for tag approval during processing"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.tag_taxonomy_path = self.vault_path / "_system" / "tag-taxonomy.md"
        self.tag_review_queue_path = self.vault_path / "_system" / "tag-review-queue.md"

        # Colors for terminal output
        self.COLORS = {
            'HEADER': '\033[95m',
            'BLUE': '\033[94m',
            'CYAN': '\033[96m',
            'GREEN': '\033[92m',
            'YELLOW': '\033[93m',
            'RED': '\033[91m',
            'BOLD': '\033[1m',
            'UNDERLINE': '\033[4m',
            'END': '\033[0m'
        }

    def colored(self, text: str, color: str) -> str:
        """Add color to terminal text"""
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['END']}"

    def print_header(self, text: str):
        """Print formatted header"""
        width = 80
        print("\n" + "=" * width)
        print(self.colored(text.center(width), 'BOLD'))
        print("=" * width + "\n")

    def print_box(self, title: str, content: List[str]):
        """Print content in a box"""
        width = 76
        print("╔" + "═" * width + "╗")
        print("║ " + self.colored(title, 'BOLD').ljust(width + 9) + " ║")  # +9 for color codes
        print("╠" + "═" * width + "╣")

        for line in content:
            # Wrap long lines
            while len(line) > width - 2:
                print("║ " + line[:width - 2] + " ║")
                line = "  " + line[width - 2:]
            print("║ " + line.ljust(width) + " ║")

        print("╚" + "═" * width + "╝\n")

    def display_proposal(self, proposal: Dict, index: int, total: int) -> None:
        """Display a single tag proposal"""
        self.print_header(f"TAG PROPOSAL {index}/{total}")

        # Main proposal info
        confidence = proposal.get('confidence', 0)
        content = [
            f"Proposed Tag: {self.colored(proposal['proposed_name'], 'CYAN')}",
            f"Confidence: {self.colored(f'{confidence:.2f}', 'YELLOW')}",
            f"Category: {proposal.get('category', 'unknown')}",
            "",
            f"Context: {proposal.get('context', 'No context provided')}"
        ]

        self.print_box("Proposal Details", content)

        # Similar tags if available
        if proposal.get('similar_tags'):
            similar_content = ["Similar Existing Tags:"]
            for tag in proposal['similar_tags']:
                similarity = tag.get('similarity', 0)
                color = 'GREEN' if similarity > 0.8 else 'YELLOW' if similarity > 0.6 else 'RED'
                similar_content.append(
                    f"  • {tag['name']} "
                    f"(similarity: {self.colored(f'{similarity:.2f}', color)})"
                )

            self.print_box("Similar Tags", similar_content)

        # Recommendation
        recommendation = proposal.get('recommendation', 'REVIEW')
        rec_color = 'GREEN' if recommendation == 'APPROVE' else 'YELLOW'
        print(f"AI Recommendation: {self.colored(recommendation, rec_color)}\n")

    def get_user_decision(self, proposal: Dict) -> Dict:
        """Get user decision for a tag proposal"""
        print(self.colored("Options:", 'BOLD'))
        print(f"  {self.colored('[A]', 'GREEN')} Approve as new tag")
        print(f"  {self.colored('[M]', 'YELLOW')} Merge into existing tag")
        print(f"  {self.colored('[R]', 'RED')} Reject (use existing tag)")
        print(f"  {self.colored('[S]', 'CYAN')} Skip (manual review later)")
        print(f"  {self.colored('[I]', 'BLUE')} More info / Edit tag name")
        print(f"  {self.colored('[Q]', 'RED')} Quit (save progress)")

        while True:
            choice = input(f"\n{self.colored('Your choice [A/M/R/S/I/Q]:', 'BOLD')} ").strip().upper()

            if choice == 'A':
                return self._handle_approve(proposal)
            elif choice == 'M':
                return self._handle_merge(proposal)
            elif choice == 'R':
                return self._handle_reject(proposal)
            elif choice == 'S':
                return self._handle_skip(proposal)
            elif choice == 'I':
                return self._handle_info(proposal)
            elif choice == 'Q':
                return {'action': 'QUIT'}
            else:
                print(self.colored("Invalid choice. Please try again.", 'RED'))

    def _handle_approve(self, proposal: Dict) -> Dict:
        """Handle tag approval"""
        tag_name = proposal['proposed_name']

        # Optional: Let user edit tag name
        print(f"\nApproving tag: {self.colored(tag_name, 'CYAN')}")
        edit = input("Edit tag name? [y/N]: ").strip().lower()

        if edit == 'y':
            new_name = input("Enter new tag name: ").strip().lower()
            if new_name:
                tag_name = new_name

        # Get category
        category = proposal.get('category', 'tech/programming')
        edit_cat = input(f"Category [{category}] (press Enter to keep): ").strip()
        if edit_cat:
            category = edit_cat

        # Get aliases
        aliases = []
        print("\nAdd aliases (comma-separated, or press Enter to skip):")
        alias_input = input("Aliases: ").strip()
        if alias_input:
            aliases = [a.strip() for a in alias_input.split(',')]

        return {
            'action': 'APPROVE',
            'tag_name': tag_name,
            'category': category,
            'aliases': aliases,
            'original_proposal': proposal
        }

    def _handle_merge(self, proposal: Dict) -> Dict:
        """Handle merging into existing tag"""
        similar_tags = proposal.get('similar_tags', [])

        if not similar_tags:
            print(self.colored("\n⚠️  No similar tags available to merge into", 'YELLOW'))
            return {'action': 'SKIP'}

        print(f"\n{self.colored('Available tags to merge into:', 'BOLD')}")
        for i, tag in enumerate(similar_tags, 1):
            print(f"  [{i}] {tag['name']} (similarity: {tag.get('similarity', 0):.2f})")

        print(f"  [0] Enter custom tag name")

        while True:
            try:
                choice = int(input("\nSelect tag number: ").strip())

                if choice == 0:
                    custom_tag = input("Enter tag name to merge into: ").strip().lower()
                    if custom_tag:
                        return {
                            'action': 'MERGE',
                            'merge_into': custom_tag,
                            'add_as_alias': proposal['proposed_name']
                        }
                elif 1 <= choice <= len(similar_tags):
                    merge_tag = similar_tags[choice - 1]['name']
                    return {
                        'action': 'MERGE',
                        'merge_into': merge_tag,
                        'add_as_alias': proposal['proposed_name']
                    }
                else:
                    print(self.colored("Invalid choice", 'RED'))
            except ValueError:
                print(self.colored("Please enter a number", 'RED'))

    def _handle_reject(self, proposal: Dict) -> Dict:
        """Handle tag rejection"""
        similar_tags = proposal.get('similar_tags', [])

        if similar_tags:
            # Use closest match
            use_tag = similar_tags[0]['name']
            print(f"\nRejecting '{proposal['proposed_name']}'")
            print(f"Will use: {self.colored(use_tag, 'GREEN')}")
            confirm = input("Confirm? [Y/n]: ").strip().lower()

            if confirm != 'n':
                return {
                    'action': 'REJECT',
                    'use_existing': use_tag
                }

        # No similar tags or user said no
        print("\nNo existing tag selected. Skipping to manual review.")
        return {'action': 'SKIP'}

    def _handle_skip(self, proposal: Dict) -> Dict:
        """Handle skip (defer to manual review)"""
        print(f"\n{self.colored('Skipping for manual review later', 'CYAN')}")

        # Use closest match temporarily if available
        similar_tags = proposal.get('similar_tags', [])
        temp_tag = similar_tags[0]['name'] if similar_tags else None

        return {
            'action': 'SKIP',
            'temporary_tag': temp_tag,
            'add_to_queue': True
        }

    def _handle_info(self, proposal: Dict) -> Dict:
        """Show more information and allow editing"""
        print(f"\n{self.colored('=== Additional Information ===', 'BOLD')}\n")

        # Show full context
        print(f"Proposed Name: {proposal['proposed_name']}")
        print(f"Confidence: {proposal.get('confidence', 0):.2f}")
        print(f"Times Encountered: {proposal.get('times_encountered', 1)}")
        print(f"\nFull Context:")
        print(f"  {proposal.get('context', 'No context available')}\n")

        # Show usage examples if available
        if proposal.get('usage_examples'):
            print("Usage Examples:")
            for example in proposal['usage_examples']:
                print(f"  • {example}")
            print()

        # Return to main menu
        input("Press Enter to return to options...")
        return self.get_user_decision(proposal)

    def approve_tags_batch(self, proposals: List[Dict]) -> List[Dict]:
        """Process multiple tag proposals in batch"""
        if not proposals:
            print(self.colored("✅ No new tags to approve!", 'GREEN'))
            return []

        self.print_header("TAG APPROVAL SESSION")
        print(f"You have {self.colored(str(len(proposals)), 'YELLOW')} tag proposal(s) to review.\n")

        # Option to approve all
        print("Quick options:")
        print(f"  {self.colored('[A]', 'GREEN')} Approve all (if you're confident)")
        print(f"  {self.colored('[R]', 'YELLOW')} Review individually")
        print(f"  {self.colored('[S]', 'CYAN')} Skip all (manual review later)")

        quick_choice = input(f"\n{self.colored('Quick action [A/R/S]:', 'BOLD')} ").strip().upper()

        if quick_choice == 'A':
            return self._approve_all(proposals)
        elif quick_choice == 'S':
            return self._skip_all(proposals)

        # Individual review
        results = []

        for i, proposal in enumerate(proposals, 1):
            self.display_proposal(proposal, i, len(proposals))
            decision = self.get_user_decision(proposal)

            if decision.get('action') == 'QUIT':
                print(f"\n{self.colored('⚠️  Quitting approval session', 'YELLOW')}")
                print(f"Progress saved: {len(results)}/{len(proposals)} reviewed")

                # Save remaining proposals for later
                remaining = proposals[i:]
                self._save_remaining_proposals(remaining)

                break

            results.append(decision)

        # Summary
        self._print_summary(results)

        return results

    def _approve_all(self, proposals: List[Dict]) -> List[Dict]:
        """Approve all proposals automatically"""
        print(f"\n{self.colored('Approving all tags...', 'GREEN')}\n")

        results = []
        for proposal in proposals:
            tag_name = proposal['proposed_name']
            category = proposal.get('category', 'tech/programming')

            results.append({
                'action': 'APPROVE',
                'tag_name': tag_name,
                'category': category,
                'aliases': [],
                'original_proposal': proposal
            })

            print(f"  ✓ Approved: {tag_name}")

        print(f"\n{self.colored(f'✅ Approved {len(results)} tags', 'GREEN')}")
        return results

    def _skip_all(self, proposals: List[Dict]) -> List[Dict]:
        """Skip all proposals (defer to manual review)"""
        print(f"\n{self.colored('Skipping all tags for manual review...', 'CYAN')}\n")

        results = []
        for proposal in proposals:
            similar_tags = proposal.get('similar_tags', [])
            temp_tag = similar_tags[0]['name'] if similar_tags else None

            results.append({
                'action': 'SKIP',
                'temporary_tag': temp_tag,
                'add_to_queue': True
            })

        self._save_to_review_queue(proposals)
        print(f"\n{self.colored(f'✅ Queued {len(results)} tags for manual review', 'CYAN')}")

        return results

    def _save_remaining_proposals(self, proposals: List[Dict]):
        """Save remaining proposals to review queue"""
        if not proposals:
            return

        print(f"\nSaving {len(proposals)} remaining proposals to tag-review-queue.md...")

        self._save_to_review_queue(proposals)

        print(f"{self.colored('✅ Saved successfully', 'GREEN')}")

    def _save_to_review_queue(self, proposals: List[Dict]):
        """Append proposals to tag review queue file"""
        try:
            with open(self.tag_review_queue_path, 'a', encoding='utf-8') as f:
                f.write(f"\n\n<!-- Batch added: {datetime.now().isoformat()} -->\n\n")

                for proposal in proposals:
                    f.write(self._format_proposal_for_queue(proposal))

        except Exception as e:
            print(self.colored(f"❌ Error saving to queue: {e}", 'RED'))

    def _format_proposal_for_queue(self, proposal: Dict) -> str:
        """Format proposal for tag-review-queue.md"""
        similar_section = ""
        if proposal.get('similar_tags'):
            similar_section = "\n**Similar existing tags**:\n"
            for tag in proposal['similar_tags']:
                similar_section += f"- `{tag['name']}` (similarity: {tag.get('similarity', 0):.2f})\n"

        return f"""### {datetime.now().strftime('%Y-%m-%d')} - Proposed Tag: `{proposal['proposed_name']}`

**Proposed by**: Processing Pipeline Agent
**Confidence**: {proposal.get('confidence', 0):.2f}
**Times encountered**: {proposal.get('times_encountered', 1)}
**Category**: {proposal.get('category', 'unknown')}
{similar_section}
**Context/Usage**:
{proposal.get('context', 'No context provided')}

**Recommendation**:
- [ ] **Approve** - Add to taxonomy as new tag
- [ ] **Merge** - Use existing tag: `________`
- [ ] **Alias** - Add as alias to existing: `________`
- [ ] **Reject** - Too specific/not needed

**Human Decision**: [To be filled]

**Action Taken**: [Date + what was done]

---

"""

    def _print_summary(self, results: List[Dict]):
        """Print summary of approval session"""
        print("\n")
        self.print_header("APPROVAL SESSION SUMMARY")

        approved = sum(1 for r in results if r.get('action') == 'APPROVE')
        merged = sum(1 for r in results if r.get('action') == 'MERGE')
        rejected = sum(1 for r in results if r.get('action') == 'REJECT')
        skipped = sum(1 for r in results if r.get('action') == 'SKIP')

        summary = [
            f"Total Reviewed: {len(results)}",
            f"",
            f"✅ Approved: {self.colored(str(approved), 'GREEN')}",
            f"🔀 Merged: {self.colored(str(merged), 'YELLOW')}",
            f"❌ Rejected: {self.colored(str(rejected), 'RED')}",
            f"⏸️  Skipped: {self.colored(str(skipped), 'CYAN')}"
        ]

        self.print_box("Results", summary)


# Example usage
if __name__ == "__main__":
    ui = TagApprovalUI("C:/obsidian-memory-vault")

    # Test with sample proposals
    sample_proposals = [
        {
            "proposed_name": "pytest",
            "confidence": 0.65,
            "category": "tech/tools",
            "context": "Python testing framework used for unit and integration tests",
            "similar_tags": [
                {"name": "testing", "similarity": 0.72},
                {"name": "python", "similarity": 0.68}
            ],
            "recommendation": "REVIEW",
            "times_encountered": 3
        },
        {
            "proposed_name": "github-actions",
            "confidence": 0.80,
            "category": "tech/infrastructure",
            "context": "CI/CD automation platform by GitHub",
            "similar_tags": [
                {"name": "ci-cd", "similarity": 0.85}
            ],
            "recommendation": "APPROVE",
            "times_encountered": 5
        }
    ]

    results = ui.approve_tags_batch(sample_proposals)

    print("\n\nReturned results:")
    print(json.dumps(results, indent=2))
