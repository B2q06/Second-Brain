#!/usr/bin/env python3
"""
Ollama Embedding Script for Smart Connections
Embeds new notes using nomic-embed-text:latest model via Ollama API
"""

import requests
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class OllamaEmbedder:
    """Embeds markdown notes using Ollama nomic-embed-text model"""

    def __init__(self, vault_path: str, ollama_url: str = "http://localhost:11434"):
        self.vault_path = Path(vault_path)
        self.ollama_url = ollama_url
        self.model = "nomic-embed-text:latest"
        self.smart_env_path = self.vault_path / ".smart-env" / "multi"

        # Chunking parameters
        self.min_chunk_size = 200
        self.max_chunk_size = 500
        self.overlap = 50

        # Ensure output directory exists
        self.smart_env_path.mkdir(parents=True, exist_ok=True)

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding vector from Ollama API"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()["embedding"]
            else:
                print(f"❌ Ollama error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"❌ Failed to get embedding: {e}")
            return None

    def chunk_text(self, text: str, file_path: str) -> List[Dict]:
        """
        Chunk text into overlapping segments for embedding

        Handles:
        - Tiny text (tags, short notes): Single chunk
        - Medium text: 2-3 chunks
        - Large text: Multiple chunks with overlap
        """
        text = text.strip()

        # For tiny text (tags, short notes), embed as-is
        if len(text) <= self.max_chunk_size:
            return [{
                "text": text,
                "start": 0,
                "end": len(text),
                "lines": [1, text.count('\n') + 1]
            }]

        # For larger text, create overlapping chunks
        chunks = []
        lines = text.split('\n')
        current_chunk = []
        current_size = 0
        line_start = 0

        for i, line in enumerate(lines, 1):
            line_len = len(line) + 1  # +1 for newline

            if current_size + line_len > self.max_chunk_size and current_chunk:
                # Save current chunk
                chunk_text = '\n'.join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "start": len('\n'.join(lines[:line_start])),
                    "end": len('\n'.join(lines[:i-1])),
                    "lines": [line_start + 1, i]
                })

                # Start new chunk with overlap
                overlap_lines = []
                overlap_size = 0
                for j in range(len(current_chunk) - 1, -1, -1):
                    overlap_size += len(current_chunk[j]) + 1
                    if overlap_size >= self.overlap:
                        break
                    overlap_lines.insert(0, current_chunk[j])

                current_chunk = overlap_lines + [line]
                current_size = sum(len(l) + 1 for l in current_chunk)
                line_start = i - len(overlap_lines) - 1
            else:
                current_chunk.append(line)
                current_size += line_len

        # Add final chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "start": len('\n'.join(lines[:line_start])),
                "end": len(text),
                "lines": [line_start + 1, len(lines) + 1]
            })

        return chunks

    def generate_key(self, file_path: str, chunk_text: str = None) -> str:
        """Generate Smart Connections compatible key"""
        # Use file path as base
        relative_path = str(file_path).replace(str(self.vault_path), "").lstrip("/\\")

        if chunk_text:
            # For chunks, include text hash
            text_hash = hashlib.md5(chunk_text.encode()).hexdigest()[:8]
            return f"{relative_path}#{text_hash}"

        return relative_path

    def save_embedding(self, file_path: Path, chunk: Dict, embedding: List[float]):
        """Save embedding in Smart Connections .ajson format"""

        key = self.generate_key(file_path, chunk["text"])

        # Generate hash for filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        output_file = self.smart_env_path / f"{key_hash}.ajson"

        # Smart Connections format
        data = {
            key: {
                "path": str(file_path.relative_to(self.vault_path)).replace("\\", "/"),
                "text": chunk["text"],
                "key": key,
                "lines": chunk["lines"],
                "embeddings": {
                    "nomic-embed-text:latest": {
                        "vec": embedding,
                        "model_key": "nomic-embed-text:latest"
                    }
                },
                "metadata": {
                    "mtime": int(file_path.stat().st_mtime),
                    "size": file_path.stat().st_size,
                    "embedded_at": datetime.now().isoformat()
                }
            }
        }

        # Save in .ajson format (JSON without outer braces, comma-separated)
        # Smart Connections expects: "key": {data},
        with open(output_file, 'w', encoding='utf-8') as f:
            content = json.dumps(data, indent=2)
            # Remove outer braces and add comma
            content = content[1:-1].strip() + ","
            f.write(content)

        return output_file

    def embed_file(self, file_path: Path, force: bool = False) -> int:
        """
        Embed a single markdown file

        Returns:
            Number of chunks embedded
        """
        # Check if already embedded (unless force)
        if not force:
            key = self.generate_key(file_path)
            key_hash = hashlib.md5(key.encode()).hexdigest()
            existing = self.smart_env_path / f"{key_hash}.ajson"

            if existing.exists():
                # Check if file modified since embedding
                existing_mtime = json.loads("{" + existing.read_text().rstrip(",") + "}")
                existing_data = list(existing_mtime.values())[0]
                file_mtime = int(file_path.stat().st_mtime)

                if existing_data.get("metadata", {}).get("mtime", 0) >= file_mtime:
                    print(f"[SKIP] Skipping {file_path.name} (already embedded)")
                    return 0

        print(f"\n[*] Processing: {file_path.name}")

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Failed to read file: {e}")
            return 0

        # Chunk text
        chunks = self.chunk_text(content, file_path)
        print(f"   Chunks: {len(chunks)}")

        embedded_count = 0

        for i, chunk in enumerate(chunks, 1):
            # Get embedding
            embedding = self.get_embedding(chunk["text"])

            if embedding:
                # Save embedding
                output_file = self.save_embedding(file_path, chunk, embedding)
                print(f"   [OK] Chunk {i}/{len(chunks)} embedded ({len(chunk['text'])} chars) -> {output_file.name}")
                embedded_count += 1
            else:
                print(f"   [X] Chunk {i}/{len(chunks)} failed")

        return embedded_count

    def embed_folder(self, folder: Path, pattern: str = "*.md", recursive: bool = True, force: bool = False) -> Dict:
        """
        Embed all markdown files in a folder

        Returns:
            Statistics dict
        """
        print(f"\n{'='*60}")
        print(f"Embedding folder: {folder}")
        print(f"{'='*60}\n")

        stats = {
            "files_processed": 0,
            "files_skipped": 0,
            "files_failed": 0,
            "chunks_embedded": 0
        }

        # Find all markdown files
        if recursive:
            files = list(folder.rglob(pattern))
        else:
            files = list(folder.glob(pattern))

        print(f"Found {len(files)} files\n")

        for file_path in files:
            try:
                chunks = self.embed_file(file_path, force=force)

                if chunks > 0:
                    stats["files_processed"] += 1
                    stats["chunks_embedded"] += chunks
                elif chunks == 0:
                    stats["files_skipped"] += 1

            except Exception as e:
                print(f"❌ Error processing {file_path.name}: {e}")
                stats["files_failed"] += 1

        return stats


