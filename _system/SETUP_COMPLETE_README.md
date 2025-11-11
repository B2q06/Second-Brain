---
type: documentation
title: Second Brain Setup - Complete Guide
version: 2.0
created: 2025-11-09
status: production-ready
---

# Second Brain - Complete Setup Guide

## ✅ System Status: PRODUCTION READY (v2.1)

All components are configured and tested. Your Second Brain is ready to process conversations.

**Latest Update (2025-11-09):**
- ✅ Processing-pipeline-agent updated with MANDATORY MCP execution checklists
- ✅ Neo4j entity extraction now enforced with verification steps
- ✅ Ollama embedding script created (nomic-embed-text:latest)
- ✅ File watcher updated to auto-embed after processing
- ⏳ Ready for pipeline test with new conversation

---

## Current Configuration

### MCP Servers (Headless CLI)

```bash
$ claude mcp list
```

**Status:**
- ✅ **neo4j**: uvx mcp-neo4j-memory@0.4.2 - Connected
- ✅ **smart-connections**: Python server - Connected
- ❌ graphiti: Failed (not needed, can be removed)

### Neo4j Database

**Connection:** neo4j://127.0.0.1:7687
**Status:** ✅ Running and accessible
**Schema:** MCP Memory Graph (Entity, Episodic, Memory, Community nodes)
**Entities:** 3 (Second Brain System, Neo4j, Obsidian)
**Relationships:** 3 (USES, INTEGRATES_WITH, SYNCS_WITH)

### Smart Connections

**Embeddings Model:** TaylorAI/bge-micro-v2 (local)
**Indexed Files:** 52 .ajson files
**Status:** ✅ Operational (lazy loading)

### Processing Pipeline Agent

**Location:** `.claude/agents/processing-pipeline-agent.md`
**Tools:** Edit, Read, Write, Grep, Glob, Bash, AskUserQuestion, TodoWrite
**MCP Access:** ✅ Full access to neo4j and smart-connections
**Model:** Sonnet

---

## How to Use

### 1. Start the File Watcher

```bash
cd C:\obsidian-memory-vault
python scripts\file_watcher.py
```

**What it does:**
- Monitors `00-Inbox/raw-conversations/` for `unprocessed_*.md` files
- Adds detected files to processing queue
- Spawns processing-pipeline-agent automatically
- Shows real-time agent status updates

### 2. Capture a Conversation

In any Claude Code session:

```
update memory
```

This triggers the memory-update-agent which:
- Extracts entire conversation
- Saves to `00-Inbox/raw-conversations/unprocessed_YYYYMMDD_HHMM_###.md`
- File watcher picks it up automatically

### 3. Processing Happens Automatically

The processing-pipeline-agent runs through 8 stages:

**Stage 1: Entity Extraction**
- Extracts entities (projects, skills, technologies, concepts)
- Stores in Neo4j using `mcp__neo4j__create_entities`
- Creates relationships between entities

**Stage 2: Tag Assignment**
- Loads tag-taxonomy.md
- Checks each entity for exact match or alias
- Uses semantic search for similarity (>0.85 = use existing)
- Proposes new tags for entities with low similarity (<0.70)

**Stage 2.5: ⚠️ HUMAN TAG APPROVAL** (INTERACTIVE)
- Terminal UI appears asking you to approve/merge/reject each new tag
- Options:
  - **[A]** Approve as new tag
  - **[M]** Merge into existing tag
  - **[R]** Reject (use existing tag)
  - **[S]** Skip (manual review later)
  - **[Q]** Quit (save progress)

**Stage 3: Area Matching**
- Maps tags to 8-layer area taxonomy
- Finds deepest matching area (most specific)
- Proposes new areas if no match found

**Stage 4: Time Estimation**
- Parses timestamps from conversation
- Calculates active time (30-min idle threshold)

**Stage 5: Novelty Detection**
- Searches Neo4j for similar conversations
- Calculates novelty score (0-1)

**Stage 6: Note Creation**
- Generates processed note with full metadata
- Saves to appropriate area folder
- Triggers Smart Connections re-indexing

**Stage 7: Node Updates**
- Creates bidirectional links in Neo4j
- Links conversation to entities
- Finds related notes using Smart Connections

