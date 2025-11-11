---
type: meta
title: Tag Review Queue
created: 2025-11-07
status: active
---

# Tag Review Queue

> **Purpose**: Human review of AI-proposed tags before adding to taxonomy
> **Process**: AI adds proposals here → Human reviews → Approve/Reject → Update taxonomy

---

## Pending Reviews

<!-- AI will add proposals below this line -->

### 2025-11-09 - Proposed Tag: `scikit-learn`

**Proposed by**: AI Agent (processing conversation: processing_test_realtime_002.md)
**Confidence**: 0.95
**Times encountered**: 1
**Category**: tech/programming
**Parent**: python

**Similar existing tags**:
- `tensorflow` (similarity: 0.65 - both ML frameworks)
- `pytorch` (similarity: 0.68 - both ML frameworks)

**Context/Usage**:
Found in conversations about: Machine learning classification, traditional ML algorithms

**Recommendation**:
- [x] **Approve** - Add to taxonomy as new tag (major Python ML library)
- Suggested aliases: [sklearn, scikit, sk-learn]

**Human Decision**: [To be filled]

---

### 2025-11-09 - Proposed Tag: `numpy`

**Proposed by**: AI Agent (processing conversation: processing_test_realtime_002.md)
**Confidence**: 0.95
**Times encountered**: 1
**Category**: tech/programming
**Parent**: python

**Similar existing tags**: None

**Context/Usage**:
Found in conversations about: Numerical computations, data science foundations

**Recommendation**:
- [x] **Approve** - Add to taxonomy as new tag (fundamental Python library)
- Suggested aliases: [np]

**Human Decision**: [To be filled]

---

### 2025-11-09 - Proposed Tag: `pandas`

**Proposed by**: AI Agent (processing conversation: processing_test_realtime_002.md)
**Confidence**: 0.95
**Times encountered**: 1
**Category**: tech/programming
**Parent**: python

**Similar existing tags**: None

**Context/Usage**:
Found in conversations about: Data manipulation, data preprocessing

**Recommendation**:
- [x] **Approve** - Add to taxonomy as new tag (core data science library)
- Suggested aliases: [pd]

**Human Decision**: [To be filled]

---

### 2025-11-09 - Proposed Tag: `jupyter`

**Proposed by**: AI Agent (processing conversation: processing_test_realtime_002.md)
**Confidence**: 0.95
**Times encountered**: 1
**Category**: tech/tools

**Similar existing tags**: None

**Context/Usage**:
Found in conversations about: Interactive development, data science notebooks

**Recommendation**:
- [x] **Approve** - Add to taxonomy as new tag (primary data science IDE)
- Suggested aliases: [jupyter-notebook, jupyterlab]

**Human Decision**: [To be filled]

---

### 2025-11-09 - Proposed Tag: `mlflow`

**Proposed by**: AI Agent (processing conversation: processing_test_realtime_002.md)
**Confidence**: 0.90
**Times encountered**: 1
**Category**: tech/tools

**Similar existing tags**: None

**Context/Usage**:
Found in conversations about: Experiment tracking, model registry, ML operations

**Recommendation**:
- [x] **Approve** - Add to taxonomy as new tag (ML experiment tracking platform)

**Human Decision**: [To be filled]

---

### 2025-11-09 - Proposed Tag: `machine-learning`

**Proposed by**: AI Agent (processing conversation: processing_test_realtime_002.md)
**Confidence**: 0.95
**Times encountered**: 1
**Category**: domain/data

**Similar existing tags**: None

**Context/Usage**:
Found in conversations about: ML model development, classification, training

**Recommendation**:
- [x] **Approve** - Add to taxonomy as new tag (major domain category)
- Suggested aliases: [ml, machine-learning]

**Human Decision**: [To be filled]

---

---

## Review Template

When AI proposes a new tag, it should use this format:

```markdown
### [Date] - Proposed Tag: `tag-name`

**Proposed by**: AI Agent (processing conversation: [[link]])
**Confidence**: 0.XX
**Times encountered**: X
**Category**: tech/programming (suggested)

**Similar existing tags**:
- `existing-tag-1` (similarity: 0.72)
- `existing-tag-2` (similarity: 0.65)

**Context/Usage**:
Found in conversations about: [brief description]

Example mentions:
- [[Conversation 1]] - "discussing tag-name..."
- [[Conversation 2]] - "learning about tag-name..."
- [[Conversation 3]] - "implementing tag-name..."

**Recommendation**:
- [ ] **Approve** - Add to taxonomy as new tag
- [ ] **Merge** - Use existing tag: `________`
- [ ] **Alias** - Add as alias to existing: `________`
- [ ] **Reject** - Too specific/not needed
- [ ] **Defer** - Wait for more examples (need 3+ uses)

**Human Decision**: [To be filled]

**Action Taken**: [Date + what was done]

---
```

