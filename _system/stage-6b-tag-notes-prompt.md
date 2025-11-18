# Stage 6b: Tag Note Creation and Updating

**CRITICAL REQUIREMENT**: This stage MUST be executed for EVERY processed conversation.
**PURPOSE**: Build semantic memory by creating/updating living tag notes that accumulate user knowledge over time.

---

## Overview

After creating the conversation node (Stage 6a), you MUST create or update tag notes for every entity extracted from the conversation. Tag notes are living documents that grow with each conversation, organized in a hierarchical taxonomy.

**This is NOT optional. This stage is MANDATORY.**

---

## Step-by-Step Execution Protocol

### STEP 1: Load Conversation Metadata

1. Read the conversation file from `00-Inbox/processed/`
2. Extract frontmatter YAML
3. Identify ALL entities from these fields:
   - `topics` - Main discussion topics
   - `skills` - Technologies, frameworks, languages
   - `concepts` - Abstract ideas, methodologies
   - `projects` - Project names
4. Create a master list of ALL unique entities
5. Extract conversation timestamp from `captured` field

**Example entities**: `["FastAPI", "Neo4j", "Python", "JWT", "Graph Databases"]`

---

### STEP 2: Load Conversation Body Text

1. Read the conversation file again
2. Extract the full markdown body (everything after frontmatter)
3. This text will be used to extract what the user discussed about each tag
4. Store in memory for knowledge extraction

---

### STEP 3: Execute Tag Note Manager Using Bash Tool

**CRITICAL**: You MUST use the Bash tool to run the Python backfill script. DO NOT manually edit tag notes!

**Use the Bash tool to execute this command**:

```bash
python scripts/backfill_tag_notes.py --vault . --limit 1
```

**What this does automatically**:
- Reads the processed conversation file
- Extracts all entities from frontmatter
- For each entity:
  - Extracts what user discussed about it (using extract_tag_knowledge.py)
  - Creates or updates the tag note (using tag_note_manager.py)
  - Adds timestamped entry under current month section
  - Includes related tags as wikilinks
  - Adds source conversation backlink
  - Updates metadata (total_conversations, total_time_minutes)

**The Python script handles EVERYTHING - you just need to run it via Bash tool!**

---

### STEP 4: Process EACH Entity (Loop)

For EVERY entity in the master list, execute these sub-steps:

#### 4a. Extract User Knowledge About This Tag

```python
# Extract what user discussed about this specific tag
conversation_text = extract_conversation_body(conversation_file_path)
discussion = extractor.extract_tag_discussion(tag_name, conversation_text, max_sentences=4)
```

**CRITICAL**: `discussion` contains ONLY what the user said about this tag in THIS conversation.
**NO external knowledge. NO Wikipedia definitions. ONLY user's words.**

