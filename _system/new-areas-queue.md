---
type: meta
title: New Knowledge Areas Queue
created: 2025-11-07
status: active
---

# New Knowledge Areas Queue

> **Purpose**: Human review of AI-proposed knowledge areas before adding to taxonomy
>
> **Process**:
> 1. AI discovers potential new areas from conversation data
> 2. Proposals added here automatically
> 3. Human reviews and decides: Approve / Edit / Merge / Ignore
> 4. Approved areas added to `area-taxonomy.json`

---

## Pending Review

<!-- Processing Pipeline Agent will add proposals below this line -->

---

## Proposal Template

### [Date] - Proposed Area: "[Name]"

**Proposed by**: Processing Pipeline Agent
**Confidence**: 0.XX (0.0-1.0)
**Source Conversations**: X
**Novelty Score**: High/Medium/Low

**Why this is a new area**:
[Reasoning for the proposal]

**Tag Cluster**:
- tag-1
- tag-2
- tag-3
- tag-4

**Suggested Parent Area**: [Parent > Area > Path]
**Suggested Level**: X (1-8)

**Related Existing Areas** (similarity scores):
- Existing Area 1 (similarity: 0.XX)
- Existing Area 2 (similarity: 0.XX)

---

**Actions** (choose one):

- [ ] **Approve** - Create area as-is with proposed name
- [ ] **Edit Name** - Create area with different name: `_________________`
- [ ] **Merge** - Merge with existing area: `_________________`
- [ ] **Ignore** - Too specific / not significant enough

**Human Decision**: [To be filled by you]
**Date Resolved**: [Date you made the decision]
**Notes**: [Any additional thoughts]

---

---

## Approved Areas (Pending Taxonomy Update)

<!-- Areas you've approved but haven't been added to area-taxonomy.json yet -->

### Instructions for Adding Approved Areas

Once you approve areas above:

1. **Copy the area details** (name, parent, level, tags)
2. **Open** `_system/area-taxonomy.json`
3. **Find the parent area** in the JSON structure
4. **Add the new area** as a child object
5. **Update metadata** (total_areas count, etc.)
6. **Save** the file
7. **Move this entry** from "Pending" to "Added to Taxonomy" below
8. **Restart Processing Pipeline Agent** (so it loads new taxonomy)

---

## Recently Added to Taxonomy

<!-- Successfully added areas - keep for reference -->

---

## Rejected Proposals

<!-- Keep history to avoid re-proposing same areas -->

### Instructions for Rejected Areas

**Why keep rejected proposals?**
- Prevents AI from re-proposing the same area
- Shows patterns in what doesn't make sense as an area
- Can be revisited later if context changes

**Review monthly**: Some rejected areas might become valid as knowledge grows.

---

---

## Review Guidelines

### ✅ When to Approve

Approve if:
- Tag cluster appears in **3+ conversations**
- No existing area covers this concept (**similarity < 0.70**)
- Fits naturally into hierarchy (has clear parent)
- Will be **useful for organizing future knowledge**
- Specific enough to be meaningful, general enough to be reusable

**Example**: "Machine Learning" (if you start learning ML, this makes sense)

### ✏️ When to Edit Name

Edit name if:
- Proposed name is too technical/jargony
- Better, clearer name exists
- Need to match existing naming conventions

**Example**:
- Proposed: "LLM Inference Optimization"
- Edit to: "AI Model Optimization"

### 🔀 When to Merge

Merge if:
- Existing area already covers **85%+** of this concept
- Difference is trivial or stylistic
- Would create unnecessary fragmentation

**Example**:
- Proposed: "Python Web Frameworks"
- Merge with: "Technology > Programming > Python > Frameworks"

### ❌ When to Reject (Ignore)

