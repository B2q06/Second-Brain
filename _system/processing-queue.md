---
type: meta
title: Processing Queue
created: 2025-11-07
status: active
---

# Processing Queue

> **Purpose**: Track files awaiting processing by the Processing Pipeline Agent
>
> **How it works**:
> 1. File watcher detects new `unprocessed_*.md` files
> 2. Renames them to `processing_*.md`
> 3. Adds entry here
> 4. Processing Pipeline Agent checks this file every 5 minutes
> 5. Processes files and marks complete

---

## Files Awaiting Processing

<!-- File watcher will add entries here automatically -->

**Queue Status**: Empty ✅

**Last Check**: Never

---

## Currently Processing

<!-- Processing Pipeline Agent moves files here when actively working on them -->

---

## Completed (Last 24 Hours)

<!-- Successfully processed files - automatically cleaned up after 24 hours -->

---

## Errors

<!-- Failed processing attempts with error messages -->

---

---

## File Entry Template

### Format for Queue Entries

```markdown
## Batch Added: {{TIMESTAMP}}

**Mode**: Batch / Single
**File Count**: X
**Total Size**: Y characters

**Files**:
- [ ] processing_conversation_20251107_001.md
- [ ] processing_conversation_20251107_002.md
- [ ] processing_conversation_20251107_003.md
```

### Format for Completed Entries

```markdown
- [x] processing_conversation_20251107_001.md
  - **Completed**: 2025-11-07 19:45:00
  - **Duration**: 2 minutes
  - **Entities Created**: 8
  - **Tags Assigned**: 6
  - **Primary Area**: Technology > Programming > Automation
  - **Status**: ✅ Success
```

### Format for Error Entries

```markdown
- [x] processing_conversation_20251107_999.md
  - **Failed**: 2025-11-07 20:15:00
  - **Error**: File corrupted / Read error / Neo4j connection failed
  - **Attempts**: 3
  - **Status**: ❌ Failed (manual intervention needed)
  - **Location**: C:/Obsidian-memory-vault/00-Inbox/raw-conversations/processing_conversation_20251107_999.md
```

---

## How to Use This Queue

### For the File Watcher (Python Script)

**When detecting a new file**:

1. Rename: `unprocessed_*.md` → `processing_*.md`
2. Add entry to "Files Awaiting Processing" section
3. Include:
   - Batch or single mode
   - File count
   - Total size (for batch detection)
4. Update "Last Check" timestamp

**Example**:
```python
# Python code in file watcher
with open('processing-queue.md', 'a') as f:
    f.write(f"\n## Batch Added: {datetime.now().isoformat()}\n")
    f.write(f"**Mode**: {'Batch' if batch else 'Single'}\n")
    f.write(f"**File count**: {len(files)}\n\n")
    for file in files:
        f.write(f"- [ ] {file.name}\n")
```

### For the Processing Pipeline Agent (Claude Code)

**Every 5 minutes**:

1. **Read this file**
2. **Check** "Files Awaiting Processing" section
3. **If files present**:
   - Determine batch vs single mode
   - Process through 8-stage pipeline
   - Move to "Currently Processing" while working
   - Mark complete (move to "Completed")
   - Or log error (move to "Errors")
4. **Update** "Last Check" timestamp

**Example workflow**:
```markdown
## Before Processing Starts

### Files Awaiting Processing
- [ ] processing_conversation_20251107_001.md

### Currently Processing
(empty)

---

## During Processing

### Files Awaiting Processing
(empty)

### Currently Processing
- processing_conversation_20251107_001.md
  - Started: 2025-11-07 19:43:00
  - Stage: 3/8 (Area Matching)

---

## After Processing Completes

### Completed (Last 24 Hours)
- [x] processing_conversation_20251107_001.md
  - Completed: 2025-11-07 19:45:00
  - Duration: 2 minutes
  - Status: ✅ Success
```

---

## Auto-Cleanup Rules

**Completed entries**:
- Keep for 24 hours
- After 24 hours, auto-delete to keep file manageable

**Error entries**:
- Keep for 7 days
- After 7 days, move to `_system/error-log-archive.md`

**Awaiting entries**:
- If sitting for >24 hours without processing: Flag as stale
- Alert user to investigate

---

## Status Indicators

| Indicator | Meaning |
|-----------|---------|
| - [ ] | Awaiting processing |
| - [⏳] | Currently processing (in progress) |
| - [x] ✅ | Successfully processed |
| - [x] ❌ | Failed (error occurred) |
| - [x] ⏸️ | Paused (waiting for user input) |
| - [x] 🔄 | Retry scheduled |

