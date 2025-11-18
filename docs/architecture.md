# The Second Brain - System Architecture

> **Last Updated**: 2025-11-17
> **Version**: 1.2
> **Project Type**: Data Pipeline & Knowledge Management System
> **Architecture Pattern**: Event-Driven Pipeline with Hierarchical Data Organization

---

## Executive Summary

The Second Brain is an **automated AI-powered knowledge management system** that captures conversations from Claude Code, intelligently organizes them into a hierarchical Obsidian vault, and builds a semantic knowledge graph in Neo4j.

**Key Characteristics**:
- **Event-Driven**: File system events trigger processing pipelines
- **Agent-Based**: Claude Code agents perform intelligent processing
- **Data-Driven Taxonomy**: Knowledge structure emerges from actual content
- **Dual Storage**: Obsidian (primary) + Neo4j (experimental semantic layer)
- **Continuous Operation**: File watcher runs 24/7, processing happens on-demand

**Primary Use Cases**:
1. **Personal Knowledge Management**: Automatically capture and organize learning from AI conversations
2. **Brain Space Tracking**: Quantify knowledge growth and cognitive patterns over time
3. **Semantic Knowledge Discovery**: Explore relationships between concepts naturally
4. **Conversational Learning Archive**: Build a searchable, interconnected repository of insights

---

## Technology Stack

### Core Technologies

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Runtime** | Python | 3.13.5 | Automation scripts and file watching |
| **Knowledge Base** | Obsidian | Latest | Primary markdown storage and navigation |
| **Graph Database** | Neo4j | 5.x+ | Secondary semantic knowledge graph |
| **AI Orchestration** | Claude Code | Latest | Conversation extraction and processing agents |
| **Integration** | MCP (Model Context Protocol) | Latest | Claude ↔ Neo4j/Obsidian communication |

### Python Dependencies

```python
# Core Dependencies (requirements.txt)
watchdog>=3.0.0          # File system event monitoring

# Future/Optional Dependencies (commented in requirements.txt)
# graphiti-core>=0.1.0    # Graphiti knowledge graph integration
# neo4j>=5.13.0           # Direct Neo4j driver (uses MCP instead)
# python-frontmatter>=1.0.0
# rich>=13.0.0            # Terminal output formatting
```

### Obsidian Plugins

**Required Plugins**:
1. **Smart Connections** - Embeddings and semantic search
2. **Dataview** - Advanced queries and dynamic views

**Optional Plugins** (enhance experience):
- Canvas (for visual knowledge maps)
- Graph view (builtin - for relationship visualization)

### MCP Servers

```json
// Claude Desktop MCP Configuration
{
  "mcpServers": {
    "neo4j": {
      "command": "uvx",
      "args": ["mcp-neo4j-memory@0.4.2"],
      "env": {
        "NEO4J_URI": "neo4j://127.0.0.1:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "<password>"
      }
    },
    "smart-connections-mcp": {
      "command": "npx",
      "args": ["-y", "@your-smart-connections-package"]
    }
  }
}
```

---

## System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                         THE SECOND BRAIN                                │
│                     (Knowledge Management System)                       │
└────────────────────────────────────────────────────────────────────────┘

┌─ LAYER 1: USER INTERACTION ─────────────────────────────────────────────┐
│                                                                          │
│  👤 User                 →  Claude Code Session                         │
│     │                            │                                       │
│     │ "update memory"            │ triggers                             │
│     │                            ▼                                       │
│     │                    Memory Update Agent                            │
│     │                    (extracts conversation)                        │
│     └────────────────────────────┬─────────────────────────────────────│
│                                  │                                       │
└──────────────────────────────────┼───────────────────────────────────────┘
                                   │
                                   ▼ creates file
┌─ LAYER 2: INTAKE & DETECTION ───────────────────────────────────────────┐
│                                                                          │
│  📁 00-Inbox/raw-conversations/                                         │
│      └── unprocessed_conversation_YYYYMMDD_HHmm_###.md                  │
│               │                                                          │
│               │ detected by                                             │
│               ▼                                                          │
│  🔍 File Watcher (Python - Continuous)                                  │
│      - Monitors for new unprocessed_*.md                                │
│      - Renames to processing_*.md                                       │
│      - Updates processing-queue.md                                      │
│      - Opens Claude Code terminal                                       │
│               │                                                          │
└───────────────┼──────────────────────────────────────────────────────────┘
                │
                ▼ user manually starts
