# The Second Brain

> **An AI-powered personal knowledge management system that automatically captures, organizes, and interconnects your conversations and knowledge.**

---

## What is This?

The Second Brain is an automated system that:

- **Captures conversations** from Claude Code and other AI tools
- **Intelligently tags** content using AI analysis
- **Builds a knowledge graph** in Neo4j with semantic connections
- **Organizes knowledge** in Obsidian with flexible taxonomy (2-8 levels)
- **Tracks time and proficiency** across projects and skills
- **Calculates brain space** based on graph coverage, connections, and time invested
- **Processes batches** efficiently when importing large conversation dumps
- **Discovers knowledge areas** organically from your actual data

**Technologies**: Claude Code agents, Neo4j graph database, Obsidian, Python file watcher, MCP (Model Context Protocol)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    YOU (Human User)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ "update memory"
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Memory Update Agent (Manual)                   │
│  - Extracts current conversation from Claude Code           │
│  - Saves to: 00-Inbox/raw-conversations/unprocessed_*.md   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ File created
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         File Watcher (Python - Always Running)              │
│  - Detects new unprocessed_*.md files                       │
│  - Renames to processing_*.md                               │
│  - Updates processing-queue.md                              │
│  - Determines batch mode vs single mode                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Queue updated
                     ▼
┌─────────────────────────────────────────────────────────────┐
│     Processing Pipeline Agent (Checks every 5 min)          │
│  - Reads processing-queue.md                                │
│  - Processes files through 8-stage pipeline:                │
│    1. Entity Extraction (Neo4j)                             │
│    2. Tag Assignment                                        │
│    3. Area Matching                                         │
│    4. Time Estimation (30-min idle detection)               │
│    5. Novelty Detection                                     │
│    6. Note Creation (in appropriate area folder)            │
│    7. Node Updates (bidirectional linking)                  │
│    8. Finalization (rename processing_ → processed_)        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Knowledge Stored In:                       │
│  - Obsidian Vault (markdown notes with metadata)            │
│  - Neo4j Graph Database (entities + relationships)          │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

Before setting up The Second Brain, ensure you have:

### Required Software

- **Claude Code** (installed at C:\ for system-level access)
- **Obsidian** (with vault at `C:\Obsidian-memory-vault`)
- **Neo4j Desktop** (running locally)
- **Python 3.8+** (with pip)
- **Node.js** (for MCP servers via uvx/npx)

### Required MCP Servers

You need these MCP servers configured in your Claude Desktop config:

1. **Neo4j MCP Server** - For knowledge graph interactions
2. **Obsidian MCP Server** - For markdown note management

---

## Installation

### Step 1: Verify Neo4j Setup

1. Open **Neo4j Desktop**
2. Ensure you have a database created (e.g., "SecondBrain")
3. **Start the database**
4. Note your connection details:
   - URL: `neo4j://127.0.0.1:7687` (default)
   - Username: `neo4j` (default)
   - Password: (whatever you set during setup)

### Step 2: Verify MCP Configuration

1. Open: `C:\Users\<YourUsername>\AppData\Roaming\Claude\claude_desktop_config.json`

2. Verify it contains (at minimum):

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
    },
    "obsidian": {
      "command": "npx",
      "args": ["-y", "@your-obsidian-mcp-package"]
    }
  }
}
```

3. **Restart Claude Desktop** after any config changes

### Step 3: Install Python Dependencies

```bash
# Navigate to vault
cd C:\Obsidian-memory-vault

# Install dependencies
pip install -r requirements.txt
```

This installs:
- `watchdog` - For file watching

### Step 4: Create Claude Code Agents

1. Open **Claude Desktop**
2. Go to **Settings** → **Agents**
3. Create two agents:

#### Agent 1: memory-update-agent

- **Name**: `memory-update-agent`
- **Working Directory**: `C:\Obsidian-memory-vault`
- **Prompt File**: `_system/memory-update-protocol.md`
- **Tools**: Read, Write, Bash

#### Agent 2: processing-pipeline-agent

- **Name**: `processing-pipeline-agent`
- **Working Directory**: `C:\Obsidian-memory-vault`
- **Prompt File**: `_system/processing-pipeline-protocol.md`
- **Tools**: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
- **MCP Servers**: neo4j, obsidian (inherited from Claude Desktop config)

### Step 5: Verify Folder Structure

Your vault should have this structure:

```
C:\Obsidian-memory-vault\
├── README.md (this file)
├── requirements.txt
├── _system\
│   ├── config.json
│   ├── area-taxonomy.json
│   ├── tag-taxonomy.md
│   ├── memory-update-protocol.md
│   ├── processing-pipeline-protocol.md
│   ├── processing-queue.md
│   └── new-areas-queue.md
├── 00-Inbox\
│   └── raw-conversations\
│       └── (conversation files will appear here)
├── scripts\
│   └── file_watcher.py
└── (knowledge area folders will be created here as needed)
```

---

## Usage

### Daily Workflow

#### 1. Start the File Watcher (Once)

Open a terminal and run:

```bash
cd C:\Obsidian-memory-vault
python scripts\file_watcher.py
```

**Keep this terminal open.** It will monitor for new conversation files.

You should see:
```
The Second Brain - File Watcher
============================================================
✅ File watcher is running!
   Press Ctrl+C to stop