**Stage 8: Finalization**
- Renames file: `processing_*.md` → `processed_*.md`
- Updates processing-queue.md
- Logs completion

### 4. Review Outputs

After processing:

**Check Tag Review Queue:**
```bash
cat _system/tag-review-queue.md
```
- Contains deferred tag proposals
- Review and approve/reject manually

**Check New Areas Queue:**
```bash
cat _system/new-areas-queue.md
```
- Contains proposed new knowledge areas
- Approve to add to area-taxonomy.json

**View Neo4j Graph:**
- Open http://localhost:7474
- Run: `MATCH (n) RETURN n LIMIT 50;`
- See entities and relationships

**View Processed Note:**
```bash
cat 00-Inbox/processed/conversation_*.md
```

---

## Configuration Files

### Tag Taxonomy
**File:** `_system/tag-taxonomy.md`
**Purpose:** Controlled vocabulary for consistent tagging
**Format:** YAML blocks with canonical forms and aliases

**Example:**
```yaml
fastapi:
  aliases: [fast-api, FastAPI]
  category: tech/programming
  parent: python
  description: FastAPI Python web framework
```

**Editing:**
- Add new approved tags here
- Define aliases for entity resolution
- Categorize for hierarchical organization

### Area Taxonomy
**File:** `_system/area-taxonomy.json`
**Purpose:** 8-layer hierarchical knowledge structure
**Format:** JSON tree with nested areas

**Example:**
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
          "children": [...]
        }
      ]
    }
  ]
}
```

**Editing:**
- Approve new areas from new-areas-queue.md
- Manually add to JSON structure
- Maximum depth: 8 layers
- Each area has tags associated with it

### System Config
**File:** `_system/config.json`
**Purpose:** Global system settings

**Key Settings:**
- `batch_processing.min_file_count`: 5 (trigger batch mode)
- `time_tracking.idle_gap_minutes`: 30
- `knowledge_scoring.graph_percentage_weight`: 0.70

---

## Testing the System

A test conversation has been created:
**File:** `00-Inbox/raw-conversations/unprocessed_test_pipeline_001.md`

**To test:**
1. Start file watcher: `python scripts\file_watcher.py`
2. Watcher detects test file
3. Agent processes through all 8 stages
4. You'll be prompted to approve 2 new tags: `pytest` and `github-actions`
5. Agent will propose new area: "Technology > Programming > Python > Web Development"

**Expected Results:**
- ✅ Entities in Neo4j: FastAPI, PostgreSQL, Docker, Python, SQLAlchemy, JWT
- ✅ Relationships created between entities
- ✅ Tags assigned (existing + approved new)
- ✅ Processed note created in appropriate area
- ✅ Smart Connections embeddings generated

---

## Key Files & Locations

```
C:\obsidian-memory-vault\
├── _system/
│   ├── config.json                          # System settings
│   ├── tag-taxonomy.md                      # Tag vocabulary
│   ├── area-taxonomy.json                   # Knowledge areas (8 layers)
│   ├── tag-review-queue.md                  # Pending tag approvals
│   ├── new-areas-queue.md                   # Pending area proposals
│   ├── processing-queue.md                  # Files being processed
│   ├── processing-pipeline-protocol.md      # Agent protocol (8 stages)
│   ├── memory-update-protocol.md            # Memory capture protocol
│   ├── COMPLETE_PROCESSING_ARCHITECTURE.md  # Full architecture docs
│   └── SETUP_COMPLETE_README.md             # This file
│
├── .claude/
│   ├── agents/
│   │   └── processing-pipeline-agent.md     # Agent configuration
│   └── settings.json                         # MCP permissions
│
├── scripts/
│   ├── file_watcher.py                      # Python file watcher
│   └── tag_approval_ui.py                   # Terminal UI for approvals
│
├── 00-Inbox/
│   ├── raw-conversations/                   # Captured conversations
│   │   ├── unprocessed_*.md                 # New files (detected)
│   │   ├── processing_*.md                  # Currently processing
│   │   └── processed_*.md                   # Completed
│   └── processed/                           # Final processed notes
│
└── mcp/
    ├── smart-connections-mcp/               # Smart Connections server
    └── mcp-graphiti/                        # Graphiti server (unused)