---

## Approved Tags (Pending Taxonomy Update)

<!-- Tags approved but not yet added to main taxonomy -->

---

## Rejected Proposals (With Reasoning)

<!-- Keep history of rejected proposals to avoid re-proposing -->

---

## Review Guidelines

### When to Approve
- ✅ Tag appears in 3+ different conversations
- ✅ No existing tag covers this concept (< 0.70 similarity)
- ✅ Fits naturally into hierarchy
- ✅ Will be useful for future tagging
- ✅ Specific enough to be meaningful, general enough to be reusable

### When to Merge
- 🔀 Existing tag covers 85%+ of the same concept
- 🔀 Difference is trivial or stylistic
- 🔀 Would lead to tag fragmentation

### When to Add as Alias
- 🔗 It's a common variation of existing tag
- 🔗 Different spelling/capitalization
- 🔗 Abbreviation or full name of existing tag

### When to Reject
- ❌ Too specific to single project
- ❌ Temporary/one-time concept
- ❌ Redundant with existing tags
- ❌ Not clearly defined

### When to Defer
- ⏸️ Only 1-2 uses so far
- ⏸️ Concept is still evolving
- ⏸️ Uncertain if it's recurring theme

---

## Statistics

**Total proposals**: 6
**Approved**: 0
**Rejected**: 0
**Pending**: 6
**Average review time**: N/A

Last updated: 2025-11-09

---

## Example Entries

### Example 1: Approved

### 2025-11-07 - Proposed Tag: `llm`

**Proposed by**: AI Agent (processing conversation: [[2025-11-07 - Building LLM Chat Interface]])
**Confidence**: 0.45
**Times encountered**: 4
**Category**: tech/programming

**Similar existing tags**:
- `ai` (similarity: 0.68)
- `ml` (similarity: 0.62)

**Context/Usage**:
Found in conversations about: Working with large language models, LLM APIs, prompt engineering

Example mentions:
- [[2025-11-01 - LLM API Integration]]
- [[2025-11-03 - Prompt Engineering Discussion]]
- [[2025-11-05 - Claude API Implementation]]
- [[2025-11-07 - Building LLM Chat Interface]]

**Recommendation**:
- [x] **Approve** - Add to taxonomy as new tag

**Human Decision**: APPROVED - LLMs are a distinct subcategory of AI/ML that appears frequently

**Action Taken**: 2025-11-07 - Added to taxonomy under tech/programming with aliases [large-language-model, language-model]

---

### Example 2: Merged

### 2025-11-06 - Proposed Tag: `authentication-system`

**Proposed by**: AI Agent (processing conversation: [[2025-11-06 - Auth System Design]])
**Confidence**: 0.55
**Times encountered**: 2
**Category**: domain/security

**Similar existing tags**:
- `authentication` (similarity: 0.92)
- `auth` (similarity: 0.90)

**Context/Usage**:
Found in conversations about: Building authentication systems

**Recommendation**:
- [x] **Merge** - Use existing tag: `authentication`

**Human Decision**: MERGED - "authentication" already covers this concept adequately

**Action Taken**: 2025-11-06 - Used existing `authentication` tag, added "authentication-system" as alias

---

### Example 3: Rejected

### 2025-11-05 - Proposed Tag: `project-xyz-config`

**Proposed by**: AI Agent (processing conversation: [[2025-11-05 - Project XYZ Setup]])
**Confidence**: 0.30
**Times encountered**: 1
**Category**: project

**Similar existing tags**: None

**Context/Usage**:
Found in conversation about: Configuring specific project XYZ

**Recommendation**:
- [x] **Reject** - Too specific to single project

**Human Decision**: REJECTED - This is project-specific and won't be reused elsewhere

**Action Taken**: 2025-11-05 - Rejected, used existing `configuration` tag instead

---

## Notes

- Review this queue **weekly** or when it has 5+ pending items
- Update taxonomy file after approving tags
- Keep rejected proposals for 3 months to track patterns
- If same tag proposed 3+ times after rejection, reconsider
