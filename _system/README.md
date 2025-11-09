---
type: meta
title: Vault System Documentation
created: 2025-11-07
---

# Obsidian Memory Vault - System Documentation

## Overview This vault is designed as an automated personal knowledge management system that captures, organizes, and interconnects your learning, projects, and skills from AI conversations and other sources.
---

## Folder Structure

```
Obsidian-memory-vault/
├── templates/                 # Note templates for automation
│   ├── conversation.md        # AI conversation capture template
│   ├── project.md            # Project tracking template
│   ├── skill.md              # Skill development template
│   └── knowledge.md          # Knowledge/concept template
│
├── _system/                   # System files (don't edit during automation)
│   ├── tag-taxonomy.md       # Master tag list for AI consistency
│   ├── tag-review-queue.md   # Proposed tags awaiting approval
│   └── README.md             # This file
│
├── 00-Inbox/                  # Unprocessed captures
│   └── raw-conversations/    # Raw conversation imports land here
│
├── 10-Projects/               # PARA: Active projects
│   # Your project notes go here
│   # Status: planning → active → paused → completed
│
├── 20-Areas/                  # PARA: Areas of responsibility
│   # Ongoing areas of focus (career, health, etc.)
│
├── 30-Resources/              # PARA: Reference material
│   ├── skills/               # Skill tracking notes
│   └── knowledge/            # Concepts, patterns, references
│
├── 40-Archive/                # PARA: Completed/inactive items
│   # Old projects, outdated notes
│
|
└── 50-Meta/                   # Meta organization
|   └── dashboards/           # Dataview dashboards for overview
```

---

## PARA Method

This vault uses the PARA method for organization:

- **Projects** (10-): Short-term efforts with goals and deadlines
- **Areas** (20-): Long-term responsibilities you maintain
- **Resources** (30-): Topics of interest, reference material
- **Archive** (40-): Inactive items from other categories

**Flow**: Items move from Inbox → Projects/Areas/Resources → Archive over time

---

## Template Usage

### Conversation Template
**Used for**: Every Claude Code session, chat exports
**Auto-populated by**: AI processing pipeline
**Key fields**: projects (linked), skills (with proficiency changes), tags

### Project Template
**Used for**: Any project you're working on
**Updated by**: AI when conversations mention the project
**Key fields**: status, lifecycle, tasks, conversations

### Skill Template
**Used for**: Tracking learning and skill development
**Updated by**: AI when skills are practiced in conversations
**Key fields**: proficiency (0-100), learning status, practice hours

### Knowledge Template
**Used for**: Concepts, patterns, reference notes
**Created by**: Manual or AI extraction from conversations
**Key fields**: knowledge_type, confidence, related_concepts

---

## Tag Taxonomy

See `_system/tag-taxonomy.md` for the complete tag system.

**Key principles**:
1. Use existing tags when possible
2. AI proposes new tags to user Tag Review Queue
3. Human reviews and approves/rejects proposals
4. Hierarchy: `category/subcategory/specific`

**Core categories**:
- `tech/*` - Technology, programming, tools
- `learning/*` - Education, courses, practice
- `project/*` - Project phases (planning, development, debugging)
- `domain/*` - Fields (web, mobile, data, security)
- `skill/*` - Skill areas (backend, frontend, devops)

---

## Automation Pipeline

**Workflow**:
1. **Capture**: Claude Code session saved to ~/.claude/projects/
2. **Watch**: File watcher detects new session
3. **Parse**: Convert JSONL to structured data
4. **Enrich**: AI generates title, summary, tags
5. **Extract**: Graphiti extracts entities (projects, skills, concepts)
6. **Resolve**: Check if entities are new or existing
7. **Store**: Save to Obsidian (markdown) + Graphiti (knowledge graph)
8. **Link**: Update related project/skill notes

**Status tracking** in frontmatter:
- `raw` - Just imported, not processed
- `processing` - Currently being analyzed
- `processed` - AI enrichment complete
- `reviewed` - Human has reviewed/edited

---

## Dataview Queries

Use Dataview plugin to create dynamic views:

### Recent Conversations
```dataview
LIST
FROM "00-Inbox" OR "10-Projects" OR "30-Resources"
WHERE type = "conversation"
SORT created DESC
LIMIT 10
```

### Active Projects
```dataview
TABLE status, priority, lifecycle.last_activity as "Last Activity"
FROM "10-Projects"
WHERE type = "project" AND status = "active"
SORT lifecycle.last_activity DESC
```