---

## Monitoring & Alerts

### When to Alert User

**Alert if**:
- Same file fails 3+ times
- Queue has files waiting >24 hours
- Processing Pipeline Agent hasn't checked in >1 hour
- Critical error in processing

**Alert Format**:
```markdown
## 🚨 ALERT - Action Required

**Issue**: [DESCRIPTION]
**Affected File**: [FILENAME]
**Time Since Last Check**: [DURATION]

**Recommended Action**:
1. [ACTION 1]
2. [ACTION 2]

**Details**: [ERROR MESSAGE OR CONTEXT]
```

### Normal Status Messages

**When queue is healthy**:
```markdown
Queue Status: Empty ✅
Last Check: 2 minutes ago
Next Check: ~3 minutes
```

**When actively processing**:
```markdown
Queue Status: Processing 1 file ⏳
Last Check: 30 seconds ago
Next Check: ~4.5 minutes
```

---

## Example Full Queue

```markdown
# Processing Queue

## Files Awaiting Processing

**Queue Status**: 3 files waiting ⏳
**Last Check**: 1 minute ago

### Batch Added: 2025-11-07T19:40:00Z

**Mode**: Single
**File count**: 1

- [ ] processing_conversation_20251107_002.md

### Batch Added: 2025-11-07T19:42:00Z

**Mode**: Batch
**File count**: 2
**Total Size**: 156,000 characters

- [ ] processing_conversation_20251107_003.md
- [ ] processing_conversation_20251107_004.md

---

## Currently Processing

- processing_conversation_20251107_001.md
  - **Started**: 2025-11-07 19:43:15
  - **Stage**: 5/8 (Novelty Detection)
  - **Elapsed**: 45 seconds

---

## Completed (Last 24 Hours)

- [x] processing_conversation_20251107_001.md
  - **Completed**: 2025-11-07 19:45:00
  - **Duration**: 2 minutes 15 seconds
  - **Entities Created**: 8
  - **Tags Assigned**: 6
  - **Primary Area**: Technology > Programming > Automation
  - **Related Notes Updated**: 3
  - **Status**: ✅ Success

- [x] processing_conversation_20251106_015.md
  - **Completed**: 2025-11-06 23:30:00
  - **Duration**: 1 minute 30 seconds
  - **Status**: ✅ Success

---

## Errors

- [x] processing_conversation_20251107_999.md
  - **Failed**: 2025-11-07 18:30:00
  - **Error**: File appears corrupted - unable to parse frontmatter
  - **Attempts**: 3
  - **Status**: ❌ Failed
  - **Location**: C:/Obsidian-memory-vault/00-Inbox/raw-conversations/processing_conversation_20251107_999.md
  - **Action Needed**: Manual inspection required
```

---

## Troubleshooting

### If Processing Stops

**Symptoms**: Files stuck in "Awaiting" for >1 hour

**Possible Causes**:
1. Processing Pipeline Agent not running
2. Agent crashed or encountered error
3. Neo4j database offline
4. System resource issue

**Resolution**:
1. Check if Processing Pipeline Agent is running
2. Restart the agent if needed
3. Check Neo4j Desktop - ensure database is active
4. Review recent error logs
5. Try processing a single file manually

### If Files Process Too Slowly

**Symptoms**: Each file takes >5 minutes

**Possible Causes**:
1. Neo4j queries are slow
2. Large conversation files
3. System resources constrained

**Resolution**:
1. Check Neo4j query performance
2. Optimize Neo4j indexes
3. Consider batch processing for large dumps
4. Split very large files if needed

### If Errors Accumulate

**Symptoms**: Multiple files in "Errors" section

**Possible Causes**:
1. Systematic issue (Neo4j connection, permissions, etc.)
2. Malformed input files
3. Bug in processing pipeline

**Resolution**:
1. Review common error pattern
2. Fix systematic issue if found
3. Re-queue failed files after fix
4. Report bug if processing logic issue

---

## Statistics

Track over time:

**Daily Metrics**:
- Files processed today: 0
- Average processing time: N/A
- Success rate: N/A
- Error rate: N/A

**All-Time Metrics**:
- Total files processed: 0
- Total entities created: 0
- Total tags assigned: 0
- Total areas discovered: 0

**Last Updated**: 2025-11-07T21:00:00Z

---

**Maintained By**: File Watcher + Processing Pipeline Agent
**Auto-Updated**: Every file detection + every 5 minutes
