# Source Tree Analysis

> **Last Updated**: 2025-11-17
> **Project**: The Second Brain - Knowledge Management System

---

## Complete Directory Structure

```
C:\obsidian-memory-vault\
├── _system/                           # 🔧 System configuration and protocols
│   ├── config.json                    # Main system configuration
│   ├── area-taxonomy.json             # Dynamic knowledge area hierarchy (data-driven)
│   ├── tag-taxonomy.md                # Tag definitions and relationships
│   ├── processing-queue.md            # Active processing queue (updated by file watcher)
│   ├── new-areas-queue.md             # Proposed knowledge areas awaiting approval
│   ├── tag-review-queue.md            # Tag review workflow
│   ├── memory-update-protocol.md      # Memory update agent protocol
│   ├── processing-pipeline-protocol.md # Processing pipeline agent protocol
│   ├── COMPLETE_PROCESSING_ARCHITECTURE.md
│   ├── TROUBLESHOOTING.md             # System troubleshooting guide
│   ├── mcp-tools-reference.md         # MCP tools documentation
│   ├── tag-note-template.md           # Template for new tag notes
│   ├── brain-space-data.json          # Brain space metrics data
│   ├── brain-space-metrics.json       # Calculated brain metrics
│   ├── neo4j_entities_batch.json      # Neo4j entity batch data
│   ├── migration-report.md            # System migration tracking
│   ├── recovery-report.md             # Recovery operations log
│   ├── timeline.md                    # Project timeline
│   ├── ITERATION_COMPLETE.md          # Iteration completion markers
│   └── logs/                          # System logs (auto-generated)
│
├── scripts/                           # 🐍 Python automation scripts (27 files, ~9,725 LOC)
│   ├── file_watcher.py                # ⭐ ENTRY POINT: Continuous file monitoring
│   ├── monthly_consolidation.py       # 📅 Monthly: Compress tag note histories
│   ├── launch_claude_processor.py     # 🚀 Manual: Launch processing pipeline agent
│   │
│   ├── brain_space_calculator.py      # Brain metrics and growth analytics
│   ├── tag_note_manager.py            # Tag note creation and updates
│   ├── tag_path_resolver.py           # Taxonomy path resolution
│   ├── health_check.py                # System health validation
│   ├── config_validator.py            # Configuration validation
│   ├── frontmatter_parser.py          # Markdown frontmatter parsing
│   │
│   ├── batch_neo4j_helper.py          # Neo4j batch operations
│   ├── entity_prominence.py           # Entity prominence calculation
│   ├── similarity_matcher.py          # Semantic similarity matching
│   │
│   ├── backfill_tag_notes.py          # Backfill tag notes from existing data
│   ├── create_category_notes.py       # Create category hub notes
│   ├── generate_tag_notes_from_taxonomy.py # Generate tag notes from taxonomy
│   ├── add_hashtags_to_tag_notes.py   # Add hashtags to tag note frontmatter
│   ├── fix_tag_note_paths.py          # Fix tag note file paths
│   ├── migrate_tag_notes.py           # Migrate tag notes to new structure
│   ├── detect_new_roots.py            # Detect new taxonomy root areas
│   │
│   ├── canvas_generator.py            # Generate Obsidian canvas visualizations
│   ├── timeline_generator.py          # Generate project timelines
│   ├── export_brain_data.py           # Export brain data for analysis
│   │
│   ├── error_recovery.py              # Error recovery utilities
│   ├── extract_tag_knowledge.py       # Extract tag knowledge from conversations
│   ├── embed_notes_ollama.py          # Embed notes using Ollama (Smart Connections)
│   ├── tag_approval_ui.py             # Tag approval UI (experimental)
│   ├── test_agent_activation.py       # Test agent activation
│   ├── logger_setup.py                # Logging configuration
│   └── __init__.py                    # Package initialization
│
├── docs/                              # 📚 Documentation and logs
│   ├── pipeline_agent/                # Pipeline agent logs
│   │   ├── README.md                  # Pipeline agent documentation
│   │   └── processing_log_*.md        # Processing logs (auto-generated)
│   └── sprint-artifacts/              # Sprint artifacts (empty placeholder)
│
├── 00-Inbox/                          # 📥 Conversation intake and processing
│   ├── raw-conversations/             # ⭐ WATCH FOLDER: Unprocessed conversations
│   │   ├── unprocessed_*.md           # New conversations (created by memory-update)
│   │   ├── processing_*.md            # Currently being processed
│   │   └── processed_*.md             # Completed processing
│   └── processed/                     # Final processed conversation notes
│
├── Knowledge Area Folders/            # 🗂️ Dynamic knowledge organization
│   ├── Technology/                    # Tech knowledge (programming, frameworks, tools)
│   │   ├── Programming/
│   │   ├── Databases/
│   │   ├── Infrastructure/
│   │   └── [tag-notes.md]
│   ├── Language/                      # Language learning (Chinese, etc.)
│   │   ├── Chinese/
│   │   ├── Uncategorized/
│   │   └── [tag-notes.md]
│   ├── Culture/                       # Cultural knowledge
│   │   ├── Regions/
│   │   └── [tag-notes.md]
│   ├── History/                       # Historical knowledge
│   │   ├── Ancient/
│   │   └── [tag-notes.md]
│   ├── Projects/                      # Project work
│   │   ├── Data Science/
│   │   └── [project-notes.md]
│   ├── 10-Projects/                   # PARA method: Projects folder
│   ├── 20-Areas/                      # PARA method: Areas of responsibility
│   ├── 30-Resources/                  # PARA method: Reference materials
│   │   ├── knowledge/
│   │   └── skills/
│   ├── 40-Archive/                    # PARA method: Archived items
│   ├── 50-Meta/                       # PARA method: System meta notes
│   │   └── dashboards/
│   └── 60-Jots/                       # Quick jots and fleeting notes
│
├── mcp/                               # 🔌 MCP server submodules (external dependencies)
│   ├── mcp-graphiti/                  # Graphiti MCP server (knowledge graph)
│   └── smart-connections-mcp/         # Smart Connections MCP server (semantic search)
│
├── .smart-env/                        # Smart Connections plugin data
│   ├── smart_chat_threads/           # Chat thread embeddings
│   ├── smart_contexts/               # Context embeddings
│   └── multi/                        # Multi-file embeddings
│
├── .bmad/                             # BMad Method workflows (installed system)
├── .claude/                           # Claude Code configuration
├── .cursor/                           # Cursor editor configuration
├── .obsidian/                         # Obsidian vault configuration
│   ├── plugins/                       # Obsidian plugins
│   └── snippets/                      # CSS snippets
├── .playwright-mcp/                   # Playwright MCP data
│
├── templates/                         # Obsidian templates
├── testing/                           # Testing files and experiments
├── planning/                          # Project planning notes
│
├── README.md                          # ⭐ Main project documentation
├── USER_GUIDE.md                      # User guide
├── requirements.txt                   # Python dependencies
└── .gitignore                         # Git ignore rules

```

