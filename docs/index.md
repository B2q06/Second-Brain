# The Second Brain - Project Documentation Index

> **Generated**: 2025-11-17
> **Version**: 1.2
> **Purpose**: Master entry point for AI-assisted development and system reference

---

## 🎯 Quick Reference

**Project**: The Second Brain - AI-Powered Knowledge Management System
**Type**: Data Pipeline & Personal Knowledge Management
**Primary Language**: Python 3.13.5
**Architecture**: Event-Driven Pipeline with Hierarchical Data Organization

### Essential Links

| Quick Access | Description |
|--------------|-------------|
| [Project Overview](./project-overview.md) | **Start here** - Executive summary and introduction |
| [Development Guide](./development-guide.md) | **Setup & daily workflow** - How to use the system |
| [Troubleshooting](./development-guide.md#troubleshooting) | **Having issues?** - Common problems and fixes |
| [Architecture](./architecture.md) | **How it works** - System design and data flow |
| [Source Tree](./source-tree-analysis.md) | **Codebase navigation** - Directory structure |
| [Data Models](./data-models.md) | **Schemas & formats** - Tag taxonomy, frontmatter, Neo4j |

---

## 📊 Project At A Glance

### System Overview

```
┌──────────────────────────────────────────────────────────────┐
│  USER says "update memory" in Claude session                 │
└─────────────────────┬────────────────────────────────────────┘
                      ▼
┌──────────────────────────────────────────────────────────────┐
│  Memory Update Agent extracts conversation                   │
│  → Saves to: 00-Inbox/raw-conversations/unprocessed_*.md     │
└─────────────────────┬────────────────────────────────────────┘
                      ▼
┌──────────────────────────────────────────────────────────────┐
│  File Watcher detects, opens Claude terminal                │
└─────────────────────┬────────────────────────────────────────┘
                      ▼
┌──────────────────────────────────────────────────────────────┐
│  User manually starts Processing Pipeline Agent              │
│  → 8-stage processing (entity, tag, area, time, etc.)       │
└─────────────────────┬────────────────────────────────────────┘
                      ▼
┌──────────────────────────────────────────────────────────────┐
│  Knowledge Stored:                                           │
│  ├─ Obsidian: Tag notes in hierarchical folders (PRIMARY)   │
│  └─ Neo4j: Entity graph (EXPERIMENTAL/SECONDARY)             │
└──────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Python 3.13.5**: Automation scripts (~9,725 LOC across 27 files)
- **Obsidian**: Primary markdown knowledge base
- **Neo4j 5.x+**: Secondary semantic knowledge graph (experimental)
- **Claude Code**: AI agents for processing and extraction
- **MCP**: Model Context Protocol for integrations
- **watchdog**: File system event monitoring

### Project Statistics (Current)

- **Conversations**: ~127 captured and processed
- **Tag Notes**: ~43 living knowledge documents
- **Knowledge Areas**: 5 root areas, 38 subareas (2-8 levels deep)
- **Total Time Tracked**: ~342.5 hours
- **Processing Success**: ~99%+ (appears bulletproof)

---

## 📚 Generated Documentation

### Core Documentation (Start Here)

#### [Project Overview](./project-overview.md)
**Purpose**: Executive summary, use cases, and vision
**When to read**: First time understanding the system
**Key sections**:
- What problem this solves
- Key features
- Technology stack
- Success metrics
- Future vision

#### [Development Guide](./development-guide.md)
**Purpose**: Complete setup, operation, and troubleshooting
**When to read**: Setting up or using the system daily
**Key sections**:
- Prerequisites and installation
- Daily workflow (3-step process)
- Monthly maintenance (consolidation)
- Testing procedures
- Troubleshooting (comprehensive)
- Advanced usage

### Technical Documentation

#### [Architecture](./architecture.md)
**Purpose**: System design, data flow, and architectural decisions
**When to read**: Understanding how the system works internally
**Key sections**:
- System architecture diagram
- 8-stage processing pipeline
- Data architecture (Obsidian + Neo4j)
- Deployment architecture
- Configuration management
- Future architecture considerations

#### [Source Tree Analysis](./source-tree-analysis.md)
**Purpose**: Complete directory structure and codebase navigation
**When to read**: Finding files, understanding project organization
**Key sections**:
- Complete directory tree with annotations
- Critical entry points (file_watcher.py, agents, monthly_consolidation.py)
- Critical directories explained
- Integration points (Claude, Neo4j, Obsidian, MCP)
- Data flow visualization
- Planned features (batch processing, future enhancements)

#### [Data Models](./data-models.md)
**Purpose**: Schemas, formats, and data structures
**When to read**: Understanding data formats, extending system
**Key sections**:
- Tag taxonomy structure (YAML)
- Area taxonomy structure (JSON with brain space metrics)
- Tag note frontmatter schema
- Conversation file frontmatter schema
- Neo4j graph schema (dynamic, emergent)
- Configuration schema
- Queue and status file formats

---

## 🗂️ Existing Documentation (Pre-Documentation)

### User Documentation

#### [README.md](../README.md)
**Purpose**: Original project documentation (comprehensive)
**Status**: Main project README, very detailed
**Key sections**:
- System architecture diagram
- Prerequisites
- Installation (step-by-step)
- Usage (daily workflow)
- Batch processing
- Troubleshooting
- Advanced usage
- FAQ

#### [USER_GUIDE.md](../USER_GUIDE.md)
**Purpose**: Quick reference guide for users
**Status**: User-facing guide

### System Documentation

#### [_system/COMPLETE_PROCESSING_ARCHITECTURE.md](../_system/COMPLETE_PROCESSING_ARCHITECTURE.md)
**Purpose**: Processing pipeline architecture details

#### [_system/TROUBLESHOOTING.md](../_system/TROUBLESHOOTING.md)
**Purpose**: System troubleshooting reference

#### [_system/mcp-tools-reference.md](../_system/mcp-tools-reference.md)
**Purpose**: MCP tools available to agents

#### [_system/memory-update-protocol.md](../_system/memory-update-protocol.md)
**Purpose**: Memory update agent protocol (how to extract conversations)

#### [_system/processing-pipeline-protocol.md](../_system/processing-pipeline-protocol.md)
**Purpose**: Processing pipeline agent protocol (8-stage processing flow)

### Pipeline Agent Documentation

#### [docs/pipeline_agent/README.md](./pipeline_agent/README.md)
**Purpose**: Pipeline agent specific documentation

---

## 🚀 Getting Started

### For First-Time Users

**Read in this order**:

1. **[Project Overview](./project-overview.md)** - Understand what this system does (10 min)
2. **[Development Guide - Prerequisites](./development-guide.md#prerequisites)** - Ensure you have required software (5 min)
3. **[Development Guide - Installation](./development-guide.md#installation)** - Set up the system (30 min)
4. **[Development Guide - Daily Workflow](./development-guide.md#daily-workflow)** - Learn how to use it (10 min)
5. **Start using it!** 🎉

### For System Understanding

**Read in this order**:

1. **[Architecture](./architecture.md)** - How the system works (20 min)
2. **[Source Tree Analysis](./source-tree-analysis.md)** - Where everything lives (15 min)
3. **[Data Models](./data-models.md)** - What data looks like (15 min)

### For Troubleshooting

**Jump directly to**:

- **[Development Guide - Troubleshooting](./development-guide.md#troubleshooting)** - Common issues and fixes
- **[_system/TROUBLESHOOTING.md](../_system/TROUBLESHOOTING.md)** - System-level troubleshooting

### For Extending the System

**Read these**:

- **[Architecture - Future Considerations](./architecture.md#future-architecture-considerations)** - Planned features
- **[Source Tree - Planned Features](./source-tree-analysis.md#planned-features-not-yet-implemented)** - What's coming
- **[Data Models](./data-models.md)** - How to work with data structures
- **Python scripts in `/scripts`** - 27 utilities to explore

---

## 🔑 Key Concepts

### Entry Points (Start Here)

| Entry Point | Type | Purpose |
|-------------|------|---------|
| **file_watcher.py** | Python script | Continuous monitoring (runs 24/7) |
| **memory-update-agent** | Claude Code agent | Extracts conversations on "update memory" |
| **processing-pipeline-agent** | Claude Code agent | Processes queued conversations (8 stages) |
| **monthly_consolidation.py** | Python script | Compress tag note histories (1st of month) |

**References**:
- `scripts/file_watcher.py:1`
- `_system/memory-update-protocol.md`
- `_system/processing-pipeline-protocol.md`
- `scripts/monthly_consolidation.py:1`

### Critical Directories

| Directory | Purpose |
|-----------|---------|
| `_system/` | System configuration, protocols, taxonomies |
| `scripts/` | 27 Python automation scripts (~9,725 LOC) |
| `00-Inbox/raw-conversations/` | **WATCH FOLDER** - Conversation intake |
| `Technology/`, `Language/`, etc. | Dynamic knowledge areas (2-8 levels) |
| `docs/` | Documentation (this directory) |

**References**:
- See [Source Tree Analysis](./source-tree-analysis.md#critical-directories-explained)

### Data Flows

#### 1. Conversation Capture → Processing

```
User: "update memory"
→ Memory Update Agent extracts conversation
→ File: 00-Inbox/raw-conversations/unprocessed_*.md
→ File Watcher detects (< 3 sec)
→ Renamed: processing_*.md
→ Queue updated: _system/processing-queue.md
→ Claude terminal opens
→ User starts Processing Pipeline Agent
→ 8 stages execute
→ Tag notes created in knowledge areas
→ Neo4j entities created
→ File renamed: processed_*.md
```

**Reference**: [Architecture - Data Flow Patterns](./architecture.md#data-flow-patterns)

#### 2. Monthly Compression

```
1st of month
→ Run: python scripts/monthly_consolidation.py --compress
→ Previous month's tag note entries compressed
→ Last-day entry preserved
→ Cross-tag references added
→ Readable history maintained
```

**Reference**: [Development Guide - Monthly Maintenance](./development-guide.md#monthly-maintenance)

### Configuration Files

| File | Format | Purpose |
|------|--------|---------|
| `_system/config.json` | JSON | Master system configuration |
| `_system/tag-taxonomy.md` | YAML + MD | Tag definitions and hierarchies |
| `_system/area-taxonomy.json` | JSON | Dynamic knowledge area structure |
| `_system/processing-queue.md` | Markdown | Active processing queue |
| `_system/new-areas-queue.md` | Markdown | Proposed knowledge areas |

**Reference**: [Data Models - Configuration Schema](./data-models.md#configuration-schema)

---

## 🛠️ Common Tasks

### Daily Operations

#### Capture a Conversation

```
1. In any Claude Code session, say: "update memory"
2. File watcher detects (< 3 sec) and opens Claude terminal
3. In opened terminal, type: "file watcher summons you"
4. Wait 2-5 minutes for processing to complete
5. Check created/updated tag notes in knowledge area folders
```

**Reference**: [Development Guide - Daily Workflow](./development-guide.md#daily-workflow)

#### Check Processing Status

```
1. Open: _system/processing-queue.md
2. See currently processing files
3. See queue of awaiting files
4. See recently completed (last 24 hours)
```

**Reference**: `_system/processing-queue.md`

#### Review Proposed Knowledge Areas

```
1. Open: _system/new-areas-queue.md
2. Review AI-proposed areas
3. Approve / Edit Name / Merge / Ignore
4. Approved areas added to area-taxonomy.json
```

**Reference**: [Data Models - Queue and Status Files](./data-models.md#queue-and-status-files)

### Monthly Maintenance

#### Run Consolidation (1st of Month)

```bash
python scripts/monthly_consolidation.py --vault C:/obsidian-memory-vault --compress
```

**What it does**:
- Compresses previous month's tag note entries
- Preserves last-day entry
- Adds cross-tag references

**Reference**: `scripts/monthly_consolidation.py:1`

#### Calculate Brain Space Metrics

```bash
python scripts/brain_space_calculator.py
```

**Outputs**:
- `_system/brain-space-metrics.json` - Calculated metrics
- `_system/brain-space-data.json` - Raw data

**Reference**: `scripts/brain_space_calculator.py:1`

### System Maintenance

#### Health Check

```bash
python scripts/health_check.py
```

Validates:
- Directory structure
- Config file validity
- Taxonomy integrity
- Tag note frontmatter
- Neo4j connection

**Reference**: `scripts/health_check.py:1`

#### View Neo4j Graph

```cypher
// Open Neo4j Browser, run queries:

// View all entities
MATCH (n) RETURN n LIMIT 25

// View relationships
MATCH (a)-[r]->(b) RETURN a, r, b LIMIT 25

// Find most-discussed topics
MATCH (n)-[r]-()
RETURN n.name, count(r) as connections
ORDER BY connections DESC
LIMIT 10
```

**Reference**: [Development Guide - Viewing the Knowledge Graph](./development-guide.md#viewing-the-knowledge-graph)

---

## 🔍 Finding What You Need

### By Task

| I want to... | See document | Section |
|--------------|--------------|---------|
| **Set up the system** | [Development Guide](./development-guide.md) | Installation |
| **Understand daily workflow** | [Development Guide](./development-guide.md) | Daily Workflow |
| **Fix an issue** | [Development Guide](./development-guide.md) | Troubleshooting |
| **Understand architecture** | [Architecture](./architecture.md) | All |
| **Find a file** | [Source Tree](./source-tree-analysis.md) | Directory Structure |
| **Understand data format** | [Data Models](./data-models.md) | Relevant schema section |
| **See what the system does** | [Project Overview](./project-overview.md) | Key Features |
| **Plan future features** | [Project Overview](./project-overview.md) | Future Vision |

### By Component

| Component | Location | Documentation |
|-----------|----------|---------------|
| **File Watcher** | `scripts/file_watcher.py` | [Source Tree - Entry Points](./source-tree-analysis.md#critical-entry-points) |
| **Processing Pipeline** | `_system/processing-pipeline-protocol.md` | [Architecture - Pipeline](./architecture.md#pipeline-architecture) |
| **Tag Taxonomy** | `_system/tag-taxonomy.md` | [Data Models - Tag Taxonomy](./data-models.md#tag-taxonomy) |
| **Area Taxonomy** | `_system/area-taxonomy.json` | [Data Models - Area Taxonomy](./data-models.md#area-taxonomy) |
| **Tag Notes** | `{KnowledgeArea}/{TagName}.md` | [Data Models - Tag Note Schema](./data-models.md#tag-note-schema) |
| **Neo4j Graph** | Neo4j Desktop | [Data Models - Neo4j Schema](./data-models.md#neo4j-graph-schema) |
| **Brain Space Metrics** | `scripts/brain_space_calculator.py` | [Development Guide - Brain Space Metrics](./development-guide.md#brain-space-metrics) |

---

## ⚠️ Important Notes

### Batch Processing - Not Yet Operational

⚠️ **The batch processing feature is designed but not yet implemented/tested**

**What it's supposed to do**:
- Process 5+ files simultaneously
- Global tag analysis across batch
- Better knowledge area discovery

**Current status**: Code exists but needs activation and testing

**Reference**: [Source Tree - Planned Features](./source-tree-analysis.md#planned-features-not-yet-implemented)

### Neo4j is Secondary (Experimental)

**Key Understanding**: Obsidian vault is PRIMARY, Neo4j is SECONDARY

- Obsidian = authoritative knowledge store
- Neo4j = experimental semantic layer for curiosity/exploration
- Neo4j schema is dynamic and emergent (no predefined structure)
- If Neo4j fails, system continues working (Obsidian remains intact)

**Reference**: [Architecture - Data Architecture](./architecture.md#data-architecture)

### Manual Step Required

**The system is NOT fully automatic**

**Required manual steps**:
1. Say "update memory" to capture conversation
2. Type "file watcher summons you" when Claude terminal opens

**Why manual**: Provides control and awareness of processing

**Reference**: [Development Guide - Daily Workflow](./development-guide.md#detailed-workflow)

---

## 🎯 Next Steps

### For First-Time Setup

1. Read [Project Overview](./project-overview.md)
2. Follow [Development Guide - Installation](./development-guide.md#installation)
3. Test with [Development Guide - Testing](./development-guide.md#testing-the-system)
4. Use daily: [Development Guide - Daily Workflow](./development-guide.md#daily-workflow)

### For AI-Assisted Development

**When planning new features**, reference:
1. [Architecture - Future Considerations](./architecture.md#future-architecture-considerations)
2. [Source Tree - Planned Features](./source-tree-analysis.md#planned-features-not-yet-implemented)
3. [Project Overview - Future Vision](./project-overview.md#future-vision)

**When modifying existing features**, reference:
1. [Source Tree](./source-tree-analysis.md) - Find the relevant files
2. [Architecture](./architecture.md) - Understand the design patterns
3. [Data Models](./data-models.md) - Understand the data structures

**When troubleshooting**, reference:
1. [Development Guide - Troubleshooting](./development-guide.md#troubleshooting)
2. Logs in `docs/pipeline_agent/processing_log_*.md`
3. Queue status in `_system/processing-queue.md`

---

## 📖 Documentation Maintenance

### Self-Updating Documentation

**Philosophy**: Documentation should evolve with the system

**How to update**:
1. Edit the relevant `.md` file in `docs/`
2. Update the "Last Updated" date
3. Add entry to version history if significant change

**AI can help**:
- When making code changes, ask AI to update relevant docs
- Run AI through this index to understand what needs updating
- Use AI to generate new sections based on code changes

**Reference**: [Project Overview - Success Metrics](./project-overview.md#success-metrics)

---

**👆 This is the master index for The Second Brain project documentation. Start with [Project Overview](./project-overview.md) for a high-level introduction, or jump directly to [Development Guide](./development-guide.md) to get started.**

*Documentation generated 2025-11-17 via BMad document-project workflow (exhaustive scan mode)*