┌─ LAYER 3: INTELLIGENT PROCESSING ───────────────────────────────────────┐
│                                                                          │
│  🤖 Processing Pipeline Agent (Claude Code)                             │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  STAGE 1: Entity Extraction (Neo4j MCP)                      │       │
│  │    - Extract entities: people, projects, skills, concepts    │       │
│  │    - Create nodes in Neo4j graph                             │       │
│  │    - Establish relationships                                 │       │
│  └─────────────────────┬─────────────────────────────────────────       │
│                        │                                                 │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  STAGE 2: Tag Assignment                                     │       │
│  │    - Analyze content against tag-taxonomy.md                 │       │
│  │    - Assign 3-7 relevant tags                                │       │
│  │    - Resolve tag aliases and hierarchies                     │       │
│  └─────────────────────┬─────────────────────────────────────────       │
│                        │                                                 │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  STAGE 3: Area Matching                                      │       │
│  │    - Match to existing area (area-taxonomy.json)             │       │
│  │    - OR propose new area (→ new-areas-queue.md)              │       │
│  │    - Resolve hierarchical folder path (2-8 levels)           │       │
│  └─────────────────────┬─────────────────────────────────────────       │
│                        │                                                 │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  STAGE 4: Time Estimation                                    │       │
│  │    - Parse conversation timestamps                           │       │
│  │    - Detect 30-minute idle gaps (exclude from time)          │       │
│  │    - Calculate active conversation duration                  │       │
│  └─────────────────────┬─────────────────────────────────────────       │
│                        │                                                 │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  STAGE 5: Novelty Detection                                  │       │
│  │    - Compare with existing tag note entries                  │       │
│  │    - Identify genuinely new insights vs. repetition          │       │
│  │    - Flag novel concepts for emphasis                        │       │
│  └─────────────────────┬─────────────────────────────────────────       │
│                        │                                                 │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  STAGE 6: Note Creation                                      │       │
│  │    - Create/update tag notes with monthly entries            │       │
│  │    - Store in hierarchical knowledge area folders            │       │
│  │    - Generate frontmatter with metadata                      │       │
│  │    - Add bidirectional wikilinks                             │       │
│  └─────────────────────┬─────────────────────────────────────────       │
│                        │                                                 │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  STAGE 7: Node Updates                                       │       │
│  │    - Update Neo4j entity properties                          │       │
│  │    - Create relationships between entities                   │       │
│  │    - Link conversation to entities                           │       │
│  └─────────────────────┬─────────────────────────────────────────       │
│                        │                                                 │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │  STAGE 8: Finalization                                       │       │
│  │    - Rename processing_* → processed_*                       │       │
│  │    - Update processing-queue.md (mark complete)              │       │
│  │    - Generate processing log                                 │       │
│  │    - Signal completion (agent_completion_signal.txt)         │       │
│  └─────────────────────┬─────────────────────────────────────────       │
│                        │                                                 │
└────────────────────────┼──────────────────────────────────────────────────┘
                         │
                         ▼ stores in
┌─ LAYER 4: KNOWLEDGE STORAGE ─────────────────────────────────────────────┐
│                                                                          │
│  📚 Obsidian Vault (PRIMARY)           🕸️ Neo4j Graph (SECONDARY)       │
│      - Hierarchical folders                - Experimental                │
│      - Tag notes with monthly entries      - Entity recognition          │
│      - Bidirectional wikilinks             - Relationship mapping        │
│      - Frontmatter metadata                - Semantic queries            │
│      - Smart Connections embeddings        - Graph analytics             │
│                                                                          │
│  Structure:                              Nodes:                          │
│  Technology/                             - Conversation                  │
│    Programming/                          - Project                       │
│      Python/                             - Skill                         │
│        FastAPI.md (tag note)             - Concept                       │
│                                          - Person                        │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Data Architecture

### Primary: Obsidian Vault (Markdown Files)

**Storage Model**: Hierarchical file system with flexible 2-8 level depth

**Tag Note Structure**:
```yaml
---
type: tag-note
tag: fastapi
tags: [fastapi]
canonical: FastAPI
taxonomy_path: Technology > Programming > Web Development > Frameworks
parent_tags: [python, web-framework, api]
root: Technology
depth: 4
created: 2025-11-07
last_updated: 2025-11-17
total_time_minutes: 127.5
conversation_count: 8
brain_space_score: 0.72
recency_score: 0.95
---

# FastAPI

> **Tag Note**: Living document tracking all discussions about FastAPI
> **Path**: Technology > Programming > Web Development > Frameworks

## Overview
High-performance modern Python web framework for building APIs.

## Related Tags
- [[Python]]
- [[API Design]]
- [[Pydantic]]
- [[Async Programming]]

## Knowledge Timeline

### November 2025

#### 2025-11-17 14:30
Discussed implementing OAuth2 authentication with FastAPI. Explored JWT tokens, dependency injection patterns, and security best practices for protecting API endpoints.

**Related**: [[OAuth2]], [[JWT]], [[Security]]
**Source**: [[conversation_20251117_1430_001]]

#### 2025-11-15 09:20
Built background task system using FastAPI's BackgroundTasks. Learned about async task execution without blocking request-response cycle.

**Related**: [[Async Programming]], [[Python]], [[Task Queues]]
**Source**: [[conversation_20251115_0920_001]]

...
```

