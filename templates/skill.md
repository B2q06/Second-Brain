---
type: skill
title: "{{skill_name}}"
created: {{created_date}}

# === CLASSIFICATION ===
category: ""  # programming, design, tools, soft-skills, domain-knowledge
subcategory: ""  # e.g., backend, frontend, databases

# === PROFICIENCY TRACKING ===
proficiency:
  level: novice  # novice → beginner → intermediate → advanced → expert
  numeric: 0  # 0-100 scale for granular tracking
  last_assessed: {{today}}

# === LEARNING STATUS ===
learning:
  status: learning  # learning → practicing → maintaining → mastered
  started: {{started_date}}
  practice_hours: 0
  last_practiced: null

# === TAGS ===
tags: []

# === RELATIONSHIPS ===
related_skills: []  # [[Skill - Name]] - prerequisites or complementary
resources: []  # [[Resource - Name]] - books, courses, docs
projects_using: []  # [[Project - Name]] - auto-populated

# === GOALS ===
learning_goals: []
next_steps: []

# === CONVERSATIONS ===
conversations: []  # Auto-populated when skill mentioned in sessions

# === GRAPH ===
graph_entity_id: null
---

# {{skill_name}}

## About
<!-- What is this skill, why learning it -->

## Learning Path
<!-- How you're approaching learning this -->

## Practice Projects
<!-- Projects where you're applying this skill -->
```dataview
LIST
FROM "10-Projects"
WHERE contains(skills_required, this.file.link)
```

## Progress Log
<!-- Milestones, breakthroughs, challenges -->

### {{date}}
-

## Resources
<!-- Links, tutorials, documentation -->