def main():
    parser = argparse.ArgumentParser(
        description="Embed markdown notes using Ollama nomic-embed-text model"
    )
    parser.add_argument(
        "--vault",
        default="C:/obsidian-memory-vault",
        help="Path to Obsidian vault (default: C:/obsidian-memory-vault)"
    )
    parser.add_argument(
        "--folder",
        help="Folder to embed (relative to vault, e.g., '00-Inbox/processed')"
    )
    parser.add_argument(
        "--file",
        help="Single file to embed (relative to vault)"
    )
    parser.add_argument(
        "--ollama-url",
        default="http://localhost:11434",
        help="Ollama API URL (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-embedding even if already embedded"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        default=True,
        help="Recursively embed subfolders (default: True)"
    )

    args = parser.parse_args()

    vault_path = Path(args.vault)

    if not vault_path.exists():
        print(f"❌ Vault not found: {vault_path}")
        return 1

    embedder = OllamaEmbedder(vault_path, args.ollama_url)

    # Test Ollama connection
    print("Testing Ollama connection...")
    test_embedding = embedder.get_embedding("test")
    if not test_embedding:
        print("❌ Cannot connect to Ollama. Ensure it's running at http://localhost:11434")
        return 1
    print(f"[OK] Connected to Ollama (embedding dimension: {len(test_embedding)})\n")

    # Embed file or folder
    if args.file:
        file_path = vault_path / args.file
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return 1

        chunks = embedder.embed_file(file_path, force=args.force)

        print(f"\n{'='*60}")
        print(f"[SUCCESS] Embedded {chunks} chunk(s)")
        print(f"{'='*60}")

    elif args.folder:
        folder_path = vault_path / args.folder
        if not folder_path.exists():
            print(f"❌ Folder not found: {folder_path}")
            return 1

        stats = embedder.embed_folder(folder_path, recursive=args.recursive, force=args.force)

        print(f"\n{'='*60}")
        print(f"EMBEDDING COMPLETE")
        print(f"{'='*60}")
        print(f"Files processed: {stats['files_processed']}")
        print(f"Files skipped:   {stats['files_skipped']}")
        print(f"Files failed:    {stats['files_failed']}")
        print(f"Chunks embedded: {stats['chunks_embedded']}")
        print(f"{'='*60}\n")

    else:
        # Default: embed entire vault
        stats = embedder.embed_folder(vault_path, recursive=True, force=args.force)

        print(f"\n{'='*60}")
        print(f"FULL VAULT EMBEDDING COMPLETE")
        print(f"{'='*60}")
        print(f"Files processed: {stats['files_processed']}")
        print(f"Files skipped:   {stats['files_skipped']}")
        print(f"Files failed:    {stats['files_failed']}")
        print(f"Chunks embedded: {stats['chunks_embedded']}")
        print(f"{'='*60}\n")

    return 0


if __name__ == "__main__":
    exit(main())