**Knowledge Area Hierarchy**:
```
Technology/                    (Root - Level 1)
  Programming/                 (Level 2)
    Web Development/           (Level 3)
      Frameworks/              (Level 4)
        FastAPI.md             (Tag Note)
        Django.md
        Flask.md
```

### Secondary: Neo4j Knowledge Graph

**Node Types**:
- `Conversation`: Captured conversations
- `Project`: Projects being worked on
- `Skill`: Technical skills and competencies
- `Concept`: Abstract concepts and ideas
- `Entity`: Generic entity type

**Relationship Types**:
- `MENTIONED_IN`: Entity mentioned in conversation
- `RELATED_TO`: Entities related to each other
- `PART_OF`: Hierarchical relationships
- `LEARNED_FROM`: Learning relationships

**Schema** (dynamic, emergent):
```cypher
// Example Neo4j graph structure
(conversation:Conversation {
  id: "conv_20251117_001",
  date: "2025-11-17",
  duration_minutes: 45
})

(fastapi:Concept {
  name: "FastAPI",
  category: "framework",
  tag: "fastapi"
})

(python:Skill {
  name: "Python",
  category: "programming-language"
})

(conversation)-[:MENTIONED]->(fastapi)
(fastapi)-[:REQUIRES]->(python)
(fastapi)-[:RELATED_TO]->(oauth2)
```

**Note**: Neo4j schema is **data-driven** and **experimental**. The graph grows organically based on conversation content. Obsidian remains the primary, authoritative knowledge store.

---

## Pipeline Architecture

### Event-Driven Flow

**Trigger**: User says "update memory" in Claude session
**Detection**: File watcher polls `00-Inbox/raw-conversations/` every 3 seconds
**Processing**: Manual activation of processing pipeline agent
**Storage**: Dual storage (Obsidian + Neo4j)
**Completion**: Signal file written, log generated

### Batch Processing (Planned Feature - Not Yet Implemented)

⚠️ **Status**: Designed but not operational

**Trigger Conditions**:
- 5+ files detected simultaneously, OR
- Single file > 100,000 characters, OR
- Total batch > 500,000 characters

**Batch Advantages**:
- Global tag frequency analysis across all files
- Better knowledge area discovery (sees full context)
- Prevents fragmenting related knowledge
- More accurate tag clustering

**Implementation**: Exists in code but needs testing and activation

---

## Data Flow Patterns

### 1. Conversation Capture → Knowledge Integration

```
User Conversation
    ↓ [Memory Update Agent]
Raw Conversation File (unprocessed_*.md)
    ↓ [File Watcher detects]
Queue Entry Created (processing-queue.md)
    ↓ [User starts Pipeline Agent]
8-Stage Processing Pipeline
    ↓ [Extraction, Tagging, Matching, etc.]
├─→ Tag Notes Created/Updated (Obsidian)
└─→ Entities & Relationships (Neo4j)
```

### 2. Monthly Compression

```
Tag Note with 30+ Daily Entries
    ↓ [Monthly Consolidation Script - 1st of month]
Compress Previous Month's Entries
    ↓ [Keep last-day entry, summarize rest]
Condensed Tag Note
    ↓ [Add cross-tag references]
More Readable History + Better Performance
```

### 3. Knowledge Area Discovery

```
Processing Pipeline Assigns Tags
    ↓ [Tag clustering analysis]
Propose New Knowledge Area
    ↓ [Add to new-areas-queue.md]
User Reviews & Approves
    ↓ [Add to area-taxonomy.json]
Future Conversations Use New Area
    ↓ [Dynamic, data-driven growth]
Emergent Knowledge Structure
```

---

## Deployment Architecture

### Local Development Environment

