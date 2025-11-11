---
type: architecture
title: Complete Processing Pipeline Architecture
version: 2.0
created: 2025-11-09
status: production-ready
---

# Complete Processing Pipeline Architecture

## System Overview

**Goal**: Fully automated headless conversation processing with human-in-the-loop tag approval

**Components**:
1. File Watcher (Python) - Detects new conversations
2. Processing Pipeline Agent (Claude Code CLI - Headless)
3. Neo4j MCP Server - Knowledge graph storage
4. Smart Connections MCP Server - Semantic search in vault
5. Terminal UI - Tag approval interface

---

## MCP Server Configuration (Headless CLI)

### Current Status
```bash
claude mcp list
```

**Active Servers**:
- ✅ `neo4j`: uvx mcp-neo4j-memory@0.4.2 (Connected)
- ✅ `smart-connections`: Python server at mcp/smart-connections-mcp (Connected)
- ❌ `graphiti`: Not needed (can be removed)

**Location**: `~/.config/claude/mcp_config.json` (or Claude Code's global config)

### Neo4j MCP Server
- **Purpose**: Store entities, relationships, observations
- **Connection**: neo4j://127.0.0.1:7687
- **Schema**: Entity, Episodic, Memory, Community nodes
- **Tools Available**:
  - create_entities
  - create_relations
  - search_memories (semantic search in graph)
  - find_memories_by_name
  - add_observations
  - read_graph

### Smart Connections MCP Server
- **Purpose**: Semantic search across Obsidian vault
- **Embeddings**: TaylorAI/bge-micro-v2 (local model)
- **Storage**: .smart-env/multi/*.ajson files
- **Current Status**: 52 files already embedded
- **Tools Available**:
  - semantic_search
  - find_related
  - get_context_blocks

---

## Auto-Embedding System

### How Smart Connections Works

1. **Automatic Embedding Trigger**:
   - When new `.md` files are created in vault
   - Obsidian plugin watches for changes
   - Embeddings generated in background

2. **For Headless Operation** (No Obsidian Open):

   **Option A: Use Smart Connections Plugin in Obsidian**
   - Keep Obsidian open in background
   - Plugin auto-embeds new notes within minutes
   - Most reliable for production use

   **Option B: Manual Embedding Script** (Create this):
   ```python
   # scripts/embed_notes.py
   from sentence_transformers import SentenceTransformer
   import json
   from pathlib import Path

   model = SentenceTransformer('TaylorAI/bge-micro-v2')

   def embed_file(file_path):
       with open(file_path, 'r', encoding='utf-8') as f:
           content = f.read()

       # Generate embedding
       vector = model.encode(content).tolist()

       # Save to .smart-env/multi/
       # Follow .ajson format
       ...
   ```

   **Option C: Trigger Embedding via MCP** (Best for headless):
   - Processing agent creates note
   - Waits 5 seconds
   - Calls Smart Connections to re-index vault
   - Embeddings generated automatically

### Recommended Approach: **Option C**

Modify Smart Connections MCP server to add a `reindex_vault()` tool:

```python
@mcp.tool()
async def reindex_vault():
    """Force re-indexing of vault to generate embeddings for new files"""
    # Clear embeddings_loaded flag
    # Reload all files
    # Generate embeddings for new files
    ...
```

Then processing agent calls this after creating notes in Stage 6.

---

## Complete Processing Workflow

### Stage 0: File Detection (File Watcher)
```
1. Detect unprocessed_*.md in raw-conversations/
2. Add to processing-queue.md
3. Spawn processing-pipeline-agent with:
   claude \
     --mcp-config neo4j,smart-connections \
     --agent processing-pipeline-agent \
     "Process queue"
```

---

### Stage 1: Entity Extraction (Neo4j)

**Input**: Raw conversation file
**Output**: Entities in Neo4j graph

```python
# Pseudo-code for agent

# Read conversation
conversation = Read("00-Inbox/raw-conversations/processing_*.md")

# Extract entities using LLM analysis
entities = extract_entities(conversation)
# Example: ["FastAPI", "PostgreSQL", "Docker", "Python"]

# Store in Neo4j
for entity in entities:
    mcp__neo4j__create_entities({
        entities: [{
            name: entity.name,
            type: entity.type,  # technology, skill, project, concept
            observations: entity.facts
        }]
    })

# Create relationships
mcp__neo4j__create_relations({
    relations: [
        {source: "FastAPI", target: "Python", relationType: "BUILT_WITH"},
        {source: "FastAPI", target: "PostgreSQL", relationType: "INTEGRATES_WITH"}
    ]
})
```

---

### Stage 2: Tag Assignment (Neo4j + Tag Taxonomy)

**Input**: Extracted entities
**Output**: Proposed tags (existing + new)

```python
# Load tag taxonomy
tag_taxonomy = Read("_system/tag-taxonomy.md")
canonical_tags = parse_taxonomy(tag_taxonomy)

proposed_tags = []
new_tag_proposals = []

for entity in entities:
    # Check exact match
    if entity.name in canonical_tags:
        proposed_tags.append(canonical_tags[entity.name])
        continue

    # Check aliases
    alias_match = find_alias(entity.name, canonical_tags)
    if alias_match:
        proposed_tags.append(alias_match)
        continue

    # Semantic similarity search in Neo4j
    similar = mcp__neo4j__search_memories({
        query: entity.name,
        limit: 5
    })

    # Calculate similarity scores
    best_match = similar[0] if similar else None

    if best_match and best_match.similarity > 0.85:
        # High confidence - use existing tag
        proposed_tags.append(best_match.name)

    elif best_match and best_match.similarity > 0.60:
        # Medium confidence - propose for human review
        new_tag_proposals.append({
            proposed_name: entity.name,
            similar_tags: [
                {name: best_match.name, similarity: best_match.similarity}
            ],
            confidence: best_match.similarity,
            context: entity.observations,
            recommendation: "REVIEW"  # Human must decide
        })

    else:
        # Low confidence - definitely new tag
        new_tag_proposals.append({
            proposed_name: entity.name,
            similar_tags: [],
            confidence: 0.0,
            context: entity.observations,
            recommendation: "NEW_TAG"
        })

# Write new tag proposals to queue
if new_tag_proposals:
    append_to_tag_review_queue(new_tag_proposals)
```

---

### Stage 2.5: **HUMAN TAG APPROVAL** (Terminal UI)

**This is the critical human-in-the-loop step**

```python
# Terminal UI appears DURING processing
# Agent BLOCKS until user responds

if new_tag_proposals:
    print("\n" + "="*60)
    print("TAG APPROVAL REQUIRED")
    print("="*60 + "\n")

    approved_tags = []

    for i, proposal in enumerate(new_tag_proposals, 1):
        print(f"\n[{i}/{len(new_tag_proposals)}] New Tag Proposal")
        print(f"Proposed Tag: '{proposal.proposed_name}'")
        print(f"Confidence: {proposal.confidence:.2f}")
        print(f"Context: {proposal.context}")

        if proposal.similar_tags:
            print("\nSimilar Existing Tags:")
            for tag in proposal.similar_tags:
                print(f"  - {tag.name} (similarity: {tag.similarity:.2f})")

        print("\nOptions:")
        print("  [A] Approve as new tag")
        print("  [M] Merge into existing tag")
        print("  [R] Reject (use existing)")
        print("  [S] Skip for now (manual review later)")

        choice = input("\nYour choice [A/M/R/S]: ").strip().upper()

        if choice == 'A':
            approved_tags.append(proposal.proposed_name)
            # Add to tag-taxonomy.md immediately
            add_tag_to_taxonomy(proposal.proposed_name)

        elif choice == 'M':
            print("\nAvailable tags to merge into:")
            for j, tag in enumerate(proposal.similar_tags, 1):
                print(f"  [{j}] {tag.name}")
            merge_choice = int(input("Select tag number: "))
            merged_tag = proposal.similar_tags[merge_choice - 1].name
            approved_tags.append(merged_tag)
            # Add as alias
            add_alias_to_taxonomy(proposal.proposed_name, merged_tag)

        elif choice == 'R':
            # Use closest existing tag
            if proposal.similar_tags:
                approved_tags.append(proposal.similar_tags[0].name)

        elif choice == 'S':
            # Add to tag-review-queue.md for manual review
            add_to_review_queue(proposal)
            # Use closest match for now
            if proposal.similar_tags:
                approved_tags.append(proposal.similar_tags[0].name)

    # Combine approved tags with existing tags
    final_tags = proposed_tags + approved_tags
```

**Alternative: Batch Mode**

```python
# Show all proposals first, then ask for approval
display_all_proposals(new_tag_proposals)

# User can:
# - Approve all (if confident)
# - Review individually
# - Defer all to manual queue
```

---

### Stage 3: Area Matching (8-Layer Taxonomy)

**Input**: Finalized tags
**Output**: Area path (up to 8 layers deep)

```python
# Load area taxonomy
area_taxonomy = Read("_system/area-taxonomy.json")

# For each tag, find its area path
area_paths = []

for tag in final_tags:
    # Search for tag in area taxonomy
    area = find_area_for_tag(tag, area_taxonomy)

    if area:
        area_paths.append(area.path)  # e.g., "Technology > Programming > Python > Web Development"
    else:
        # Tag has no area - propose new area
        propose_new_area(tag, new_areas_queue)

# Determine primary area (most specific)
primary_area = get_most_specific_area(area_paths)

# Example: If tags include [python, fastapi, backend, web-dev]
# Areas might be:
#   - Technology > Programming > Python (3 layers)
#   - Technology > Programming > Python > Web Development (4 layers)
#   - Technology > Programming > Backend (3 layers)
#
# Primary = "Technology > Programming > Python > Web Development" (deepest)

# Secondary areas (other significant areas)
secondary_areas = [a for a in area_paths if a != primary_area]
```

**Area Taxonomy Structure** (JSON):
```json
{
  "root_areas": [
    {
      "id": "technology",
      "name": "Technology",
      "level": 0,
      "tags": ["technology", "tech"],
      "children": [
        {
          "id": "tech_programming",
          "name": "Programming",
          "level": 1,
          "tags": ["programming", "coding"],
          "children": [
            {
              "id": "tech_prog_python",
              "name": "Python",
              "level": 2,
              "tags": ["python", "py"],
              "children": [
                {
                  "id": "tech_prog_python_web",
                  "name": "Web Development",
                  "level": 3,
                  "tags": ["fastapi", "django", "flask", "web-dev"],
                  "children": []
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

**Tag-to-Area Mapping Logic**:
1. Search for tag in all area nodes
2. Return the **deepest matching area**
3. If multiple matches at same depth, choose most relevant (by other tags)
4. If no match, propose new area to `new-areas-queue.md`

---

### Stage 4: Time Estimation

```python
# Parse timestamps from conversation
timestamps = extract_timestamps(conversation)

# Calculate active time (30-min idle threshold)
active_time = calculate_active_time(timestamps, idle_threshold=30)

# Store in metadata
duration_minutes = active_time
```

---

### Stage 5: Novelty Detection

```python
# Search Neo4j for similar conversations
similar_conversations = mcp__neo4j__search_memories({
    query: conversation_summary,
    limit: 10
})

if similar_conversations and max(similar_conversations.similarity) > 0.80:
    novelty_score = 0.2  # Low - similar content exists
elif similar_conversations and max(similar_conversations.similarity) > 0.50:
    novelty_score = 0.6  # Medium
else:
    novelty_score = 1.0  # High - new knowledge

# If novelty > 0.7, may trigger new area proposal
```

---

### Stage 6: Note Creation

```python
# Generate final note
note_content = f"""---
type: conversation
title: "{generated_title}"
created: {conversation_date}
session_id: {session_id}
source: claude-code-cli

# PROCESSING STATUS
processing:
  status: processed
  processed_date: {today}
  ai_tagged: true
  entities_extracted: true
  graph_synced: true

# TAGS
tags: {final_tags}

# AREAS
areas:
  primary: "{primary_area}"
  secondary: {secondary_areas}

# TEMPORAL
date: {date}
duration_minutes: {duration_minutes}

# GRAPH
graph:
  entities_created: {len(entities)}
  relationships_created: {len(relationships)}
  neo4j_synced: true

# NOVELTY
novelty_score: {novelty_score}
---

# {title}

## Summary
{ai_generated_summary}

## Key Outcomes
- {outcome_1}
- {outcome_2}

## Conversation
{full_conversation_content}
"""

# Save to appropriate area folder
folder_path = primary_area.replace(" > ", "/")
Write(f"{folder_path}/{filename}.md", note_content)

# Trigger re-embedding (if using MCP reindex)
mcp__smart_connections__reindex_vault()
```

---

### Stage 7: Node Updates (Bidirectional Linking)

```python
# Link conversation to entities in Neo4j
conversation_id = generate_id(conversation)

# Create episode node
mcp__neo4j__create_entities({
    entities: [{
        name: conversation_id,
        type: "episode",
        observations: [summary, f"Duration: {duration_minutes} min"]
    }]
})

# Link episode to entities
for entity in entities:
    mcp__neo4j__create_relations({
        relations: [{
            source: conversation_id,
            target: entity.name,
            relationType: "DISCUSSES"
        }]
    })

# Find related notes using Smart Connections
related_notes = mcp__smart_connections__semantic_search({
    query: summary,
    limit: 5,
    min_similarity: 0.6
})

# Update related notes with backlinks (optional)
for note in related_notes:
    if note.similarity > 0.7:
        append_backlink_to_note(note.path, conversation_id)
```

---

### Stage 8: Finalization

```python
# Rename file
rename("processing_*.md", "processed_*.md")

# Update queue
update_queue_status(file, "completed", {
    entities_created: len(entities),
    tags_assigned: len(final_tags),
    primary_area: primary_area,
    duration: duration_minutes,
    novelty_score: novelty_score
})

# Log completion
print(f"✅ Processed: {filename}")
print(f"   Entities: {len(entities)}")
print(f"   Tags: {', '.join(final_tags)}")
print(f"   Area: {primary_area}")
```

---

## Edge Cases & Robustness

### 1. **Empty or Malformed Conversation Files**
**Edge Case**: File exists but has no content or broken frontmatter
**Solution**:
```python
try:
    content = Read(file_path)
    if len(content.strip()) < 50:
        raise ValueError("File too short")
    validate_frontmatter(content)
except Exception as e:
    log_error(file, "Malformed file", e)
    move_to_errors_folder(file)
    continue  # Skip to next file
```

### 2. **Neo4j Connection Lost During Processing**
**Edge Case**: Database goes offline mid-processing
**Solution**:
```python
def safe_neo4j_call(func, *args, retries=3):
    for attempt in range(retries):
        try:
            return func(*args)
        except ConnectionError:
            if attempt < retries - 1:
                sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                # Fall back to local storage
                save_to_pending_sync_queue(*args)
                return None
```

### 3. **Duplicate Conversations**
**Edge Case**: Same conversation processed twice
**Solution**:
```python
# Check for duplicates before processing
existing = mcp__neo4j__search_memories({
    query: conversation_title,
    limit: 1
})

if existing and existing[0].similarity > 0.95:
    print(f"⚠️  Duplicate detected: {existing[0].name}")
    choice = input("Continue anyway? [y/N]: ")
    if choice.lower() != 'y':
        skip_file()
```

### 4. **User Abandons Tag Approval (Ctrl+C)**
**Edge Case**: User interrupts during terminal UI
**Solution**:
```python
import signal

def signal_handler(sig, frame):
    print("\n\n⚠️  Processing interrupted!")
    print("Saving progress...")

    # Save partial state
    save_checkpoint({
        file: current_file,
        stage: 2,
        approved_tags: approved_tags,
        pending_tags: remaining_proposals
    })

    # Move file back to unprocessed
    rename(current_file, current_file.replace("processing_", "unprocessed_"))

    print("✅ State saved. Run again to resume.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
```

### 5. **Tag Conflicts (Same Name, Different Meaning)**
**Edge Case**: "Python" (language) vs "Python" (snake)
**Solution**:
```python
# Use context to disambiguate
if "programming" in entity.context or "code" in entity.context:
    tag = "python_language"
else:
    # Ask user
    print(f"Ambiguous tag: {entity.name}")
    print(f"Context: {entity.context}")
    print("1. Python (programming language)")
    print("2. Python (reptile)")
    choice = input("Select meaning [1/2]: ")
```

### 6. **Area Taxonomy Becomes Too Deep (> 8 Levels)**
**Edge Case**: Auto-discovery creates 10-layer hierarchy
**Solution**:
```python
MAX_DEPTH = 8

def add_area_to_taxonomy(area_path):
    levels = area_path.split(" > ")

    if len(levels) > MAX_DEPTH:
        print(f"⚠️  Area too deep: {area_path} ({len(levels)} levels)")
        # Suggest merging
        suggest_merge(levels)
        return False
```

### 7. **No Matching Area for Tags**
**Edge Case**: Tags exist but no area contains them
**Solution**:
```python
# Propose new area automatically
if not area_found:
    propose_new_area({
        tags: unmatched_tags,
        suggested_parent: infer_parent_area(tags),
        confidence: 0.7,
        reason: "Tag cluster with no matching area"
    })

    # Temporarily assign to root or closest parent
    temporary_area = find_closest_parent_area(tags)
```

### 8. **Circular Tag References**
**Edge Case**: TagA is alias of TagB, TagB is alias of TagA
**Solution**:
```python
def validate_tag_taxonomy():
    """Run this check before processing"""
    for tag, data in taxonomy.items():
        for alias in data.aliases:
            if alias in taxonomy and tag in taxonomy[alias].aliases:
                raise ValueError(f"Circular reference: {tag} <-> {alias}")
```

### 9. **Smart Connections Embeddings Out of Sync**
**Edge Case**: Note created but embedding not generated
**Solution**:
```python
# Wait for embedding before proceeding to Stage 7
max_wait = 30  # seconds
waited = 0

while waited < max_wait:
    results = mcp__smart_connections__semantic_search({
        query: note_title,
        limit: 1
    })

    if results and results[0].path == new_note_path:
        break  # Embedding found

    sleep(2)
    waited += 2

if waited >= max_wait:
    print("⚠️  Embedding timeout - proceeding anyway")
```

### 10. **Multiple Files Processed Simultaneously**
**Edge Case**: File watcher spawns multiple agents at once
**Solution**:
```python
# Use file locking
import fcntl

def acquire_processing_lock(file_path):
    lock_file = f"{file_path}.lock"

    if os.path.exists(lock_file):
        print(f"⚠️  File already being processed: {file_path}")
        return False

    # Create lock
    with open(lock_file, 'w') as f:
        f.write(str(os.getpid()))

    return True

def release_processing_lock(file_path):
    lock_file = f"{file_path}.lock"
    if os.path.exists(lock_file):
        os.remove(lock_file)
```

### 11. **Tag Taxonomy File Corrupted**
**Edge Case**: YAML parsing fails due to syntax error
**Solution**:
```python
# Always validate before writing
def safe_update_taxonomy(new_tag):
    try:
        # Read and validate
        taxonomy = parse_yaml(Read("tag-taxonomy.md"))

        # Make backup
        backup_path = "tag-taxonomy.backup.md"
        Write(backup_path, Read("tag-taxonomy.md"))

        # Add new tag
        taxonomy[new_tag.name] = new_tag.data

        # Write and validate again
        Write("tag-taxonomy.md", yaml.dump(taxonomy))
        parse_yaml(Read("tag-taxonomy.md"))  # Validate

        # Success - remove backup
        os.remove(backup_path)

    except Exception as e:
        # Restore from backup
        if os.path.exists(backup_path):
            Write("tag-taxonomy.md", Read(backup_path))
        raise
```

### 12. **User Provides Invalid Input in Terminal UI**
**Edge Case**: Types "X" instead of A/M/R/S
**Solution**:
```python
def get_user_choice(prompt, valid_options):
    while True:
        choice = input(prompt).strip().upper()

        if choice in valid_options:
            return choice

        print(f"Invalid choice. Please enter one of: {', '.join(valid_options)}")
```

### 13. **Area Taxonomy JSON Schema Changes**
**Edge Case**: New version of system expects different structure
**Solution**:
```python
# Version migration
def migrate_area_taxonomy(taxonomy_data):
    current_version = taxonomy_data.get("version", "1.0")

    if current_version == "1.0":
        # Migrate to 2.0
        taxonomy_data = migrate_1_to_2(taxonomy_data)
        current_version = "2.0"

    return taxonomy_data
```

### 14. **Extremely Long Conversations (>100k tokens)**
**Edge Case**: Conversation too large for LLM context
**Solution**:
```python
MAX_CONVERSATION_LENGTH = 100000  # chars

if len(conversation) > MAX_CONVERSATION_LENGTH:
    print(f"⚠️  Large conversation detected: {len(conversation)} chars")

    # Process in chunks
    chunks = split_conversation_intelligently(conversation)

    all_entities = []
    for chunk in chunks:
        entities = extract_entities(chunk)
        all_entities.extend(entities)

    # Deduplicate entities
    unique_entities = deduplicate_by_similarity(all_entities)
```

### 15. **Network Timeout to MCP Servers**
**Edge Case**: MCP request hangs indefinitely
**Solution**:
```python
import asyncio

async def call_mcp_with_timeout(func, *args, timeout=30):
    try:
        return await asyncio.wait_for(func(*args), timeout=timeout)
    except asyncio.TimeoutError:
        print(f"⚠️  MCP call timed out after {timeout}s")
        return None
```

---

## Production Checklist

Before going live:

- [ ] All MCP servers connected (`claude mcp list`)
- [ ] Neo4j database running and accessible
- [ ] Smart Connections embeddings exist (52+ files)
- [ ] Tag taxonomy validated (no circular references)
- [ ] Area taxonomy validated (JSON parseable)
- [ ] Terminal UI tested with sample inputs
- [ ] File locking mechanism tested
- [ ] Error recovery tested (Ctrl+C handling)
- [ ] Backup strategy for taxonomies in place
- [ ] Logging configured for debugging
- [ ] Queue monitoring dashboard working

---

## Performance Optimizations

### Batch Processing
When processing 5+ files:
1. Extract entities from ALL files first
2. Batch tag proposals (show all at once)
3. Batch Neo4j writes (single transaction)
4. Parallel embedding generation

### Caching
- Cache tag taxonomy in memory
- Cache area taxonomy in memory
- Cache recent Neo4j entity searches
- Reuse embedding model instance

### Parallel Stages
- Stage 1 (entities) + Stage 4 (time) can run in parallel
- Stage 5 (novelty) + Stage 6 (note creation) can overlap
- Embedding generation asynchronous (non-blocking)

---

## Monitoring & Metrics

Track these metrics:
- Average processing time per file
- Tag approval rate (approved vs rejected)
- New areas discovered per week
- Entity count growth over time
- Graph density (connections per entity)
- Processing errors per day

Store in `_system/metrics.json`:
```json
{
  "total_processed": 127,
  "average_time_seconds": 45.3,
  "tag_approvals": {
    "approved": 89,
    "rejected": 12,
    "merged": 26
  },
  "areas_discovered": 15,
  "entities_in_graph": 1247,
  "last_updated": "2025-11-09T15:45:00Z"
}
```

---

**Version**: 2.0
**Last Updated**: 2025-11-09
**Status**: Production-Ready
