---
type: project
title: "{{car_flipping}}"
created:
  "{ created_date }":
status: planning
priority: medium
category: ""
subcategory: ""
lifecycle:
  started:
    "{ started_date }":
  target_completion:
  last_activity:
    "{ last_activity }":
  completion_percentage: 0
tags: []
skills_required: []
related_projects: []
parent_project:
repository: ""
documentation: ""
tasks:
  total: 0
  completed: 0
  in_progress: 0
  blocked: 0
conversations: []
graph_entity_id:
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