**Operating System**: Windows (file watcher uses `wt.exe` for terminal)
**Vault Location**: `C:\Obsidian-memory-vault\`
**Python Environment**: System Python 3.13.5 (global installation)
**Neo4j**: Neo4j Desktop (local database at `neo4j://127.0.0.1:7687`)
**Claude Code**: Installed globally (`C:\` for system-level access)

### Process Management

**Continuous Processes**:
1. **File Watcher**: `python scripts/file_watcher.py` (runs 24/7)
   - No auto-restart mechanism (manual restart required)
   - Logs to stdout (terminal output)

**On-Demand Processes**:
1. **Processing Pipeline Agent**: Launched by file watcher, manually activated by user
2. **Monthly Consolidation**: Manual execution on 1st of month

**No Background Services**: All processes are foreground terminal applications

---

## Testing Strategy

### Current Testing

**Manual Testing**:
- Test conversation capture: Say "update memory" and verify file creation
- Test file watcher: Drop test file in raw-conversations folder
- Test processing: Manually activate pipeline agent and verify completion

**Health Checks**:
- `scripts/health_check.py`: Validates system configuration and file structure
- Checks: Directory structure, config validity, taxonomy integrity

### Planned Testing (To Be Implemented)

⚠️ **Needed**: Validation test in file watcher to ensure agent completed job
- **Current Status**: System seems bulletproof, but formal validation missing
- **Proposed**: Agent completion signal validation beyond just file existence check

---

## Configuration Management

### Primary Configuration (`_system/config.json`)

```json
{
  "version": "1.0",
  "system_name": "The Second Brain",

  "batch_processing": {
    "min_file_count": 5,
    "large_file_threshold_chars": 100000,
    "total_batch_threshold_chars": 500000
  },

  "time_tracking": {
    "idle_gap_minutes": 30,
    "default_session_minutes": 5
  },

  "knowledge_scoring": {
    "graph_percentage_weight": 0.70,
    "connection_density_weight": 0.15,
    "time_invested_weight": 0.15
  },

  "neo4j": {
    "uri": "neo4j://127.0.0.1:7687",
    "database": "neo4j"
  },

  "taxonomy": {
    "max_depth": 8,
    "flexible_depth": true,
    "discovery_mode": "data_driven"
  }
}
```

### Agent Protocols

**Location**: `_system/*.md`

**Memory Update Protocol**: Defines how to extract conversations
**Processing Pipeline Protocol**: Defines 8-stage processing flow

These protocols are loaded by Claude Code agents at runtime and define their behavior.

---

## Security Considerations

### Data Privacy
- **All data is local**: No cloud storage (Obsidian vault, Neo4j database)
- **No API calls**: Claude Code uses local Max subscription (not API)
- **MCP is local**: Neo4j MCP connects to localhost only

### Access Control
- **File system**: Standard OS-level permissions
- **Neo4j**: Password-protected (configured in Claude Desktop config)
- **Obsidian**: No built-in authentication (vault access = file access)

### Backup Strategy
**User Responsibility**: No automated backups implemented
**Recommended**:
- Git repository for vault (markdown files)
- Neo4j Desktop database export (manual)
- Cloud sync for Obsidian vault (optional: iCloud, Dropbox, etc.)

---

## Performance Characteristics

### Processing Times

| Operation | Duration | Notes |
|-----------|----------|-------|
| File detection | < 3 seconds | Polling interval |
| Pipeline processing | 2-5 minutes | Per conversation |
| Monthly consolidation | 1-10 minutes | Depends on tag note count |
| Brain space calculation | 30-60 seconds | For full vault |

### Scalability

**Current Limits**:
- **Tag notes**: Tested with ~100s of tags, should scale to 1000s
- **Conversations**: Tested with ~100s, should scale to 10,000s
- **Neo4j graph**: Tested with ~1,000 entities, should scale to 100,000s
- **Obsidian vault**: Tested with ~1,000 notes, should scale to 50,000+ (per Obsidian limits)

**Bottlenecks**:
- **Pipeline processing**: Single-threaded, processes one conversation at a time
- **File watcher**: Polls every 3 seconds (not instant detection)
- **Smart Connections**: Embedding generation can be slow for large batches

---

## Future Architecture Considerations

### Planned Enhancements

1. **Project Tracking Integration**
   - Track project progress across conversations
   - Link conversations to specific project phases
   - Calculate project time investment

2. **Media Integration**
   - Ingest images, audio, video from conversations
   - Store in Obsidian vault with metadata
   - Extract text from images (OCR)

3. **Handwritten Note Ingestion**
   - OCR for handwritten notes
   - Integration with tablet/stylus input
   - Preserve original scans with transcription

4. **Mass Information Collection**
   - Section for curated information (not conversation-based)
   - Bulk import from sources like articles, PDFs, videos
   - Different processing pipeline (less conversational context)

5. **Advanced Memory Metrics Dashboard**
   - "stats.fm for your brain"
   - Track knowledge growth over time
   - Visualize thinking evolution
   - Show project progress and cognitive patterns
   - Compare learning velocity across domains

---

*For operational procedures and daily usage, see `development-guide.md`
For data structures and schemas, see `data-models.md`*
