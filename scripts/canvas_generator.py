#!/usr/bin/env python3
"""
Canvas Generator
Generates Obsidian canvas files (.canvas) for knowledge graph visualization
"""

import json
import re
import math
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict
from logger_setup import get_logger, TimedOperation


class CanvasGenerator:
    """Generate Obsidian canvas files for knowledge visualization"""

    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path)
        self.logger = get_logger(__name__, str(vault_path))

    def generate_area_canvas(self, area: str, output_file: Path = None) -> Dict:
        """Generate canvas for a specific knowledge area"""
        self.logger.info(f"Generating canvas for area: {area}")

        if output_file is None:
            output_file = self.vault_path / f"{area}_knowledge_graph.canvas"

        # Find all tag notes in this area
        tag_notes = self._find_tag_notes_by_area(area)

        if not tag_notes:
            self.logger.warning(f"No tag notes found for area: {area}")
            return {}

        # Build node and edge data
        nodes = []
        edges = []
        node_positions = {}

        # Calculate layout
        positions = self._calculate_radial_layout(len(tag_notes))

        for i, (tag_file, tag_data) in enumerate(tag_notes.items()):
            # Create node
            x, y = positions[i]
            node_id = f"node_{i}"

            # Node size based on conversations
            conversations = tag_data.get("conversations", 0)
            size = self._calculate_node_size(conversations)

            # Node color based on depth
            depth = tag_data.get("depth", 1)
            color = self._get_depth_color(depth)

            node = {
                "id": node_id,
                "type": "file",
                "file": str(tag_file.relative_to(self.vault_path)),
                "x": x,
                "y": y,
                "width": size,
                "height": size,
                "color": color
            }

            nodes.append(node)
            node_positions[tag_data["tag"]] = node_id

            # Create label node
            label_node = {
                "id": f"label_{i}",
                "type": "text",
                "text": tag_data["tag"],
                "x": x,
                "y": y + size + 20,
                "width": 120,
                "height": 40,
                "color": "0"
            }
            nodes.append(label_node)

        # Create edges based on parent_tags
        for tag_file, tag_data in tag_notes.items():
            tag = tag_data["tag"]
            parent_tags = tag_data.get("parent_tags", [])

            if tag not in node_positions:
                continue

            from_id = node_positions[tag]

            for parent in parent_tags:
                if parent in node_positions:
                    to_id = node_positions[parent]

                    edge = {
                        "id": f"edge_{from_id}_{to_id}",
                        "fromNode": from_id,
                        "toNode": to_id,
                        "color": "2"
                    }

                    edges.append(edge)

        # Build canvas JSON
        canvas = {
            "nodes": nodes,
            "edges": edges
        }

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(canvas, f, indent=2)

        self.logger.info(f"Canvas generated: {output_file}")
        self.logger.info(f"  Nodes: {len(nodes)}, Edges: {len(edges)}")

        return canvas

    def generate_conversation_canvas(self, conversation_file: Path, output_file: Path = None) -> Dict:
        """Generate canvas for a single conversation showing all entities"""
        self.logger.info(f"Generating canvas for conversation: {conversation_file.name}")

        if output_file is None:
            output_file = conversation_file.with_suffix(".canvas")

        # Extract entities from conversation
        with open(conversation_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse frontmatter
        fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not fm_match:
            self.logger.error("No frontmatter found")
            return {}

        # Extract entities
        entities_match = re.search(r'entities:\s*\[(.*?)\]', fm_match.group(1), re.DOTALL)
        if not entities_match:
            self.logger.warning("No entities found in conversation")
            return {}

        entities = [e.strip() for e in entities_match.group(1).split(',')]

        # Create nodes
        nodes = []
        edges = []

        # Center conversation node
        conv_node = {
            "id": "conversation",
            "type": "file",
            "file": str(conversation_file.relative_to(self.vault_path)),
            "x": 0,
            "y": 0,
            "width": 400,
            "height": 300,
            "color": "1"
        }
        nodes.append(conv_node)

        # Entity nodes in circle around conversation
        positions = self._calculate_circular_layout(len(entities), radius=600)

        for i, entity in enumerate(entities):
            x, y = positions[i]

            # Find tag note for entity
            tag_file = self._find_tag_note(entity)

            if tag_file:
                node = {
                    "id": f"entity_{i}",
                    "type": "file",
                    "file": str(tag_file.relative_to(self.vault_path)),
                    "x": x,
                    "y": y,
                    "width": 200,
                    "height": 150,
                    "color": "3"
                }
            else:
                # Text node if tag note not found
                node = {
                    "id": f"entity_{i}",
                    "type": "text",
                    "text": entity,
                    "x": x,
                    "y": y,
                    "width": 150,
                    "height": 80,
                    "color": "5"
                }

            nodes.append(node)

            # Edge to conversation
            edge = {
                "id": f"edge_conv_{i}",
                "fromNode": "conversation",
                "toNode": f"entity_{i}",
                "color": "4"
            }
            edges.append(edge)

        # Build canvas
        canvas = {
            "nodes": nodes,
            "edges": edges
        }

        # Save
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(canvas, f, indent=2)

        self.logger.info(f"Conversation canvas generated: {output_file}")
        return canvas

    def generate_global_canvas(self, output_file: Path = None) -> Dict:
        """Generate global canvas showing all areas and connections"""
        self.logger.info("Generating global knowledge canvas")

        if output_file is None:
            output_file = self.vault_path / "Global_Knowledge_Graph.canvas"

        # Find all areas
        areas = self._find_all_areas()

        if not areas:
            self.logger.warning("No areas found")
            return {}

        nodes = []
        edges = []

        # Area nodes in grid layout
        grid_size = math.ceil(math.sqrt(len(areas)))
        spacing = 600

        for i, (area, area_data) in enumerate(areas.items()):
            row = i // grid_size
            col = i % grid_size

            x = col * spacing
            y = row * spacing

            # Area size based on entity count
            entity_count = area_data["entity_count"]
            size = 200 + (entity_count * 5)

            node = {
                "id": f"area_{i}",
                "type": "text",
                "text": f"**{area}**\n\nEntities: {entity_count}\nTime: {area_data['time_hours']}h",
                "x": x,
                "y": y,
                "width": size,
                "height": size,
                "color": str((i % 5) + 1)
            }

            nodes.append(node)

        # No edges for now (could add cross-area connections later)

        canvas = {
            "nodes": nodes,
            "edges": edges
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(canvas, f, indent=2)

        self.logger.info(f"Global canvas generated: {output_file}")
        return canvas

    def _find_tag_notes_by_area(self, area: str) -> Dict[Path, Dict]:
        """Find all tag notes in a specific area"""
        tag_notes = {}

        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(1000)

                    if 'type: tag-note' not in content:
                        continue

                    # Check if matches area
                    root_match = re.search(r'root:\s*(\w+)', content)
                    if not root_match or root_match.group(1) != area:
                        continue

                    # Extract tag data
                    tag_match = re.search(r'^tag:\s*(.+)$', content, re.MULTILINE)
                    conv_match = re.search(r'total_conversations:\s*(\d+)', content)
                    depth_match = re.search(r'depth:\s*(\d+)', content)
                    parent_match = re.search(r'parent_tags:\s*\[(.*?)\]', content)

                    tag_data = {
                        "tag": tag_match.group(1).strip() if tag_match else md_file.stem,
                        "conversations": int(conv_match.group(1)) if conv_match else 0,
                        "depth": int(depth_match.group(1)) if depth_match else 1,
                        "parent_tags": []
                    }

                    if parent_match:
                        parents = parent_match.group(1).split(',')
                        tag_data["parent_tags"] = [p.strip() for p in parents]

                    tag_notes[md_file] = tag_data

            except:
                pass

        return tag_notes

    def _find_tag_note(self, tag: str) -> Optional[Path]:
        """Find tag note file for a given tag"""
        for md_file in self.vault_path.rglob("*.md"):
            if any(part in md_file.parts for part in ["00-Inbox", "_system", ".obsidian"]):
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read(500)

                    if 'type: tag-note' not in content:
                        continue

                    tag_match = re.search(r'^tag:\s*(.+)$', content, re.MULTILINE)
                    if tag_match and tag_match.group(1).strip() == tag:
                        return md_file
            except:
                pass

        return None

    def _find_all_areas(self) -> Dict[str, Dict]:
        """Find all knowledge areas with statistics"""
        areas = defaultdict(lambda: {"entity_count": 0, "time_hours": 0})

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

                    if root_match:
                        area = root_match.group(1)
                        areas[area]["entity_count"] += 1

                        if time_match:
                            areas[area]["time_hours"] += float(time_match.group(1)) / 60

            except:
                pass

        # Round time
        for area in areas:
            areas[area]["time_hours"] = round(areas[area]["time_hours"], 1)

        return dict(areas)

    def _calculate_radial_layout(self, count: int, radius: int = 500) -> List[Tuple[int, int]]:
        """Calculate radial layout positions"""
        positions = []

        for i in range(count):
            angle = (2 * math.pi * i) / count
            x = int(radius * math.cos(angle))
            y = int(radius * math.sin(angle))
            positions.append((x, y))

        return positions

    def _calculate_circular_layout(self, count: int, radius: int = 500) -> List[Tuple[int, int]]:
        """Calculate circular layout positions (same as radial)"""
        return self._calculate_radial_layout(count, radius)

    def _calculate_node_size(self, conversations: int) -> int:
        """Calculate node size based on conversation count"""
        base_size = 150
        return base_size + min(conversations * 10, 300)

    def _get_depth_color(self, depth: int) -> str:
        """Get color code for depth level"""
        # Obsidian canvas colors: 0=default, 1=red, 2=orange, 3=yellow, 4=green, 5=cyan, 6=purple
        color_map = {
            1: "1",  # Red (root)
            2: "2",  # Orange
            3: "3",  # Yellow
            4: "4",  # Green
            5: "5",  # Cyan
        }
        return color_map.get(depth, "6")  # Purple for 6+


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate Obsidian canvas files")
    parser.add_argument("--vault", type=str, default="C:/obsidian-memory-vault",
                       help="Path to vault")
    parser.add_argument("--area", type=str,
                       help="Generate canvas for specific area")
    parser.add_argument("--conversation", type=str,
                       help="Generate canvas for specific conversation file")
    parser.add_argument("--global", dest="global_canvas", action="store_true",
                       help="Generate global canvas")

    args = parser.parse_args()

    generator = CanvasGenerator(Path(args.vault))

    if args.area:
        canvas = generator.generate_area_canvas(args.area)
        print(f"\n[OK] Area Canvas Generated: {args.area}")
        print(f"   Nodes: {len(canvas.get('nodes', []))}")
        print(f"   Edges: {len(canvas.get('edges', []))}")

    elif args.conversation:
        conv_file = Path(args.conversation)
        canvas = generator.generate_conversation_canvas(conv_file)
        print(f"\n[OK] Conversation Canvas Generated")
        print(f"   Nodes: {len(canvas.get('nodes', []))}")
        print(f"   Edges: {len(canvas.get('edges', []))}")

    elif args.global_canvas:
        canvas = generator.generate_global_canvas()
        print(f"\n[OK] Global Canvas Generated")
        print(f"   Nodes: {len(canvas.get('nodes', []))}")

    else:
        print("\n[INFO] Canvas Generator")
        print("   Use --area, --conversation, or --global to generate canvas")

    print()


if __name__ == "__main__":
    main()
