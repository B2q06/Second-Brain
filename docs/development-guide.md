# Development Guide

> **Last Updated**: 2025-11-17
> **Purpose**: Complete setup, operation, and troubleshooting guide for The Second Brain

---

## Prerequisites

Before setting up The Second Brain, ensure you have the following installed:

### Required Software

| Software | Version | Purpose | Installation |
|----------|---------|---------|--------------|
| **Python** | 3.8+ (tested with 3.13.5) | Automation scripts | [python.org](https://python.org) |
| **Claude Code** | Latest | AI orchestration and agents | Installed at C:\ for system access |
| **Obsidian** | Latest | Markdown vault and knowledge base | [obsidian.md](https://obsidian.md) |
| **Neo4j Desktop** | 5.x+ | Knowledge graph database | [neo4j.com/download](https://neo4j.com/download) |
| **Node.js** | Latest LTS | For MCP servers (uvx/npx) | [nodejs.org](https://nodejs.org) |

### Required Obsidian Plugins

Install these plugins through Obsidian's Community Plugins:

1. **Smart Connections** - For embeddings and semantic search
2. **Dataview** - For advanced queries and dynamic views

### Required MCP Servers

Configure these in Claude Desktop config (`C:\Users\<YourUsername>\AppData\Roaming\Claude\claude_desktop_config.json`):

1. **Neo4j MCP Server** - For knowledge graph interactions
2. **Smart Connections MCP** (optional) - For enhanced Obsidian integration

---

## Installation

### Step 1: Verify Neo4j Setup

1. Open **Neo4j Desktop**
2. Create a new database (or use existing)
   - Click **"+ Add"** → **"Local DBMS"**
   - Name: `SecondBrain` (or your preference)
   - Password: Choose a strong password (you'll need this for MCP config)
   - Version: Latest 5.x
3. **Start the database** (click the play ▶️ button)
4. Note your connection details:
   - URL: `neo4j://127.0.0.1:7687` (default)
   - Username: `neo4j` (default)
   - Password: (what you set above)

### Step 2: Configure MCP Servers in Claude Desktop

1. Locate Claude Desktop config file:
   ```
   C:\Users\<YourUsername>\AppData\Roaming\Claude\claude_desktop_config.json
   ```

2. Open in text editor and add MCP servers:

```json
{
  "isUsingBuiltInNodeForMcp": true,
  "mcpServers": {
    "neo4j": {
      "command": "uvx",
      "args": ["mcp-neo4j-memory@0.4.2"],
      "env": {
        "NEO4J_URI": "neo4j://127.0.0.1:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your_password_here"
      }
    }
  }
}
```

3. **Restart Claude Desktop** for changes to take effect

### Step 3: Install Python Dependencies

```bash
# Navigate to vault
cd C:\obsidian-memory-vault

# Install dependencies
pip install -r requirements.txt
```

This installs:
- `watchdog>=3.0.0` - File system monitoring

### Step 4: Install Obsidian Plugins

1. Open Obsidian
2. Open your vault at `C:\obsidian-memory-vault`
3. Go to **Settings** → **Community Plugins**
4. Disable **Safe Mode** if enabled
5. Click **Browse** and install:
   - **Smart Connections**
   - **Dataview**
6. Enable both plugins after installation

### Step 5: Verify Folder Structure

Your vault should have this structure (created automatically):

```
C:\obsidian-memory-vault\
├── _system/           # System config (should exist)
├── scripts/           # Python scripts (should exist)
├── 00-Inbox/
│   └── raw-conversations/  # File watcher monitors this
├── docs/              # Documentation (you're reading this!)
└── (knowledge areas will be created automatically)
```

If any required folders are missing:

```bash
# Run health check to identify issues
python scripts/health_check.py
```

---

## Daily Workflow

### Quick Start (3 Steps)

1. **Start File Watcher** (once, keeps running)
2. **Use Claude** → Say "update memory" to capture conversations
3. **Start Processing Agent** (when file watcher opens Claude)

### Detailed Workflow

#### 1. Start the File Watcher

Open a terminal and run:

```bash
cd C:\obsidian-memory-vault
python scripts\file_watcher.py
```

**Expected Output**:
```
============================================================
The Second Brain - File Watcher
============================================================

[.] Vault path: C:\obsidian-memory-vault
[.] Watching: C:\obsidian-memory-vault\00-Inbox\raw-conversations

[#] Configuration loaded:
    - Batch threshold: 5 files
    - Large file threshold: 100,000 chars
    - Batch timeout: 5s

[*] Checking for existing unprocessed files...
[i] No existing unprocessed files found

[✓] File watcher is running!
    Press Ctrl+C to stop

Monitoring for new conversation files...
------------------------------------------------------------
```

**Keep this terminal open** - it will monitor for new conversation files 24/7.

#### 2. Capture Conversations

**In any Claude Code session**, when you want to save the conversation:

```
update memory
```

This triggers the **memory-update-agent** which:
- Extracts the complete conversation
- Saves to: `00-Inbox/raw-conversations/unprocessed_conversation_YYYYMMDD_HHmm_###.md`

**What happens next**:
1. File watcher detects the new file (~3 seconds)
2. Renames it to `processing_*.md`
3. Adds entry to `_system/processing-queue.md`
4. **Opens a new Claude Code terminal window automatically**

#### 3. Start Processing Pipeline Agent

**In the newly opened Claude terminal**, you'll see it opened in your vault directory.

Type:
```
file watcher summons you
```

**The processing pipeline agent will**:
1. Read the processing queue
2. Process files through 8 stages:
   - Entity Extraction (Neo4j)
   - Tag Assignment
   - Area Matching
   - Time Estimation
   - Novelty Detection
   - Note Creation
   - Node Updates
   - Finalization
3. Create organized tag notes in knowledge area folders
4. Update Neo4j graph with entities
5. Rename files to `processed_*.md` when complete

**Processing takes** 2-5 minutes per conversation.

**Agent completion**:
- Creates signal file: `_system/agent_completion_signal.txt`
- Generates processing log: `docs/pipeline_agent/processing_log_*.md`
- File watcher detects completion and displays summary

**After completion**: Close the Claude terminal window (or leave it open for next batch)

---

## Monthly Maintenance

### Monthly Consolidation (1st of Each Month)

**Purpose**: Compress previous month's tag note entries into summaries

**Run manually on the 1st**:

```bash
python scripts/monthly_consolidation.py --vault C:/obsidian-memory-vault --compress
```

**What it does**:
- Finds all tag notes in vault
- Compresses previous month's entries into summary
- Preserves last-day entry for each month
- Adds cross-tag references

**Expected output**:
```
============================================================
Monthly Consolidation: November 2025
Mode: Compress previous month
============================================================

[i] Found 43 tag note(s)

[~] Processing: FastAPI.md
[✓] Compressed October 2025 (12 entries)

[~] Processing: Python.md
[✓] Compressed October 2025 (18 entries)

...

============================================================
[✓] Consolidation complete
    Processed: 43/43 tag notes
============================================================
```

---

## Testing the System

### Test 1: File Watcher Detection

**Test**: Verify file watcher can detect new files

```bash
# 1. Start file watcher
python scripts\file_watcher.py

# 2. In another terminal, create a test file:
cd C:\obsidian-memory-vault\00-Inbox\raw-conversations
echo "Test conversation" > unprocessed_test_001.md

# 3. Watch file watcher terminal - should see:
#    📥 Detected new file: unprocessed_test_001.md
#    ✏️  Renamed to: processing_test_001.md
#    ✅ Updated processing queue: 1 file(s) added
```

### Test 2: Memory Update Agent

**Test**: Verify memory capture works

1. Open Claude Code in any project
2. Have a short conversation (2-3 exchanges)
3. Say: **"update memory"**
4. Agent should extract conversation and save to raw-conversations folder
5. File watcher should detect it and open new Claude terminal

### Test 3: Processing Pipeline Agent

**Test**: Verify full pipeline processing

1. Ensure test file exists in queue (from Test 1 or Test 2)
2. When Claude terminal opens, type: **"file watcher summons you"**
3. Watch agent process through 8 stages
4. Check for:
   - Tag notes created/updated in knowledge area folders
   - Processing log generated in `docs/pipeline_agent/`
   - Completion signal displayed by file watcher

### Test 4: Neo4j Connection

**Test**: Verify Neo4j MCP integration

1. Ensure Neo4j database is running (Neo4j Desktop)
2. In Claude Code (processing-pipeline-agent), try:
   ```
   Use the neo4j MCP to query all entities
   ```
3. Should return entities if any exist, or empty list if fresh database
4. If error: Check Neo4j is running and MCP config is correct

### Test 5: System Health Check

**Test**: Validate entire system configuration

```bash
python scripts/health_check.py --vault C:/obsidian-memory-vault
```

**Expected output**:
```
Running health checks...

✅ Directory Structure: All required directories present
✅ Config File: Config valid
✅ Taxonomy: tag-taxonomy.md found
✅ Tag Notes: 43 tag notes validated
✅ Conversations: 127 conversations found
✅ Scripts: All 27 scripts present
✅ Logs: Log directory accessible
✅ Disk Space: 45 GB available

Health check complete: healthy
```

---

## Troubleshooting

### File Watcher Not Detecting Files

**Symptoms**: Drop file in raw-conversations, nothing happens

**Fixes**:
1. Verify file watcher is running: Check terminal for "File watcher is running!" message
2. Ensure filename starts with `unprocessed_` and ends with `.md`
3. Check file watcher terminal for errors
4. Try manual poll: File watcher polls every 3 seconds (wait a moment)
5. Restart file watcher: Ctrl+C then restart

### Processing Pipeline Agent Not Processing

**Symptoms**: Files stuck in queue for >1 hour

**Fixes**:
1. Ensure processing-pipeline-agent is running (you must manually start it)
2. Check Neo4j database is running (Neo4j Desktop → click play button)
3. Verify MCP configuration in Claude Desktop config
4. Restart Claude Desktop if config changed
5. Check `_system/processing-queue.md` for status/errors
6. Look at latest processing log in `docs/pipeline_agent/` for error details

### Neo4j Connection Failed

**Symptoms**: Agent reports "Cannot connect to Neo4j" or MCP errors

**Fixes**:
1. Open Neo4j Desktop
2. Ensure database is **started** (green play button, not paused)
3. Check connection details in Claude Desktop config:
   - URI: `neo4j://127.0.0.1:7687`
   - Username: `neo4j`
   - Password: (your password - check it's correct)
4. Test connection in Neo4j Browser (click "Open" on running database)
5. Restart Claude Desktop after config changes
6. Try manual Neo4j query in Neo4j Browser:
   ```cypher
   MATCH (n) RETURN n LIMIT 5
   ```

### MCP Server Not Found

**Symptoms**: "Tool not available" or "MCP server not found" errors

**Fixes**:
1. Verify `isUsingBuiltInNodeForMcp: true` is at **root level** of config (not inside mcpServers)
2. Check MCP servers defined correctly in config
3. Ensure Node.js is installed: `node --version`
4. Restart Claude Desktop after config changes
5. Try manually installing MCP package:
   ```bash
   uvx mcp-neo4j-memory@0.4.2
   ```
6. Check Claude Desktop logs: `%APPDATA%\Claude\logs\`

### Areas Not Being Discovered

**Symptoms**: All notes go to root, no hierarchical area structure

**Fixes**:
1. Check `_system/new-areas-queue.md` for pending proposals
2. Approve proposed areas (edit the queue file and set action to "Approve")
3. Verify approved areas added to `_system/area-taxonomy.json`
4. Process more conversations (need 3+ related conversations to discover area)
5. Ensure `_system/tag-taxonomy.md` has relevant tags defined
6. Check tag categories in taxonomy match actual content

### File Watcher Crashes

**Symptoms**: Python script exits unexpectedly

**Fixes**:
1. Check for syntax errors: `python scripts\file_watcher.py`
2. Ensure watchdog installed: `pip install watchdog`
3. Check file paths in config match your vault location
4. Run with error output logged:
   ```bash
   python scripts\file_watcher.py 2> errors.log
   ```
5. Check errors.log for detailed error messages
6. Verify permissions to read/write in vault directories

### Smart Connections Not Working

**Symptoms**: No semantic search, no embeddings

**Fixes**:
1. Ensure Smart Connections plugin installed and enabled in Obsidian
2. Check `.smart-env/` folder exists (created by plugin)
3. Run embedding generation in Smart Connections settings
4. For new notes: Smart Connections auto-embeds on file save
5. Manual embedding: Smart Connections → Settings → "Re-index vault"

### Tag Notes Not Created

**Symptoms**: Processing completes but no tag notes appear

**Fixes**:
1. Check `_system/tag-taxonomy.md` has tag definitions
2. Verify taxonomy paths map to valid folder structures
3. Check permissions on vault folders (must be writable)
4. Look at processing log for errors: `docs/pipeline_agent/processing_log_*.md`
5. Manually check if notes exist in unexpected locations
6. Re-run tag note generation:
   ```bash
   python scripts/backfill_tag_notes.py
   ```

### Conversation Files Missing Content

**Symptoms**: Empty or incomplete conversation captures

**Fixes**:
1. Ensure memory-update-agent protocol is up to date
2. Check Claude Code session is not truncated (very long conversations may be cut)
3. Verify file isn't being accessed by another process during save
4. Manual check: Open the raw file and verify content exists
5. Re-trigger capture: Say "update memory" again

---

## Advanced Usage

### Customizing Tag Taxonomy

**File**: `_system/tag-taxonomy.md`

**Add a new tag**:

```yaml
pytorch:
  canonical: PyTorch
  aliases: [torch, pytorch-framework]
  category: tech/programming/machine-learning
  parent: [python, deep-learning, ml-framework]
  description: Deep learning framework for Python
  related: [tensorflow, keras, neural-networks]
```

**After editing**:
1. Save file
2. Next conversation will use updated taxonomy
3. Existing tag notes are NOT automatically updated

### Adjusting Knowledge Scoring

**File**: `_system/config.json`

**Edit weights**:

```json
"knowledge_scoring": {
  "graph_percentage_weight": 0.70,    // How much of total knowledge (70%)
  "connection_density_weight": 0.15,  // Interconnection strength (15%)
  "time_invested_weight": 0.15        // Time spent (15%)
}
```

**Weights must sum to 1.0**

**After editing**:
1. Run: `python scripts/brain_space_calculator.py`
2. New scores calculated and stored
3. View in `_system/brain-space-metrics.json`

### Manual Entity Creation in Neo4j

**Via processing-pipeline-agent**:

```
Create a new entity called 'Docker' with type 'technology' and category 'infrastructure'
```

Agent will use neo4j MCP to create it.

**Via Neo4j Browser**:

```cypher
CREATE (n:Entity {
  name: "Docker",
  type: "technology",
  category: "infrastructure",
  created: date()
})
RETURN n
```

### Viewing the Knowledge Graph

1. Open **Neo4j Desktop**
2. Click **Open** on your running database (opens Neo4j Browser)
3. Run Cypher queries:

```cypher
// View all entities
MATCH (n) RETURN n LIMIT 25

// View all relationships
MATCH (a)-[r]->(b) RETURN a, r, b LIMIT 25

// Find entities by tag
MATCH (n:Entity {canonical_tag: 'python'}) RETURN n

// Find most connected entities
MATCH (n)-[r]-()
RETURN n.name, count(r) as connections
ORDER BY connections DESC
LIMIT 10

// Find conversation history for a topic
MATCH (e:Entity {name: 'FastAPI'})-[:MENTIONED_IN]->(c:Conversation)
RETURN c.date, c.id
ORDER BY c.date DESC
```

### Brain Space Metrics

**Calculate manually**:

```bash
python scripts/brain_space_calculator.py
```

**View results**:
- `_system/brain-space-metrics.json` - Calculated metrics
- `_system/brain-space-data.json` - Raw data

**Metrics included**:
- Knowledge coverage by area
- Learning velocity (entities/conversations per week)
- Cognitive depth (average taxonomy depth)
- Connection density (how interconnected knowledge is)
- Domain diversity (spread across knowledge areas)
- Temporal patterns (when you learn most)
- Entity prominence (most-discussed topics)
- Growth trajectory (acceleration over time)

---

## File Naming Conventions

### Conversation Files

**Pattern**: `{status}_{source}_{YYYYMMDD}_{HHmm}_{sequence}.md`

**Examples**:
- `unprocessed_conversation_20251117_1430_001.md` - New conversation
- `processing_conversation_20251117_1430_001.md` - Being processed
- `processed_conversation_20251117_1430_001.md` - Processing complete

### Tag Notes

**Pattern**: `{CanonicalTagName}.md`

**Location**: `{KnowledgeArea}/{Subfolders}/{TagName}.md`

**Examples**:
- `Technology/Programming/Languages/Python.md`
- `Language/Chinese/Grammar.md`
- `Culture/Regions/China.md`

### Log Files

**Pattern**: `processing_log_{YYYYMMDD}_{HHmmss}.md`

**Location**: `docs/pipeline_agent/processing_log_*.md`

**Example**: `processing_log_20251117_143045.md`

---

## Maintenance Tasks

### Weekly Tasks

**Check pending areas**:
```bash
# Review new area proposals
notepad _system/new-areas-queue.md

# Approve/reject as needed (edit file directly)
```

**Check processing queue**:
```bash
# Ensure no files stuck
notepad _system/processing-queue.md
```

**Browse Neo4j graph**:
```
# Explore new entities and relationships
Neo4j Desktop → Open Browser → Run queries
```

### Monthly Tasks (1st of Month)

**Run consolidation**:
```bash
python scripts/monthly_consolidation.py --vault C:/obsidian-memory-vault --compress
```

**Review area taxonomy**:
```bash
# Check for areas to merge or reorganize
notepad _system/area-taxonomy.json
```

**Update tag taxonomy**:
```bash
# Add new tags for emerging topics
notepad _system/tag-taxonomy.md
```

**Archive old processed files**:
```bash
# Move from raw-conversations to archive
mkdir 00-Inbox/archive
move 00-Inbox/raw-conversations/processed_2025-10*.md 00-Inbox/archive/
```

### Quarterly Tasks

**Analyze knowledge growth**:
```bash
python scripts/brain_space_calculator.py
python scripts/export_brain_data.py
```

**Backup Neo4j database**:
```
Neo4j Desktop → Database → ... menu → Dump
```

**Backup Obsidian vault**:
```bash
# Commit to git (if using version control)
git add .
git commit -m "Quarterly backup - Q4 2025"
git push
```

**Review system health**:
```bash
python scripts/health_check.py
```

---

## Performance Optimization

### Speed Up Processing

**If processing is slow** (>5 minutes per conversation):

1. **Reduce Neo4j overhead**: Neo4j can be slow on first connection
   - Keep Neo4j Desktop running continuously
   - Don't restart database frequently

2. **Optimize Smart Connections**: Large vault = slow embeddings
   - Disable auto-embedding in Smart Connections settings
   - Run manual embedding batches weekly instead

3. **Simplify taxonomy**: Deep hierarchies = more processing
   - Keep depth ≤ 5 levels when possible
   - Merge overly specific areas

### Reduce Disk Usage

**If `.smart-env/` is too large** (>1 GB):

1. **Clear old embeddings**:
   ```bash
   # Delete and re-generate
   rm -r .smart-env/*
   # Then: Smart Connections → Settings → Re-index vault
   ```

2. **Exclude folders**: In Smart Connections settings, exclude:
   - `_system/logs/`
   - `00-Inbox/raw-conversations/`
   - `.playwright-mcp/`

### Speed Up File Watcher

**If detection is slow** (>10 seconds):

1. **Check polling interval**: Should be 3 seconds (default)
2. **Use SSD**: File watcher performs better on SSD vs HDD
3. **Reduce watched files**: Only watch `raw-conversations/` folder

---

## Frequently Asked Questions

### Q: Do I need to keep file watcher running all the time?

**A**: Yes, for automatic processing. If you stop it, files won't be detected until you restart. You can restart anytime and it will catch up.

### Q: Can I manually edit processed conversation files?

**A**: Yes, but be careful not to break frontmatter YAML. Edits won't be reflected in Neo4j unless you reprocess the file.

### Q: How do I delete an entity from the knowledge graph?

**A**: Use Neo4j Browser:
```cypher
MATCH (n:Entity {name: 'EntityToDelete'})
DETACH DELETE n
```

Or ask processing-pipeline-agent to delete it using neo4j MCP.

### Q: Can I use this with ChatGPT conversations?

**A**: Yes! Export ChatGPT conversations to markdown, name them `unprocessed_chatgpt_001.md`, and drop them in raw-conversations folder.

### Q: What if I don't want an area the AI proposed?

**A**: In `new-areas-queue.md`, select **Ignore** for that proposal. It won't be created and won't be re-proposed.

### Q: Can I customize the 8-stage processing pipeline?

**A**: Yes, edit `_system/processing-pipeline-protocol.md` to modify agent behavior. Be careful not to break core logic.

### Q: How much does this cost to run?

**A**: Zero recurring costs (assuming you have Claude Desktop). Neo4j Desktop is free. No OpenAI API needed. Claude Code uses your Max subscription (not API calls).

### Q: Can I run this on Mac/Linux?

**A**: Mostly yes, but file_watcher.py uses Windows-specific terminal commands (`wt.exe`). You'd need to adapt terminal launching for Mac/Linux.

### Q: What happens if processing fails mid-pipeline?

**A**: File remains as `processing_*.md`. Check `docs/pipeline_agent/processing_log_*.md` for error details. You can manually retry by activating the agent again.

---

*For system architecture details, see `architecture.md`*
*For data structures, see `data-models.md`*
*For codebase structure, see `source-tree-analysis.md`*