Monitoring for new conversation files...
```

#### 2. Start the Processing Pipeline Agent (Once)

Open **another terminal** (separate from file watcher):

```bash
# Open Claude Code at system level
cd C:\

# Launch the processing-pipeline-agent
# (Use Claude Desktop to start the agent)
```

In Claude Desktop, navigate to the `processing-pipeline-agent` and it will automatically read its protocol from `_system/processing-pipeline-protocol.md`.

The agent will check the processing queue every 5 minutes.

#### 3. Capture Conversations

Whenever you're in a Claude Code conversation you want to save:

**In your main Claude Code session**, say:
```
update memory
```

This triggers the **memory-update-agent** which will:
- Extract the complete conversation
- Save it as `unprocessed_conversation_YYYYMMDD_###.md`
- Place it in `00-Inbox/raw-conversations/`

#### 4. Automatic Processing

Once saved:

1. **File Watcher** detects the new file
2. Renames it to `processing_*.md`
3. Adds entry to `_system/processing-queue.md`
4. **Processing Pipeline Agent** (checking every 5 min) picks it up
5. Processes through 8-stage pipeline
6. Creates organized note in appropriate knowledge area
7. Updates Neo4j graph with entities and relationships
8. Renames to `processed_*.md` when complete

#### 5. Review Proposed Knowledge Areas

Periodically check: `_system/new-areas-queue.md`

When the AI discovers potential new knowledge areas, they appear here for your approval:

- **Approve** - Accept as-is
- **Edit Name** - Approve with different name
- **Merge** - Merge with existing area
- **Ignore** - Reject (too specific/temporary)

After approving, the areas are added to `_system/area-taxonomy.json` and used for organizing future notes.

---

## Configuration

### System Settings

Edit `_system/config.json` to customize:

**Batch Processing Thresholds**:
```json
"batch_processing": {
  "min_file_count": 5,
  "large_file_threshold_chars": 100000,
  "total_batch_threshold_chars": 500000
}
```

**Time Tracking**:
```json
"time_tracking": {
  "idle_gap_minutes": 30,
  "default_session_minutes": 5
}
```

**Knowledge Scoring Weights**:
```json
"knowledge_scoring": {
  "graph_percentage_weight": 0.70,
  "connection_density_weight": 0.15,
  "time_invested_weight": 0.15
}
```

### Tag Taxonomy

Edit `_system/tag-taxonomy.md` to:
- Add new tags for your specific tech stack
- Define aliases for entity resolution
- Update hierarchical categories

### Area Taxonomy

The `_system/area-taxonomy.json` file is **data-driven** and grows organically.

- AI discovers areas from your conversations
- Proposes them in `new-areas-queue.md`
- You approve/edit/merge/reject
- Approved areas added to taxonomy

**Don't manually edit this file** unless you know what you're doing. Let the system discover your knowledge structure naturally.

---

## Testing the System

### Test 1: File Watcher

1. Start file watcher: `python scripts\file_watcher.py`
2. Manually create a test file:
   ```
   C:\Obsidian-memory-vault\00-Inbox\raw-conversations\unprocessed_test_001.md
   ```
3. Watch the terminal - you should see:
   ```
   📥 Detected new file: unprocessed_test_001.md
   ✏️  Renamed to: processing_test_001.md
   ✅ Updated processing queue: 1 file(s) added
   ```

### Test 2: Memory Update Agent

1. In Claude Code, open the `memory-update-agent`
2. Say: "update memory"
3. Agent should extract the conversation and save to raw-conversations folder
4. File watcher should detect it

### Test 3: Processing Pipeline Agent

1. Ensure there's a file in the processing queue (`_system/processing-queue.md`)
2. Open the `processing-pipeline-agent`
3. It will automatically check the queue and process files
4. Watch as it:
   - Extracts entities
   - Assigns tags
   - Matches/creates areas
   - Creates organized note
   - Updates Neo4j graph