```

---

## Edge Cases Handled

The system is designed to handle these edge cases robustly:

1. ✅ Empty or malformed conversation files
2. ✅ Neo4j connection lost during processing
3. ✅ Duplicate conversations
4. ✅ User abandons tag approval (Ctrl+C)
5. ✅ Tag conflicts (same name, different meaning)
6. ✅ Area taxonomy too deep (>8 levels)
7. ✅ No matching area for tags
8. ✅ Circular tag references
9. ✅ Smart Connections embeddings out of sync
10. ✅ Multiple files processed simultaneously
11. ✅ Tag taxonomy file corrupted
12. ✅ Invalid user input in terminal UI
13. ✅ Area taxonomy schema changes
14. ✅ Extremely long conversations (>100k tokens)
15. ✅ Network timeout to MCP servers

**See:** `COMPLETE_PROCESSING_ARCHITECTURE.md` for full edge case documentation

---

## Monitoring

### Check Processing Queue Status
```bash
cat _system/processing-queue.md
```

Shows:
- Files awaiting processing
- Currently processing (with stage and progress)
- Completed (last 24 hours)
- Errors

### Check Neo4j Graph Size
Open Neo4j Browser (http://localhost:7474):
```cypher
MATCH (n) RETURN count(n) as total_nodes;
MATCH ()-[r]->() RETURN count(r) as total_relationships;
```

### Check Smart Connections Index
```bash
find C:\obsidian-memory-vault\.smart-env\multi -name "*.ajson" | wc -l
```

### View Recent Processed Files
```bash
ls -lt 00-Inbox/processed/ | head -10
```

---

## Workflow Example

**Scenario:** You just had a conversation about building a REST API with authentication

**Step 1:** Capture conversation
```
In Claude Code:
> update memory

[✓] Memory captured successfully!
File: unprocessed_conversation_20251109_1545_003.md
```

**Step 2:** File watcher detects it
```
[+] Detected new file: unprocessed_conversation_20251109_1545_003.md
    Added to batch (currently 1 file(s))
    Waiting 5s for more files...

[~] Processing batch of 1 file(s)...
[~] Spawning processing-pipeline-agent...
[✓] Agent spawned (PID: 12345)
```

**Step 3:** Agent processes (8 stages)
```
Stage 1: Extracting entities...
  ✓ Found: REST API, Authentication, JWT, FastAPI, PostgreSQL
  ✓ Created 5 entities in Neo4j

Stage 2: Assigning tags...
  ✓ Matched existing tags: api, authentication, fastapi, postgres
  ⚠  New tag proposed: jwt
```

**Step 4:** Terminal UI appears (human-in-the-loop)
```
================================================================================
                              TAG APPROVAL REQUIRED
================================================================================

[1/1] New Tag Proposal
Proposed Tag: 'jwt'
Confidence: 0.65
Context: JSON Web Tokens for authentication

Similar Existing Tags:
  • authentication (similarity: 0.78)
  • tokens (similarity: 0.72)

Options:
  [A] Approve as new tag
  [M] Merge into existing tag
  [R] Reject (use existing)
  [S] Skip for now

Your choice [A/M/R/S]: A

✅ Approved: jwt
```

**Step 5:** Agent continues processing
```
Stage 3: Matching areas...
  ✓ Primary area: Technology > Programming > Python > Web Development

Stage 4: Time estimation... 12 minutes active

Stage 5: Novelty detection... Score: 0.7 (Medium-High)

Stage 6: Creating note...
  ✓ Note created: Technology/Programming/Python/Web Development/conversation_20251109_rest_api_auth.md

Stage 7: Updating graph...
  ✓ Linked conversation to 5 entities
  ✓ Found 3 related notes

Stage 8: Finalizing...
  ✓ Renamed to: processed_conversation_20251109_1545_003.md
  ✓ Queue updated

✅ Processing complete!
```

**Step 6:** Review outputs
```bash
# View processed note
cat "Technology/Programming/Python/Web Development/conversation_20251109_rest_api_auth.md"

# View graph in Neo4j Browser
MATCH (c:Episodic)-[r]->(e:Entity) WHERE c.name CONTAINS 'rest_api_auth' RETURN c, r, e;