Reject if:
- **Too specific to single project** (won't be reused)
- **Temporary/one-time topic** (not recurring)
- **Redundant** with multiple existing areas
- **Not clearly defined** (vague concept)
- **Only 1-2 mentions** (not enough evidence)

**Example**: "Project XYZ Configuration" (too project-specific)

### ⏸️ When to Defer

Neither approve nor reject if:
- **Only 1-2 uses** so far (wait for more data)
- **Concept is still evolving** (unclear if it's distinct)
- **Uncertain if recurring theme**

Mark as "Under Observation" and revisit in 1 month.

---

## Statistics

**Total Proposals**: 0
**Approved**: 0
**Edited**: 0
**Merged**: 0
**Rejected**: 0
**Pending**: 0

**Last Review Date**: N/A
**Next Review Due**: Weekly or when 5+ pending

---

## Example Entries

### Example 1: Approved Area

### 2025-11-07 - Proposed Area: "Machine Learning"

**Proposed by**: Processing Pipeline Agent
**Confidence**: 0.87
**Source Conversations**: 12
**Novelty Score**: High

**Why this is a new area**:
User has started multiple conversations about ML topics (neural networks, training models, PyTorch). This doesn't fit cleanly into existing "Programming" or "Data Science" areas.

**Tag Cluster**:
- machine-learning
- neural-networks
- pytorch
- tensorflow
- ml-models
- training

**Suggested Parent Area**: Technology > Programming
**Suggested Level**: 2

**Related Existing Areas**:
- Technology > Programming > Python (similarity: 0.68)
- Technology > Programming > Data (similarity: 0.55)

**Actions**:
- [x] **Approve** - Create area as-is

**Human Decision**: APPROVED - ML is distinct enough to warrant its own area. Will be useful as I learn more.
**Date Resolved**: 2025-11-07
**Notes**: Add this under Technology > Programming > Machine Learning

---

### Example 2: Edited Name

### 2025-11-08 - Proposed Area: "REST API Authentication Mechanisms"

**Proposed by**: Processing Pipeline Agent
**Confidence**: 0.72
**Source Conversations**: 5

**Why this is a new area**:
Multiple conversations about API authentication (JWT, OAuth, API keys). Specific enough to separate from general API development.

**Tag Cluster**:
- authentication
- jwt
- oauth
- api-security
- tokens

**Suggested Parent Area**: Technology > Programming > Web Development > APIs
**Suggested Level**: 5

**Actions**:
- [ ] ~~Approve~~
- [x] **Edit Name** - Create area with name: `API Authentication`

**Human Decision**: APPROVED with name change. "REST API Authentication Mechanisms" is too long and technical.
**Date Resolved**: 2025-11-08
**Notes**: Shorter name "API Authentication" is clearer and covers all API auth, not just REST

---

### Example 3: Merged

### 2025-11-09 - Proposed Area: "Python Web Development"

**Proposed by**: Processing Pipeline Agent
**Confidence**: 0.65
**Source Conversations**: 8

**Why this is a new area**:
Conversations about Flask, Django, FastAPI cluster together.

**Tag Cluster**:
- python
- flask
- django
- fastapi
- web-dev

**Suggested Parent Area**: Technology > Programming
**Suggested Level**: 2

**Related Existing Areas**:
- Technology > Programming > Python (similarity: 0.88)
- Technology > Programming > Web Development (similarity: 0.85)

**Actions**:
- [ ] ~~Approve~~
- [ ] ~~Edit Name~~
- [x] **Merge** with existing: `Technology > Programming > Web Development > Backend`

**Human Decision**: MERGED - This is already covered by "Web Development > Backend" area. Python is just the language used.
**Date Resolved**: 2025-11-09
**Notes**: Tag conversations with both "python" and "backend" tags, no new area needed

---

### Example 4: Rejected

### 2025-11-10 - Proposed Area: "Project Alpha Configuration Files"

**Proposed by**: Processing Pipeline Agent
**Confidence**: 0.45
**Source Conversations**: 3

**Why this is a new area**:
Conversations about configuring specific project "Alpha"

**Tag Cluster**:
- project-alpha
- config
- yaml
- settings

**Suggested Parent Area**: Projects
**Suggested Level**: 2

**Actions**:
- [ ] ~~Approve~~
- [ ] ~~Edit Name~~
- [ ] ~~Merge~~
- [x] **Ignore** - Too project-specific

**Human Decision**: REJECTED - This is too specific to a single project. Not a reusable knowledge area.
**Date Resolved**: 2025-11-10
**Notes**: Project-specific configuration should be tagged with the project name, not create its own area

---

## Maintenance Tasks

### Weekly Review

When queue has **5+ pending** proposals OR **weekly** (whichever comes first):

1. **Review all pending** proposals
2. **Make decisions** (approve/edit/merge/reject)
3. **Update `area-taxonomy.json`** with approved areas
4. **Move resolved** proposals to appropriate section
5. **Update statistics**

### Monthly Cleanup

Once per month:

- **Review rejected** proposals - any worth reconsidering?
- **Check approved** areas - any duplicates that emerged?
- **Merge similar** areas if needed
- **Update guidelines** based on patterns

### Quarterly Analysis

Every 3 months:

- **Analyze growth** patterns (which areas growing fastest?)
- **Identify gaps** (missing areas that should exist?)
- **Restructure** if needed (move areas to better parents)
- **Prune** unused areas (if any have 0 notes after 6 months)

---

## Notes for AI Agents

When proposing new areas:

1. **Check similarity** to all existing areas first (use Neo4j semantic search)
2. **Only propose if similarity < 0.50** to closest match
3. **Provide clear reasoning** (why is this distinct?)
4. **Include evidence** (conversation count, tag frequency)
5. **Suggest parent** (where does it fit in hierarchy?)
6. **Calculate confidence** honestly (don't over-propose)

**Proposal frequency**: Don't flood the queue. Batch proposals weekly or when you have 5+ high-confidence candidates.

---

**Last Updated**: 2025-11-07
**Next Review**: When 5+ pending proposals OR 1 week from now
