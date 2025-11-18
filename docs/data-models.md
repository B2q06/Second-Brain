# Data Models & Schemas

> **Last Updated**: 2025-11-17
> **Version**: 1.2
> **Purpose**: Complete reference for all data structures in The Second Brain system

---

## Overview

The Second Brain uses a combination of **structured data** (JSON, YAML frontmatter) and **semi-structured data** (markdown content) across multiple storage systems.

**Data Storage Layers**:
1. **Obsidian Vault** (Primary) - Markdown files with YAML frontmatter
2. **Neo4j Graph** (Secondary) - Dynamic entity-relationship graph
3. **Configuration Files** (System) - JSON configuration and metadata

**Design Philosophy**:
- **Data-Driven**: Schema emerges from actual usage, not predefined
- **Flexible Depth**: Hierarchical structures adapt to knowledge complexity (2-8 levels)
- **Human-Readable**: All data is text-based and version-controllable

---

## Table of Contents

1. [Tag Taxonomy](#tag-taxonomy)
2. [Area Taxonomy](#area-taxonomy)
3. [Tag Note Schema](#tag-note-schema)
4. [Conversation File Schema](#conversation-file-schema)
5. [Neo4j Graph Schema](#neo4j-graph-schema)
6. [Configuration Schema](#configuration-schema)
7. [Queue and Status Files](#queue-and-status-files)

---

## Tag Taxonomy

**File**: `_system/tag-taxonomy.md`
**Format**: YAML frontmatter + Markdown
**Purpose**: Define tags, their hierarchies, and metadata for intelligent tagging

### Structure

```yaml
---
# Tag Taxonomy Definition
# Each tag can have: aliases, category, parent tags, description

fastapi:
  canonical: FastAPI
  aliases: [fast-api, fastapi-framework]
  category: tech/programming/web-frameworks
  parent: [python, web-framework, api]
  description: Modern async Python web framework
  related: [uvicorn, pydantic, starlette]

python:
  canonical: Python
  aliases: [py, python3]
  category: tech/programming/languages
  parent: [programming-language]
  description: High-level general-purpose programming language
  related: [pip, virtualenv, pypi]

chinese:
  canonical: Chinese
  aliases: [mandarin, zhongwen]
  category: language/east-asian
  parent: [language-learning, asian-languages]
  description: Chinese language and culture
  related: [pinyin, hanzi, grammar]
---

# Tag Taxonomy

Hierarchical tag definitions for intelligent content classification.

## Technology Tags

### Programming Languages
- `python`: Python programming language
- `javascript`: JavaScript and related ecosystems
- `rust`: Rust systems programming language

### Frameworks & Libraries
- `fastapi`: FastAPI web framework (Python)
- `react`: React JavaScript library
- `django`: Django web framework (Python)

...
```

### Tag Entry Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `canonical` | string | Yes | Official display name (e.g., "FastAPI") |
| `aliases` | array[string] | No | Alternative names for fuzzy matching |
| `category` | string | Yes | Hierarchical category path (slash-separated) |
| `parent` | array[string] | No | Parent tag(s) for inheritance |
| `description` | string | Yes | Brief description of tag meaning |
| `related` | array[string] | No | Related tags (semantic connections) |

### Category Path Format

Categories use **slash-separated hierarchical paths**:

```
tech/programming/languages             → Technology > Programming > Languages
tech/programming/web-frameworks        → Technology > Programming > Web Frameworks
language/east-asian                    → Language > East Asian
culture/regions/china                  → Culture > Regions > China
```

**Mapping to Folders**:
- Category paths map directly to Obsidian folder structure
- First segment = root folder (Technology, Language, Culture, etc.)
- Subsequent segments = subfolders

---

## Area Taxonomy

**File**: `_system/area-taxonomy.json`
**Format**: JSON
**Purpose**: Dynamic knowledge area hierarchy with brain space metrics

### Structure

```json
{
  "system_name": "The Second Brain",
  "version": "1.0",
  "created": "2025-11-07T21:00:00Z",
  "last_updated": "2025-11-17T14:30:00Z",

  "settings": {
    "max_depth": 8,
    "flexible_depth": true,
    "discovery_mode": "data_driven",
    "description": "Areas are discovered from actual knowledge, not predefined"
  },

  "metadata": {
    "total_notes": 127,
    "total_areas": 43,
    "total_root_areas": 5,
    "total_hours_tracked": 342.5,
    "date_range": {
      "first_note": "2025-10-01",
      "last_note": "2025-11-17"
    }
  },

  "root_areas": [
    {
      "id": "technology",
      "name": "Technology",
      "level": 0,
      "parent_id": null,

      "brain_space_score": 0.68,
      "recency_score": 0.92,

      "tags": ["python", "javascript", "docker", "fastapi", "react"],

      "metadata": {
        "total_notes": 78,
        "graph_percentage": 0.61,
        "connection_density": 0.74,
        "time_invested_hours": 234.2,
        "connections_to": ["language", "projects"],
        "last_activity": "2025-11-17",
        "created": "2025-10-01"
      },

      "children": [
        {
          "id": "technology_programming",
          "name": "Programming",
          "level": 1,
          "parent_id": "technology",

          "brain_space_score": 0.82,
          "recency_score": 0.95,

          "tags": ["python", "javascript", "rust", "code"],

          "metadata": {
            "total_notes": 52,
            "graph_percentage": 0.41,
            "connection_density": 0.81,
            "time_invested_hours": 187.5,
            "connections_to": ["technology_databases", "technology_infrastructure"],
            "last_activity": "2025-11-17",
            "created": "2025-10-01"
          },

          "children": [
            {
              "id": "technology_programming_python",
              "name": "Python",
              "level": 2,
              "parent_id": "technology_programming",

              "brain_space_score": 0.91,
              "recency_score": 0.98,

              "tags": ["python", "fastapi", "pandas", "asyncio"],

              "metadata": {
                "total_notes": 34,
                "graph_percentage": 0.27,
                "connection_density": 0.86,
                "time_invested_hours": 142.3,
                "connections_to": ["technology_programming_webdev", "technology_databases"],
                "last_activity": "2025-11-17",
                "created": "2025-10-03"
              },

              "children": []
            }
          ]
        }
      ]
    }
  ],

  "pending_areas": [
    {
      "proposed_name": "Machine Learning",
      "proposed_parent": "technology_programming",
      "reason": "3 recent conversations about ML topics (PyTorch, neural networks, training)",
      "proposed_by": "processing-pipeline-agent",
      "proposed_date": "2025-11-16",
      "status": "pending_approval",
      "related_tags": ["pytorch", "neural-networks", "ml-training"]
    }
  ],

  "_schema_documentation": {
    "area_object": {
      "id": "Unique identifier (snake_case, includes parent path)",
      "name": "Display name",
      "level": "Depth level (0 = root, 1-7 = nested)",
      "parent_id": "ID of parent area (null for roots)",
      "brain_space_score": "Knowledge coverage score (0-1)",
      "recency_score": "Activity recency score (0-1)",
      "tags": "Associated canonical tags",
      "metadata": {
        "total_notes": "Count of tag notes in this area",
        "graph_percentage": "% of total knowledge graph this area represents",
        "connection_density": "% of possible connections to other areas",
        "time_invested_hours": "Total conversation time in this area",
        "connections_to": "Array of area IDs this area connects to",
        "last_activity": "ISO date of most recent update",
        "created": "ISO date when area was discovered"
      },
      "children": "Array of nested child areas (recursive structure)"
    }
  }
}
```

### Brain Space Score Calculation

```
brain_space_score = (graph_percentage * 0.70) +
                    (connection_density * 0.15) +
                    (time_invested * 0.15)

recency_score = exp(-days_since_last_activity / 30)
```

**Interpretation**:
- **brain_space_score**: 0-1 (higher = more knowledge/attention in this area)
- **recency_score**: 0-1 (higher = more recent activity)

---

## Tag Note Schema

**Files**: `{KnowledgeArea}/{Subfolders}/{TagName}.md`
**Format**: YAML frontmatter + Markdown
**Purpose**: Living documents that accumulate knowledge about specific tags over time

### Frontmatter Schema

```yaml
---
type: tag-note
tag: fastapi                          # Normalized tag name
tags: [fastapi]                       # Array form (for Obsidian tag search)
canonical: FastAPI                    # Display name

# Taxonomy
taxonomy_path: Technology > Programming > Web Development > Frameworks
parent_tags: [python, web-framework, api]
root: Technology
depth: 4

# Timestamps
created: 2025-10-15
last_updated: 2025-11-17

# Metrics
total_time_minutes: 127.5
conversation_count: 8
entry_count: 12

# Brain Space
brain_space_score: 0.72
recency_score: 0.95

# Knowledge Maturity
knowledge_level: intermediate        # beginner | intermediate | advanced | expert
---
```

### Content Structure

```markdown
# FastAPI

> **Tag Note**: Living document tracking all discussions about FastAPI
> **Path**: Technology > Programming > Web Development > Frameworks

## Overview
High-performance modern Python web framework for building APIs with automatic interactive documentation.

## Related Tags
- [[Python]] - Required language
- [[Pydantic]] - Data validation
- [[Uvicorn]] - ASGI server
- [[API Design]] - REST patterns
- [[Async Programming]] - Async/await concepts

## Knowledge Timeline

### November 2025

#### 2025-11-17 14:30
Implemented OAuth2 password flow with JWT tokens. Learned about FastAPI's dependency injection system for securing endpoints. Used `Depends()` to inject current user into protected routes.

**Related**: [[OAuth2]], [[JWT]], [[Dependency Injection]]
**Source**: [[conversation_20251117_1430_001]]

#### 2025-11-15 09:20
Built background task system using `BackgroundTasks`. Tasks run after returning response, perfect for sending emails or updating analytics without blocking API response.

**Related**: [[Async Programming]], [[Task Queues]], [[Python]]
**Source**: [[conversation_20251115_0920_001]]

### October 2025

*Compressed from 8 entries*

This month's work covered FastAPI fundamentals including request validation, response models, path operations, and query parameters. Explored automatic OpenAPI documentation generation and Pydantic integration for type safety.

**Related explorations**:
- [[Pydantic]]
- [[OpenAPI]]
- [[REST API]]
- [[Type Hints]]

#### 2025-10-31 16:45
Final entry: Built complete CRUD API with SQLAlchemy integration. Learned about async database sessions and proper connection pooling.

**Related**: [[SQLAlchemy]], [[Async Database]], [[Python]]
**Source**: [[conversation_20251031_1645_003]]

```

### Tag Note Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Always "tag-note" |
| `tag` | string | Yes | Normalized tag name (lowercase, hyphens) |
| `tags` | array[string] | Yes | Same as tag, but array for Obsidian compatibility |
| `canonical` | string | Yes | Display name from taxonomy |
| `taxonomy_path` | string | Yes | Full hierarchical path |
| `parent_tags` | array[string] | No | Parent tag names from taxonomy |
| `root` | string | Yes | Root knowledge area (Technology, Language, etc.) |
| `depth` | integer | Yes | Folder depth level (1-8) |
| `created` | date | Yes | ISO date when tag note was created |
| `last_updated` | date | Yes | ISO date of most recent update |
| `total_time_minutes` | float | Yes | Cumulative conversation time about this tag |
| `conversation_count` | integer | Yes | Number of conversations mentioning this tag |
| `entry_count` | integer | No | Number of timeline entries |
| `brain_space_score` | float | No | Knowledge coverage score (0-1) |
| `recency_score` | float | No | Activity recency score (0-1) |
| `knowledge_level` | enum | No | beginner, intermediate, advanced, expert |

---

## Conversation File Schema

**Files**: `00-Inbox/processed/conversation_*.md`
**Format**: YAML frontmatter + Markdown
**Purpose**: Processed conversation records with metadata

### Frontmatter Schema

```yaml
---
type: conversation
status: processed
source: claude-code

# Identifiers
conversation_id: conv_20251117_1430_001
original_file: unprocessed_conversation_20251117_1430_001.md

# Timestamps
created: 2025-11-17T14:30:15Z
processed: 2025-11-17T14:45:22Z
duration_minutes: 42.5

# Content Classification
tags: [fastapi, oauth2, jwt, python, security]
primary_tag: fastapi
knowledge_areas: [Technology/Programming/Web Development]

# Processing Metadata
processing_agent: processing-pipeline-agent
processing_version: 1.0
novelty_score: 0.78
entities_extracted: 12

# Metrics
word_count: 3547
message_count: 24
code_blocks: 8
---
```

### Content Structure

```markdown
# Conversation: FastAPI OAuth2 Implementation

**Date**: November 17, 2025
**Duration**: 42.5 minutes
**Topics**: OAuth2, JWT tokens, FastAPI security

## Summary

Implemented OAuth2 password flow authentication in FastAPI application. Covered JWT token generation, password hashing, dependency injection for protected routes, and proper error handling.

## Key Insights

1. **Security First**: Never store passwords in plain text - use bcrypt or Argon2
2. **Dependency Injection**: FastAPI's `Depends()` makes auth elegant and reusable
3. **Token Expiration**: Always set reasonable expiration times (15-30 min for access tokens)

## Conversation

[Full conversation transcript follows...]

## Extracted Entities

- **FastAPI** (framework)
- **OAuth2** (protocol)
- **JWT** (token standard)
- **bcrypt** (hashing library)
- **Pydantic** (validation)

## Related Conversations

- [[conversation_20251115_0920_001]] - FastAPI background tasks
- [[conversation_20251110_1530_002]] - API authentication patterns

```

---

## Neo4j Graph Schema

**Database**: Neo4j (local at `neo4j://127.0.0.1:7687`)
**Schema**: **Dynamic and emergent** (evolves from conversation content)
**Purpose**: Secondary semantic layer for entity recognition and relationship mapping

### Node Types

#### Conversation Node
```cypher
CREATE (c:Conversation {
  id: "conv_20251117_001",
  date: "2025-11-17",
  duration_minutes: 42.5,
  word_count: 3547,
  source_file: "conversation_20251117_1430_001.md",
  primary_tag: "fastapi",
  tags: ["fastapi", "oauth2", "jwt"]
})
```

#### Entity Node (Generic)
```cypher
CREATE (e:Entity {
  name: "FastAPI",
  type: "framework",
  category: "technology",
  canonical_tag: "fastapi",
  first_mentioned: "2025-10-15",
  mention_count: 34
})
```

#### Skill Node
```cypher
CREATE (s:Skill {
  name: "Python",
  proficiency: "advanced",
  hours_practiced: 234.5,
  last_practiced: "2025-11-17"
})
```

#### Project Node
```cypher
CREATE (p:Project {
  name: "Second Brain",
  status: "active",
  start_date: "2025-10-01",
  total_time_hours: 87.3
})
```

### Relationship Types

#### MENTIONED_IN
```cypher
(entity)-[:MENTIONED_IN {
  timestamp: "2025-11-17T14:30:00Z",
  context: "discussion about OAuth2 implementation",
  relevance: 0.92
}]->(conversation)
```

#### RELATED_TO
```cypher
(fastapi)-[:RELATED_TO {
  relationship_type: "uses",
  strength: 0.88,
  discovered: "2025-10-15"
}]->(pydantic)
```

#### REQUIRES
```cypher
(fastapi)-[:REQUIRES {
  dependency_type: "language",
  version: "3.8+"
}]->(python)
```

#### PART_OF
```cypher
(oauth2)-[:PART_OF {
  hierarchy_level: 3
}]->(api_security)
```

### Graph Evolution

**Key Principle**: The Neo4j schema is **intentionally dynamic** and grows organically based on:
1. Conversation content
2. Tag relationships from taxonomy
3. AI-detected entity relationships
4. User's actual knowledge patterns

**Not Predefined**: Unlike traditional databases, this schema has no rigid structure. New node types and relationships emerge naturally.

**Experimental Layer**: Neo4j serves as a **curiosity experiment** to see how the semantic graph grows. Obsidian remains the primary, authoritative storage.

---

## Configuration Schema

**File**: `_system/config.json`
**Format**: JSON
**Purpose**: System-wide configuration and tuning parameters

### Schema

```json
{
  "version": "1.0",
  "system_name": "The Second Brain",
  "created": "2025-11-07",

  "brain_space_calculation": {
    "mode": "file_count",                    // "daily" or "file_count"
    "threshold": 10,                         // Recalculate after N files
    "description": "Trigger for recalculating brain space metrics"
  },

  "batch_processing": {
    "min_file_count": 5,                     // Min files for batch mode
    "large_file_threshold_chars": 100000,    // Single file threshold
    "total_batch_threshold_chars": 500000,   // Total batch threshold
    "description": "Batch mode triggers if any condition met"
  },

  "time_tracking": {
    "idle_gap_minutes": 30,                  // Gap to exclude from duration
    "default_session_minutes": 5,            // Default if no timestamps
    "description": "Conversation time calculation parameters"
  },

  "file_watcher": {
    "check_interval_seconds": 10,            // Polling interval (deprecated - now uses watchdog)
    "watch_path": "C:/Obsidian-memory-vault/00-Inbox/raw-conversations",
    "enabled": true
  },

  "taxonomy": {
    "max_depth": 8,                          // Maximum folder depth
    "flexible_depth": true,                  // Allow variable depth
    "discovery_mode": "data_driven",         // Areas from content, not predefined
    "description": "Taxonomy growth strategy"
  },

  "knowledge_scoring": {
    "graph_percentage_weight": 0.70,         // % of total graph (most important)
    "connection_density_weight": 0.15,       // Interconnection strength
    "time_invested_weight": 0.15,            // Time spent on topic
    "description": "Brain space score weights (must sum to 1.0)"
  },

  "neo4j": {
    "uri": "neo4j://127.0.0.1:7687",
    "database": "neo4j",
    "description": "Neo4j connection (password in Claude Desktop config)"
  },

  "agents": {
    "memory_update_agent": {
      "name": "memory-update-agent",
      "protocol_file": "_system/memory-update-protocol.md",
      "tools": ["Read", "Write", "Bash"]
    },
    "processing_pipeline_agent": {
      "name": "processing-pipeline-agent",
      "protocol_file": "_system/processing-pipeline-protocol.md",
      "tools": ["Read", "Write", "Edit", "Glob", "Grep", "Bash", "AskUserQuestion"],
      "mcp_servers": ["neo4j", "obsidian"]
    }
  }
}
```

---

## Queue and Status Files

### Processing Queue (`_system/processing-queue.md`)

**Format**: Markdown with structured sections
**Purpose**: Track files awaiting processing and current status

```markdown
# Processing Queue

**Queue Status**: 3 file(s) awaiting processing ⏳
**Last Check**: 2025-11-17T14:45:00Z

---

## Currently Processing

<!-- Active processing entry (managed by agent) -->
- processing_conversation_20251117_1430_001.md
  - **Started**: 2025-11-17 14:45:30
  - **Stage**: 3/8 (Area Matching)
  - **Elapsed**: 45 seconds

---

## Files Awaiting Processing

<!-- File watcher will add entries here automatically -->

### Batch Added: 2025-11-17T14:30:00Z
**Mode**: Single
**File count**: 1
**Total Size**: 8,547 bytes

**Files**:
- [ ] processing_conversation_20251117_1230_002.md
- [ ] processing_conversation_20251117_1100_003.md

---

## Completed (Last 24 Hours)

<!-- Recently completed entries (auto-archived after 24h) -->
- [x] processing_conversation_20251116_2215_001.md
  - **Completed**: 2025-11-16 22:45:12
  - **Duration**: 3m 15s
  - **Status**: ✅ Success - 5 tag notes updated, 12 entities created
  - **Agent**: processing-pipeline-agent v1.0

---

## Errors & Retries

<!-- Failed processing attempts -->
*No errors in last 7 days*

```

### New Areas Queue (`_system/new-areas-queue.md`)

**Format**: Markdown with pending area proposals
**Purpose**: User approval workflow for discovered knowledge areas

```markdown
# New Areas Queue

Proposed knowledge areas discovered by the AI, awaiting your approval.

---

## Pending Approval

### Machine Learning
**Proposed Parent**: Technology > Programming
**Reason**: 3 recent conversations about ML (PyTorch, neural networks, training)
**Related Tags**: pytorch, neural-networks, ml-training, supervised-learning
**Proposed By**: processing-pipeline-agent
**Date**: 2025-11-16

**Action**:
- [ ] **Approve** - Accept as-is
- [ ] **Edit Name** - Approve with different name: _______________
- [ ] **Merge** - Merge with existing area: _______________
- [ ] **Ignore** - Reject (too specific/temporary)

---

### Containerization
**Proposed Parent**: Technology > Infrastructure
**Reason**: 5 conversations about Docker, Kubernetes, container orchestration
**Related Tags**: docker, kubernetes, containers, devops
**Proposed By**: processing-pipeline-agent
**Date**: 2025-11-14

**Status**: ✅ **APPROVED** (2025-11-15)
**Final Name**: Containerization
**Parent**: Technology/Infrastructure

---

## Recently Approved

*(Last 30 days)*

- Containerization → Technology/Infrastructure (2025-11-15)
- Chinese Grammar → Language/Chinese (2025-11-10)
- API Design → Technology/Programming/Web Development (2025-11-05)

---

## Rejected

*(Last 30 days)*

- "FastAPI Tips" → Too specific, merged into FastAPI tag note (2025-11-12)
- "Code Snippets" → Too generic, no clear taxonomy path (2025-11-08)
```

---

## Migration and Versioning

### Schema Versions

| Version | Date | Changes |
|---------|------|---------|
| 1.2 | 2025-11-17 | Added brain_space_score and recency_score to area taxonomy |
| 1.1 | 2025-11-10 | Added novelty_score to conversation schema |
| 1.0 | 2025-11-07 | Initial schema definition |

### Backward Compatibility

**Philosophy**: Additive changes only (no breaking changes)
**Migration Strategy**: Scripts in `scripts/migrate_*.py` handle schema updates
**Example**: `scripts/migrate_tag_notes.py` adds new frontmatter fields to existing tag notes

---

## Data Validation

### Health Checks

**Script**: `scripts/health_check.py`
**Validates**:
- Configuration file JSON validity
- Taxonomy file existence and format
- Tag note frontmatter completeness
- Directory structure integrity
- Neo4j connection (if configured)

**Usage**:
```bash
python scripts/health_check.py --vault C:/obsidian-memory-vault
```

### Config Validation

**Script**: `scripts/config_validator.py`
**Validates**:
- Required fields present
- Weight values sum to 1.0
- File paths exist
- Integer/float types correct

---

*For operational procedures, see `development-guide.md`*
*For system architecture, see `architecture.md`*