---

## Critical Entry Points

### 1. **File Watcher** (`scripts/file_watcher.py`)
- **Runs**: Continuously (background process)
- **Watches**: `00-Inbox/raw-conversations/` for `unprocessed_*.md` files
- **Triggers**: Opens Claude Code when new files detected
- **Signals**: User to manually start processing pipeline agent

### 2. **Memory Update Agent** (Claude Code agent)
- **Activated**: User says "update memory" in any Claude session
- **Protocol**: `_system/memory-update-protocol.md`
- **Creates**: `00-Inbox/raw-conversations/unprocessed_YYYYMMDD_HHmm_###.md`
- **Trigger**: File watcher detects new file

### 3. **Processing Pipeline Agent** (Claude Code agent)
- **Activated**: Manually by user after file watcher opens Claude
- **Protocol**: `_system/processing-pipeline-protocol.md`
- **Processes**: 8-stage pipeline (entity extraction → tag assignment → area matching → time estimation → novelty detection → note creation → node updates → finalization)
- **Outputs**: Processed conversation in knowledge area folder + Neo4j entities

### 4. **Monthly Consolidation** (`scripts/monthly_consolidation.py`)
- **Runs**: 1st of each month (manual execution)
- **Purpose**: Compress previous month's tag note entries into summaries
- **Preserves**: Last-day entry for each month
- **Usage**: `python scripts/monthly_consolidation.py --vault C:/obsidian-memory-vault --compress`

---

## Critical Directories Explained

### `_system/` - System Configuration
**Purpose**: All system configuration, protocols, and metadata
**Key Files**:
- `config.json`: Master configuration (batch thresholds, time tracking, Neo4j connection)
- Agent protocols: Define behavior for Claude Code agents
- Taxonomies: Dynamic knowledge organization structures
- Queue files: Track processing status

### `scripts/` - Automation Scripts
**Purpose**: All Python automation and utilities
**Key Scripts**:
- **Entry points**: `file_watcher.py`, `monthly_consolidation.py`, `launch_claude_processor.py`
- **Core utilities**: `tag_note_manager.py`, `brain_space_calculator.py`, `health_check.py`
- **Batch operations**: `batch_neo4j_helper.py`, `backfill_tag_notes.py`
- **Migrations**: `migrate_tag_notes.py`, `fix_tag_note_paths.py`

### `00-Inbox/raw-conversations/` - Conversation Intake
**Purpose**: Staging area for conversation processing
**Workflow**:
1. User says "update memory" → creates `unprocessed_*.md`
2. File watcher detects → renames to `processing_*.md` → adds to queue
3. Processing agent processes → creates organized note → renames to `processed_*.md`

### Knowledge Area Folders - Dynamic Organization
**Purpose**: Hierarchical knowledge organization (2-8 levels deep)
**Strategy**: Data-driven discovery (AI proposes areas based on actual content)
**Structure**:
- Root folders: Technology, Language, Culture, History, Projects
- Subfolder depth: Flexible (2-8 levels based on knowledge complexity)
- Tag notes: Living documents that accumulate knowledge over time

