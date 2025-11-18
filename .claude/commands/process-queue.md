---
description: Process conversations from queue (activated by file watcher)
---

# Processing Queue Activation

You have been **activated by the file watcher system** to process unprocessed conversations.

## Your Task

Process all files in the processing queue following the complete 8-stage pipeline.

### Step 1: Read the Queue

Read `_system/processing-queue.md` to find files awaiting processing (unchecked boxes).

### Step 2: Process Each File

For EACH unchecked file in the queue:

1. **Follow the complete protocol**: Read and execute `_system/processing-pipeline-protocol.md`
2. **Execute ALL 8 stages**:
   - Stage 1: Entity Extraction
   - Stage 2: Metadata Extraction
   - Stage 3: Taxonomy Matching
   - Stage 4: Temporal Analysis
   - Stage 5: Area Classification
   - Stage 6a: Create Conversation Node
   - **Stage 6b: Create/Update Tag Notes** (NEW - ACTIVE)
   - Stage 7: Neo4j Sync (skip if unavailable)
   - Stage 8: Finalize

3. **Stage 6b is CRITICAL**:
   - Read `_system/stage-6b-tag-notes-prompt.md` for complete instructions
   - You MUST create/update tag notes for every entity
   - Add knowledge entries with timestamps
   - Include hashtag field, parent links, hierarchy sections
   - Use Python modules: `TagNoteManager`, `TagKnowledgeExtractor`

### Step 3: Mark Complete

After processing each file:
- Check the box in `_system/processing-queue.md`
- Add completion details

### Step 4: Write Completion Signal

When ALL files are processed:

```python
with open('_system/agent_completion_signal.txt', 'w') as f:
    f.write('COMPLETE')
```

### Important Notes

- You have `--dangerously-skip-permissions` enabled
- Execute without asking for confirmations
- Process thoroughly - this is critical knowledge capture
- Stage 6b must create tag notes in hierarchical folders
- Verify tag notes have `tags:` field for hashtag merging

---

## Execution

Process the queue now. Report summary when complete.
