---
type: project
title: "{{project_name}}"
created: {{created_date}}

# === STATUS ===
status: planning  # planning → active → paused → completed → archived
priority: medium  # low | medium | high | critical

# === CLASSIFICATION ===
category: ""  # development, research, personal, learning
subcategory: ""  # web, cli, api, infrastructure, etc.

# === LIFECYCLE ===
lifecycle:
  started: {{started_date}}
  target_completion: null
  last_activity: {{last_activity}}
  completion_percentage: 0

# === TAGS ===
tags: []

# === RELATIONSHIPS ===
skills_required: []  # [[Skill - Name]]
related_projects: []  # [[Project - Name]]
parent_project: null  # [[Parent Project]] if this is a subproject

# === TRACKING ===
repository: ""  # GitHub URL if applicable
documentation: ""  # Link to docs

# === TASKS ===
tasks:
  total: 0
  completed: 0
  in_progress: 0
  blocked: 0

# === CONVERSATIONS ===
conversations: []  # Auto-populated by pipeline: [[conversation links]]

# === GRAPH ===
graph_entity_id: null
---

# {{project_name}}

## Overview
<!-- High-level description of what this project is -->

## Goals
- [ ] Goal 1
- [ ] Goal 2

## Current Status
<!-- What's happening now -->

## Next Steps
- [ ] Next action 1
- [ ] Next action 2

## Blockers
<!-- What's preventing progress -->

## Related Conversations
<!-- Auto-populated via dataview -->
```dataview
LIST
FROM "conversations"
WHERE contains(projects, this.file.link)
SORT created DESC
LIMIT 10
```

## Notes
<!-- Freeform notes, thoughts, decisions -->