---

## Integration Points

### Claude Code Agents
- **Memory Update Agent**: Extracts conversations on command
- **Processing Pipeline Agent**: Processes queued conversations through 8 stages
- **Activation**: Via protocols in `_system/*.md`

### Neo4j Knowledge Graph
- **Connection**: `neo4j://127.0.0.1:7687` (via MCP)
- **Purpose**: Secondary semantic database (experimental)
- **Usage**: Entity recognition and relationship mapping
- **Primary**: Obsidian vault is primary reference (Neo4j is curiosity/experiment)

### Obsidian Vault
- **Primary Storage**: All knowledge lives in markdown files
- **Plugins Used**:
  - Smart Connections: Embeddings and semantic search
  - Dataview: Advanced queries
- **Navigation**: Hierarchical folders + wikilinks + tags

### MCP Servers
- **neo4j**: Knowledge graph operations
- **smart-connections-mcp**: Semantic search and embeddings
- **playwright**: (Available but not primary to this system)

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  USER: "update memory" in Claude session                        │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  Memory Update Agent (Claude Code)                              │
│  - Extracts full conversation                                   │
│  - Saves to: 00-Inbox/raw-conversations/unprocessed_*.md        │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  File Watcher (Python - Continuous)                             │
│  - Detects new unprocessed_*.md                                 │
│  - Renames to processing_*.md                                   │
│  - Updates processing-queue.md                                  │
│  - Opens Claude Code terminal                                   │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  User: Manually starts Processing Pipeline Agent                │
│  (Types "file watcher summons you" in opened Claude terminal)   │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  Processing Pipeline Agent (Claude Code - 8 Stages)             │
│  1. Entity Extraction (Neo4j MCP)                               │
│  2. Tag Assignment (tag-taxonomy.md)                            │
│  3. Area Matching (area-taxonomy.json)                          │
│  4. Time Estimation (30-min idle detection)                     │
│  5. Novelty Detection (compare with existing tag notes)         │
│  6. Note Creation (in appropriate knowledge area folder)        │
│  7. Node Updates (bidirectional linking in Obsidian)            │
│  8. Finalization (rename processing_* → processed_*)            │
└────────────────────┬────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  Knowledge Stored In:                                           │
│  - Obsidian Vault: Tag notes in hierarchical folders (PRIMARY)  │
│  - Neo4j Graph: Entities + relationships (EXPERIMENTAL)         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Planned Features (Not Yet Implemented)

⚠️ **Batch Processing**: Feature exists in code but not yet operational
- Designed for mass conversation history imports
- Will process 5+ files simultaneously
- Global tag analysis across batch for better area discovery
- Needs to be built and tested

🚧 **Future Enhancements**:
- Project tracking integration
- Media (images, audio, video) ingestion
- Handwritten note ingestion (OCR)
- Mass information collection section (beyond conversational learning)
- Advanced memory metrics dashboard (stats.fm for your brain)
- Thinking evolution tracking over time

---

## File Naming Conventions

### Conversation Files
- **Unprocessed**: `unprocessed_conversation_YYYYMMDD_HHmm_###.md`
- **Processing**: `processing_conversation_YYYYMMDD_HHmm_###.md`
- **Processed**: `processed_conversation_YYYYMMDD_HHmm_###.md`

### Tag Notes
- **Location**: `{KnowledgeArea}/{Subfolders}/{TagName}.md`
- **Example**: `Technology/Programming/Languages/Python.md`
- **Naming**: Uses canonical tag name from taxonomy

### Log Files
- **Pipeline logs**: `docs/pipeline_agent/processing_log_YYYYMMDD_HHmmss.md`
- **System logs**: `_system/logs/{script_name}_YYYYMMDD.log`

---

## Directory Size Estimates

| Directory | Typical Size | Growth Rate |
|-----------|-------------|-------------|
| `scripts/` | ~9,725 LOC | Stable |
| `_system/` | ~50 KB | Slow |
| `00-Inbox/processed/` | 10-100 MB | Fast (conversations) |
| Knowledge Areas | 1-10 MB | Medium (tag notes) |
| `.smart-env/` | 100 MB - 1 GB | Fast (embeddings) |
| `docs/pipeline_agent/` | 1-10 MB | Slow (logs) |

---

## Notes on External Dependencies

### MCP Submodules (`mcp/`)
These are **external MCP servers** cloned as git submodules:
- Not part of core Second Brain codebase
- Provide integration with external services (Neo4j, Smart Connections)
- Can be updated independently

### Obsidian Plugins
Required plugins (installed via Obsidian):
- **Smart Connections**: Enables semantic search and embeddings
- **Dataview**: Enables advanced queries in Obsidian

Configuration in `.obsidian/plugins/`

---

*For more details on system architecture and workflows, see `architecture.md`*