### Test 4: Neo4j Connection

1. Open Neo4j Desktop and ensure database is running
2. In the `processing-pipeline-agent`, try:
   ```
   Use the neo4j MCP to query all entities
   ```
3. Should return entities if any exist, or empty list if fresh database

---

## Batch Processing

### When to Use Batch Mode

Batch processing automatically triggers when:
- **5+ files** are added at once, OR
- **Single file > 100,000 characters**, OR
- **Total batch > 500,000 characters**

### Importing Large Conversation Dumps

If you have a large export from ChatGPT, Claude, or other sources:

1. **Prepare the files**:
   - Convert to markdown if needed
   - Name them: `unprocessed_source_001.md`, `unprocessed_source_002.md`, etc.
   - Add basic frontmatter if possible

2. **Place in raw-conversations folder**:
   ```
   C:\Obsidian-memory-vault\00-Inbox\raw-conversations\
   ```

3. **File watcher will**:
   - Detect all files
   - Recognize as batch (5+ files)
   - Add to queue with "Batch" mode flag

4. **Processing Pipeline Agent will**:
   - Tag **all files first** (globally)
   - Analyze tag frequency across all files
   - Discover knowledge areas from tag clusters
   - Match files to discovered areas
   - Process efficiently

**Benefits of batch mode**:
- More accurate area discovery (sees full picture)
- Better tag clustering
- Prevents fragmenting related knowledge
- Faster than sequential processing

---

## Troubleshooting

### File Watcher Not Detecting Files

**Symptoms**: Drop file in raw-conversations, nothing happens

**Fixes**:
1. Check file watcher is running: `python scripts\file_watcher.py`
2. Ensure filename starts with `unprocessed_`
3. Ensure file extension is `.md`
4. Check terminal for error messages

### Processing Pipeline Agent Not Processing

**Symptoms**: Files stuck in queue for >1 hour

**Fixes**:
1. Ensure `processing-pipeline-agent` is running
2. Check Neo4j database is running (Neo4j Desktop)
3. Verify MCP configuration in Claude Desktop config
4. Restart Claude Desktop if config changed
5. Check `_system/processing-queue.md` for error messages

### Neo4j Connection Failed

**Symptoms**: Agent reports "Cannot connect to Neo4j"

**Fixes**:
1. Open Neo4j Desktop
2. Ensure database is **started** (play button)
3. Check connection details in Claude Desktop config:
   - URI: `neo4j://127.0.0.1:7687`
   - Username: `neo4j`
   - Password: (your password)
4. Test connection in Neo4j Browser
5. Restart Claude Desktop

### MCP Server Not Found

**Symptoms**: "Tool not available" or "MCP server not found"

**Fixes**:
1. Check `isUsingBuiltInNodeForMcp: true` is at **root level** of config (not inside mcpServers)
2. Verify MCP servers defined in config
3. Ensure Node.js is installed (`node --version`)
4. Restart Claude Desktop after config changes
5. Try manually installing: `uvx mcp-neo4j-memory@0.4.2`

### Areas Not Being Discovered

**Symptoms**: All notes go to root, no area structure

**Fixes**:
1. Check `_system/new-areas-queue.md` for pending proposals
2. Approve proposed areas
3. Add approved areas to `_system/area-taxonomy.json`
4. Process more conversations (need 3+ related conversations to discover area)
5. Ensure tag-taxonomy.md has relevant tags defined

### File Watcher Crashes

**Symptoms**: Python script exits unexpectedly

**Fixes**:
1. Check for syntax errors: `python scripts\file_watcher.py`
2. Ensure watchdog installed: `pip install watchdog`
3. Check file paths in script match your vault location
4. Run with error output: `python scripts\file_watcher.py 2> errors.log`

---

## Advanced Usage

### Customizing Tag Taxonomy

Edit `_system/tag-taxonomy.md` to add your specific technologies:

```yaml
# Example: Add a new framework
flutter:
  aliases: []
  category: tech/programming
  parent: [mobile, dart]
  description: Flutter mobile framework
```

### Adjusting Knowledge Scoring

Edit weights in `_system/config.json`:

```json
"knowledge_scoring": {
  "graph_percentage_weight": 0.70,   // How much of total knowledge this area covers
  "connection_density_weight": 0.15, // How interconnected entities are
  "time_invested_weight": 0.15       // Time spent on this area
}
```

### Manual Entity Creation

You can manually add entities to Neo4j using the processing-pipeline-agent:

```
In processing-pipeline-agent, say:
"Create a new entity called 'Docker' with type 'technology' and properties category='infrastructure'"
```