If `discussion` is None or empty, skip this tag (user didn't actually discuss it).

#### 4b. Determine Related Tags

```python
# Other tags from same conversation = related tags
related_tags = manager.extract_related_tags(all_entities, current_tag)
```

Example: If processing "FastAPI", related tags might be `["Neo4j", "Python", "JWT"]`

#### 4c. Create/Update Tag Note

```python
# Extract conversation duration (in minutes)
duration_minutes = extract_conversation_duration(frontmatter)  # Try duration_minutes, total_time_minutes, or estimate

# Get hierarchical path and create tag note
tag_path, created_new = manager.create_or_update_tag_note(
    tag_name=tag_name,
    discussion_text=discussion,
    timestamp=conversation_timestamp,
    conversation_link=f"[[{conversation_filename.replace('.md', '')}]]",
    related_tags=related_tags,
    conversation_duration_minutes=duration_minutes
)
```

**What this does**:
1. Resolves hierarchical path (e.g., `Technology/Programming/Python/FastAPI.md`)
2. Creates folders if they don't exist (`Technology/`, `Programming/`, etc.)
3. If tag note doesn't exist: Creates new one from template
4. If tag note exists: Opens it
5. Adds timestamped entry to current month section (e.g., `## November 2025`)
6. Entry format:
   ```markdown
   ### 2025-11-11 16:30
   [discussion text from extraction]
   **Related**: [[Python]], [[Neo4j]], [[JWT]]
   **Source**: [[conversation_20251111_...]]
   ```
7. Updates frontmatter metadata (last_updated, total_conversations, etc.)
8. Saves file

#### 4d. Verify Tag Note Created

```python
if not tag_path.exists():
    print(f"[!] ERROR: Tag note was NOT created for {tag_name}")
    print(f"[!] Expected path: {tag_path}")
    raise Exception(f"Tag note creation failed for {tag_name}")
```

**If this check fails, STOP and report error. Do NOT continue.**

#### 4e. Log Success

```python
print(f"[✓] Tag note {'created' if created_new else 'updated'}: {tag_name}")
print(f"    Path: {tag_path}")
print(f"    Related: {', '.join(related_tags)}")
```

---

### STEP 5: Check for Month Rollover

After processing all entities:

```python
from scripts.monthly_consolidation import MonthlyConsolidation
from datetime import datetime

# Check if we're in a new month
consolidator = MonthlyConsolidation('C:\\obsidian-memory-vault')

# If first conversation of new month, compress previous month
current_date = datetime.now()
if current_date.day <= 3:  # First 3 days of month
    print("[*] Checking for month rollover...")

    # Find all tag notes
    tag_notes = consolidator.find_all_tag_notes()

    for tag_note in tag_notes:
        # Compress previous month
        consolidator.compress_previous_month_if_needed(tag_note)
```

**Month compression logic**:
- Detects if previous month section exists
- Compresses all entries EXCEPT last-day-of-month entry
- Preserves leap year last days (Feb 29, etc.)
- Adds cross-tag wikilinks in compressed summary
- Example output:
  ```markdown
  ## October 2025
  *Compressed from 8 entries*

  This month's work spanned 8 conversation(s). Built FastAPI endpoints with async patterns. Integrated Neo4j graph database for knowledge storage. Explored JWT authentication and token validation.

  **Related explorations:**
  - [[Neo4j]]
  - [[Python]]
  - [[async-programming]]
  - [[authentication]]

  ### 2025-10-31 14:22
  [Full entry from last day of October preserved]
  **Related**: [[Python]]
  **Source**: [[conversation_20251031_...]]
  ```

---

### STEP 6: Validation and Reporting

1. Count how many tag notes were created vs updated
2. Verify all entities have corresponding tag notes
3. Report summary:
   ```
   [✓] Stage 6b Complete
       Entities processed: 5
       Tag notes created: 2
       Tag notes updated: 3
       Folders created: Technology/Programming/Python/, Technology/Databases/
       Month compression: October 2025 compressed (3 tag notes affected)
   ```

---

## Absolute Requirements (DO NOT DEVIATE)

### ✅ MUST DO:

1. **Process EVERY entity** - Do not skip any
2. **Extract user knowledge ONLY** - No external information
3. **Create folder hierarchy** - Technology/, Language/, History/ etc.
4. **Add timestamped entries** - Format: `### YYYY-MM-DD HH:MM`
5. **Include related tags** - Wikilinks to co-mentioned tags
6. **Include source link** - Backlink to conversation
7. **Preserve last-day entries** - When compressing months
8. **Handle leap years** - February 29 is last day in leap years
9. **Cross-reference tags** - Add wikilinks in compressed summaries
10. **Verify file creation** - Check that tag notes exist after creation

### ❌ MUST NOT DO:

1. **Add external knowledge** - Only capture user's discussion
2. **Skip entities** - Every entity gets a tag note
3. **Hardcode paths** - Use tag taxonomy for hierarchy
4. **Ignore month rollover** - Always check and compress if needed
5. **Compress last-day entries** - They are anchor points
6. **Create tag notes outside taxonomy** - Follow hierarchy
7. **Forget backlinks** - Always link back to conversation
8. **Skip verification** - Always check files were created

---

## Error Handling

If ANY of these errors occur, STOP and report:

1. **Tag note creation failed** - File doesn't exist after creation
2. **Folder creation failed** - Cannot create hierarchy
3. **Knowledge extraction failed** - Cannot parse conversation
4. **Taxonomy not loaded** - Cannot resolve paths
5. **Month compression failed** - Error during compression

**DO NOT silently continue if errors occur.**

---

## Example Full Execution

```python
# Assuming conversation just processed: conversation_20251111_1630_fastapi_neo4j.md

# Entities extracted: ["FastAPI", "Neo4j", "Python", "JWT Authentication", "Graph Databases"]

# For "FastAPI":
discussion = "Explored building REST API endpoints with async/await patterns. Integrated with Neo4j database using official driver. Implemented JWT token validation for protected routes."

related_tags = ["Neo4j", "Python", "JWT Authentication", "Graph Databases"]

tag_path = manager.create_or_update_tag_note(
    tag_name="FastAPI",
    discussion_text=discussion,
    timestamp=datetime(2025, 11, 11, 16, 30),
    conversation_link="[[conversation_20251111_1630_fastapi_neo4j]]",
    related_tags=related_tags
)

# Result:
# File created: C:\obsidian-memory-vault\Technology\Programming\Python\Frameworks\Web\FastAPI.md
# Entry added under "## November 2025"
# Related tags: [[Neo4j]], [[Python]], [[JWT Authentication]], [[Graph Databases]]
# Source: [[conversation_20251111_1630_fastapi_neo4j]]
```

---

## Integration with Processing Pipeline

**When this runs**: After Stage 6a (conversation node creation), before Stage 7 (Neo4j sync)

**How to invoke**:
```python
# In processing-pipeline-agent code
import sys
from pathlib import Path

# CRITICAL: Add vault to Python path first
vault_path = Path.cwd()  # Agent runs from vault root
sys.path.insert(0, str(vault_path))

print("\n[*] Stage 6b: Creating/updating tag notes...")

from scripts.tag_note_manager import TagNoteManager
from scripts.extract_tag_knowledge import TagKnowledgeExtractor, extract_conversation_body
from datetime import datetime

# Initialize
manager = TagNoteManager(vault_path)
extractor = TagKnowledgeExtractor()

# Load conversation
conversation_file = Path(f"{vault_path}/00-Inbox/processed/{conversation_filename}")
frontmatter = extract_frontmatter(conversation_file)
conversation_text = extract_conversation_body(conversation_file)
timestamp = parse_timestamp(frontmatter['captured'])

# Get all entities
all_entities = []
all_entities.extend(frontmatter.get('topics', []))
all_entities.extend(frontmatter.get('skills', []))
all_entities.extend(frontmatter.get('concepts', []))
all_entities.extend(frontmatter.get('projects', []))
all_entities = list(set(all_entities))  # Unique

print(f"[*] Processing {len(all_entities)} entities...")

# Process each entity
created_count = 0
updated_count = 0

for tag_name in all_entities:
    discussion = extractor.extract_tag_discussion(tag_name, conversation_text)

    if not discussion:
        print(f"[-] Skipping {tag_name} (not discussed)")
        continue

    related_tags = manager.extract_related_tags(all_entities, tag_name)

    tag_path, created_new = manager.create_or_update_tag_note(
        tag_name=tag_name,
        discussion_text=discussion,
        timestamp=timestamp,
        conversation_link=f"[[{conversation_filename.replace('.md', '')}]]",
        related_tags=related_tags
    )

    if created_new:
        created_count += 1
    else:
        updated_count += 1

    print(f"[✓] {tag_name} -> {tag_path.name}")

print(f"\n[✓] Stage 6b complete: {created_count} created, {updated_count} updated")

# Check month rollover
if datetime.now().day <= 3:
    from scripts.monthly_consolidation import MonthlyConsolidation
    print("[*] Checking month rollover...")
    consolidator = MonthlyConsolidation(vault_path)
    # Compress previous month for all tag notes
    consolidator.run(compress=True)
```

---

## Summary

**This stage transforms episodic memory (conversations) into semantic memory (tag notes).**

Every conversation contributes to growing tag notes that accumulate your knowledge over time. Monthly compression keeps them manageable while preserving key anchor points (last day of month).

**Result**: A second brain where you can see what you know about any topic by reading its tag note, with full timeline of learning progression.

---

**YOU HAVE ALL PERMISSIONS. EXECUTE THIS STAGE COMPLETELY. NO SHORTCUTS.**
