---
# === REQUIRED METADATA ===
type: conversation
title: "{{title}}"
created: {{created_date}}
session_id: "{{session_id}}"
source: claude-code-cli

# === PROCESSING STATUS ===
processing:
  status: raw  # raw → processing → processed → reviewed
  processed_date: null
  ai_tagged: false
  entities_extracted: false
  graph_synced: false

# === CONTENT CLASSIFICATION ===
content_types: []  # AI fills: learning, development, troubleshooting, planning, etc.
primary_focus: ""  # AI determines main focus

# === LINKING (AI-populated) ===
projects: []  # [[Project - Name]] links
skills: []    # {name: [[Skill]], proficiency_change: +N, status: learning/practicing}
concepts: []  # [[Concept - Name]] links

# === TAGS (AI-generated from taxonomy) ===
tags: []

# === TEMPORAL CONTEXT ===
date: {{date}}
week: {{week}}  # e.g., 2025-W45
quarter: {{quarter}}  # e.g., Q4-2025

# === METRICS ===
metrics:
  duration_minutes: 0
  message_count: 0
  tools_used: []
  files_modified: 0

# === GRAPH SYNC ===
graph:
  episode_id: null
  entities_created: 0
  relationships_created: 0
  last_sync: null
---

# {{title}}

## Summary
<!-- AI-generated 2-3 sentence summary -->

## Key Outcomes
<!-- AI extracts main achievements/learnings -->
-

## Conversation
<!-- Full conversation transcript goes here -->