The agent will use the neo4j MCP to create it.

### Viewing the Knowledge Graph

1. Open **Neo4j Desktop**
2. Click **Open** on your database (opens Neo4j Browser)
3. Run Cypher queries:

```cypher
// View all entities
MATCH (n) RETURN n LIMIT 25

// View all relationships
MATCH (a)-[r]->(b) RETURN a, r, b LIMIT 25

// Find entities by tag
MATCH (n {tag: 'python'}) RETURN n

// Find most connected entities
MATCH (n)-[r]-()
RETURN n.name, count(r) as connections
ORDER BY connections DESC
LIMIT 10
```

### Brain Space Calculation

Brain space scores are calculated automatically during processing using:

**Formula**: `brain_space_score = (graph_percentage * 0.70) + (connection_density * 0.15) + (time_invested * 0.15)`

**Components**:
- **Graph Percentage**: What % of total knowledge graph this area represents
- **Connection Density**: How interconnected entities within this area are
- **Time Invested**: Total time spent on conversations in this area

**Recency Score** (separate): `recency_score = exp(-days_since_last_activity / 30)`

Scores are stored in `_system/area-taxonomy.json` and can be visualized in Obsidian.

---

## File Naming Conventions

### Raw Conversation Files

- **Unprocessed**: `unprocessed_conversation_YYYYMMDD_###.md`
- **Processing**: `processing_conversation_YYYYMMDD_###.md`
- **Processed**: `processed_conversation_YYYYMMDD_###.md`

### Created Notes

Notes are created in knowledge area folders with format:
```
[Area]/[Subarea]/YYYY-MM-DD - [Title].md
```

Example:
```
Technology/Programming/Python/2025-11-07 - FastAPI Authentication Setup.md
```

---

## Maintenance

### Weekly Tasks

- **Review new-areas-queue.md**: Approve/reject proposed knowledge areas
- **Check processing-queue.md**: Ensure no files stuck in processing
- **View Neo4j graph**: Explore new connections and entities

### Monthly Tasks

- **Review area taxonomy**: Merge similar areas if needed
- **Update tag taxonomy**: Add new tags for emerging topics
- **Archive old processed files**: Move from raw-conversations to archive folder
- **Backup Neo4j database**: Export graph database

### Quarterly Tasks

- **Analyze knowledge growth**: Review brain space scores by area
- **Restructure taxonomy**: Move areas to better parents if needed
- **Prune unused areas**: Remove areas with 0 notes after 6 months
- **Update documentation**: Revise this README based on learnings

---

## FAQ

### Q: Do I need to keep the file watcher running all the time?

**A**: Yes, for automatic processing. If you stop it, files won't be detected. You can restart it anytime and it will catch up.

### Q: Can I manually edit processed conversation files?

**A**: Yes, but be careful not to break the frontmatter YAML. Edits won't be reflected in Neo4j unless you reprocess the file.

### Q: How do I delete an entity from the knowledge graph?

**A**: Use the `processing-pipeline-agent` and ask it to delete using the neo4j MCP, or manually in Neo4j Browser with Cypher.

### Q: Can I use this with ChatGPT conversations?

**A**: Yes! Export your ChatGPT conversations to markdown, name them `unprocessed_chatgpt_001.md`, and drop them in raw-conversations folder.

### Q: What if I don't want an area the AI proposed?

**A**: In `new-areas-queue.md`, select **Ignore** for that proposal. It won't be created and won't be re-proposed.

### Q: Can I customize the 8-stage processing pipeline?

**A**: Yes, edit `_system/processing-pipeline-protocol.md` to modify agent behavior. Be careful not to break the core logic.

### Q: How much does this cost to run?

**A**: Zero recurring costs (assuming you have Claude Desktop). Neo4j Desktop is free. No OpenAI API needed.

---

## Credits

**Created by**: [Your Name]
**Version**: 1.0
**Last Updated**: 2025-11-07

**Technologies Used**:
- [Claude Code](https://claude.ai/claude-code) - AI orchestration and agents
- [Neo4j](https://neo4j.com/) - Knowledge graph database
- [Obsidian](https://obsidian.md/) - Markdown note-taking
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol
- [Watchdog](https://github.com/gorakhargosh/watchdog) - Python file watching

---

## License

This is your personal knowledge management system. Use and modify as you see fit.

---

## Support

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review agent protocol files in `_system/` for detailed instructions
3. Check `_system/processing-queue.md` for error messages
4. Verify Neo4j database is running
5. Ensure MCP servers are configured correctly

**Happy knowledge building!** 🧠