### Skills Being Learned
```dataview
TABLE proficiency.level, proficiency.numeric, learning.last_practiced
FROM "30-Resources/skills"
WHERE type = "skill" AND learning.status = "learning"
SORT learning.last_practiced DESC
```

---

## Getting Started

### Phase 1: Manual Testing (Do This First!)
1. ✅ Templates created (done!)
2. ✅ Tag taxonomy created (done!)
3. ✅ Folder structure created (done!)
4. ⬜ Create 1-2 test notes using templates
5. ⬜ Practice linking notes together
6. ⬜ Test Dataview queries
7. ⬜ Customize tag taxonomy for your tech stack

### Phase 2: Graphiti Setup
1. ⬜ Install Neo4j Desktop
2. ⬜ Create "memory-graph" database
3. ⬜ Test Graphiti connection
4. ⬜ Manual entity creation test

### Phase 3: MCP Server Installation
1. ⬜ Install Obsidian MCP server
2. ⬜ Install Graphiti/Memento MCP
3. ⬜ Test MCP connections
4. ⬜ Verify can read/write notes via MCP

### Phase 4: Automation
1. ⬜ Create file watcher script
2. ⬜ Build processing pipeline
3. ⬜ Setup background service
4. ⬜ Process first conversation automatically

---

## Best Practices

### For Humans
- Review Tag Review Queue weekly
- Update projects with current status
- Archive completed projects monthly
- Refine tag taxonomy based on usage
- Add manual notes for insights not captured in conversations

### For AI Agents
- Always check tag taxonomy before tagging
- Propose uncertain tags to review queue
- Update project last_activity dates
- Link conversations to relevant entities
- Use confidence thresholds (>0.85 auto, <0.60 new)

### Maintenance
- **Daily**: Process new conversations automatically
- **Weekly**: Review tag proposals, update project statuses
- **Monthly**: Archive completed items, consolidate tags
- **Quarterly**: Backup vault, review taxonomy, optimize queries

---

## Knowledge Graph Integration

**Obsidian stores**: Human-readable markdown with full content
**Graphiti stores**: Semantic relationships, entities, temporal data

**When to query Graphiti**:
- Semantic search ("find similar concepts")
- Entity resolution ("is this project new?")
- Relationship traversal ("what skills does this project use?")
- Temporal queries ("what was I working on in October?")

**When to use Obsidian**:
- Reading full conversations
- Manual editing and curation
- Visual graph view
- Daily note-taking
- Human review

---

## Troubleshooting

### Conversations not being processed
- Check file watcher is running: `systemctl --user status claude-watcher`
- Check logs: `~/logs/pkm-automation.log`
- Verify idle detection threshold (default 5 min)

### Tags not consistent
- Review Tag Review Queue for proposals
- Update aliases in tag taxonomy
- Check entity resolution confidence thresholds

### Dataview queries not working
- Ensure Dataview plugin is enabled
- Check frontmatter field names match exactly
- Verify file paths in FROM clauses

### Links broken
- Use [[Note Title]] format, not file paths
- Ensure linked notes exist in vault
- Check for typos in note names

---

## Customization

### Adding Your Tech Stack
Edit `_system/tag-taxonomy.md` and add your specific:
- Programming languages
- Frameworks you use
- Tools in your workflow
- Domains you work in

### Changing Folder Structure
If you prefer different organization:
1. Update folder paths in processing scripts
2. Update Dataview queries to match new paths
3. Move existing notes to new locations
4. Update template file paths

### Custom Templates
Create additional templates for:
- Meeting notes
- Book summaries
- Course notes
- Research papers
- Code snippets

Store in `templates/` and reference in processing pipeline.

---

## Next Steps

Now that your vault structure is set up:

1. **Test the templates** - Manually create notes using each template
2. **Customize tag taxonomy** - Add/remove tags based on your actual work
3. **Install Neo4j** - Complete the knowledge graph setup
4. **Extract test conversations** - Get 2-3 real Claude conversations
5. **Manual tagging practice** - Apply tags manually to understand the system

Once comfortable with manual workflow, move to automation in Phase 3!

---

## Resources

- Obsidian Dataview: https://blacksmithgu.github.io/obsidian-dataview/
- PARA Method: https://fortelabs.com/blog/para/
- Neo4j Graph Database: https://neo4j.com/docs/
- Graphiti: https://github.com/getzep/graphiti
- MCP Protocol: https://modelcontextprotocol.io/

---

**Version**: 1.0
**Last Updated**: 2025-11-07
**Status**: Initial setup complete, ready for testing