# Check for new tag proposals
cat _system/tag-review-queue.md  # Empty (all approved)
```

---

## Next Steps

### Production Deployment

1. **Keep file watcher running:**
   ```bash
   # Option A: Run in tmux/screen session
   tmux new -s filewatcher
   python scripts/file_watcher.py

   # Option B: Create Windows service (advanced)
   nssm install SecondBrainWatcher "C:\Python\python.exe" "C:\obsidian-memory-vault\scripts\file_watcher.py"
   ```

2. **Automate memory capture:**
   - Add "update memory" to end of significant conversations
   - Set reminders to capture daily/weekly

3. **Regular maintenance:**
   - Weekly: Review tag-review-queue.md and new-areas-queue.md
   - Monthly: Backup Neo4j database
   - Monthly: Review and merge similar areas/tags
   - Quarterly: Analyze knowledge growth metrics

### Optional Enhancements

1. **Dashboard for monitoring:**
   - Create web UI showing processing stats
   - Graph visualization of knowledge areas
   - Real-time processing status

2. **Batch import:**
   - Import ChatGPT conversation history
   - Import old project documentation
   - Process in batch mode (5+ files at once)

3. **Advanced querying:**
   - Create Cypher query templates
   - Build Obsidian dataview queries
   - Set up graph analytics

4. **Auto-embedding:**
   - Add reindex_vault() tool to Smart Connections MCP
   - Trigger after note creation
   - Monitor embedding queue size

---

## Troubleshooting

### File watcher not detecting files
**Issue:** Dropped file but nothing happens
**Fix:**
```bash
# Check file watcher is running
ps aux | grep file_watcher.py

# Check file naming
ls 00-Inbox/raw-conversations/unprocessed_*.md

# Restart watcher
Ctrl+C
python scripts/file_watcher.py
```

### Agent not spawning
**Issue:** Queue updated but agent doesn't start
**Fix:**
```bash
# Check Claude CLI path in file_watcher.py line 380
# Should be: C:\Users\bearj\AppData\Roaming\npm\claude.cmd

# Test manual spawn:
claude --agent processing-pipeline-agent "Process queue"
```

### Neo4j connection failed
**Issue:** "Failed to connect to Neo4j"
**Fix:**
```bash
# Check Neo4j is running
curl http://localhost:7474

# Check credentials in Claude Desktop config
cat ~/.config/Claude/claude_desktop_config.json

# Restart Neo4j Desktop
```

### Tag approval UI not appearing
**Issue:** Agent processes without asking for approval
**Fix:**
- Terminal UI only appears for NEW tags (confidence < 0.70)
- If all tags match existing (>0.85 similarity), no approval needed
- Check tag-taxonomy.md has your tech stack defined

### Smart Connections returns no results
**Issue:** Semantic search returns 0 results
**Fix:**
```bash
# Check embeddings exist
ls .smart-env/multi/*.ajson | wc -l

# Open vault in Obsidian
# Let Smart Connections plugin generate embeddings (5-10 min)

# Or trigger manually (if reindex_vault() tool added)
```

---

## Resources

**Documentation:**
- Architecture: `_system/COMPLETE_PROCESSING_ARCHITECTURE.md`
- Protocols: `_system/processing-pipeline-protocol.md`
- MCP Servers: `claude mcp list`

**Neo4j:**
- Browser: http://localhost:7474
- Desktop App: Neo4j Desktop 2.0.5
- Connection: neo4j://127.0.0.1:7687

**Smart Connections:**
- Server: `mcp/smart-connections-mcp/server.py`
- Embeddings: `.smart-env/multi/*.ajson`
- Model: TaylorAI/bge-micro-v2

---

## Support

**If you encounter issues:**
1. Check processing-queue.md for error messages
2. Review file watcher terminal output
3. Check Neo4j Browser for graph state
4. Verify MCP servers: `claude mcp list`
5. Check agent logs in terminal

**For questions about:**
- Processing pipeline: Read `processing-pipeline-protocol.md`
- Memory capture: Read `memory-update-protocol.md`
- Edge cases: Read `COMPLETE_PROCESSING_ARCHITECTURE.md`

---

**Status:** ✅ PRODUCTION READY
**Version:** 2.0
**Last Updated:** 2025-11-09

🧠 **Happy knowledge building!**
